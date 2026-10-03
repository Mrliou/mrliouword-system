import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from resolve_sync_targets import apply_policy, chunk, load_policy  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = "Mrliou/mrliouword-system"


def record(full_name, **overrides):
    base = {
        "full_name": full_name,
        "default_branch": "main",
        "fork": False,
        "private": False,
        "archived": False,
        "disabled": False,
        "size": 10,
    }
    base.update(overrides)
    return base


class ResolveSyncTargetsTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_policy(REPO_ROOT / ".mrliou" / "sync.targets.json")

    def test_live_policy_is_all_repositories_under_owners(self):
        # MR.liou's decision 2026-10-03: the dictionary is the language, no territory split.
        self.assertEqual(self.policy["policy"], "all_repositories_under_owners")
        self.assertTrue(self.policy["include_forks"])
        self.assertTrue(self.policy["include_private"])
        self.assertIn("dofaromg", self.policy["owners"])
        self.assertIn("Mrliou", self.policy["owners"])
        self.assertEqual(self.policy["write_gate"], "candidate_branch_only_never_default_branch")

    def test_source_is_never_a_target_even_if_not_listed(self):
        policy = dict(self.policy, exclude=[])
        resolved = apply_policy(policy, [record(SOURCE), record("dofaromg/a")], SOURCE)
        names = [t["full_name"] for t in resolved["targets"]]
        self.assertEqual(names, ["dofaromg/a"])
        self.assertEqual(resolved["skipped"][SOURCE], "excluded_by_policy")

    def test_only_declared_owners_are_accepted(self):
        resolved = apply_policy(
            self.policy,
            [record("dofaromg/a"), record("Mrliou/b"), record("someone-else/c")],
            SOURCE,
        )
        names = [t["full_name"] for t in resolved["targets"]]
        self.assertEqual(names, ["dofaromg/a", "Mrliou/b"])
        self.assertEqual(resolved["skipped"]["someone-else/c"], "owner_not_approved")

    def test_forks_and_private_repos_are_included_under_live_policy(self):
        resolved = apply_policy(
            self.policy,
            [record("dofaromg/ClickHouse", fork=True), record("Mrliou/Mrl_Mother", private=True)],
            SOURCE,
        )
        names = [t["full_name"] for t in resolved["targets"]]
        self.assertEqual(names, ["dofaromg/ClickHouse", "Mrliou/Mrl_Mother"])
        self.assertTrue(resolved["targets"][0]["fork"])
        self.assertTrue(resolved["targets"][1]["private"])

    def test_archived_disabled_empty_are_skipped(self):
        resolved = apply_policy(
            self.policy,
            [
                record("dofaromg/old", archived=True),
                record("dofaromg/off", disabled=True),
                record("dofaromg/blank", size=0),
                record("dofaromg/nobranch", default_branch=None),
            ],
            SOURCE,
        )
        self.assertEqual(resolved["targets"], [])
        self.assertEqual(resolved["skipped"]["dofaromg/old"], "archived")
        self.assertEqual(resolved["skipped"]["dofaromg/off"], "disabled")
        self.assertEqual(resolved["skipped"]["dofaromg/blank"], "empty")
        self.assertEqual(resolved["skipped"]["dofaromg/nobranch"], "empty")

    def test_fork_policy_can_be_tightened(self):
        policy = dict(self.policy, include_forks=False)
        resolved = apply_policy(policy, [record("dofaromg/odoo", fork=True)], SOURCE)
        self.assertEqual(resolved["targets"], [])
        self.assertEqual(resolved["skipped"]["dofaromg/odoo"], "fork_not_included")

    def test_include_extra_only_adds_approved_owner_repos(self):
        policy = dict(self.policy, include_extra=["dofaromg/manual", "evil/manual"])
        resolved = apply_policy(policy, [], SOURCE)
        names = [t["full_name"] for t in resolved["targets"]]
        self.assertEqual(names, ["dofaromg/manual"])
        self.assertEqual(resolved["skipped"]["evil/manual"], "owner_not_approved")

    def test_chunking_matches_policy_size(self):
        targets = [record(f"dofaromg/r{i:03d}") for i in range(45)]
        groups = chunk(targets, self.policy["chunk_size"])
        self.assertEqual(len(groups), 3)
        self.assertEqual(sum(len(g) for g in groups), 45)

    def test_malformed_policy_names_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p.json"
            path.write_text(json.dumps({"owners": ["x"], "exclude": ["not-a-repo"]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_policy(path)


if __name__ == "__main__":
    unittest.main()
