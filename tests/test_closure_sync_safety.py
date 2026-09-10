import sys
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from merkle_builder import build_particle_merkle_tree, discover_particle_files
from sync_manager import ClosureSyncManager
from verify_consistency import verify_consistency


def write_particle(repo: Path, relative: str, content: str) -> None:
    destination = repo / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


class ClosureSyncSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_generated_metadata_is_not_a_merkle_input(self):
        repo = self.root / "repo"
        write_particle(repo, "core/particles/a.json", '{"a": 1}')
        first = build_particle_merkle_tree(repo, repo / ".mrliou" / "merkle.json").merkle_root
        write_particle(repo, ".mrliou/health.json", '{"status": "changed"}')
        write_particle(repo, ".mrliou/sync_report.json", '{"run": 99}')
        second = build_particle_merkle_tree(repo, repo / ".mrliou" / "merkle.json").merkle_root
        self.assertEqual(first, second)
        self.assertTrue(
            all(
                path.name not in {"merkle.json", "health.json", "sync_report.json"}
                for path in discover_particle_files(repo)
            )
        )

    def test_merkle_binds_relative_path(self):
        left = self.root / "left"
        right = self.root / "right"
        write_particle(left, "core/particles/a.json", "same")
        write_particle(right, "core/particles/b.json", "same")
        self.assertNotEqual(
            build_particle_merkle_tree(left).merkle_root,
            build_particle_merkle_tree(right).merkle_root,
        )

    def test_sync_is_source_authoritative_and_detects_changed_content(self):
        source = self.root / "source"
        target = self.root / "target"
        write_particle(source, "core/particles/a.json", "authoritative")
        write_particle(target, "core/particles/a.json", "external-change")
        write_particle(target, "core/particles/external.json", "must-not-flow-back")
        manager = ClosureSyncManager(source, [target])
        manager.observe()
        resolution = manager.resolve()
        key = str(target.resolve())
        self.assertEqual(resolution["changed_in_targets"][key], ["core/particles/a.json"])
        self.assertEqual(resolution["extra_in_targets"][key], ["core/particles/external.json"])
        manager.mirror(dry_run=False)
        self.assertFalse((source / "core/particles/external.json").exists())
        self.assertEqual((target / "core/particles/a.json").read_text(encoding="utf-8"), "authoritative")

    def test_dry_run_never_writes(self):
        source = self.root / "source"
        target = self.root / "target"
        write_particle(source, "core/particles/a.json", "source")
        write_particle(target, "core/particles/a.json", "target")
        manager = ClosureSyncManager(source, [target])
        manager.observe()
        manager.resolve()
        result = manager.mirror(dry_run=True)
        self.assertEqual(result["files_copied"], 0)
        self.assertEqual((target / "core/particles/a.json").read_text(encoding="utf-8"), "target")

    def test_missing_target_fails_closed(self):
        source = self.root / "source"
        write_particle(source, "core/particles/a.json", "source")
        manager = ClosureSyncManager(source, [self.root / "missing"])
        with self.assertRaises(FileNotFoundError):
            manager.observe()

    def test_verifier_rejects_missing_and_empty_repositories(self):
        source = self.root / "source"
        empty = self.root / "empty"
        write_particle(source, "core/particles/a.json", "source")
        empty.mkdir()
        self.assertFalse(verify_consistency([source, self.root / "missing"])["consistent"])
        self.assertFalse(verify_consistency([empty])["consistent"])

    def test_unsafe_bidirectional_config_is_rejected(self):
        source = self.root / "source"
        write_particle(source, "core/particles/a.json", "source")
        write_particle(
            source,
            ".mrliou/sync.config.json",
            '{"authority":{"mode":"source_only","target_to_source":true},"auto_heal":false}',
        )
        with self.assertRaises(ValueError):
            ClosureSyncManager(source, [])

    def test_workflow_has_no_external_fallback_or_direct_main_push(self):
        content = (Path(__file__).resolve().parents[1] / ".github/workflows/closure-sync.yml").read_text(encoding="utf-8")
        self.assertNotIn("dofaromg/", content)
        self.assertNotIn("HEAD:main", content)
        self.assertNotIn("|| echo", content)
        self.assertIn("MRL_SYNC_ALLOWED_OWNER", content)
        self.assertIn("inputs.dry_run == false", content)
        self.assertIn("Mrliou_MRL_closure_sync/${{ github.run_id }}", content)


if __name__ == "__main__":
    unittest.main()
