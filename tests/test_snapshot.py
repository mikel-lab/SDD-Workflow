"""Real Git/filesystem capture regressions; no production helpers build expectations."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/sdd-workflow/scripts/validate_state.py'


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sdd-state-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.artifacts = self.root / 'specs/assigned'
        self.artifacts.mkdir(parents=True)
        (self.root / '.specify').mkdir()
        (self.root / '.specify/feature.json').write_text(json.dumps({'feature_directory': 'specs/assigned'}))
        (self.artifacts / 'spec.md').write_text('Required: **FR-001**: works\n')
        (self.artifacts / 'tasks.md').write_text('- [ ] T001 implement FR-001\n')
        self.manifest = self.artifacts / 'sdd-cycle.json'
        self.manifest.write_text(json.dumps({'schema_version': 1, 'cycle_id': 'fixture', 'workspace_root': str(self.root), 'speckit_root': str(self.root), 'primary_source': 'request:fixture', 'source_ids': ['request:fixture'], 'artifact_directory': 'specs/assigned', 'artifacts': ['spec.md', 'tasks.md'], 'continuation_of': None}))
        self.control = self.root / '.sdd/cycles/fixture'
        (self.control / 'evidence').mkdir(parents=True)
        (self.control / 'events').mkdir()
        self.scope = self.control / 'evidence/scope.json'
        self.write_scope()
        (self.root / 'src').mkdir()
        (self.root / 'src/main.py').write_text('print(1)\n')
        (self.root / '.gitignore').write_text('cache/\nsecret-input.txt\n')
        self.git('init', '-q')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'user.name', 'Fixture')
        self.git('add', 'src', '.gitignore', '.specify', 'specs')
        self.git('commit', '-qm', 'base')
        self.base = self.git('rev-parse', 'HEAD').stdout.strip()
        self.identity_args = ['--manifest', str(self.manifest), '--expected-workspace', str(self.root), '--expected-speckit-root', str(self.root), '--expected-cycle-id', 'fixture', '--expected-source', 'request:fixture', '--expected-source-id', 'request:fixture', '--expected-artifact-directory', 'specs/assigned', '--new-cycle']

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], text=True, capture_output=True, check=True)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *self.identity_args, *args], text=True, capture_output=True, timeout=15, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'GIT_OPTIONAL_LOCKS': '0'})

    def write_scope(self, required=None, outputs=None):
        self.scope.write_text(json.dumps({'schema_version': 1, 'required_inputs': required or [], 'excluded_outputs': outputs or []}))

    def capture(self, mode='product'):
        args = ['--capture', mode]
        if mode == 'product':
            args += ['--base-revision', self.base, '--snapshot-scope', str(self.scope)]
        result = self.cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return json.loads(result.stdout)


class SnapshotTests(Fixture):
    def ignored_checkout(self):
        checkout = self.root / 'cache/embedded checkout'
        checkout.mkdir(parents=True)
        subprocess.run(['git', 'init', '-q', str(checkout)], check=True, capture_output=True)
        (checkout / 'input.dat').write_bytes(b'dependency')
        return checkout

    def test_ignored_embedded_checkout_summary_is_an_explicit_unverified_omission(self):
        self.ignored_checkout()
        raw = self.git('ls-files', '--others', '--ignored', '--exclude-standard', '-z').stdout
        self.assertIn('cache/embedded checkout/\0', raw)
        snap = self.capture()
        self.assertNotIn('cache/embedded checkout/input.dat', {i['path'] for i in snap['inventory']})
        omission = next(e for e in snap['exclusions'] if e['path'] == 'cache' and e['kind'] == 'ignored')
        self.assertIn('semantic completeness unproven', omission['reason'])

    def test_unneeded_ignored_framework_links_are_omitted_without_following(self):
        framework = self.root / 'cache/binary.framework'
        framework.mkdir(parents=True)
        (framework / 'Versions').symlink_to('/outside-never-read', target_is_directory=True)
        snap = self.capture()
        self.assertTrue(any(e['path'] == 'cache' and e['kind'] == 'ignored' for e in snap['exclusions']))
        self.assertFalse(any(i['path'].startswith('cache/') for i in snap['inventory']))

    def test_required_file_inside_ignored_summary_changes_identity_without_ancestor_omission(self):
        checkout = self.ignored_checkout()
        self.write_scope(['cache/embedded checkout/input.dat'])
        before = self.capture()
        self.assertIn('cache/embedded checkout/input.dat', {i['path'] for i in before['inventory']})
        self.assertFalse(any(e['path'] in ('cache', 'cache/embedded checkout') for e in before['exclusions']))
        (checkout / 'input.dat').write_bytes(b'changed dependency')
        self.assertNotEqual(self.capture()['id'], before['id'])

    def test_ignored_directory_output_cannot_conceal_source_in_embedded_checkout(self):
        checkout = self.ignored_checkout()
        (checkout / 'module.py').write_text('source')
        self.write_scope(outputs=[{'path': 'cache', 'kind': 'build', 'reason': 'claimed generated'}])
        result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('source/config/resource output exclusion is forbidden', result.stderr)

    def test_required_ignored_tree_rejects_links_and_fifo(self):
        checkout = self.ignored_checkout()
        self.write_scope(['cache'])
        link = checkout / 'link'
        link.symlink_to('/outside-never-read')
        result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope))
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        link.unlink()
        os.mkfifo(checkout / 'pipe')
        result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope))
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)

    def test_tracked_and_reincluded_source_inside_ignored_tree_stays_covered(self):
        cache = self.root / 'cache'
        cache.mkdir()
        (cache / 'tracked.py').write_text('tracked source')
        self.git('add', '-f', 'cache/tracked.py')
        (self.root / '.gitignore').write_text('cache/*\n!cache/visible.py\n')
        (cache / 'visible.py').write_text('untracked source')
        (cache / 'other.bin').write_bytes(b'ignored output')
        snap = self.capture()
        paths = {i['path'] for i in snap['inventory']}
        self.assertIn('cache/tracked.py', paths)
        self.assertIn('cache/visible.py', paths)
        self.assertFalse(any(e['path'] == 'cache' for e in snap['exclusions']))
        (cache / 'pipe').symlink_to('/outside-never-read')
        result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope))
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)

    def test_ignored_summary_parser_rejects_malformed_duplicates_and_invalid_types(self):
        # Real Git cannot emit these corrupt records: inject only its byte boundary,
        # leaving the production parser and real filesystem validation intact.
        sys.path.insert(0, str(SCRIPT.parent))
        self.addCleanup(lambda: sys.path.remove(str(SCRIPT.parent)))
        from validate_state import Context, Invalid
        context = Context.__new__(Context)
        context.workspace = self.root
        (self.root / 'cache').mkdir()
        (self.root / 'cache-link').symlink_to('/outside-never-read', target_is_directory=True)
        os.mkfifo(self.root / 'pipe')
        records = [b'/absolute/\0', b'../escape/\0', b'cache//\0', b'cache/./\0',
                   b'cache/../escape/\0', b'\0', b'cache/\0cache/\0',
                   b'cache\0cache/\0', b'cache/\0cache\0', b'cache-link/\0',
                   b'pipe/\0', b'src/main.py/\0', b'missing/\0', b'cache/', b'\xff\0']
        for raw in records:
            with self.subTest(raw=raw), patch.object(context, 'git', return_value=raw):
                with self.assertRaises(Invalid):
                    context.git_names('ls-files', ignored_directories=set())
        with patch.object(context, 'git', return_value=b'cache/\0'):
            with self.assertRaises(Invalid):
                context.git_names('ls-files')  # Directory terminators are not regular filenames.

    def test_ignored_summary_keeps_literal_whitespace_filename(self):
        name = 'cache/space and\nnewline'
        directory = self.root / name
        directory.mkdir(parents=True)
        self.write_scope([name])
        (directory / 'input.dat').write_bytes(b'whitespace dependency')
        snap = self.capture()
        self.assertIn(name + '/input.dat', {i['path'] for i in snap['inventory']})

    def test_real_capture_covers_colocated_source_untracked_and_exact_artifacts(self):
        (self.root / 'specs/other.txt').write_text('other source')
        (self.root / '.specify/config.txt').write_text('configuration')
        snap = self.capture()
        paths = {x['path'] for x in snap['inventory']}
        self.assertIn('src/main.py', paths)
        self.assertIn('specs/other.txt', paths)
        self.assertIn('.specify/config.txt', paths)
        self.assertNotIn('specs/assigned/spec.md', paths)
        self.assertNotIn('.specify/feature.json', paths)
        self.assertFalse(any(x.startswith('.sdd/cycles/fixture/') for x in paths))
        item = next(x for x in snap['inventory'] if x['path'] == 'src/main.py')
        self.assertEqual(item['sha256'], hashlib.sha256(b'print(1)\n').hexdigest())
        self.assertEqual(item['size'], 9)
        self.assertIn('specs/other.txt', snap['changed_paths'])

    def test_staging_and_commit_do_not_change_content_identity(self):
        (self.root / 'src/main.py').write_text('print(2)\n')
        before = self.capture()
        self.git('add', 'src/main.py')
        self.assertEqual(self.capture()['id'], before['id'])
        self.git('commit', '-qm', 'changed')
        self.assertEqual(self.capture()['id'], before['id'])
        self.base = self.git('rev-parse', 'HEAD').stdout.strip()
        self.assertNotEqual(self.capture()['id'], before['id'])

    def test_deleted_and_executable_content_in_snapshot(self):
        (self.root / 'src/main.py').unlink()
        f = self.root / 'script.sh'
        f.write_text('#!/bin/sh\n')
        f.chmod(0o755)
        snap = self.capture()
        self.assertEqual(snap['deleted_paths'], ['src/main.py'])
        self.assertTrue(next(x for x in snap['inventory'] if x['path'] == 'script.sh')['executable'])

    def test_ignored_dependencies_expanded_and_hashed(self):
        (self.root / 'cache').mkdir()
        (self.root / 'cache/input.dat').write_bytes(b'input')
        self.write_scope(['cache'])
        before = self.capture()
        self.assertIn('cache/input.dat', {x['path'] for x in before['inventory']})
        (self.root / 'cache/input.dat').write_bytes(b'changed')
        self.assertNotEqual(self.capture()['id'], before['id'])

    def test_output_exclusion_cannot_hide_tracked_or_source_or_dependencies(self):
        for path, required in [('src', []), ('specs', []), ('cache', ['cache'])]:
            with self.subTest(path=path):
                (self.root / 'cache').mkdir(exist_ok=True)
                (self.root / 'cache/input.dat').write_text('input')
                self.write_scope(required, [{'path': path, 'kind': 'cache', 'reason': 'fixture output'}])
                result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope))
                self.assertEqual(result.returncode, 1, result.stderr)

    def test_invalid_scope_duplicate_unknown_keys_and_paths_rejected(self):
        invalid = ['{"schema_version":1,"schema_version":1,"required_inputs":[],"excluded_outputs":[]}', '{"schema_version":1,"required_inputs":[],"excluded_outputs":[],"unknown":true}', '{"schema_version":1,"required_inputs":["../escape"],"excluded_outputs":[]}', '{"schema_version":1,"required_inputs":null,"excluded_outputs":[]}']
        for raw in invalid:
            with self.subTest(raw=raw):
                self.scope.write_text(raw)
                result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope))
                self.assertEqual(result.returncode, 1, result.stderr)

    def test_scope_outside_evidence_and_symlinks_fail_closed(self):
        outside = self.root / 'scope.json'
        outside.write_bytes(self.scope.read_bytes())
        result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(outside))
        self.assertEqual(result.returncode, 3)
        (self.root / 'link').symlink_to('src/main.py')
        result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope))
        self.assertEqual(result.returncode, 3)

    def test_capture_does_not_write_or_read_invalid_checkpoint(self):
        state = self.control / 'state.json'
        state.write_text('invalid state must never be read for capture')
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.capture()
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_wrong_external_identity_and_cli_mode_fail(self):
        self.identity_args[self.identity_args.index('--expected-cycle-id') + 1] = 'foreign'
        self.assertEqual(self.cli('--capture', 'planning').returncode, 1)
        self.identity_args[self.identity_args.index('--expected-cycle-id') + 1] = 'fixture'
        self.assertEqual(self.cli('--capture', 'planning', '--base-revision', self.base).returncode, 2)
        self.assertEqual(self.cli('--capture', 'product').returncode, 2)

    def test_planning_bytes_change_baseline(self):
        before = self.capture('planning')
        (self.artifacts / 'spec.md').write_text('Required: **FR-001**: changed\n')
        self.assertNotEqual(self.capture('planning')['id'], before['id'])


    def test_untracked_source_file_cannot_be_hidden_as_output(self):
        (self.root / 'new-module.py').write_text('product source')
        self.write_scope(outputs=[{'path': 'new-module.py', 'kind': 'temp', 'reason': 'claimed output'}])
        result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_missing_ignored_required_input_and_fifo_fail_unsupported(self):
        self.write_scope(['secret-input.txt'])
        result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope))
        self.assertEqual(result.returncode, 3)
        self.write_scope()
        os.mkfifo(self.root / 'pipe')
        result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope))
        self.assertEqual(result.returncode, 3)

    def test_index_submodule_fails_before_partial_capture(self):
        self.git('update-index', '--add', '--cacheinfo', '160000,' + self.base + ',vendor/module')
        result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope))
        self.assertEqual(result.returncode, 3)

    def test_safe_specific_ignored_build_output_is_excluded(self):
        (self.root / 'cache').mkdir()
        (self.root / 'cache/output.bin').write_bytes(b'build output')
        self.write_scope(outputs=[{'path': 'cache/output.bin', 'kind': 'cache', 'reason': 'generated artifact'}])
        snap = self.capture()
        self.assertNotIn('cache/output.bin', {i['path'] for i in snap['inventory']})
        self.assertTrue(any(e['path'] == 'cache/output.bin' and e['kind'] == 'cache' for e in snap['exclusions']))
        (self.root / 'cache/output.bin').write_bytes(b'new generated artifact')
        self.assertEqual(self.capture()['id'], snap['id'])



    def test_planning_symlink_and_unreadable_required_artifact_fail_unsupported(self):
        artifact = self.artifacts / 'spec.md'
        artifact.unlink()
        artifact.symlink_to(self.root / 'src/main.py')
        result = self.cli('--capture', 'planning')
        self.assertEqual(result.returncode, 3, result.stderr)
        artifact.unlink()
        result = self.cli('--capture', 'planning')
        self.assertEqual(result.returncode, 3, result.stderr)


    def test_default_environment_cli_never_writes_bytecode_for_capture_or_failure(self):
        import shutil
        scripts = self.root / 'tools/scripts'
        scripts.mkdir(parents=True)
        for name in ('validate_state.py','validate_cycle.py'):
            shutil.copyfile(SCRIPT.parent / name,scripts / name)
        shutil.copytree(SCRIPT.parent.parent / 'schemas',self.root / 'tools/schemas')
        env = dict(os.environ)
        env.pop('PYTHONDONTWRITEBYTECODE',None)
        env['GIT_OPTIONAL_LOCKS']='0'
        before={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result=subprocess.run([sys.executable,str(scripts/'validate_state.py'),*self.identity_args,'--capture','product','--base-revision',self.base,'--snapshot-scope',str(self.scope)],env=env,capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        after={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after,'successful default invocation must be read-only')
        result=subprocess.run([sys.executable,str(scripts/'validate_state.py'),*self.identity_args,'--state',str(self.control/'missing.json'),'--transition','complete','--json'],env=env,capture_output=True,text=True,timeout=15)
        self.assertNotEqual(result.returncode,0)
        after={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after,'failed default invocation must be read-only')



class ProtectedIgnoredDependencyTests(Fixture):
    def sdk_fixture(self):
        sdk = self.root / 'cache/checkouts/sdk/production'
        sdk.mkdir(parents=True)
        (sdk / 'module.dat').write_bytes(b'dependency')
        self.write_scope(['cache/checkouts/sdk/production'])
        return sdk

    def test_required_sdk_and_collateral_framework_link_capture_exact_bytes(self):
        self.sdk_fixture()
        framework = self.root / 'cache/frameworks/macOS'
        framework.mkdir(parents=True)
        (framework / 'Versions').symlink_to('/outside-never-read', target_is_directory=True)
        snap = self.capture()
        item = next(i for i in snap['inventory'] if i['path'] == 'cache/checkouts/sdk/production/module.dat')
        self.assertEqual(item['sha256'], hashlib.sha256(b'dependency').hexdigest())
        self.assertEqual(item['size'], 10)
        ignored = {e['path'] for e in snap['exclusions'] if e['kind'] == 'ignored'}
        self.assertIn('cache/frameworks', ignored)
        self.assertFalse(any('cache/checkouts/sdk/production'.startswith(n + '/') for n in ignored))

    def test_optional_ignored_documentation_link_is_disclosed_without_following(self):
        self.sdk_fixture()
        (self.root / 'cache/checkouts/sdk/documentation.md').symlink_to('/outside-never-read')
        snap = self.capture()
        omission = next(e for e in snap['exclusions'] if e['path'] == 'cache/checkouts/sdk/documentation.md')
        self.assertEqual(omission['kind'], 'ignored')
        self.assertIn('semantic completeness unproven', omission['reason'])
        self.assertFalse(any(i['path'].endswith('documentation.md') for i in snap['inventory']))

    def test_required_sdk_link_and_fifo_still_rejected(self):
        sdk = self.sdk_fixture()
        for kind in ('link', 'fifo'):
            with self.subTest(kind=kind):
                path = sdk / 'unsafe'
                if kind == 'link':
                    path.symlink_to('/outside-never-read')
                else:
                    os.mkfifo(path)
                result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope), '--json')
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                self.assertFalse(json.loads(result.stdout)['valid'])
                path.unlink()

    def test_tracked_and_nonignored_links_remain_rejected(self):
        self.sdk_fixture()
        link = self.root / 'cache/owned-link'
        link.symlink_to('/outside-never-read')
        self.git('add', '-f', 'cache/owned-link')
        result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope))
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.git('rm', '-f', 'cache/owned-link')
        (self.root / 'visible-link').symlink_to('/outside-never-read')
        result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope))
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)

    def test_tracked_source_under_ignored_branch_is_not_omitted(self):
        self.sdk_fixture()
        directory = self.root / 'cache/settings'
        directory.mkdir()
        (directory / 'owned.dat').write_bytes(b'protected')
        self.git('add', '-f', 'cache/settings/owned.dat')
        snap = self.capture()
        self.assertIn('cache/settings/owned.dat', {i['path'] for i in snap['inventory']})
        self.assertNotIn('cache/settings', {e['path'] for e in snap['exclusions'] if e['kind'] == 'ignored'})

    def test_former_opaque_config_becomes_hashed_when_later_required(self):
        self.sdk_fixture()
        settings = self.root / 'cache/settings/config.json'
        settings.parent.mkdir()
        settings.write_bytes(b'{"fixture":true}')
        first = self.capture()
        self.assertIn('cache/settings', {e['path'] for e in first['exclusions'] if e['kind'] == 'ignored'})
        self.write_scope(['cache/checkouts/sdk/production', 'cache/settings/config.json'])
        second = self.capture()
        self.assertIn('cache/settings/config.json', {i['path'] for i in second['inventory']})
        self.assertNotIn('cache/settings', {e['path'] for e in second['exclusions'] if e['kind'] == 'ignored'})
        settings.write_bytes(b'{"fixture":false}')
        self.assertNotEqual(self.capture()['id'], second['id'])

    def test_derived_opaque_backslash_name_is_structured_failure(self):
        self.sdk_fixture()
        (self.root / 'cache/home\\odd').mkdir()
        result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope), '--json')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(json.loads(result.stdout)['valid'])

    def test_control_root_link_is_rejected_before_capture(self):
        self.sdk_fixture()
        parked = self.root / '.sdd/parked-fixture-controls'
        self.control.rename(parked)
        self.control.symlink_to(parked, target_is_directory=True)
        result = self.cli('--capture', 'product', '--base-revision', self.base, '--snapshot-scope', str(self.scope), '--json')
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertFalse(json.loads(result.stdout)['valid'])

    def test_derived_non_utf8_name_fails_with_structured_invalid(self):
        # APFS refuses raw non-UTF8 filenames; inject only the same byte/name boundary.
        # The collector's validation and error classification remain real.
        sys.path.insert(0, str(SCRIPT.parent))
        self.addCleanup(lambda: sys.path.remove(str(SCRIPT.parent)))
        from validate_state import _derived_ignored_name, Invalid
        with self.assertRaises(Invalid) as caught:
            _derived_ignored_name('cache/home\udcff')
        self.assertEqual(caught.exception.code, 'INPUT_UNSUPPORTED')


class RequiredFileAliasTests(Fixture):
    alias_name = 'cache/sdk/include/header.h'
    target_name = 'cache/sdk/Source/header.h'

    def alias_fixture(self):
        source = self.root / 'cache/sdk/Source'
        source.mkdir(parents=True)
        (source / 'header.h').write_bytes(b'header bytes')
        (source / 'other.h').write_bytes(b'header bytes')
        alias = self.root / self.alias_name
        alias.parent.mkdir()
        alias.symlink_to('../Source/header.h')
        self.alias_scope()
        return alias, source

    def alias_scope(self, aliases=None, required=None, outputs=None):
        self.scope.write_text(json.dumps({'schema_version': 2,
            'required_inputs': required if required is not None else ['cache/sdk/Source'],
            'required_file_aliases': aliases if aliases is not None else [self.alias_name],
            'excluded_outputs': outputs or []}))

    def reject_capture(self, code=None):
        result = self.cli('--capture', 'product', '--base-revision', self.base,
                          '--snapshot-scope', str(self.scope), '--json')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report['valid'])
        if code:
            self.assertIn(code, {e['code'] for e in report['errors']})
        return report

    def test_declared_alias_binds_required_bytes_without_ignored_ancestor(self):
        self.alias_fixture()
        snap = self.capture()
        self.assertEqual(snap['file_aliases'], [{'path': self.alias_name,
            'link_target': '../Source/header.h', 'resolved_path': self.target_name}])
        item = next(i for i in snap['inventory'] if i['path'] == self.target_name)
        self.assertEqual(item['sha256'], hashlib.sha256(b'header bytes').hexdigest())
        self.assertEqual(item['size'], 12)
        self.assertNotIn(self.alias_name, {i['path'] for i in snap['inventory']})
        for omission in snap['exclusions']:
            if omission['kind'] == 'ignored':
                self.assertFalse(self.alias_name == omission['path'] or
                                 self.alias_name.startswith(omission['path'] + '/'))

    def test_binding_raw_spelling_target_bytes_and_mode_change_identity(self):
        alias, source = self.alias_fixture()
        initial = self.capture()['id']
        for target in ['../Source/other.h', '../Source/./header.h', '../Source/../Source/header.h']:
            with self.subTest(target=target):
                alias.unlink()
                alias.symlink_to(target)
                self.assertNotEqual(self.capture()['id'], initial)
        alias.unlink()
        alias.symlink_to('../Source/header.h')
        self.assertEqual(self.capture()['id'], initial)
        (source / 'header.h').write_bytes(b'different header')
        self.assertNotEqual(self.capture()['id'], initial)
        (source / 'header.h').write_bytes(b'header bytes')
        (source / 'header.h').chmod(0o755)
        self.assertNotEqual(self.capture()['id'], initial)

    def test_safe_real_directory_then_parent_target_is_allowed(self):
        alias, source = self.alias_fixture()
        (source / 'real').mkdir()
        alias.unlink()
        alias.symlink_to('../Source/real/../header.h')
        snap = self.capture()
        self.assertEqual(snap['file_aliases'][0]['resolved_path'], self.target_name)
        self.assertEqual(snap['file_aliases'][0]['link_target'], '../Source/real/../header.h')

    def test_literal_jump_parent_rejects_symlink_missing_and_file_components(self):
        alias, source = self.alias_fixture()
        (source / 'jump-link').symlink_to(source, target_is_directory=True)
        (source / 'jump-file').write_bytes(b'not directory')
        # The unsafe siblings are outside the required individual files.
        self.alias_scope(required=[self.target_name, 'cache/sdk/Source/other.h'])
        for jump in ['jump-link', 'jump-missing', 'jump-file']:
            with self.subTest(jump=jump):
                alias.unlink()
                alias.symlink_to('../Source/' + jump + '/../header.h')
                self.reject_capture('INPUT_UNSUPPORTED')

    def test_escape_then_return_is_rejected_at_escape_component(self):
        alias, _ = self.alias_fixture()
        alias.unlink()
        alias.symlink_to('../../../../' + self.root.name + '/' + self.target_name)
        self.reject_capture('INPUT_UNSUPPORTED')

    def test_unsafe_binding_types_targets_and_spellings_fail_closed(self):
        alias, source = self.alias_fixture()
        (source / 'chain.h').symlink_to('header.h')
        self.alias_scope(required=[self.target_name, 'cache/sdk/Source/other.h'])
        targets = ['/absolute', '../Source/missing.h', '../Source/chain.h', '../Source',
                   '../Source/header.h/', '', '../Source\\header.h', '../Source/\udcff.h',
                   '../../../.sdd/cycles/fixture/evidence/scope.json']
        for target in targets:
            with self.subTest(target=repr(target)):
                alias.unlink()
                if '\udcff' in target:
                    # APFS cannot create non-UTF8 targets: inject the readlink byte boundary.
                    sys.path.insert(0, str(SCRIPT.parent))
                    try:
                        from validate_state import Context, Invalid
                        context = Context.__new__(Context)
                        context.workspace = self.root
                        alias.symlink_to('../Source/header.h')
                        with patch('os.readlink', return_value=target):
                            with self.assertRaises(Invalid):
                                context.file_alias(self.alias_name, {self.target_name})
                    finally:
                        sys.path.remove(str(SCRIPT.parent))
                elif target:
                    alias.symlink_to(target)
                    self.reject_capture()
                else:
                    alias.write_bytes(b'regular alias is forbidden')
                    self.reject_capture('INPUT_UNSUPPORTED')

    def test_target_must_be_explicitly_required_even_if_tracked(self):
        alias, _ = self.alias_fixture()
        alias.unlink()
        alias.symlink_to('../../../src/main.py')
        self.reject_capture('SCHEMA_INVALID')

    def test_alias_paths_reject_duplicate_unsafe_and_ordinary_input_overlap(self):
        self.alias_fixture()
        for aliases in [[self.alias_name, self.alias_name], ['../escape'], ['/absolute'],
                        ['cache//header.h'], ['cache/./header.h'], ['cache\\header.h'], ['cache/\udcff.h']]:
            with self.subTest(aliases=repr(aliases)):
                self.alias_scope(aliases=aliases)
                self.reject_capture()
        self.alias_scope(required=['cache/sdk'])
        self.reject_capture('SCHEMA_INVALID')

    def test_alias_parent_symlink_and_control_alias_rejected(self):
        alias, _ = self.alias_fixture()
        alternate = self.root / 'cache/sdk/alternate'
        alternate.symlink_to('include', target_is_directory=True)
        self.alias_scope(aliases=['cache/sdk/alternate/header.h'])
        self.reject_capture('INPUT_UNSUPPORTED')
        control_alias = self.control / 'evidence/header.h'
        control_alias.symlink_to('../../../../src/main.py')
        self.alias_scope(aliases=['.sdd/cycles/fixture/evidence/header.h'], required=['src/main.py'])
        self.reject_capture('SCHEMA_INVALID')

    def test_alias_output_and_ancestor_exclusion_rejected(self):
        self.alias_fixture()
        for name in [self.alias_name, 'cache/sdk/include', 'cache']:
            with self.subTest(name=name):
                self.alias_scope(outputs=[{'path': name, 'kind': 'cache', 'reason': 'claimed output'}])
                self.reject_capture()

    def test_undeclared_protected_alias_still_rejected(self):
        alias, source = self.alias_fixture()
        extra = source / 'undeclared.h'
        extra.symlink_to('header.h')
        self.reject_capture('INPUT_UNSUPPORTED')
        extra.unlink()
        self.write_scope(required=[self.alias_name])
        self.reject_capture('INPUT_UNSUPPORTED')

    def test_legacy_shape_and_scope_versions_remain_strict(self):
        before = self.capture()
        self.assertNotIn('file_aliases', before)
        self.assertEqual(before['id'], digest({k: v for k, v in before.items() if k != 'id'}))
        raw = json.loads(self.scope.read_text())
        raw['required_file_aliases'] = []
        self.scope.write_text(json.dumps(raw))
        self.reject_capture('SCHEMA_INVALID')
        raw['schema_version'] = 2
        self.scope.write_text(json.dumps(raw))
        self.assertNotIn('file_aliases', self.capture())
        del raw['required_file_aliases']
        self.scope.write_text(json.dumps(raw))
        self.reject_capture('SCHEMA_INVALID')

    def test_tracked_alias_is_explicitly_bound_and_staging_preserves_identity(self):
        alias, _ = self.alias_fixture()
        before = self.capture()
        self.git('add', '-f', self.alias_name)
        self.assertEqual(self.capture()['id'], before['id'])
        self.git('commit', '-qm', 'explicit alias')
        self.assertEqual(self.capture()['id'], before['id'])
        self.base = self.git('rev-parse', 'HEAD').stdout.strip()
        snap = self.capture()
        self.assertNotIn(self.alias_name, snap['deleted_paths'])
        self.assertNotIn(self.alias_name, snap['changed_paths'])
        alias.unlink()
        alias.symlink_to('../Source/other.h')
        self.assertIn(self.alias_name, self.capture()['changed_paths'])

    def test_nonignored_alias_and_multiple_bindings_are_captured_in_path_order(self):
        self.alias_fixture()
        (self.root / 'visible-header.h').symlink_to(self.target_name)
        extra = self.root / 'cache/sdk/include/another.h'
        extra.symlink_to('../Source/other.h')
        self.alias_scope(aliases=['visible-header.h', self.alias_name,
                                  'cache/sdk/include/another.h'])
        snap = self.capture()
        self.assertEqual([b['path'] for b in snap['file_aliases']],
                         ['cache/sdk/include/another.h', self.alias_name, 'visible-header.h'])
        self.assertNotIn('visible-header.h', {i['path'] for i in snap['inventory']})

    def test_version_two_rejects_malformed_alias_collection_and_overlapping_aliases(self):
        self.alias_fixture()
        for aliases in [None, True, {}, 'cache/header.h', [42],
                        [self.alias_name, 'cache/sdk/include']]:
            with self.subTest(aliases=aliases):
                self.alias_scope()
                raw = json.loads(self.scope.read_text())
                raw['required_file_aliases'] = aliases
                self.scope.write_text(json.dumps(raw))
                self.reject_capture('SCHEMA_INVALID')

    def test_alias_target_fifo_and_regular_parent_are_rejected(self):
        alias, source = self.alias_fixture()
        self.alias_scope(required=[self.target_name])
        os.mkfifo(source / 'pipe.h')
        alias.unlink()
        alias.symlink_to('../Source/pipe.h')
        self.reject_capture('INPUT_UNSUPPORTED')
        self.alias_scope(aliases=[self.target_name + '/alias.h'], required=['src/main.py'])
        self.reject_capture('INPUT_UNSUPPORTED')


if __name__ == '__main__':
    unittest.main()
