"""Lifecycle gates exercised against committed event chains and actual evidence."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from test_snapshot import Fixture, canonical, digest

CATEGORIES = ['auth_authorization', 'security_sensitive', 'persistence_schema', 'destructive_irreversible', 'external_contracts', 'critical_infrastructure', 'architectural_boundaries', 'cross_system_consistency', 'data_loss_privacy']


class StateTests(Fixture):
    def payload(self, phase='intake'):
        return {'schema_version': 1, 'cycle_id': 'fixture', 'identity': {'workspace_root': str(self.root), 'speckit_root': str(self.root), 'manifest': str(self.manifest), 'primary_source': 'request:fixture', 'source_ids': ['request:fixture'], 'artifact_directory': 'specs/assigned', 'identity_mode': 'new-cycle', 'continuation_of': None}, 'state': phase, 'paused_from': None, 'resume_state': None, 'correction_origin': None, 'planning_baseline': None, 'planning_evidence': None, 'risk_assessment': None, 'implementation_snapshot': None, 'task_progress': [], 'verification_requirements': [], 'assignments': [], 'verification': [], 'reviews': [], 'findings': [], 'blockers': [], 'next_action': 'continue', 'reviewer_history': []}

    def evidence(self, baseline, snapshot=None, name='result', producer='Main', content='observed fixture result'):
        path = self.control / f'evidence/{name}.txt'
        path.write_text(content)
        return {'id': name, 'path': f'evidence/{name}.txt', 'sha256': hashlib.sha256(content.encode()).hexdigest(), 'kind': 'inspection', 'produced_by': producer, 'planning_baseline_id': baseline, 'implementation_snapshot_id': snapshot}

    def ready(self):
        p = self.payload('planning')
        p['planning_baseline'] = self.capture('planning')
        bid = p['planning_baseline']['id']
        e = self.evidence(bid)
        p['planning_evidence'] = {'status': 'coherent', 'planning_baseline_id': bid, 'criteria': ['FR-001'], 'tasks': ['T001'], 'coverage': [{'criterion_id': 'FR-001', 'task_ids': ['T001'], 'existing_behavior_evidence_refs': []}], 'evidence_refs': [e]}
        p['risk_assessment'] = {'id': 'risk', 'planning_baseline_id': bid, 'categories': {x: {'status': 'not_triggered', 'evidence': 'inspection no trigger'} for x in CATEGORIES}, 'escalated': False, 'escalation_reason': None, 'planning_review_required': False}
        p['task_progress'] = [{'task_id': 'T001', 'status': 'pending', 'result_ref': None}]
        p['verification_requirements'] = [{'criterion_id': 'FR-001', 'check_ids': ['check'], 'equivalence_ref': None}]
        return p

    def review(self, p, kind='planning', reviewer='Reviewer', name='review'):
        bid = p['planning_baseline']['id']
        sid = p['implementation_snapshot']['id'] if kind != 'planning' else None
        return {'id': name, 'reviewer_id': reviewer, 'kind': kind, 'scope': 'full integrated result' if kind == 'final' else 'all required planning criteria', 'planning_baseline_id': bid, 'implementation_snapshot_id': sid, 'evidence_refs': [self.evidence(bid, sid, name, reviewer)], 'findings': [], 'conditioned_checks': [], 'status': 'approved'}

    def complete_ready(self):
        p = self.ready()
        p['state'] = 'final_review'
        p['implementation_snapshot'] = self.capture()
        bid, sid = p['planning_baseline']['id'], p['implementation_snapshot']['id']
        e = self.evidence(bid, sid)
        p['task_progress'][0].update(status='delivered', result_ref=e)
        p['verification'] = [{**self.evidence(bid, sid, 'check'), 'criteria': ['FR-001'], 'command_or_inspection': 'inspect src/main.py', 'exit_status': 0, 'status': 'passed', 'dependency_coverage': {'required_inputs': ['src/main.py'], 'complete': True}, 'equivalence_ref': None}]
        p['reviews'] = [self.review(p, 'final')]
        return p

    def commit(self, payload, predecessors=None):
        last = None
        for seq, p in enumerate([*(predecessors or []), payload], 1):
            event = {'schema_version': 1, 'cycle_id': 'fixture', 'seq': seq, 'previous_event_hash': last['hash'] if last else None, 'reason': 'fixture transition', 'recorded_at': '2026-10-02T12:00:00Z', 'payload': copy.deepcopy(p), 'payload_hash': digest(p)}
            h = digest(event)
            filename = f'events/{seq}-{h}.json'
            (self.control / filename).write_bytes(canonical(event))
            last = {'seq': seq, 'hash': h, 'file': filename}
        state = {**payload, 'last_event': last}
        self.state = self.control / 'state.json'
        self.state.write_bytes(canonical(state))
        return last

    def validate(self, transition, expected=0, code=None):
        result = self.cli('--state', str(self.state), '--transition', transition, '--json')
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['valid'], expected == 0)
        if code:
            self.assertIn(code, {e['code'] for e in report['errors']})
        return report

    def test_pending_intake_self_and_planning_without_later_records(self):
        self.commit(self.payload())
        self.validate('intake')
        self.validate('planning')
        self.validate('implementation', 1)

    def test_complete_schema_not_missing_null_or_unknown(self):
        for change in ['missing', 'unknown', 'wrong_collection']:
            p = self.payload()
            if change == 'missing': del p['planning_baseline']
            if change == 'unknown': p['surprise'] = True
            if change == 'wrong_collection': p['reviews'] = None
            self.commit(p)
            self.validate('planning', 1, 'SCHEMA_INVALID')

    def test_low_risk_enters_implementation_with_current_evidence(self):
        self.commit(self.ready())
        self.validate('implementation')

    def test_each_risk_trigger_requires_current_independent_planning_review(self):
        for category in CATEGORIES:
            with self.subTest(category=category):
                p = self.ready()
                p['risk_assessment']['categories'][category]['status'] = 'triggered'
                p['risk_assessment']['planning_review_required'] = True
                self.commit(p)
                self.validate('implementation', 1, 'PLANNING_REVIEW_REQUIRED')
                p['reviews'] = [self.review(p)]
                self.commit(p)
                self.validate('implementation')

    def test_unresolved_and_falsely_derived_risk_rejected(self):
        p = self.ready()
        p['risk_assessment']['categories']['security_sensitive']['status'] = 'unresolved'
        self.commit(p)
        self.validate('implementation', 1, 'RISK_UNRESOLVED')
        p['risk_assessment']['categories']['security_sensitive']['status'] = 'triggered'
        self.commit(p)
        self.validate('implementation', 1, 'PLANNING_REVIEW_REQUIRED')

    def test_current_baseline_and_evidence_files_recomputed(self):
        p = self.ready()
        self.commit(p)
        (self.artifacts / 'spec.md').write_text('Required **FR-001** changed')
        self.validate('implementation', 1, 'BASELINE_STALE')
        p = self.ready()
        self.commit(p)
        (self.control / 'evidence/result.txt').write_text('tampered')
        self.validate('implementation', 1, 'VERIFICATION_INCOMPLETE')

    def test_actual_snapshot_change_revokes_completion(self):
        p = self.complete_ready()
        self.commit(p)
        self.validate('complete')
        (self.root / 'src/main.py').write_text('changed')
        self.validate('complete', 1, 'BASELINE_STALE')

    def test_checks_require_passed_exit_current_criterion_and_dependency_coverage(self):
        for field, value in [('status', 'incomplete'), ('exit_status', 1), ('criteria', []), ('implementation_snapshot_id', '0' * 64), ('dependency_coverage', {'required_inputs': ['src/main.py'], 'complete': False})]:
            with self.subTest(field=field):
                p = self.complete_ready()
                p['verification'][0][field] = value
                self.commit(p)
                self.validate('complete', 1, 'VERIFICATION_INCOMPLETE')

    def test_conditional_or_self_review_cannot_complete(self):
        for field, value, code in [('status', 'conditionally verified', 'FINAL_REVIEW_REQUIRED'), ('conditioned_checks', ['check'], 'FINAL_REVIEW_REQUIRED'), ('reviewer_id', 'Main', 'REVIEW_OWNER_INVALID')]:
            p = self.complete_ready()
            p['reviews'][0][field] = value
            self.commit(p)
            self.validate('complete', 1, code)

    def writer(self, p, owner='Main', path='src', name='writer'):
        return {'id': name, 'owner_id': owner, 'mode': 'write', 'objective': 'implement', 'criteria': ['FR-001'], 'owned_paths': [path], 'prohibited_paths': ['specs/assigned'], 'dependencies': [], 'base_planning_id': p['planning_baseline']['id'], 'checks': ['check'], 'result_ref': None, 'status': 'active'}

    def test_main_directory_child_and_generated_output_overlap(self):
        for parent, child in [('src', 'src/main.py'), ('build/output', 'build/output/a.json')]:
            p = self.ready()
            p['state'] = 'implementation'
            p['assignments'] = [self.writer(p, path=parent), self.writer(p, 'worker', child, 'worker')]
            self.commit(p)
            self.validate('implementation', 1, 'OWNERSHIP_OVERLAP')

    def test_writer_dependency_and_prohibition_prevent_assignment(self):
        p = self.ready()
        p['state'] = 'implementation'
        p['assignments'] = [self.writer(p)]
        p['assignments'][0]['dependencies'] = ['absent']
        self.commit(p)
        self.validate('implementation', 1, 'DEPENDENCY_INCOMPLETE')
        p['assignments'][0]['dependencies'] = []
        p['assignments'][0]['prohibited_paths'] = ['src/main.py']
        self.commit(p)
        self.validate('implementation', 1, 'OWNERSHIP_OVERLAP')

    def test_pause_and_blocked_resume_history_cannot_jump(self):
        p = self.payload('planning')
        p['paused_from'] = 'planning'
        self.commit(p)
        self.validate('planning')
        self.validate('planning_review', 1)
        active = self.payload('planning')
        blocked = self.payload('blocked')
        blocked['resume_state'] = 'planning'
        blocked['blockers'] = []
        self.commit(blocked, [active])
        self.validate('planning')
        self.validate('implementation', 1)
        blocked['resume_state'] = 'implementation'
        self.commit(blocked, [active])
        self.validate('blocked', 1, 'STATE_HISTORY_INVALID')

    def test_event_hash_corruption_checkpoint_mismatch_and_orphan_disclosed(self):
        p = self.payload()
        head = self.commit(p)
        orphan = self.control / 'events/2-uncommitted.json'
        orphan.write_text('partial event')
        report = self.validate('planning')
        self.assertIn('uncommitted', str(report))
        event = self.control / head['file']
        original = event.read_bytes()
        event.write_text('{}')
        self.validate('planning', 1, 'STATE_HISTORY_INVALID')
        event.write_bytes(original)
        state = json.loads(self.state.read_text())
        state['next_action'] = 'forged'
        self.state.write_text(json.dumps(state))
        self.validate('planning', 1, 'STATE_HISTORY_INVALID')

    def test_unknown_duplicate_and_nonfinite_json_rejected(self):
        self.commit(self.payload())
        raw = self.state.read_text()
        self.state.write_text(raw.replace('"schema_version":1', '"schema_version":1,"schema_version":1'))
        self.validate('planning', 1, 'SCHEMA_INVALID')
        self.state.write_text(raw.replace('"schema_version":1', '"schema_version":NaN'))
        self.validate('planning', 1, 'SCHEMA_INVALID')

    def test_correction_returns_only_origin_with_passing_current_checks(self):
        p = self.complete_ready()
        p['state'] = 'implementation_correction'
        p['correction_origin'] = 'final_review'
        assignment = self.writer(p)
        assignment.update(status='completed', result_ref=p['task_progress'][0]['result_ref'])
        p['assignments'] = [assignment]
        self.commit(p)
        self.validate('final_review')
        self.validate('implementation_review', 1)
        p['verification'][0]['status'] = 'incomplete'
        self.commit(p)
        self.validate('final_review', 1, 'VERIFICATION_INCOMPLETE')

    def test_finding_requires_same_reviewer_resolution(self):
        p = self.complete_ready()
        origin = self.review(p, 'final', 'original', 'origin')
        origin.update(status='corrections required', findings=['F1'])
        p['reviews'].insert(0, origin)
        p['findings'] = [{'id': 'F1', 'review_id': 'origin', 'criterion': 'FR-001', 'evidence_ref': self.evidence(p['planning_baseline']['id'], p['implementation_snapshot']['id'], 'finding'), 'correction_ref': self.evidence(p['planning_baseline']['id'], p['implementation_snapshot']['id'], 'correction'), 'resolution_review_id': 'review', 'status': 'resolved'}]
        self.commit(p)
        self.validate('complete', 1, 'FINDING_OPEN')
        p['reviews'][-1]['reviewer_id'] = 'original'
        p['reviews'][-1]['evidence_refs'] = [self.evidence(p['planning_baseline']['id'], p['implementation_snapshot']['id'], 'review', 'original')]
        p['reviews'][-1]['findings'] = ['F1']
        self.commit(p)
        self.validate('complete')


    def test_incomplete_planning_self_preserves_pending_records(self):
        p = self.ready()
        p['planning_evidence']['status'] = 'incomplete'
        p['risk_assessment']['categories']['security_sensitive']['status'] = 'unresolved'
        p['task_progress'] = []
        p['verification_requirements'] = []
        self.commit(p)
        self.validate('planning')
        self.validate('implementation', 1)

    def test_approved_review_with_unknown_conditioned_check_fails_self_check(self):
        p = self.ready()
        p['reviews'] = [self.review(p)]
        p['reviews'][0]['conditioned_checks'] = ['missing-check']
        self.commit(p)
        self.validate('planning', 1, 'VERIFICATION_INCOMPLETE')

    def test_verification_command_missing_exit_cannot_claim_passed(self):
        p = self.complete_ready()
        p['verification'][0]['kind'] = 'command'
        p['verification'][0]['command_or_inspection'] = 'python -m unittest'
        p['verification'][0]['exit_status'] = None
        self.commit(p)
        self.validate('complete', 1, 'VERIFICATION_INCOMPLETE')

    def test_snapshot_scope_bytes_change_revokes_current_evidence(self):
        p = self.complete_ready()
        self.commit(p)
        self.scope.write_text(self.scope.read_text() + '\n')
        self.validate('complete', 1, 'BASELINE_STALE')

    def test_missing_nested_and_duplicate_record_ids_fail(self):
        p = self.ready()
        del p['risk_assessment']['categories']['data_loss_privacy']
        self.commit(p)
        self.validate('implementation', 1, 'SCHEMA_INVALID')
        p = self.ready()
        p['task_progress'] *= 2
        self.commit(p)
        self.validate('implementation', 1, 'SCHEMA_INVALID')

    def test_missing_criterion_task_or_check_coverage_closes_gate(self):
        for field in ['coverage', 'tasks', 'criteria']:
            p = self.ready()
            p['planning_evidence'][field] = []
            self.commit(p)
            self.validate('implementation', 1, 'VERIFICATION_INCOMPLETE')
        p = self.complete_ready()
        p['verification_requirements'][0]['check_ids'] = []
        self.commit(p)
        self.validate('complete', 1, 'VERIFICATION_INCOMPLETE')

    def test_history_predecessor_corrupt_and_wrong_state_root(self):
        first = self.payload()
        second = self.payload('planning')
        self.commit(second, [first])
        predecessor = next((self.control / 'events').glob('1-*.json'))
        predecessor.write_text('corrupt')
        self.validate('planning', 1, 'STATE_HISTORY_INVALID')
        self.commit(second, [first])
        foreign = self.root / 'state.json'
        foreign.write_bytes(self.state.read_bytes())
        result = self.cli('--state', str(foreign), '--transition', 'planning', '--json')
        self.assertEqual(result.returncode, 1)
        self.assertIn('IDENTITY_MISMATCH', result.stdout)

    def test_current_review_waiting_and_terminal_self_checks(self):
        p = self.complete_ready()
        p['reviews'][0]['status'] = 'conditionally verified'
        p['reviews'][0]['conditioned_checks'] = ['check']
        self.commit(p)
        self.validate('final_review')
        self.validate('complete', 1, 'FINAL_REVIEW_REQUIRED')
        p['reviews'][0].update(status='approved', conditioned_checks=[])
        p['state'] = 'complete'
        self.commit(p)
        self.validate('complete')
        self.validate('planning', 1)

    def test_reviewer_loss_requires_actual_observation_full_current_review(self):
        p = self.complete_ready()
        origin = self.review(p, 'final', 'original', 'origin')
        origin.update(status='corrections required', findings=['F1'])
        p['reviews'].insert(0, origin)
        bid, sid = p['planning_baseline']['id'], p['implementation_snapshot']['id']
        p['reviews'][-1]['findings'] = ['F1']
        p['findings'] = [{'id': 'F1', 'review_id': 'origin', 'criterion': 'FR-001', 'evidence_ref': self.evidence(bid, sid, 'finding'), 'correction_ref': self.evidence(bid, sid, 'correction'), 'resolution_review_id': 'review', 'status': 'resolved'}]
        def record(status, observation):
            return {'prior_reviewer_id': 'original', 'new_reviewer_id': 'Reviewer', 'unavailability_evidence_ref': self.evidence(bid, sid, 'loss', content=json.dumps({'reviewer_id': 'original', 'status': status, 'observation': observation})), 'pending_scope_review_id': 'review'}
        p['reviewer_history'] = [record('unavailable', 'timeout elapsed')]
        self.commit(p)
        self.validate('complete', 1, 'FINDING_OPEN')
        p['reviewer_history'] = [record('terminated', 'runtime process exited; observed termination')]
        self.commit(p)
        self.validate('complete')

    def test_active_delivered_writer_still_blocks_verification(self):
        p = self.complete_ready()
        p['state'] = 'implementation'
        p['assignments'] = [self.writer(p)]
        self.commit(p)
        self.validate('verification', 1, 'OWNERSHIP_OVERLAP')



    def test_reverification_returns_to_intermediate_origin(self):
        p = self.complete_ready()
        p['state'] = 'verification'
        p['correction_origin'] = 'implementation_review'
        self.commit(p)
        self.validate('implementation_review')
        self.validate('final_review', 1)
        p['verification'][0]['status'] = 'incomplete'
        self.commit(p)
        self.validate('implementation_review', 1, 'VERIFICATION_INCOMPLETE')

    def test_correction_origin_history_cannot_clear_before_reverification(self):
        correction = self.complete_ready()
        correction['state'] = 'implementation_correction'
        correction['correction_origin'] = 'final_review'
        correction['assignments'] = [self.writer(correction)]
        correction['assignments'][0].update(status='completed', result_ref=correction['task_progress'][0]['result_ref'])
        verification = copy.deepcopy(correction)
        verification['state'] = 'verification'
        verification['correction_origin'] = None
        self.commit(verification, [correction])
        self.validate('final_review', 1, 'STATE_HISTORY_INVALID')
        verification['correction_origin'] = 'final_review'
        self.commit(verification, [correction])
        self.validate('final_review')

    def test_late_trigger_rejects_stale_planning_review_and_escalation_requires_reason(self):
        p = self.ready()
        p['risk_assessment'].update(escalated=True, escalation_reason='cross-component uncertainty', planning_review_required=True)
        self.commit(p)
        self.validate('implementation', 1, 'PLANNING_REVIEW_REQUIRED')
        p['reviews'] = [self.review(p)]
        self.commit(p)
        self.validate('implementation')
        p['risk_assessment']['escalation_reason'] = None
        self.commit(p)
        self.validate('implementation', 1, 'RISK_UNRESOLVED')
        p['risk_assessment']['escalation_reason'] = 'uncertain'
        p['reviews'][0]['planning_baseline_id'] = '0' * 64
        self.commit(p)
        self.validate('implementation', 1, 'PLANNING_REVIEW_REQUIRED')

    def test_unresolved_finding_blocks_dependent_writer(self):
        p = self.ready()
        p['state'] = 'implementation'
        origin = self.review(p)
        origin.update(status='corrections required', findings=['F1'])
        p['reviews'] = [origin]
        p['findings'] = [{'id': 'F1', 'review_id': 'review', 'criterion': 'FR-001', 'evidence_ref': self.evidence(p['planning_baseline']['id'], name='finding'), 'correction_ref': None, 'resolution_review_id': None, 'status': 'open'}]
        p['assignments'] = [self.writer(p)]
        self.commit(p)
        self.validate('implementation', 1, 'DEPENDENCY_INCOMPLETE')

    def test_state_validation_is_read_only_even_when_invalid(self):
        p = self.complete_ready()
        p['reviews'][0]['status'] = 'conditionally verified'
        self.commit(p)
        before = {str(f.relative_to(self.root)): f.read_bytes() for f in self.root.rglob('*') if f.is_file()}
        self.validate('complete', 1, 'FINAL_REVIEW_REQUIRED')
        after = {str(f.relative_to(self.root)): f.read_bytes() for f in self.root.rglob('*') if f.is_file()}
        self.assertEqual(before, after)

    def test_committed_event_fifo_fails_without_reading(self):
        self.commit(self.payload())
        event = next((self.control / 'events').glob('1-*.json'))
        event.unlink()
        import os
        os.mkfifo(event)
        try:
            result = self.cli('--state', str(self.state), '--transition', 'planning', '--json')
        except __import__('subprocess').TimeoutExpired:
            self.fail('validator attempted to read FIFO event')
        self.assertIn(result.returncode, (1, 3))
        self.assertIn('STATE_HISTORY_INVALID', result.stdout)



    def test_cancelled_preserves_historical_snapshot_without_claiming_eligibility(self):
        p = self.complete_ready()
        p['state'] = 'cancelled'
        self.commit(p)
        (self.root / 'src/main.py').write_text('later independent work')
        self.validate('cancelled')
        self.validate('complete', 1)

    def test_pending_correction_can_preserve_prior_snapshot_while_code_changes(self):
        p = self.complete_ready()
        p['state'] = 'implementation_correction'
        p['correction_origin'] = 'final_review'
        p['assignments'] = [self.writer(p)]
        p['verification'][0]['status'] = 'incomplete'
        self.commit(p)
        (self.root / 'src/main.py').write_text('correcting')
        self.validate('implementation_correction')
        self.validate('verification', 1, 'BASELINE_STALE')



    def test_completed_dependency_must_bind_current_planning_and_result(self):
        p = self.ready()
        p['state'] = 'implementation'
        prerequisite = self.writer(p, 'earlier-worker', 'other', 'earlier')
        prerequisite.update(status='completed', base_planning_id='0' * 64, result_ref=self.evidence(p['planning_baseline']['id'], name='earlier-result'))
        active = self.writer(p)
        active['dependencies'] = ['earlier']
        p['assignments'] = [prerequisite, active]
        self.commit(p)
        self.validate('implementation', 1, 'DEPENDENCY_INCOMPLETE')
        prerequisite['base_planning_id'] = p['planning_baseline']['id']
        self.commit(p)
        self.validate('implementation')

    def test_unrelated_writer_can_proceed_around_bounded_open_finding(self):
        (self.artifacts / 'spec.md').write_text('**FR-001**: first criterion\n**FR-002**: second criterion\n')
        (self.artifacts / 'tasks.md').write_text('- [ ] T001 first task\n- [ ] T002 second task\n')
        p = self.ready()
        p['state'] = 'implementation'
        p['planning_evidence']['criteria'].append('FR-002')
        p['planning_evidence']['tasks'].append('T002')
        p['planning_evidence']['coverage'].append({'criterion_id': 'FR-002', 'task_ids': ['T002'], 'existing_behavior_evidence_refs': []})
        p['task_progress'].append({'task_id': 'T002', 'status': 'pending', 'result_ref': None})
        p['verification_requirements'].append({'criterion_id': 'FR-002', 'check_ids': ['check-2'], 'equivalence_ref': None})
        review = self.review(p)
        review.update(status='corrections required', findings=['F1'])
        p['reviews'] = [review]
        p['findings'] = [{'id': 'F1', 'review_id': 'review', 'criterion': 'FR-001', 'evidence_ref': self.evidence(p['planning_baseline']['id'], name='finding'), 'correction_ref': None, 'resolution_review_id': None, 'status': 'open'}]
        writer = self.writer(p)
        writer['criteria'] = ['FR-002']
        writer['checks'] = ['check-2']
        p['assignments'] = [writer]
        self.commit(p)
        self.validate('implementation')


    def test_blocked_corrections_and_reverification_preserve_origin(self):
        for phase, origin in [('planning_correction', 'planning_review'),
                              ('implementation_correction', 'final_review'),
                              ('verification', 'final_review')]:
            with self.subTest(phase=phase):
                p = self.ready() if phase == 'planning_correction' else self.complete_ready()
                p.update(state=phase, correction_origin=origin)
                if phase == 'implementation_correction':
                    p['assignments'] = [self.writer(p)]
                blocked = copy.deepcopy(p)
                blocked.update(state='blocked', resume_state=phase)
                self.commit(blocked, [p])
                self.validate('blocked')
                self.validate(phase)
                blocked['correction_origin'] = None
                self.commit(blocked, [p])
                self.validate(phase, 1, 'STATE_HISTORY_INVALID')

    def test_conditioned_intermediate_cannot_resume_dependent_implementation(self):
        p = self.complete_ready()
        p['state'] = 'implementation_review'
        review = self.review(p, 'intermediate', name='intermediate')
        review.update(status='conditionally verified', conditioned_checks=['check'])
        p['reviews'] = [review]
        self.commit(p)
        self.validate('implementation', 1, 'VERIFICATION_INCOMPLETE')
        p['assignments'] = [self.writer(p)]
        self.commit(p)
        self.validate('implementation_review', 1, 'DEPENDENCY_INCOMPLETE')
        p['assignments'] = []
        p['reviews'].append(self.review(p, 'intermediate', name='resolved-intermediate'))
        self.commit(p)
        self.validate('implementation')
        p['reviews'][-1]['planning_baseline_id'] = '0' * 64
        self.commit(p)
        self.validate('implementation', 1, 'VERIFICATION_INCOMPLETE')
        p['reviews'][-1]['planning_baseline_id'] = p['planning_baseline']['id']
        p['reviews'][-1]['implementation_snapshot_id'] = '0' * 64
        self.commit(p)
        self.validate('implementation', 1, 'VERIFICATION_INCOMPLETE')

    def test_approved_intermediate_checks_actual_bytes_without_requiring_all_tasks_delivered(self):
        p = self.ready()
        p['state'] = 'implementation_review'
        p['implementation_snapshot'] = self.capture()
        p['reviews'] = [self.review(p, 'intermediate', name='bounded-approved')]
        self.commit(p)
        self.validate('implementation')
        (self.root / 'src/main.py').write_text('changed after bounded review')
        self.validate('implementation', 1, 'BASELINE_STALE')

    def test_independent_writer_can_work_while_other_intermediate_check_waits(self):
        (self.artifacts / 'spec.md').write_text('**FR-001**: first\n**FR-002**: second\n')
        (self.artifacts / 'tasks.md').write_text('- [ ] T001 first\n- [ ] T002 second\n')
        p = self.ready()
        p['state'] = 'implementation_review'
        p['planning_evidence']['criteria'].append('FR-002')
        p['planning_evidence']['tasks'].append('T002')
        p['planning_evidence']['coverage'].append({'criterion_id':'FR-002','task_ids':['T002'],'existing_behavior_evidence_refs':[]})
        p['task_progress'].append({'task_id':'T002','status':'pending','result_ref':None})
        p['verification_requirements'].append({'criterion_id':'FR-002','check_ids':['check-2'],'equivalence_ref':None})
        p['implementation_snapshot'] = self.capture()
        review = self.review(p, 'intermediate', name='waiting')
        review.update(status='conditionally verified', conditioned_checks=['check'])
        p['reviews'] = [review]
        writer = self.writer(p)
        writer.update(criteria=['FR-002'], checks=['check-2'])
        p['assignments'] = [writer]
        self.commit(p)
        self.validate('implementation_review')
        writer.update(criteria=['FR-001'], checks=['check'])
        self.commit(p)
        self.validate('implementation_review', 1, 'DEPENDENCY_INCOMPLETE')

    def test_reviewer_owner_change_without_findings_requires_observed_loss(self):
        p = self.complete_ready()
        p['reviews'] = [self.review(p,'intermediate','R1','prior'), self.review(p,'final','R2','final')]
        self.commit(p)
        self.validate('complete',1,'REVIEW_OWNER_INVALID')
        bid,sid = p['planning_baseline']['id'],p['implementation_snapshot']['id']
        loss = self.evidence(bid,sid,'loss',content=json.dumps({'reviewer_id':'R1','status':'terminated','observation':'runtime confirmed process termination'}))
        p['reviewer_history'] = [{'prior_reviewer_id':'R1','new_reviewer_id':'R2','unavailability_evidence_ref':loss,'pending_scope_review_id':'final'}]
        self.commit(p)
        self.validate('complete')

    def test_replacement_supports_full_pending_planning_review(self):
        p = self.ready()
        p['state'] = 'planning_review'
        p['risk_assessment'].update(escalated=True, escalation_reason='architecture', planning_review_required=True)
        old = self.review(p,'planning','R1','prior-plan')
        old['status'] = 'conditionally verified'
        new = self.review(p,'planning','R2','new-plan')
        p['reviews'] = [old,new]
        self.commit(p)
        self.validate('implementation',1,'REVIEW_OWNER_INVALID')
        loss = self.evidence(p['planning_baseline']['id'],None,'planning-loss',content=json.dumps({'reviewer_id':'R1','status':'unavailable','observation':'runtime confirmed owner cannot continue'}))
        p['reviewer_history'] = [{'prior_reviewer_id':'R1','new_reviewer_id':'R2','unavailability_evidence_ref':loss,'pending_scope_review_id':'new-plan'}]
        self.commit(p)
        self.validate('implementation')

    def test_committed_history_cannot_drop_original_reviewer_result(self):
        old = self.complete_ready()
        old['reviews'] = [self.review(old,'final','R1','original-result')]
        current = copy.deepcopy(old)
        current['reviews'] = [self.review(current,'final','R2','replacement-result')]
        self.commit(current,[old])
        self.validate('complete',1,'STATE_HISTORY_INVALID')

if __name__ == '__main__':
    unittest.main()
