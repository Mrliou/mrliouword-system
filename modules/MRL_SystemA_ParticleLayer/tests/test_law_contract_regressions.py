"""LAW-0 authority and LAW-2 compatibility regressions.

origin_signature: MrLiouWord
Uses unittest so the same regressions also run without pytest installed.
"""

import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_DIR))

from MRL_SystemA_ParticleLayer import (  # noqa: E402 - legacy module import path
    FileIndexAdapter,
    MemoryAdapter,
    OriginSignatureError,
    ParticleLayerError,
    PersonaAdapter,
    RoundtripViolation,
    verify_law2,
)
from Mrliou_MRL_Law2_Report_v1 import (  # noqa: E402
    Mrliou_MRL_build_law2_report as build_report,
)
from Mrliou_MRL_Provenance_v1 import (  # noqa: E402
    Mrliou_MRL_classify_source as classify,
)


class LawContractRegressions(unittest.TestCase):
    def test_conflicting_signatures_rejected_in_both_directions(self):
        for origin, signature in (
            ("MrLiouWord", "foreign"), ("foreign", "MrLiouWord")
        ):
            row = {"id": "conflict", "origin": origin,
                   "origin_signature": signature, "payload": {"x": [1, 2]}}
            original = deepcopy(row)
            self.assertEqual(classify(row), "foreign_marked")
            for adapter in (PersonaAdapter(), MemoryAdapter(), FileIndexAdapter()):
                with self.assertRaises(OriginSignatureError):
                    adapter.to_unified(row)
                with self.assertRaises(OriginSignatureError):
                    verify_law2(adapter, [row])
            report = build_report(PersonaAdapter(), [row], "sandbox")
            self.assertEqual(report["foreign_marked_located"], ["conflict"])
            self.assertEqual(report["failures"][0]["reason"], "OriginSignatureError")
            self.assertEqual(row, original)

    def test_authority_states_and_verbatim_roundtrip(self):
        for fields, state in (
            ({}, "unsigned_pending"),
            ({"origin": "MrLiouWord"}, "mrl_owned"),
            ({"origin_signature": "MrLiouWord"}, "mrl_owned"),
            ({"origin": "MrLiouWord", "origin_signature": "MrLiouWord"}, "mrl_owned"),
        ):
            row = {"id": "r", "nested": {"values": [1, None]}, **fields}
            original = deepcopy(row)
            adapter = MemoryAdapter()
            particle = adapter.to_unified(row)
            self.assertEqual(particle.source_provenance, state)
            self.assertEqual(adapter.from_unified(particle), original)
            self.assertEqual(row, original)
            self.assertEqual(particle.state, original)

    def test_missing_identifier_preserves_exception_and_report_diagnostic(self):
        adapter = PersonaAdapter()
        with self.assertRaises(ParticleLayerError) as raised:
            verify_law2(adapter, [{"origin": "MrLiouWord"}])
        self.assertIs(type(raised.exception), ParticleLayerError)
        self.assertIn("no identifier found", str(raised.exception))
        report = build_report(adapter, [{"origin": "MrLiouWord"}], "sandbox")
        self.assertEqual(report["failures"][0]["reason"], "ParticleLayerError")
        self.assertEqual(report["failures"][0]["located"], "row-1")

    def test_original_exception_instance_propagates(self):
        error = ValueError("original diagnostic")

        class RaisingAdapter(PersonaAdapter):
            def roundtrip_check(self, row):
                raise error
        with self.assertRaises(ValueError) as raised:
            verify_law2(RaisingAdapter(), [{"id": "r"}])
        self.assertIs(raised.exception, error)

    def test_real_mismatch_retains_roundtrip_violation(self):
        class MismatchAdapter(PersonaAdapter):
            def roundtrip_check(self, row):
                return False
        rows = [{"id": "bad"}]
        with self.assertRaises(RoundtripViolation):
            verify_law2(MismatchAdapter(), rows)
        report = build_report(MismatchAdapter(), rows, "sandbox")
        self.assertEqual(report["failure_count"], 1)
        self.assertEqual(report["failures"][0]["reason"], "RoundtripMismatch")

    def test_sample_never_requests_row_101(self):
        def guarded():
            for i in range(100):
                yield {"id": str(i)}
            raise AssertionError("read beyond sample")
        adapter = PersonaAdapter()
        self.assertEqual(verify_law2(adapter, guarded())["checked"], 100)
        for options in ({}, {"count_total": False}):
            report = build_report(adapter, guarded(), "sandbox", sample_n=100, **options)
            self.assertEqual(report["checked"], 100)
            self.assertIsNone(report["total_rows"])
            self.assertIsNone(report["coverage"])
            self.assertFalse(report["global_claim"])

    def test_large_and_unbounded_sources_remain_resumable(self):
        from itertools import count
        for indices in (range(10**9), count()):
            rows = ({"id": i} for i in indices)
            self.assertEqual(verify_law2(PersonaAdapter(), rows)["checked"], 100)
            self.assertEqual(next(rows)["id"], 100)

    def test_zero_sample_does_not_touch_source(self):
        def forbidden():
            raise AssertionError("zero sample read input")
            yield
        report = build_report(PersonaAdapter(), forbidden(), "sandbox", sample_n=0)
        self.assertEqual(report["checked"], 0)
        self.assertFalse(report["global_claim"])

    def test_explicit_total_count_and_full_verification(self):
        rows = [{"id": str(i)} for i in range(250)]
        report = build_report(PersonaAdapter(), iter(rows), "sandbox", sample_n=100,
                              count_total=True)
        self.assertEqual(report["total_rows"], 250)
        self.assertEqual(report["coverage"], 0.4)
        self.assertFalse(report["global_claim"])
        report = build_report(PersonaAdapter(), iter(rows[:3]), "sandbox", sample_n=100)
        self.assertEqual(report["total_rows"], 3)
        self.assertTrue(report["global_claim"])

    def test_mother_corpus_roundtrips_without_changes(self):
        corpus = json.loads((MODULE_DIR.parents[1] / "core/particle_dict.json").read_text())
        particles = corpus["particles"]
        for adapter in (PersonaAdapter(), MemoryAdapter(), FileIndexAdapter()):
            rows = [{"id": key, "origin": corpus["origin"], "particle": particle}
                    for key, particle in particles.items()]
            original = deepcopy(rows)
            report = build_report(adapter, rows, "sandbox")
            self.assertEqual(report["failure_count"], 0)
            self.assertTrue(report["global_claim"])
            self.assertEqual(report["provenance"]["mrl_owned"], len(particles))
            self.assertEqual(rows, original)


if __name__ == "__main__":
    unittest.main()
