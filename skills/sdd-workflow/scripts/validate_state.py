#!/usr/bin/env python3
"""Read-only SDD checkpoint gates and canonical planning/product capture (Python 3.11+)."""
from __future__ import annotations

import sys
# Suppress bytecode before any local or standard-library helper imports.
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from datetime import datetime

from validate_cycle import validate_cycle

SCHEMA_PATH = Path(__file__).resolve().parent.parent / 'schemas/operational-state.schema.json'
ACTIVE = {'intake', 'planning', 'planning_review', 'planning_correction', 'implementation',
          'implementation_review', 'implementation_correction', 'verification', 'final_review'}
STATES = ACTIVE | {'blocked', 'cancelled', 'complete'}
EDGES = {
    'intake': {'planning'},
    'planning': {'planning_review', 'implementation'},
    'planning_review': {'planning_correction', 'implementation'},
    'planning_correction': {'planning_review'},
    'implementation': {'implementation_review', 'verification', 'planning'},
    'implementation_review': {'implementation', 'implementation_correction', 'planning'},
    'verification': {'final_review', 'implementation_correction', 'planning'},
    'final_review': {'complete', 'implementation_correction', 'planning'},
    'implementation_correction': {'verification', 'planning'},
    'blocked': set(), 'cancelled': set(), 'complete': set(),
}
READY_PLANNING = STATES - {'intake', 'planning', 'blocked', 'cancelled'}
CODE_PHASES = {'implementation', 'implementation_review', 'implementation_correction',
               'verification', 'final_review', 'complete'}
PASSING_PHASES = {'final_review', 'complete'}
EVIDENCE_KEYS = {'id', 'path', 'sha256', 'kind', 'produced_by', 'planning_baseline_id',
                 'implementation_snapshot_id'}


class Invalid(Exception):
    def __init__(self, code, path, message, exit_status=1):
        self.code, self.path, self.message, self.exit_status = code, str(path), message, exit_status
        super().__init__(message)

    def record(self):
        return {'code': self.code, 'path': self.path, 'message': self.message}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'),
                      allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def strict_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result

    def constant(value):
        raise ValueError(f'non-finite JSON value: {value}')

    try:
        require(path.is_file() and not path.is_symlink(), 'INPUT_UNSUPPORTED', path,
                'readable regular nonsymlink JSON file required', 3)
        return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs,
                          parse_constant=constant)
    except (ValueError, UnicodeError) as error:
        raise Invalid('SCHEMA_INVALID', path, str(error)) from error
    except OSError as error:
        raise Invalid('INPUT_UNSUPPORTED', path, str(error), 3) from error


def require(condition, code, path, message, exit_status=1):
    if not condition:
        raise Invalid(code, path, message, exit_status)


def relative_path(value):
    require(isinstance(value, str) and value and '\\' not in value and '\x00' not in value,
            'SCHEMA_INVALID', str(value), 'expected nonempty POSIX relative path')
    require(not value.startswith('/') and all(p not in ('', '.', '..') for p in value.split('/')),
            'SCHEMA_INVALID', value, 'absolute, empty or traversal path component')
    return PurePosixPath(value).as_posix()


def safe_path(root, relative):
    relative = relative_path(relative)
    require(root.is_dir() and not root.is_symlink(), 'INPUT_UNSUPPORTED', root,
            'root must be an existing nonsymlink directory', 3)
    current = root
    for component in relative.split('/'):
        current /= component
        require(not current.is_symlink(), 'INPUT_UNSUPPORTED', current,
                'symlink input is unsupported', 3)
    return current


def absolute_regular(path):
    require(path.is_absolute(), 'INPUT_UNSUPPORTED', path, 'absolute path required', 3)
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        require(not current.is_symlink(), 'INPUT_UNSUPPORTED', current,
                'symlink path is unsupported', 3)
    require(path.is_file(), 'INPUT_UNSUPPORTED', path, 'readable regular file required', 3)
    return path


def file_item(path, name, executable=False):
    try:
        mode = path.lstat().st_mode
        require(stat.S_ISREG(mode), 'INPUT_UNSUPPORTED', path, 'regular file required', 3)
        contents = path.read_bytes()
    except OSError as error:
        raise Invalid('INPUT_UNSUPPORTED', path, str(error), 3) from error
    item = {'path': name, 'sha256': hashlib.sha256(contents).hexdigest(), 'size': len(contents)}
    if executable:
        item['executable'] = bool(mode & 0o111)
    else:
        item['type'] = 'file'
    return item


def byte_sorted(values):
    return sorted(values, key=lambda v: v.encode('utf-8'))


def overlaps(left, right):
    return left == right or left.startswith(right + '/') or right.startswith(left + '/')


def schema_check(value, schema, definitions, path='$'):
    """Validate the closed schema subset shipped here without third-party dependencies."""
    if '$ref' in schema:
        return schema_check(value, definitions[schema['$ref'].split('/')[-1]], definitions, path)
    if 'anyOf' in schema:
        for candidate in schema['anyOf']:
            try:
                schema_check(value, candidate, definitions, path)
                return
            except Invalid:
                continue
        raise Invalid('SCHEMA_INVALID', path, 'value does not match any permitted type')
    if 'const' in schema:
        require(type(value) is type(schema['const']) and value == schema['const'],
                'SCHEMA_INVALID', path, 'incorrect constant or version')
    if 'enum' in schema:
        require(value in schema['enum'], 'SCHEMA_INVALID', path, 'unknown enum value')
    kind = schema.get('type')
    types = {'object': dict, 'array': list, 'string': str, 'integer': int,
             'boolean': bool, 'null': type(None)}
    if kind:
        require(type(value) is types[kind], 'SCHEMA_INVALID', path, f'expected {kind}')
    if kind == 'object':
        require(set(schema.get('required', [])) <= set(value), 'SCHEMA_INVALID', path,
                'missing required fields')
        props = schema.get('properties', {})
        require(schema.get('additionalProperties') is not False or set(value) <= set(props),
                'SCHEMA_INVALID', path, 'unknown fields')
        for key, child in value.items():
            if key in props:
                schema_check(child, props[key], definitions, f'{path}.{key}')
    elif kind == 'array':
        require(len(value) >= schema.get('minItems', 0), 'SCHEMA_INVALID', path, 'array too short')
        if schema.get('uniqueItems'):
            require(len({canonical(v) for v in value}) == len(value), 'SCHEMA_INVALID', path,
                    'duplicate array entries')
        for index, child in enumerate(value):
            schema_check(child, schema['items'], definitions, f'{path}[{index}]')
    elif kind == 'string':
        require(len(value.strip()) >= schema.get('minLength', 0), 'SCHEMA_INVALID', path,
                'empty string')
        if 'pattern' in schema:
            require(re.search(schema['pattern'], value) is not None, 'SCHEMA_INVALID', path,
                    'string pattern mismatch')
    elif kind == 'integer':
        require(value >= schema.get('minimum', value), 'SCHEMA_INVALID', path, 'integer below minimum')


def _derived_ignored_name(name):
    try:
        name.encode('utf-8')
    except UnicodeError as error:
        raise Invalid('INPUT_UNSUPPORTED', name, 'non-UTF-8 ignored entry', 3) from error
    return relative_path(name)


