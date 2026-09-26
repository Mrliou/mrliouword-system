"""Run the configuration gate and check report prerequisites without GitHub writes."""

import itertools
import subprocess
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = yaml.safe_load((ROOT / '.github/workflows/closure-sync.yml').read_text())
STEPS = WORKFLOW['jobs']['sync-consistency']['steps']
VALIDATE = next(step for step in STEPS if step.get('id') == 'validate_config')
REPORT = next(step for step in STEPS if step['name'] == 'Generate report with actual targets')


class ClosureWorkflowWiringTests(unittest.TestCase):
    def run_gate(self, **overrides):
        env = {'PATH': '/usr/bin:/bin', 'SOURCE_REPOSITORY': 'Mrliou/mrliouword-system',
               'GITHUB_REPOSITORY': 'Mrliou/mrliouword-system',
               'TARGET_REPOSITORY_1': '', 'TARGET_REPOSITORY_2': '',
               'ALLOWED_OWNER': 'Mrliou', 'SYNC_TOKEN': '',
               'MODE': 'observe', 'APPLY_CHANGES': 'false', **overrides}
        return subprocess.run(['bash', '-e', '-c', VALIDATE['run']],
                              env=env, text=True, capture_output=True)

    def test_empty_target_and_token_are_both_reported(self):
        result = self.run_gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn('Missing Actions variable MRL_SYNC_TARGET_1', result.stdout)
        self.assertIn('Missing Actions secret SYNC_TOKEN', result.stdout)

    def test_token_is_required_even_with_valid_target(self):
        result = self.run_gate(TARGET_REPOSITORY_1='Mrliou/test-target')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Missing Actions secret SYNC_TOKEN', result.stdout)

    def test_valid_configuration_does_not_print_token(self):
        result = self.run_gate(TARGET_REPOSITORY_1='Mrliou/test-target',
                               SYNC_TOKEN='synthetic-test-value')
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('synthetic-test-value', result.stdout + result.stderr)

    def test_other_owner_requires_explicit_owner_configuration(self):
        result = self.run_gate(TARGET_REPOSITORY_1='OtherOwner/test-target',
                               SYNC_TOKEN='synthetic-test-value')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Unapproved repository owner', result.stdout)

    def test_source_authority_is_preserved(self):
        result = self.run_gate(SOURCE_REPOSITORY='OtherOwner/source')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Source must be the repository running this workflow', result.stdout)

    def test_optional_target_has_the_same_owner_gate(self):
        result = self.run_gate(TARGET_REPOSITORY_1='Mrliou/test-target',
                               TARGET_REPOSITORY_2='OtherOwner/second-target',
                               SYNC_TOKEN='synthetic-test-value')
        self.assertEqual(result.returncode, 1)

    def test_report_guard_all_prerequisite_combinations(self):
        # Interpret only the small boolean grammar used by this Actions condition.
        for cancelled, source, target1, target2, python, optional in itertools.product(
                (False, True), repeat=6):
            expression = REPORT['if'].removeprefix('${{').removesuffix('}}').strip()
            expression = expression.replace('!cancelled()', str(not cancelled))
            expression = expression.replace("env.TARGET_REPOSITORY_2 == ''", str(not optional))
            states = {'checkout_source': source, 'checkout_target_1': target1,
                      'checkout_target_2': target2, 'setup_python': python}
            for step_id, ok in states.items():
                expression = expression.replace(f"steps.{step_id}.outcome == 'success'", str(ok))
            expression = expression.replace('&&', ' and ').replace('||', ' or ')
            self.assertRegex(expression, r'^[TrueFals andor()]+$')
            actual = eval(expression, {'__builtins__': {}}, {})
            expected = not cancelled and source and target1 and python and (not optional or target2)
            self.assertEqual(actual, expected)

    def test_configuration_names_and_source_scope_are_unchanged(self):
        self.assertEqual(WORKFLOW['env']['TARGET_REPOSITORY_1'], '${{ vars.MRL_SYNC_TARGET_1 }}')
        self.assertEqual(VALIDATE['env']['SYNC_TOKEN'], '${{ secrets.SYNC_TOKEN }}')
        self.assertNotIn('environment', WORKFLOW['jobs']['sync-consistency'])
        for step in STEPS:
            if step.get('uses') == 'actions/checkout@v4':
                self.assertEqual(step['with']['token'], '${{ secrets.SYNC_TOKEN }}')


if __name__ == '__main__':
    unittest.main()