class Context:
    def __init__(self, args):
        self.args = args
        self.workspace = args.expected_workspace
        self.speckit = args.expected_speckit_root
        # Resolve identity only after refusing symlinks in the externally supplied paths.
        for root in (self.workspace, self.speckit):
            require(root.is_absolute(), 'IDENTITY_MISMATCH', root, 'absolute identity root required')
            current = Path(root.anchor)
            for part in root.parts[1:]:
                current /= part
                require(not current.is_symlink(), 'INPUT_UNSUPPORTED', current,
                        'symlink identity root is unsupported', 3)
            require(root.is_dir(), 'INPUT_UNSUPPORTED', root, 'identity root unavailable', 3)
        self.workspace = self.workspace.resolve()
        self.speckit = self.speckit.resolve()
        require(re.fullmatch(r'[^/\\\s]+', args.expected_cycle_id) is not None and
                args.expected_cycle_id not in ('.', '..'), 'SCHEMA_INVALID', 'cycle_id', 'unsafe cycle ID')
        self.artifact_root = safe_path(self.speckit, args.expected_artifact_directory)
        absolute_regular(args.manifest)
        self.manifest = strict_json(args.manifest)
        require(isinstance(self.manifest, dict), 'SCHEMA_INVALID', args.manifest, 'manifest object required')
        require(type(self.manifest.get('schema_version')) is int,
                'SCHEMA_INVALID', args.manifest, 'manifest version must be integer')
        artifacts = self.manifest.get('artifacts')
        require(isinstance(artifacts, list), 'SCHEMA_INVALID', args.manifest, 'manifest artifacts array required')
        for name in artifacts:
            absolute_regular(safe_path(self.artifact_root, name))
        errors = validate_cycle(args.manifest, self.workspace, args.expected_source,
                                args.expected_cycle_id, self.speckit, args.expected_artifact_directory,
                                args.expected_source_id, args.expected_continuation_of, False)
        require(not errors, 'IDENTITY_MISMATCH', args.manifest, '; '.join(errors))
        self.control_relative = '.sdd/cycles/' + args.expected_cycle_id
        self.control = safe_path(self.workspace, self.control_relative)
        self.identity = {'workspace_root': str(self.workspace), 'speckit_root': str(self.speckit),
                         'manifest': str(args.manifest.resolve()), 'primary_source': args.expected_source,
                         'source_ids': args.expected_source_id,
                         'artifact_directory': args.expected_artifact_directory,
                         'identity_mode': 'new-cycle' if args.new_cycle else 'continuation',
                         'continuation_of': args.expected_continuation_of}

    def planning(self):
        names = byte_sorted([*self.manifest['artifacts'], 'sdd-cycle.json'])
        inventory = [file_item(safe_path(self.artifact_root, n), n) for n in names]
        bootstrap_path = safe_path(self.speckit, '.specify/feature.json')
        bootstrap = file_item(bootstrap_path, '.specify/feature.json')
        content = {'inventory': inventory, 'bootstrap': bootstrap}
        return {'id': digest(content), **content}

    def control_exclusions(self):
        result = {self.control_relative: {'path': self.control_relative, 'kind': 'control',
                                         'reason': 'exact active cycle control store'}}
        for path in [self.args.manifest, *(self.artifact_root / n for n in self.manifest['artifacts']),
                     self.speckit / '.specify/feature.json']:
            try:
                name = path.relative_to(self.workspace).as_posix()
            except ValueError:
                continue
            result[name] = {'path': name, 'kind': 'control', 'reason': 'exact active planning artifact/bootstrap'}
        return result

    def git(self, *args):
        result = subprocess.run(['git', '-C', str(self.workspace), *args], capture_output=True,
                                env={**os.environ, 'GIT_OPTIONAL_LOCKS': '0', 'GIT_NO_REPLACE_OBJECTS': '1'})
        require(result.returncode == 0, 'INPUT_UNSUPPORTED', self.workspace,
                'Git input unavailable: ' + result.stderr.decode('utf-8', errors='replace').strip(), 3)
        return result.stdout

    def git_names(self, *args, ignored_directories=None):
        data = self.git(*args)
        require(not data or data.endswith(b'\0'), 'INPUT_UNSUPPORTED', self.workspace,
                'unterminated Git filename record', 3)
        names = set()
        try:
            for encoded in data.split(b'\0')[:-1]:
                value = encoded.decode('utf-8')
                is_directory = ignored_directories is not None and value.endswith('/')
                # Git's ignored directory summary has exactly one slash terminator.
                # Validate the remaining components; do not normalize arbitrary paths.
                name = relative_path(value[:-1] if is_directory else value)
                require(name not in names, 'SCHEMA_INVALID', name, 'duplicate Git filename record')
                if is_directory:
                    path = safe_path(self.workspace, name)
                    require(path.is_dir(), 'INPUT_UNSUPPORTED', name,
                            'ignored summary must name an existing nonsymlink directory', 3)
                    ignored_directories.add(name)
                names.add(name)
            return names
        except UnicodeError as error:
            raise Invalid('INPUT_UNSUPPORTED', self.workspace, 'non-UTF-8 Git filename', 3) from error

    def load_scope(self, path):
        absolute_regular(path)
        try:
            name = path.relative_to(self.control).as_posix()
        except ValueError as error:
            raise Invalid('INPUT_UNSUPPORTED', path, 'scope must be in exact active cycle evidence/', 3) from error
        require(name.startswith('evidence/'), 'INPUT_UNSUPPORTED', path,
                'scope must be in exact active cycle evidence/', 3)
        scope = strict_json(path)
        keys = {'schema_version', 'required_inputs', 'excluded_outputs'}
        version = scope.get('schema_version') if type(scope) is dict else None
        if type(version) is int and version == 2:
            keys.add('required_file_aliases')
        require(type(scope) is dict and set(scope) == keys
                and type(version) is int and version in (1, 2),
                'SCHEMA_INVALID', path, 'invalid snapshot scope fields/version')
        require(type(scope['required_inputs']) is list and type(scope['excluded_outputs']) is list,
                'SCHEMA_INVALID', path, 'scope collections must be arrays')
        required = [relative_path(n) for n in scope['required_inputs']]
        require(len(required) == len(set(required)), 'SCHEMA_INVALID', path, 'duplicate required input')
        aliases = scope.get('required_file_aliases', [])
        require(type(aliases) is list, 'SCHEMA_INVALID', path, 'required file aliases must be an array')
        aliases = [self.alias_path(n) for n in aliases]
        require(len(aliases) == len(set(aliases)), 'SCHEMA_INVALID', path, 'duplicate required file alias')
        for alias in aliases:
            require(not any(overlaps(alias, n) for n in required), 'SCHEMA_INVALID', alias,
                    'file alias overlaps ordinary required input')
            require(not any(overlaps(alias, n) for n in aliases if n != alias),
                    'SCHEMA_INVALID', alias, 'file aliases overlap')
        outputs = []
        for output in scope['excluded_outputs']:
            require(type(output) is dict and set(output) == {'path', 'kind', 'reason'},
                    'SCHEMA_INVALID', path, 'invalid excluded output fields')
            relative_path(output['path'])
            require(output['kind'] in ('build', 'cache', 'temp') and
                    isinstance(output['reason'], str) and output['reason'].strip(),
                    'SCHEMA_INVALID', path, 'invalid output kind/reason')
            require(not any(overlaps(output['path'], n) for n in aliases), 'SCHEMA_INVALID',
                    output['path'], 'output exclusion overlaps required file alias')
            safe_path(self.workspace, output['path'])
            outputs.append(output)
        require(len({o['path'] for o in outputs}) == len(outputs), 'SCHEMA_INVALID', path,
                'duplicate excluded output')
        return required, aliases, outputs, {'path': path.relative_to(self.workspace).as_posix(),
                                  'kind': 'control_metadata', 'reason': 'mandatory snapshot scope bytes',
                                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    @staticmethod
    def alias_path(name):
        name = relative_path(name)
        try:
            name.encode('utf-8')
        except UnicodeError as error:
            raise Invalid('INPUT_UNSUPPORTED', repr(name), 'non-UTF-8 file alias path', 3) from error
        return name

    def file_alias(self, name, expanded):
        """Bind one declared link without ever normalizing away unsafe traversal."""
        name = self.alias_path(name)
        parent = self.workspace
        try:
            for component in name.split('/')[:-1]:
                parent /= component
                require(stat.S_ISDIR(parent.lstat().st_mode), 'INPUT_UNSUPPORTED', parent,
                        'file alias parent must be a nonsymlink directory', 3)
            path = parent / name.split('/')[-1]
            require(stat.S_ISLNK(path.lstat().st_mode), 'INPUT_UNSUPPORTED', path,
                    'declared file alias must be a symlink', 3)
            target = os.readlink(path)
            try:
                target.encode('utf-8')
            except UnicodeError as error:
                raise Invalid('INPUT_UNSUPPORTED', path, 'non-UTF-8 file alias target', 3) from error
            require(target and not target.startswith('/') and '\\' not in target and '\x00' not in target
                    and all(target.split('/')), 'INPUT_UNSUPPORTED', path,
                    'file alias target must be a nonempty relative POSIX file path', 3)
            current = parent
            parts = target.split('/')
            for index, component in enumerate(parts):
                require(stat.S_ISDIR(current.lstat().st_mode), 'INPUT_UNSUPPORTED', current,
                        'every traversed target parent must be a nonsymlink directory', 3)
                if component == '..':
                    require(current != self.workspace, 'INPUT_UNSUPPORTED', path,
                            'file alias target escapes workspace', 3)
                    current = current.parent
                elif component != '.':
                    current /= component
                mode = current.lstat().st_mode
                require(not stat.S_ISLNK(mode), 'INPUT_UNSUPPORTED', current,
                        'chained or intermediate symlink target is unsupported', 3)
                require(stat.S_ISREG(mode) if index == len(parts) - 1 else stat.S_ISDIR(mode),
                        'INPUT_UNSUPPORTED', current,
                        'target must end at a regular file through existing nonsymlink directories', 3)
            resolved = self.alias_path(current.relative_to(self.workspace).as_posix())
            require(resolved in expanded, 'SCHEMA_INVALID', name,
                    'file alias target is not an expanded required input')
            return {'path': name, 'link_target': target, 'resolved_path': resolved}
        except OSError as error:
            raise Invalid('INPUT_UNSUPPORTED', name, str(error), 3) from error

    def expand(self, name):
        path = safe_path(self.workspace, name)
        require(path.exists(), 'INPUT_UNSUPPORTED', path, 'required input is absent', 3)
        if path.is_file():
            return {name}
        require(path.is_dir(), 'INPUT_UNSUPPORTED', path, 'unsupported required input', 3)
        files = set()
        for current, directories, names in os.walk(path, followlinks=False):
            for child in [*directories, *names]:
                candidate = Path(current) / child
                require(not candidate.is_symlink(), 'INPUT_UNSUPPORTED', candidate,
                        'symlink required input is unsupported', 3)
                require(candidate.is_file() or candidate.is_dir(), 'INPUT_UNSUPPORTED', candidate,
                        'unsupported required input', 3)
                if candidate.is_file():
                    files.add(candidate.relative_to(self.workspace).as_posix())
        return files

    def product(self, revision, scope_path):
        required, aliases, outputs, scope_entry = self.load_scope(scope_path)
        actual_root = self.git('rev-parse', '--show-toplevel').decode().strip()
        require(Path(actual_root).resolve() == self.workspace, 'IDENTITY_MISMATCH', self.workspace,
                'workspace must be Git top-level root')
        base = self.git('rev-parse', '--verify', '--end-of-options', revision + '^{commit}').decode().strip()
        controls = self.control_exclusions()
        for name in aliases:
            require(not any(overlaps(name, n) for n in controls), 'SCHEMA_INVALID', name,
                    'required file alias overlaps control metadata')
        expanded = set()
        for name in required:
            require(not any(overlaps(name, n) for n in controls), 'SCHEMA_INVALID', name,
                    'required dependency overlaps control metadata')
            expanded |= self.expand(name)
        bindings = [self.file_alias(name, expanded) for name in byte_sorted(aliases)]
        alias_names = set(aliases)
        tracked = self.git_names('ls-files', '--cached', '-z')
        untracked = self.git_names('ls-files', '--others', '--exclude-standard', '-z')
        ignored_directories = set()
        ignored = self.git_names('ls-files', '--others', '--ignored', '--exclude-standard',
                                 '--directory', '-z', ignored_directories=ignored_directories)
        # Index mode inspection catches submodules even when their working directories look regular.
        for entry in self.git('ls-files', '--stage', '-z').split(b'\0'):
            if not entry:
                continue
            metadata, name = entry.split(b'\t', 1)
            mode, _, stage = metadata.split()
            require(stage == b'0', 'INPUT_UNSUPPORTED', name.decode(errors='replace'), 'unmerged Git index', 3)
            require(mode != b'160000' and (mode != b'120000' or name.decode('utf-8') in alias_names),
                    'INPUT_UNSUPPORTED', name.decode(errors='replace'),
                    'symlinks and submodules are unsupported', 3)
        source_names = {'src', 'source', 'sources', 'config', 'resources', 'resource', 'docs',
                        'specs', '.specify', '.sdd', '.git'}
        for output in outputs:
            name = output['path']
            require(not any(overlaps(name, n) for n in required), 'SCHEMA_INVALID', name,
                    'output exclusion overlaps required input')
            require(not any(overlaps(name, n) for n in tracked if n not in controls),
                    'SCHEMA_INVALID', name, 'output exclusion covers tracked product')
            require(not any(overlaps(name, n) for n in controls), 'SCHEMA_INVALID', name,
                    'output exclusion broadens exact control exception')
            require(not any(part.lower() in source_names for part in name.split('/')),
                    'SCHEMA_INVALID', name, 'source/config/resource/control exclusion is forbidden')
        source_suffixes = {'.py', '.swift', '.c', '.h', '.cpp', '.java', '.js', '.jsx', '.ts',
                           '.tsx', '.rs', '.go', '.rb', '.php', '.json', '.yaml', '.yml',
                           '.toml', '.plist', '.strings', '.md', '.png', '.jpg', '.svg'}
        for output in outputs:
            hidden = {n for n in tracked | untracked | ignored
                      if n == output['path'] or n.startswith(output['path'] + '/')}
            self_path = output['path']
            # A Git directory summary does not enumerate its source/config leaves.
            # Inspect an explicit output before permitting it to hide that subtree.
            if any(overlaps(self_path, n) for n in ignored_directories):
                path = safe_path(self.workspace, self_path)
                if path.exists():
                    hidden |= self.expand(self_path)
            require(not any(PurePosixPath(n).suffix.lower() in source_suffixes for n in hidden | {self_path}),
                    'SCHEMA_INVALID', self_path, 'source/config/resource output exclusion is forbidden')
        exclusions = [*controls.values(), *outputs, scope_entry]

        def excluded(name):
            return any(name == c or name.startswith(c + '/') for c in controls) or any(
                name == o['path'] or name.startswith(o['path'] + '/') for o in outputs)

        protected = tracked | untracked | set(required) | set(controls) | alias_names
        opaque_ignored = {name for name in ignored_directories
                          if not any(overlaps(name, other) for other in protected)}
        # Nonopaque summaries overlap included inputs. Their residual regular leaves
        # get individual ignored records, never an ancestor omission over a dependency.
        ignored_leaves = ignored - ignored_directories
        # Git omits FIFOs/devices from ls-files --others. Inspect the covered filesystem
        # independently so an unsupported untracked entry cannot disappear from evidence.
        for current, directories, filenames in os.walk(self.workspace, followlinks=False):
            keep = []
            for child in [*directories, *filenames]:
                path = Path(current) / child
                name = path.relative_to(self.workspace).as_posix()
                if name == '.git' or name.startswith('.git/') or excluded(name):
                    continue
                if name in alias_names:
                    continue  # Only exact bindings validated above bypass regular-file collection.
                mode = path.lstat().st_mode
                inherited_ignored = any(name.startswith(n + '/') for n in ignored_directories)
                disjoint = not any(overlaps(name, other) for other in protected)
                if inherited_ignored and disjoint:
                    _derived_ignored_name(name)
                    # Optional ignored links are disclosed without reading their target.
                    # Required, tracked, untracked and control inputs remain protected.
                    if stat.S_ISLNK(mode):
                        ignored_leaves.add(name)
                        continue
                require(stat.S_ISREG(mode) or stat.S_ISDIR(mode), 'INPUT_UNSUPPORTED', name,
                        'covered symlink/device/FIFO/socket is unsupported', 3)
                if child in directories:
                    # Split reopened ancestors only at genuine disjoint directories.
                    if inherited_ignored and disjoint:
                        opaque_ignored.add(name)
                    if name not in opaque_ignored:
                        keep.append(child)
                elif any(name.startswith(n + '/') for n in ignored_directories - opaque_ignored):
                    if name not in tracked | untracked:
                        ignored_leaves.add(name)
            directories[:] = keep
        names = {n for n in tracked | untracked | expanded if not excluded(n) and n not in alias_names}
        inventory = []
        for name in byte_sorted(names):
            path = safe_path(self.workspace, name)
            if not path.exists() and name in tracked and name not in expanded:
                continue  # Real tracked deletion, reflected against pinned tree below.
            inventory.append(file_item(path, name, executable=True))
        for name in byte_sorted((ignored_leaves | opaque_ignored) - expanded - alias_names):
            if not excluded(name):
                exclusions.append({'path': name, 'kind': 'ignored',
                                   'reason': ('ignored directory contents not inspected or hashed; '
                                              'semantic completeness unproven' if name in opaque_ignored else
                                              'ignored input not declared required; semantic completeness unproven')})
        current = {i['path']: i for i in inventory}
        base_items = {}
        base_aliases = {}
        for entry in self.git('ls-tree', '-r', '-z', base).split(b'\0'):
            if not entry:
                continue
            metadata, encoded_name = entry.split(b'\t', 1)
            mode, kind, blob = metadata.split()
            try:
                name = relative_path(encoded_name.decode('utf-8'))
            except UnicodeError as error:
                raise Invalid('INPUT_UNSUPPORTED', self.workspace, 'non-UTF-8 base filename', 3) from error
            if excluded(name):
                continue
            if name in alias_names and kind == b'blob' and mode == b'120000':
                base_aliases[name] = self.git('cat-file', 'blob', blob.decode('ascii'))
                continue
            require(kind == b'blob' and mode in (b'100644', b'100755'), 'INPUT_UNSUPPORTED', name,
                    'unsupported pinned-base file type', 3)
            content = self.git('cat-file', 'blob', blob.decode('ascii'))
            base_items[name] = {'sha256': hashlib.sha256(content).hexdigest(),
                                'executable': mode == b'100755'}
        changed = [name for name, item in current.items() if name not in base_items or
                   any(item[field] != base_items[name][field] for field in ('sha256', 'executable'))]
        changed.extend(b['path'] for b in bindings if b['path'] not in base_aliases or
                       b['link_target'].encode('utf-8') != base_aliases[b['path']])
        result = {'base_revision': base, 'inventory': inventory, 'changed_paths': byte_sorted(changed),
                  'deleted_paths': byte_sorted(set(base_items) - set(current)),
                  'required_inputs': byte_sorted(required),
                  'exclusions': sorted(exclusions, key=lambda i: (i['path'].encode(), i['kind']))}
        if bindings:
            result['file_aliases'] = bindings
        return {'id': digest(result), **result}


class Validator:
    def __init__(self, context, schema):
        self.context, self.schema = context, schema
        self.definitions = schema['$defs']
        self.errors = []
        self.uncommitted = []

    def error(self, code, path, message):
        self.errors.append({'code': code, 'path': str(path), 'message': message})

    def check(self, condition, code, path, message):
        if not condition:
            self.error(code, path, message)
        return condition

    def record_schema(self, value, definition):
        schema_check(value, self.definitions[definition], self.definitions)

    def history(self, state_path):
        expected = self.context.control / 'state.json'
        require(state_path == expected, 'IDENTITY_MISMATCH', state_path,
                'checkpoint must be state.json at exact externally selected cycle root')
        absolute_regular(state_path)
        state = strict_json(state_path)
        schema_check(state, self.schema, self.definitions)
        payload = {k: v for k, v in state.items() if k != 'last_event'}
        head = state['last_event']
        require(head['file'] == f"events/{head['seq']}-{head['hash']}.json", 'STATE_HISTORY_INVALID',
                'last_event.file', 'head filename does not match sequence and hash')
        chain = []
        expected_hash = head['hash']
        for seq in range(head['seq'], 0, -1):
            name = f'events/{seq}-{expected_hash}.json'
            path = safe_path(self.context.control, name)
            try:
                event = strict_json(path)
                self.record_schema(event, 'event')
                datetime.fromisoformat(event['recorded_at'].replace('Z', '+00:00'))
            except (Invalid, ValueError) as error:
                raise Invalid('STATE_HISTORY_INVALID', name, f'invalid committed event: {error}') from error
            require(event['seq'] == seq and event['cycle_id'] == payload['cycle_id'] and
                    digest(event) == expected_hash and digest(event['payload']) == event['payload_hash'],
                    'STATE_HISTORY_INVALID', name, 'event sequence/identity/content hash mismatch')
            require((seq == 1) == (event['previous_event_hash'] is None), 'STATE_HISTORY_INVALID', name,
                    'invalid first/predecessor event link')
            chain.append(event)
            expected_hash = event['previous_event_hash']
        require(chain[0]['payload'] == payload, 'STATE_HISTORY_INVALID', state_path,
                'checkpoint payload differs from committed head event')
        chain.reverse()
        for previous, current in zip(chain, chain[1:]):
            old, new = previous['payload'], current['payload']
            if new['state'] != old['state']:
                require(self.edge_allowed(old, new['state']), 'STATE_HISTORY_INVALID', current['seq'],
                        'committed history has an invalid lifecycle edge')
            require(old['identity'] == new['identity'] and old['cycle_id'] == new['cycle_id'],
                    'STATE_HISTORY_INVALID', current['seq'], 'cycle identity changed in history')
            old_reviews = old['reviews']
            require(new['reviews'][:len(old_reviews)] == old_reviews, 'STATE_HISTORY_INVALID', current['seq'],
                    'original reviewer results must remain unchanged and ordered in committed history')
            origin = old['correction_origin']
            if new['state'] == 'blocked' or old['state'] == 'blocked':
                require(new['correction_origin'] == origin, 'STATE_HISTORY_INVALID', current['seq'],
                        'blocked correction/reverification must preserve its origin')
            if old['state'] in {'implementation_correction', 'verification'} and origin is not None:
                if new['state'] == origin:
                    require(new['correction_origin'] is None, 'STATE_HISTORY_INVALID', current['seq'],
                            'origin must clear only upon return to originating phase')
                elif new['state'] in {'implementation_correction', 'verification'}:
                    require(new['correction_origin'] == origin, 'STATE_HISTORY_INVALID', current['seq'],
                            'correction origin must survive reverification')
            if new['state'] == 'implementation_correction' and old['state'] in {
                    'implementation_review', 'verification', 'final_review'}:
                require(new['correction_origin'] == (origin or old['state']), 'STATE_HISTORY_INVALID',
                        current['seq'], 'code correction origin differs from originating phase')
            if new['state'] == 'planning_correction':
                require(new['correction_origin'] == 'planning_review', 'STATE_HISTORY_INVALID',
                        current['seq'], 'planning correction must preserve planning_review origin')
            if new['state'] == 'blocked':
                require(new['resume_state'] == (old['resume_state'] if old['state'] == 'blocked' else old['state']),
                        'STATE_HISTORY_INVALID', current['seq'], 'blocked resume does not preserve last active state')
        if payload['state'] == 'blocked':
            require(len(chain) > 1, 'STATE_HISTORY_INVALID', 'resume_state',
                    'blocked resume requires committed active predecessor')
            active_predecessor = next((e['payload']['state'] for e in reversed(chain[:-1])
                                       if e['payload']['state'] in ACTIVE), None)
            require(payload['resume_state'] == active_predecessor, 'STATE_HISTORY_INVALID', 'resume_state',
                    'blocked resume differs from last committed active phase')
        committed = {f"{e['seq']}-{digest(e)}.json" for e in chain}
        events_dir = safe_path(self.context.control, 'events')
        for entry in events_dir.iterdir():
            require(not entry.is_symlink(), 'INPUT_UNSUPPORTED', entry, 'event symlink unsupported', 3)
            if entry.name not in committed:
                self.uncommitted.append(entry.name)
        return payload, chain

    @staticmethod
    def edge_allowed(payload, target):
        current = payload['state']
        if target == current:
            return True
        if payload['paused_from'] is not None:
            return False
        if current == 'blocked':
            return target == payload['resume_state'] and not payload['blockers']
        if current in ACTIVE and target in ('blocked', 'cancelled'):
            return True
        if current in {'implementation_correction', 'verification'} and payload['correction_origin'] is not None and target in ('implementation_review', 'final_review'):
            return target == payload['correction_origin']
        return target in EDGES[current]

    def evidence(self, evidence, path, planning=None, snapshot=None, current=False):
        if evidence is None:
            self.error('VERIFICATION_INCOMPLETE', path, 'required original evidence missing')
            return False
        actual = safe_path(self.context.control, evidence['path'])
        if not evidence['path'].startswith('evidence/'):
            self.error('SCHEMA_INVALID', path, 'evidence must be beneath cycle evidence/')
            return False
        try:
            item = file_item(actual, evidence['path'])
        except Invalid as error:
            self.error('VERIFICATION_INCOMPLETE', path, error.message)
            return False
        valid = self.check(item['sha256'] == evidence['sha256'] and item['size'] > 0,
                           'VERIFICATION_INCOMPLETE', path, 'original evidence missing/empty/hash mismatch')
        if current:
            valid &= self.check(evidence['planning_baseline_id'] == planning and
                                evidence['implementation_snapshot_id'] == snapshot,
                                'VERIFICATION_INCOMPLETE', path, 'evidence version is not current')
        return valid

    def inspect_all_evidence(self, value, path='$'):
        if isinstance(value, dict):
            if EVIDENCE_KEYS <= set(value):
                self.evidence(value, path)
                # Verification equivalence is a nested reference, still inspect it.
                if 'equivalence_ref' in value and value['equivalence_ref'] is not None:
                    self.inspect_all_evidence(value['equivalence_ref'], path + '.equivalence_ref')
            else:
                for key, child in value.items():
                    self.inspect_all_evidence(child, path + '.' + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                self.inspect_all_evidence(child, f'{path}[{index}]')

    def identity(self, payload):
        expected = self.context.identity
        identity = payload['identity']
        self.check(payload['cycle_id'] == self.context.args.expected_cycle_id,
                   'IDENTITY_MISMATCH', 'cycle_id', 'wrong cycle identity')
        for key in expected:
            actual, wanted = identity[key], expected[key]
            if key == 'source_ids':
                actual, wanted = set(actual), set(wanted)
            self.check(actual == wanted, 'IDENTITY_MISMATCH', 'identity.' + key, 'external identity mismatch')

    def identifiers(self):
        spec = safe_path(self.context.artifact_root, 'spec.md').read_text(encoding='utf-8')
        tasks = safe_path(self.context.artifact_root, 'tasks.md').read_text(encoding='utf-8')
        # Definition lines, not cross-references elsewhere in the package.
        criteria = set(re.findall(r'^\s*(?:[-*]\s+)?\*{0,2}((?:FR|SC)-\d+)\*{0,2}\s*:', spec, re.M))
        if not criteria:
            criteria = set(re.findall(r'\b(?:FR|SC)-\d+\b', spec))
        task_ids = set(re.findall(r'^\s*[-*]\s+\[[ xX]\]\s+(T\d+)\b', tasks, re.M))
        if not task_ids:
            task_ids = set(re.findall(r'^\s*(T\d+)\b', tasks, re.M))
        self.check(bool(criteria) and bool(task_ids), 'VERIFICATION_INCOMPLETE', 'planning_evidence',
                   'current spec/tasks must declare explicit criterion/task IDs')
        return criteria, task_ids

    def planning(self, payload, required):
        baseline, evidence, risk = (payload[k] for k in
                                     ('planning_baseline', 'planning_evidence', 'risk_assessment'))
        if not required:
            # Intake, partial planning and cancelled records preserve observations without
            # asserting later-phase readiness. Their declared bytes still must be genuine.
            bid = baseline['id'] if baseline is not None else None
            if baseline is not None:
                self.check(baseline == self.context.planning(), 'BASELINE_STALE', 'planning_baseline',
                           'declared planning bytes differ from current baseline')
            if evidence is not None:
                self.check(bid is not None and evidence['planning_baseline_id'] == bid,
                           'BASELINE_STALE', 'planning_evidence', 'planning evidence baseline mismatch')
            derived = False
            if risk is not None:
                self.check(bid is not None and risk['planning_baseline_id'] == bid,
                           'BASELINE_STALE', 'risk_assessment', 'risk baseline mismatch')
                derived = risk['escalated'] or any(c['status'] == 'triggered' for c in risk['categories'].values())
                self.check(derived == risk['planning_review_required'], 'PLANNING_REVIEW_REQUIRED',
                           'risk_assessment', 'risk review requirement contradicts trigger derivation')
            return bid, set(evidence['criteria']) if evidence else set(), set(evidence['tasks']) if evidence else set(), derived
        if not self.check(baseline is not None and evidence is not None and risk is not None,
                          'VERIFICATION_INCOMPLETE', 'planning', 'complete planning records required'):
            return None, set(), set(), False
        bid = baseline['id']
        self.check(baseline == self.context.planning(), 'BASELINE_STALE', 'planning_baseline',
                   'planning inventory/bootstrap bytes differ from frozen baseline')
        criteria, tasks = self.identifiers()
        self.check(evidence['status'] == 'coherent' and evidence['planning_baseline_id'] == bid and
                   set(evidence['criteria']) == criteria and set(evidence['tasks']) == tasks,
                   'VERIFICATION_INCOMPLETE', 'planning_evidence', 'coherent exact criterion/task coverage required')
        coverage = evidence['coverage']
        self.check(len(coverage) == len(criteria) and {c['criterion_id'] for c in coverage} == criteria,
                   'VERIFICATION_INCOMPLETE', 'planning_evidence.coverage', 'criterion coverage gap/duplicate')
        covered_tasks = set()
        for c in coverage:
            covered_tasks |= set(c['task_ids'])
            self.check(set(c['task_ids']) <= tasks and (c['task_ids'] or c['existing_behavior_evidence_refs']),
                       'VERIFICATION_INCOMPLETE', c['criterion_id'], 'criterion needs tasks or original existing behavior evidence')
            for ref in c['existing_behavior_evidence_refs']:
                self.evidence(ref, c['criterion_id'], bid, None, True)
        self.check(covered_tasks == tasks, 'VERIFICATION_INCOMPLETE', 'planning_evidence',
                   'every task needs criterion coverage')
        self.check(bool(evidence['evidence_refs']), 'VERIFICATION_INCOMPLETE', 'planning_evidence.evidence_refs',
                   'planning coherence requires original evidence')
        for ref in evidence['evidence_refs']:
            self.evidence(ref, 'planning_evidence.evidence_refs', bid, None, True)
        self.check(risk['planning_baseline_id'] == bid, 'BASELINE_STALE', 'risk_assessment', 'risk baseline stale')
        self.check(all(c['status'] != 'unresolved' for c in risk['categories'].values()),
                   'RISK_UNRESOLVED', 'risk_assessment.categories', 'unresolved risk closes eligibility')
        derived = risk['escalated'] or any(c['status'] == 'triggered' for c in risk['categories'].values())
        self.check(risk['planning_review_required'] == derived, 'PLANNING_REVIEW_REQUIRED',
                   'risk_assessment.planning_review_required', 'review requirement contradicts derived risk')
        self.check(not risk['escalated'] or bool(risk['escalation_reason']), 'RISK_UNRESOLVED',
                   'risk_assessment.escalation_reason', 'escalation requires reason')
        progress = payload['task_progress']
        self.check(len(progress) == len(tasks) and {t['task_id'] for t in progress} == tasks,
                   'VERIFICATION_INCOMPLETE', 'task_progress', 'task progress must exactly cover current tasks')
        for task in progress:
            if task['status'] == 'delivered':
                self.evidence(task['result_ref'], task['task_id'])
        requirements = payload['verification_requirements']
        self.check(len(requirements) == len(criteria) and {r['criterion_id'] for r in requirements} == criteria,
                   'VERIFICATION_INCOMPLETE', 'verification_requirements', 'exact criterion check coverage required')
        for req in requirements:
            self.check(bool(req['check_ids']) or req['equivalence_ref'] is not None,
                       'VERIFICATION_INCOMPLETE', req['criterion_id'], 'criterion requires checks or equivalence evidence')
        return bid, criteria, tasks, derived

    def unique_records(self, payload):
        for collection, key in [('assignments', 'id'), ('verification', 'id'), ('reviews', 'id'),
                                ('findings', 'id'), ('task_progress', 'task_id'),
                                ('verification_requirements', 'criterion_id')]:
            ids = [item[key] for item in payload[collection]]
            self.check(len(ids) == len(set(ids)), 'SCHEMA_INVALID', collection, 'duplicate record IDs')

    def assignments(self, payload, bid, criteria):
        assignments = {a['id']: a for a in payload['assignments']}
        active = []
        for assignment in assignments.values():
            for path in [*assignment['owned_paths'], *assignment['prohibited_paths']]:
                safe_path(self.context.workspace, path)
            if assignment['mode'] != 'write' or assignment['status'] != 'active':
                continue
            active.append(assignment)
            effective = payload['resume_state'] if payload['state'] == 'blocked' else payload['state']
            if effective != 'implementation_correction':
                self.check(not any(f['status'] != 'resolved' and f['criterion'] in assignment['criteria']
                                   for f in payload['findings']), 'DEPENDENCY_INCOMPLETE', assignment['id'],
                           'unresolved finding blocks dependent criterion work outside correction')
                self.check(not any(set(assignment['criteria']) & affected for _, affected in
                                   self.pending_intermediate(payload, criteria)),
                           'DEPENDENCY_INCOMPLETE', assignment['id'],
                           'conditioned or unresolved intermediate review blocks dependent criterion work')
            self.check(bid is not None and assignment['base_planning_id'] == bid,
                       'BASELINE_STALE', assignment['id'], 'writer requires current planning baseline')
            self.check(bool(assignment['criteria']) and set(assignment['criteria']) <= criteria and
                       bool(assignment['owned_paths']) and bool(assignment['prohibited_paths']) and
                       bool(assignment['checks']), 'SCHEMA_INVALID', assignment['id'], 'writer brief is incomplete')
            self.check(all(d in assignments and assignments[d]['status'] == 'completed' and
                           assignments[d]['result_ref'] is not None and
                           assignments[d]['base_planning_id'] == bid and
                           assignments[d]['result_ref']['planning_baseline_id'] == bid
                           for d in assignment['dependencies']),
                       'DEPENDENCY_INCOMPLETE', assignment['id'], 'writer dependency is absent or incomplete')
            self.check(not any(overlaps(o, p) for o in assignment['owned_paths']
                               for p in assignment['prohibited_paths']), 'OWNERSHIP_OVERLAP', assignment['id'],
                       'prohibited paths override owned boundary')
            self.check(not any(overlaps(o, self.context.args.expected_artifact_directory)
                               for o in assignment['owned_paths']) if self.context.speckit == self.context.workspace else True,
                       'OWNERSHIP_OVERLAP', assignment['id'], 'writer overlaps frozen planning artifacts')
        for index, left in enumerate(active):
            for right in active[index + 1:]:
                self.check(not any(overlaps(a, b) for a in left['owned_paths'] for b in right['owned_paths']),
                           'OWNERSHIP_OVERLAP', left['id'] + '/' + right['id'], 'active write boundaries overlap')
        return active

    def pending_intermediate(self, payload, criteria):
        """Latest result for each bounded review scope governs its dependent work."""
        latest = {}
        for review in payload['reviews']:
            if review['kind'] == 'intermediate':
                latest[review['scope']] = review
        findings = {f['id']: f for f in payload['findings']}
        pending = []
        for review in latest.values():
            unresolved = [findings[f] for f in review['findings']
                          if f in findings and findings[f]['status'] != 'resolved']
            snapshot = payload['implementation_snapshot']
            baseline = payload['planning_baseline']
            current_version = (baseline is not None and snapshot is not None and
                               review['planning_baseline_id'] == baseline['id'] and
                               review['implementation_snapshot_id'] == snapshot['id'])
            if (current_version and review['status'] == 'approved' and
                    not review['conditioned_checks'] and not unresolved):
                continue
            affected = {f['criterion'] for f in unresolved}
            for check_id in review['conditioned_checks']:
                mapped = {r['criterion_id'] for r in payload['verification_requirements']
                          if check_id in r['check_ids']}
                affected |= mapped or set(criteria)
            # Without a demonstrated bound, do not guess an unrelated safe criterion.
            pending.append((review, affected or set(criteria)))
        return pending

    def review_independence(self, payload):
        writers = {'Main'} | {a['owner_id'] for a in payload['assignments'] if a['mode'] == 'write'}
        finding_statuses = {f['id']: f['status'] for f in payload['findings']}
        for review in payload['reviews']:
            if review['status'] == 'approved':
                self.check(not review['conditioned_checks'] and
                           all(finding_statuses.get(f) == 'resolved' for f in review['findings']),
                           'VERIFICATION_INCOMPLETE', review['id'],
                           'approved verdict cannot retain unresolved findings or conditioned checks')
            self.check(review['reviewer_id'] not in writers, 'REVIEW_OWNER_INVALID', review['id'],
                       'reviewer is Main or a writer of reviewed result')
            self.check(bool(review['evidence_refs']) and all(e['produced_by'] == review['reviewer_id']
                       for e in review['evidence_refs']), 'REVIEW_OWNER_INVALID', review['id'],
                       'original reviewer output/provenance required')

        previous = None
        for review in payload['reviews']:
            if previous is not None and previous['reviewer_id'] != review['reviewer_id']:
                self.check(self.replacement(payload, previous['reviewer_id'], review,
                                            review['planning_baseline_id'], review['implementation_snapshot_id']),
                           'REVIEW_OWNER_INVALID', review['id'],
                           'reviewer owner changes require observed loss and full pending-scope review')
            previous = review

    def approved_review(self, payload, kind, bid, sid):
        for review in reversed(payload['reviews']):
            if review['kind'] != kind or review['planning_baseline_id'] != bid or review['implementation_snapshot_id'] != sid:
                continue
            # Latest applicable verdict governs; old approvals cannot override new corrections.
            findings = {f['id']: f for f in payload['findings']}
            if review['status'] != 'approved' or review['conditioned_checks'] or not review['evidence_refs']:
                return False
            if any(i not in findings or findings[i]['status'] != 'resolved' for i in review['findings']):
                return False
            return all(self.evidence(e, review['id'], bid, sid, True) for e in review['evidence_refs'])
        return False

    def current_snapshot(self, payload, required):
        snapshot = payload['implementation_snapshot']
        if snapshot is None:
            if required:
                self.error('VERIFICATION_INCOMPLETE', 'implementation_snapshot', 'current actual snapshot required')
            return None
        self.check(snapshot['id'] == digest({k: v for k, v in snapshot.items() if k != 'id'}),
                   'BASELINE_STALE', 'implementation_snapshot.id', 'snapshot identity does not hash declared payload')
        names = [item['path'] for item in snapshot['inventory']]
        self.check(names == byte_sorted(set(names)), 'SCHEMA_INVALID', 'implementation_snapshot.inventory',
                   'inventory must contain distinct bytewise sorted paths')
        for name in [*names, *snapshot['required_inputs'], *snapshot['changed_paths'], *snapshot['deleted_paths']]:
            relative_path(name)
        aliases = snapshot.get('file_aliases', [])
        alias_names = [b['path'] for b in aliases]
        self.check(bool(aliases) if 'file_aliases' in snapshot else True, 'SCHEMA_INVALID',
                   'implementation_snapshot.file_aliases', 'unused alias field must be omitted')
        self.check(alias_names == byte_sorted(set(alias_names)), 'SCHEMA_INVALID',
                   'implementation_snapshot.file_aliases', 'aliases must be distinct bytewise sorted paths')
        for binding in aliases:
            self.context.alias_path(binding['path'])
            self.context.alias_path(binding['resolved_path'])
            self.check(binding['resolved_path'] in names and binding['path'] not in names,
                       'SCHEMA_INVALID', binding['path'], 'alias must bind captured regular target')
        if not required:
            return snapshot['id']  # Pending correction/cancellation retains previous evidence without promoting it.
        metadata = [e for e in snapshot['exclusions'] if e['kind'] == 'control_metadata']
        if not self.check(len(metadata) == 1, 'BASELINE_STALE', 'implementation_snapshot.exclusions',
                          'snapshot must reference exact mandatory scope file bytes'):
            return snapshot['id']
        scope_path = safe_path(self.context.workspace, metadata[0]['path'])
        current = self.context.product(snapshot['base_revision'], scope_path)
        if self.check(snapshot == current, 'BASELINE_STALE', 'implementation_snapshot',
                      'actual product/base/dependency/scope bytes differ from bound snapshot'):
            self.validated_aliases = {b['path']: b['resolved_path'] for b in current.get('file_aliases', [])}
        return snapshot['id']

    def equivalence_assessed(self, payload, ref, bid, sid):
        if ref is None or not self.evidence(ref, 'equivalence_ref', bid, sid, True):
            return False
        return any(r['status'] == 'approved' and not r['conditioned_checks'] and
                   r['planning_baseline_id'] == bid and r['implementation_snapshot_id'] == sid and
                   any(e['path'] == ref['path'] and e['sha256'] == ref['sha256'] for e in r['evidence_refs'])
                   for r in payload['reviews'])

    def verification(self, payload, bid, sid):
        checks = {v['id']: v for v in payload['verification']}
        inventory = {i['path'] for i in (payload['implementation_snapshot'] or {}).get('inventory', [])}
        for requirement in payload['verification_requirements']:
            criterion = requirement['criterion_id']
            if not requirement['check_ids']:
                self.check(self.equivalence_assessed(payload, requirement['equivalence_ref'], bid, sid),
                           'VERIFICATION_INCOMPLETE', criterion, 'criterion equivalence needs current independent assessment')
            for check_id in requirement['check_ids']:
                check = checks.get(check_id)
                if not self.check(check is not None, 'VERIFICATION_INCOMPLETE', check_id, 'required check absent'):
                    continue
                valid = check['status'] == 'passed' and check['exit_status'] in (None, 0) and criterion in check['criteria']
                if check['kind'] in {'command', 'test', 'execution'}:
                    valid &= check['exit_status'] == 0
                valid &= check['planning_baseline_id'] == bid and check['dependency_coverage']['complete']
                valid &= check['implementation_snapshot_id'] == sid or self.equivalence_assessed(
                    payload, check['equivalence_ref'], bid, sid)
                for dependency in check['dependency_coverage']['required_inputs']:
                    aliases = getattr(self, 'validated_aliases', {})
                    claimed_aliases = {b['path'] for b in (payload['implementation_snapshot'] or {}).get('file_aliases', [])}
                    if dependency in claimed_aliases:
                        files = {aliases[dependency]} if dependency in aliases else set()
                    else:
                        files = self.context.expand(dependency)
                    valid &= files <= inventory and bool(files)
                self.check(valid, 'VERIFICATION_INCOMPLETE', check_id,
                           'check must pass current criterion/version/dependency coverage (or assessed equivalence)')
                self.evidence(check, check_id)

    def findings(self, payload, bid, sid, complete):
        reviews = {r['id']: r for r in payload['reviews']}
        for finding in payload['findings']:
            origin = reviews.get(finding['review_id'])
            self.check(origin is not None and finding['id'] in origin['findings'], 'FINDING_OPEN', finding['id'],
                       'finding must resolve to originating review')
            if finding['status'] == 'corrected':
                self.evidence(finding['correction_ref'], finding['id'])
            if finding['status'] == 'resolved':
                resolution = reviews.get(finding['resolution_review_id'])
                valid = origin is not None and resolution is not None
                if valid:
                    valid &= resolution['status'] == 'approved' and not resolution['conditioned_checks']
                    valid &= finding['id'] in resolution['findings']
                    valid &= resolution['planning_baseline_id'] == bid and resolution['implementation_snapshot_id'] == sid
                    valid &= finding['correction_ref'] is not None
                    if origin['reviewer_id'] != resolution['reviewer_id']:
                        valid &= self.replacement(payload, origin['reviewer_id'], resolution, bid, sid)
                self.check(valid, 'FINDING_OPEN', finding['id'],
                           'resolved requires original correction and same Reviewer current resolution (or evidenced loss)')
                if finding['correction_ref'] is not None:
                    self.evidence(finding['correction_ref'], finding['id'], bid, sid, True)
            elif complete:
                self.error('FINDING_OPEN', finding['id'], 'open/corrected finding blocks completion')
        for review in reviews.values():
            self.check(set(review['findings']) <= {f['id'] for f in payload['findings']},
                       'FINDING_OPEN', review['id'], 'review references absent findings')

    def replacement(self, payload, prior, resolution, bid, sid):
        for record in payload['reviewer_history']:
            if record['prior_reviewer_id'] != prior or record['new_reviewer_id'] != resolution['reviewer_id']:
                continue
            if record['pending_scope_review_id'] != resolution['id']:
                continue
            ref = record['unavailability_evidence_ref']
            if not self.evidence(ref, 'reviewer_history', bid, sid, True):
                continue
            # Evidence must preserve an explicit observed runtime loss; elapsed time is never proof.
            text = safe_path(self.context.control, ref['path']).read_text(encoding='utf-8')
            try:
                loss = json.loads(text)
            except ValueError:
                continue
            if (type(loss) is dict and set(loss) == {'reviewer_id', 'status', 'observation'} and
                loss['reviewer_id'] == prior and loss['status'] in ('terminated', 'unavailable') and
                isinstance(loss['observation'], str) and loss['observation'].strip() and
                not re.search(r'\b(timeout|unknown)\b', loss['observation'], re.I) and
                self.full_pending_scope(resolution)):
                return True
        return False

    @staticmethod
    def full_pending_scope(review):
        scope = review['scope'].lower()
        full = bool(re.search(r'\b(full|all)\b', scope))
        if review['kind'] == 'final':
            return full and 'integrated' in scope
        if review['kind'] == 'planning':
            return full and ('planning' in scope or 'package' in scope)
        return full and ('scope' in scope or 'pending' in scope or 'criteria' in scope)

    def phase(self, payload, target):
        self.identity(payload)
        self.unique_records(payload)
        self.inspect_all_evidence(payload)
        current = payload['state']
        self.check(self.edge_allowed(payload, target), 'SCHEMA_INVALID', 'transition',
                   'requested lifecycle edge is forbidden or paused')
        self.check(payload['paused_from'] is None or payload['paused_from'] == current,
                   'SCHEMA_INVALID', 'paused_from', 'pause must preserve active current state')
        self.check((current == 'blocked') == (payload['resume_state'] is not None),
                   'SCHEMA_INVALID', 'resume_state', 'resume_state belongs only to blocked')
        origin = payload['correction_origin']
        phase = payload['resume_state'] if current == 'blocked' else current
        if phase == 'planning_correction':
            self.check(origin == 'planning_review', 'SCHEMA_INVALID', 'correction_origin', 'planning correction origin required')
        elif phase == 'implementation_correction':
            self.check(origin in {'implementation_review', 'final_review', 'verification'}, 'SCHEMA_INVALID',
                       'correction_origin', 'code correction origin required')
            self.check(any(a['mode'] == 'write' and a['owned_paths'] for a in payload['assignments']) or
                       bool(payload['findings']), 'SCHEMA_INVALID', 'assignments', 'corrected scope must be identified')
        elif phase != 'verification':
            self.check(origin is None, 'SCHEMA_INVALID', 'correction_origin', 'origin only belongs to correction/reverification')
        # Returning to planning cannot bypass corruption/current phase gates, but intake/planning permit pending.
        required_planning = phase in READY_PLANNING or target in READY_PLANNING
        bid, criteria, tasks, review_required = self.planning(payload, required_planning)
        active = self.assignments(payload, bid, criteria)
        self.review_independence(payload)
        if active:
            self.check(phase in {'implementation', 'implementation_correction', 'implementation_review'}, 'SCHEMA_INVALID', 'assignments',
                       'active writers require implementation/correction phase')
        if phase == 'implementation_review' and target == 'implementation':
            self.check(not self.pending_intermediate(payload, criteria), 'VERIFICATION_INCOMPLETE',
                       'reviews', 'intermediate review must resolve before dependent implementation resumes')
        if target == 'planning_review':
            self.check(review_required, 'PLANNING_REVIEW_REQUIRED', 'risk_assessment',
                       'planning_review requires a derived trigger or Main escalation')
        if phase in CODE_PHASES or target in CODE_PHASES:
            if review_required:
                self.check(self.approved_review(payload, 'planning', bid, None), 'PLANNING_REVIEW_REQUIRED',
                           'reviews', 'current independent approved planning review required')
        delivered_required = phase in {'verification', 'final_review', 'complete'} or target in {
            'verification', 'final_review', 'complete'}
        # A bounded review may precede full delivery, but its release must cover actual current bytes.
        snapshot_required = delivered_required or (phase == 'implementation_review' and target == 'implementation')
        sid = self.current_snapshot(payload, snapshot_required)
        if delivered_required:
            self.check(bool(tasks) and len(payload['task_progress']) == len(tasks) and
                       all(t['status'] == 'delivered' and t['result_ref'] is not None for t in payload['task_progress']),
                       'VERIFICATION_INCOMPLETE', 'task_progress', 'all required tasks must be delivered')
            self.check(not active, 'OWNERSHIP_OVERLAP', 'assignments', 'review/verification gate has active incompatible writers')
        passing = phase in PASSING_PHASES or target in PASSING_PHASES
        if current in {'implementation_correction', 'verification'} and target in ('implementation_review', 'final_review') and origin is not None:
            passing = True
        if passing:
            self.verification(payload, bid, sid)
        complete = phase == 'complete' or target == 'complete'
        self.findings(payload, bid, sid, complete)
        if complete:
            self.check(self.approved_review(payload, 'final', bid, sid), 'FINAL_REVIEW_REQUIRED', 'reviews',
                       'current integrated independent final approved required')
            self.check(not payload['blockers'], 'DEPENDENCY_INCOMPLETE', 'blockers', 'unresolved blockers prevent completion')
        if phase == 'final_review' or target == 'final_review':
            self.check(any(r['kind'] == 'final' and r['planning_baseline_id'] == bid and
                           r['implementation_snapshot_id'] == sid for r in payload['reviews']),
                       'FINAL_REVIEW_REQUIRED', 'reviews', 'neutral current final Reviewer record required')
        return bid, sid


def parser_and_args():
    parser = argparse.ArgumentParser(description=__doc__, epilog='Product scope must be an absolute regular file in the exact cycle evidence/ directory. Its exact byte hash is represented by one control_metadata exclusion entry; this does not permit output exclusion. Capture writes JSON stdout only.')
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--expected-workspace', required=True, type=Path)
    parser.add_argument('--expected-cycle-id', required=True)
    parser.add_argument('--expected-speckit-root', required=True, type=Path)
    parser.add_argument('--expected-source', required=True)
    parser.add_argument('--expected-source-id', action='append', required=True)
    parser.add_argument('--expected-artifact-directory', required=True)
    identity = parser.add_mutually_exclusive_group(required=True)
    identity.add_argument('--new-cycle', action='store_true')
    identity.add_argument('--expected-continuation-of')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--capture', choices=('planning', 'product'))
    mode.add_argument('--state', type=Path)
    parser.add_argument('--transition', choices=sorted(STATES))
    parser.add_argument('--base-revision')
    parser.add_argument('--snapshot-scope', type=Path)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    if args.capture:
        if args.transition:
            parser.error('--transition is only valid in state mode')
        if args.capture == 'planning' and (args.base_revision or args.snapshot_scope):
            parser.error('planning capture rejects product-only flags')
        if args.capture == 'product' and (not args.base_revision or not args.snapshot_scope):
            parser.error('product capture requires --base-revision and --snapshot-scope')
    elif not args.transition or args.base_revision or args.snapshot_scope:
        parser.error('state mode requires --transition and rejects capture-only flags')
    return args


def main():
    args = parser_and_args()
    report = {'valid': False, 'requested_transition': args.transition, 'errors': [],
              'planning_baseline_id': None, 'implementation_snapshot_id': None}
    try:
        context = Context(args)
        if args.capture:
            result = context.planning() if args.capture == 'planning' else context.product(args.base_revision, args.snapshot_scope)
            print(json.dumps(result, sort_keys=True, ensure_ascii=False, allow_nan=False))
            return 0
        validator = Validator(context, strict_json(SCHEMA_PATH))
        payload, _ = validator.history(args.state)
        bid, sid = validator.phase(payload, args.transition)
        report.update(valid=not validator.errors, errors=validator.errors,
                      planning_baseline_id=bid, implementation_snapshot_id=sid)
        # Recovery disclosure is informational; orphan candidates never contribute eligibility.
        if validator.uncommitted:
            report['recovery'] = {'uncommitted_events': byte_sorted(validator.uncommitted),
                                  'commit_point': 'state.json', 'promoted': False}
        status = 0 if report['valid'] else 1
    except Invalid as error:
        report['errors'].append(error.record())
        status = error.exit_status
    except (OSError, UnicodeError) as error:
        report['errors'].append({'code': 'INPUT_UNSUPPORTED', 'path': '', 'message': str(error)})
        status = 3
    if args.json:
        print(json.dumps(report, sort_keys=True, ensure_ascii=False, allow_nan=False))
    else:
        if report['valid']:
            print('State validation passed.')
        for error in report['errors']:
            print(f"{error['code']}: {error['path']}: {error['message']}", file=sys.stderr)
        if 'recovery' in report:
            print('Uncommitted events ignored: ' + ', '.join(report['recovery']['uncommitted_events']), file=sys.stderr)
    return status


if __name__ == '__main__':
    raise SystemExit(main())
