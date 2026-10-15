"""MRL_SystemB_CommerceLayer 的授權、計量與報告合約測試。

origin_signature: MrLiouWord
用 unittest 撰寫，所以在沒有 pytest 的環境也能以
`python3 -m unittest discover -s tests` 跑同一組斷言。
"""

import json
import math
import sys
import tempfile
import unittest
from copy import deepcopy
from decimal import Decimal
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT))

from modules.MRL_SystemA_ParticleLayer import (  # noqa: E402
    MemoryAdapter,
    OriginSignatureError,
    PersonaAdapter,
    Mrliou_MRL_classify_source,
    Mrliou_MRL_normalize_authority,
    Mrliou_MRL_source_signature_values,
)
from modules.MRL_SystemB_CommerceLayer import (  # noqa: E402
    AXIS_CORPUS,
    MrliouMRLRateCardAuthorityError,
    Mrliou_MRL_invalid_usage,
    Mrliou_MRL_rate,
    Mrliou_MRL_rate_card_currency,
    Mrliou_MRL_sum_usage,
    Mrliou_MRL_usage_problem,
    AXIS_PARTICLE,
    AXIS_VERIFICATION,
    COMMERCE_AXES,
    ENV_SANDBOX,
    FOREIGN_CLAIMED,
    MRL_GRANTED,
    PHASE1_PRIVATE,
    PHASE2_EXTERNAL,
    UNGRANTED_PENDING,
    MrliouMRLGrant,
    MrliouMRLGrantError,
    MrliouMRLMeterError,
    MrliouMRLPhaseViolation,
    MrliouMRLUnpricedUnitError,
    Mrliou_MRL_authorize,
    Mrliou_MRL_build_commerce_report,
    Mrliou_MRL_check_signature_retention,
    Mrliou_MRL_classify_grant,
    Mrliou_MRL_format_commerce_report,
    Mrliou_MRL_load_rate_card,
    Mrliou_MRL_price,
    Mrliou_MRL_read_usage,
    Mrliou_MRL_record_usage,
)

#: 同一個權威的保留名，依 .mrliou/authority-lock.json。全部必須被認得。
AUTHORITY_SPELLINGS = (
    "MrLiouWord",
    "MrLiou",
    "Mrliou",
    "Mr.liou",
    "MR.liou",
    "Mr. Liou",
    "mrliouword",
    "MRL",
    "MRL_",
    "dofaromg",
)

#: 不屬於本權威的簽名。放寬到連這些都認得，就等於把權威送出去。
FOREIGN_SPELLINGS = (
    "SomeOtherVendor",
    "foreign",
    "MRLSomething",
    "MrLiouWordFake",
    "mrliouword-system",
)


def _priced_card(rate="0.5", currency="TWD", axis=AXIS_PARTICLE,
                 unit="sdk_call"):
    """複製一份出貨費率表，填上單價與幣別——計價的兩個前提都要齊。"""
    card = deepcopy(Mrliou_MRL_load_rate_card())
    card["currency"] = currency
    card["rates"][axis][unit] = rate
    return card


def _grant(**overrides):
    base = dict(
        grantee="acme-internal",
        axes=(AXIS_CORPUS, AXIS_VERIFICATION),
        artifact_owner="Mr.liou",
        source_repo="dofaromg/mrliouword-system",
        projection_role="licensed_carrier",
        seats=3,
        scope=("trace",),
        phase=PHASE1_PRIVATE,
        environment=ENV_SANDBOX,
    )
    base.update(overrides)
    return MrliouMRLGrant(**base)


class AuthorityAliasEquivalence(unittest.TestCase):
    """mrliou = mrliouword = MRL = Mr.liou，同一個權威。"""

    def test_every_reserved_spelling_is_own_authority(self):
        for spelling in AUTHORITY_SPELLINGS:
            self.assertEqual(
                Mrliou_MRL_normalize_authority(spelling), "MrLiouWord", spelling
            )

    def test_aliases_are_granted_and_retained(self):
        for spelling in AUTHORITY_SPELLINGS:
            row = {"id": f"a-{spelling}", "origin": spelling}
            self.assertEqual(Mrliou_MRL_classify_grant(row), MRL_GRANTED, spelling)
            retention = Mrliou_MRL_check_signature_retention(row)
            self.assertTrue(retention["retained"], spelling)
            self.assertEqual(retention["located"], f"a-{spelling}")

    def test_aliases_are_not_judged_foreign_by_particle_layer(self):
        """修正前這些別名會 raise OriginSignatureError（把自有資料擋在門外）。"""
        for spelling in AUTHORITY_SPELLINGS:
            row = {"id": "p", "origin_signature": spelling}
            self.assertEqual(Mrliou_MRL_classify_source(row), "mrl_owned", spelling)
            particle = PersonaAdapter().to_unified(row)
            self.assertEqual(particle.source_provenance, "mrl_owned")
            # LAW-0 不放寬：粒子寫出去的簽名仍是正規形
            self.assertEqual(particle.origin_signature, "MrLiouWord")

    def test_foreign_spellings_still_rejected(self):
        for spelling in FOREIGN_SPELLINGS:
            row = {"id": "f", "origin": spelling}
            self.assertEqual(
                Mrliou_MRL_classify_grant(row), FOREIGN_CLAIMED, spelling
            )
            self.assertFalse(Mrliou_MRL_check_signature_retention(row)["retained"])
            with self.assertRaises(OriginSignatureError, msg=spelling):
                MemoryAdapter().to_unified(row)

    def test_conflicting_alias_and_foreign_is_still_foreign(self):
        """一欄別名、一欄他方 → 矛盾即他方，兩個方向都要擋。"""
        for origin, signature in (("MRL", "SomeOtherVendor"),
                                  ("SomeOtherVendor", "MRL")):
            row = {"id": "c", "origin": origin, "origin_signature": signature}
            self.assertEqual(Mrliou_MRL_classify_grant(row), FOREIGN_CLAIMED)
            self.assertEqual(Mrliou_MRL_classify_source(row), "foreign_marked")

    def test_structured_values_never_fold_into_an_alias(self):
        """摺疊會去掉標點，所以 str(["MRL"]) 曾摺成 "mrl" 而取得 MRL 權威。

        這是權威洗白，方向與未簽名資料被蓋章完全相同。只有真正的 str 能進入
        別名比對；結構化或畸形的值欄位裡有東西，但不是本權威的簽名。
        """
        for value in (["MRL"], ["MrLiouWord"], ["M", "R", "L"], ("MRL",),
                      {"MRL"}, {"a": "MRL"}, 0, 123, 1.5, b"MRL"):
            row = {"id": "s", "origin": value}
            self.assertIsNone(
                Mrliou_MRL_normalize_authority(value), repr(value)
            )
            self.assertEqual(
                Mrliou_MRL_classify_grant(row), FOREIGN_CLAIMED, repr(value)
            )
            self.assertEqual(
                Mrliou_MRL_classify_source(row), "foreign_marked", repr(value)
            )
            self.assertFalse(
                Mrliou_MRL_check_signature_retention(row)["retained"],
                repr(value),
            )
            with self.assertRaises(OriginSignatureError, msg=repr(value)):
                MemoryAdapter().to_unified(row)

    def test_both_layers_classify_through_the_same_values(self):
        """License 與 Provenance 必須對同一列給同一個判定，否則一層擋了
        另一層會漏。"""
        pairs = [(MRL_GRANTED, "mrl_owned"), (FOREIGN_CLAIMED, "foreign_marked"),
                 (UNGRANTED_PENDING, "unsigned_pending")]
        rows = [{"id": "g", "origin": "MRL"},
                {"id": "f", "origin": ["MRL"]},
                {"id": "u"}]
        for row, (grant_state, source_state) in zip(rows, pairs):
            self.assertEqual(Mrliou_MRL_classify_grant(row), grant_state)
            self.assertEqual(Mrliou_MRL_classify_source(row), source_state)

    def test_unsigned_stays_pending_and_is_not_upgraded(self):
        row = {"id": "u", "payload": {"x": 1}}
        self.assertEqual(Mrliou_MRL_classify_grant(row), UNGRANTED_PENDING)
        self.assertFalse(Mrliou_MRL_check_signature_retention(row)["retained"])
        for blank in ("", "   ", "___"):
            self.assertEqual(
                Mrliou_MRL_classify_grant({"id": "u", "origin": blank}),
                UNGRANTED_PENDING,
                repr(blank),
            )


class GrantContract(unittest.TestCase):
    def test_four_field_declaration_is_mandatory(self):
        """authority-lock invariant：四欄宣告缺一不可。"""
        for missing in ("artifact_owner", "source_repo", "projection_role"):
            with self.assertRaises(MrliouMRLGrantError, msg=missing):
                _grant(**{missing: "  "})

    def test_grant_accepts_alias_but_stores_canonical_form(self):
        for spelling in AUTHORITY_SPELLINGS:
            self.assertEqual(
                _grant(origin_signature=spelling).origin_signature, "MrLiouWord"
            )

    def test_grant_rejects_foreign_signature(self):
        for spelling in FOREIGN_SPELLINGS:
            with self.assertRaises(MrliouMRLGrantError, msg=spelling):
                _grant(origin_signature=spelling)

    def test_grant_rejects_unknown_axis_empty_axes_and_negative_seats(self):
        with self.assertRaises(MrliouMRLGrantError):
            _grant(axes=("saas_tier",))
        with self.assertRaises(MrliouMRLGrantError):
            _grant(axes=())
        with self.assertRaises(MrliouMRLGrantError):
            _grant(seats=-1)
        with self.assertRaises(MrliouMRLGrantError):
            _grant(phase="phase3_whatever")

    def test_grant_is_frozen(self):
        grant = _grant()
        with self.assertRaises(Exception):
            grant.seats = 999  # type: ignore[misc]

    def test_authorize_requires_axis_to_be_in_grant(self):
        grant = _grant(axes=(AXIS_CORPUS,))
        ack = Mrliou_MRL_authorize(grant, AXIS_CORPUS)
        self.assertEqual(ack["axis"], AXIS_CORPUS)
        self.assertEqual(ack["origin_signature"], "MrLiouWord")
        self.assertEqual(ack["network_phase"], PHASE1_PRIVATE)
        self.assertTrue(ack["phase_known"])
        with self.assertRaises(MrliouMRLGrantError):
            Mrliou_MRL_authorize(grant, AXIS_PARTICLE)
        with self.assertRaises(MrliouMRLGrantError):
            Mrliou_MRL_authorize(grant, "saas_tier")


class PhaseGate(unittest.TestCase):
    """registry/system_registry.yaml：母體不公開；映射外部留到 Phase 2。"""

    def test_repo_registry_is_still_phase1(self):
        registry = REPO_ROOT / "registry" / "system_registry.yaml"
        self.assertIn("PHASE1_PRIVATE_LAN_ONLY", registry.read_text())

    def test_phase2_grant_blocked_under_phase1(self):
        grant = _grant(phase=PHASE2_EXTERNAL)
        with self.assertRaises(MrliouMRLPhaseViolation):
            Mrliou_MRL_authorize(grant, AXIS_CORPUS)

    def test_phase2_grant_allowed_once_registry_declares_phase2(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "registry").mkdir()
            (root / "registry" / "system_registry.yaml").write_text(
                'network_phase: "PHASE2_EXTERNAL_MAPPING"\n', encoding="utf-8"
            )
            ack = Mrliou_MRL_authorize(
                _grant(phase=PHASE2_EXTERNAL), AXIS_CORPUS, repo_root=root
            )
            self.assertEqual(ack["network_phase"], PHASE2_EXTERNAL)
            self.assertTrue(ack["phase_known"])

    def test_unreadable_registry_falls_back_to_most_conservative_phase(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(MrliouMRLPhaseViolation):
                Mrliou_MRL_authorize(
                    _grant(phase=PHASE2_EXTERNAL), AXIS_CORPUS, repo_root=root
                )
            ack = Mrliou_MRL_authorize(_grant(), AXIS_CORPUS, repo_root=root)
            self.assertEqual(ack["network_phase"], PHASE1_PRIVATE)
            self.assertFalse(ack["phase_known"])


class MeteringContract(unittest.TestCase):
    def test_ledger_is_append_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "nested" / "usage.jsonl"
            for i in range(3):
                Mrliou_MRL_record_usage(
                    ledger, "acme", AXIS_PARTICLE, "sdk_call", i + 1, ENV_SANDBOX
                )
            lines = ledger.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 3)
            first = json.loads(lines[0])
            self.assertEqual(first["qty"], 1)
            self.assertEqual(first["origin_signature"], "MrLiouWord")
            self.assertEqual(first["environment"], ENV_SANDBOX)
            self.assertTrue(first["recorded_at"].endswith("Z"))
            # 再寫一筆不得動到既有的行
            Mrliou_MRL_record_usage(
                ledger, "acme", AXIS_PARTICLE, "sdk_call", 9, ENV_SANDBOX
            )
            again = ledger.read_text(encoding="utf-8").splitlines()
            self.assertEqual(again[:3], lines)

    def test_environment_is_mandatory(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "usage.jsonl"
            with self.assertRaises(MrliouMRLMeterError):
                Mrliou_MRL_record_usage(
                    ledger, "acme", AXIS_PARTICLE, "sdk_call", 1, "  "
                )
            self.assertFalse(ledger.exists())

    def test_unknown_axis_unit_grantee_and_qty_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "usage.jsonl"
            for kwargs in (
                {"axis": "saas_tier", "unit": "sdk_call"},
                {"axis": AXIS_PARTICLE, "unit": "seat_year"},
            ):
                with self.assertRaises(MrliouMRLMeterError, msg=str(kwargs)):
                    Mrliou_MRL_record_usage(
                        ledger, "acme", qty=1, environment=ENV_SANDBOX, **kwargs
                    )
            with self.assertRaises(MrliouMRLMeterError):
                Mrliou_MRL_record_usage(
                    ledger, "  ", AXIS_PARTICLE, "sdk_call", 1, ENV_SANDBOX
                )
            with self.assertRaises(MrliouMRLMeterError):
                Mrliou_MRL_record_usage(
                    ledger, "acme", AXIS_PARTICLE, "sdk_call", -1, ENV_SANDBOX
                )

    def test_non_finite_and_non_numeric_quantities_never_reach_the_ledger(self):
        """NaN / ±Inf 通得過 `qty < 0`，但 json 會寫成 NaN / Infinity——

        那不是合法 JSON，別的解析器讀不回來，而這是 append-only 的帳本：
        寫壞的那一行永遠在裡面。
        """
        self.assertFalse(float("nan") < 0)  # 舊的負數檢查擋不住它
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "usage.jsonl"
            for qty in (float("nan"), float("inf"), float("-inf"),
                        "5", True, None, [1]):
                with self.assertRaises(MrliouMRLMeterError, msg=repr(qty)):
                    Mrliou_MRL_record_usage(
                        ledger, "acme", AXIS_PARTICLE, "sdk_call", qty,
                        ENV_SANDBOX,
                    )
            self.assertFalse(ledger.exists())
            # 合法的值照寫，且寫出來是能讀回來的合法 JSON
            Mrliou_MRL_record_usage(
                ledger, "acme", AXIS_PARTICLE, "sdk_call", 2.5, ENV_SANDBOX
            )
            text = ledger.read_text(encoding="utf-8")
            self.assertNotIn("NaN", text)
            self.assertNotIn("Infinity", text)
            self.assertEqual(json.loads(text)["qty"], 2.5)
            self.assertTrue(math.isfinite(json.loads(text)["qty"]))

    def test_malformed_line_is_surfaced_not_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "usage.jsonl"
            Mrliou_MRL_record_usage(
                ledger, "acme", AXIS_PARTICLE, "sdk_call", 1, ENV_SANDBOX
            )
            with ledger.open("a", encoding="utf-8") as handle:
                handle.write("{not json\n")
                handle.write("[1, 2]\n")
            records = list(Mrliou_MRL_read_usage(ledger))
            self.assertEqual(len(records), 3)
            self.assertEqual(
                [bool(r.get("malformed")) for r in records], [False, True, True]
            )

    def test_missing_ledger_reads_empty_without_raising(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                list(Mrliou_MRL_read_usage(Path(tmp) / "nope.jsonl")), []
            )


class UnpricedNeverZero(unittest.TestCase):
    """對照 cost_tracker.py:44-45 的靜默歸零：這裡一定要吵。"""

    def setUp(self):
        self.card = Mrliou_MRL_load_rate_card()

    def test_shipped_rate_card_has_no_rates_filled(self):
        self.assertEqual(self.card["status"], "rates_pending_rights_holder")
        for axis, units in self.card["rates"].items():
            self.assertIn(axis, COMMERCE_AXES)
            for unit, value in units.items():
                self.assertIsNone(value, f"{axis}/{unit}")

    def test_unset_rate_raises_instead_of_returning_zero(self):
        for axis, units in self.card["rates"].items():
            for unit in units:
                with self.assertRaises(MrliouMRLUnpricedUnitError):
                    Mrliou_MRL_price(self.card, axis, unit, 1000)

    def test_non_numeric_rate_raises(self):
        for bad in ("3.00", True, [], {}):
            card = deepcopy(self.card)
            card["rates"][AXIS_PARTICLE]["sdk_call"] = bad
            with self.assertRaises(MrliouMRLUnpricedUnitError, msg=repr(bad)):
                Mrliou_MRL_price(card, AXIS_PARTICLE, "sdk_call", 1)

    def test_filled_rate_prices_correctly(self):
        card = _priced_card(rate="0.25")
        self.assertEqual(
            Mrliou_MRL_price(card, AXIS_PARTICLE, "sdk_call", 40), Decimal("10.00")
        )

    def test_currency_is_required_before_any_price(self):
        """單價填了但幣別沒填，仍然不得輸出金額。"""
        card = _priced_card(currency=None)
        with self.assertRaises(MrliouMRLUnpricedUnitError):
            Mrliou_MRL_rate_card_currency(card)
        with self.assertRaises(MrliouMRLUnpricedUnitError):
            Mrliou_MRL_price(card, AXIS_PARTICLE, "sdk_call", 10)
        for blank in ("", "   ", 123, []):
            with self.assertRaises(MrliouMRLUnpricedUnitError, msg=repr(blank)):
                Mrliou_MRL_rate_card_currency(_priced_card(currency=blank))

    def test_rate_card_authority_checked_at_the_point_of_pricing(self):
        """只在 load 檢查簽名是不夠的——呼叫端可以自己湊一個 dict 傳進來。"""
        card = _priced_card()
        card["origin_signature"] = "SomeOtherVendor"
        with self.assertRaises(MrliouMRLRateCardAuthorityError):
            Mrliou_MRL_rate(card, AXIS_PARTICLE, "sdk_call")
        with self.assertRaises(MrliouMRLRateCardAuthorityError):
            Mrliou_MRL_price(card, AXIS_PARTICLE, "sdk_call", 1)
        for spelling in AUTHORITY_SPELLINGS:  # 別名簽的費率表仍可用
            ok = _priced_card()
            ok["origin_signature"] = spelling
            self.assertEqual(
                Mrliou_MRL_rate(ok, AXIS_PARTICLE, "sdk_call"), Decimal("0.5")
            )

    def test_money_uses_exact_decimal_not_binary_float(self):
        """0.1 × 3 在 float 下是 0.30000000000000004；金額不得長這樣。"""
        self.assertNotEqual(0.1 * 3, 0.3)
        card = _priced_card(rate="0.1")
        self.assertEqual(
            Mrliou_MRL_price(card, AXIS_PARTICLE, "sdk_call", 3), Decimal("0.3")
        )
        report = Mrliou_MRL_build_commerce_report(
            [{"id": "a", "origin": "MRL"}], ENV_SANDBOX,
            usage_records=[{"axis": AXIS_PARTICLE, "unit": "sdk_call", "qty": 3}],
            rate_card=card,
        )
        self.assertEqual(report["amount_total"], "0.3")
        self.assertEqual(report["currency"], "TWD")

    def test_foreign_signed_rate_card_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            card = deepcopy(self.card)
            card["origin_signature"] = "SomeOtherVendor"
            path = Path(tmp) / "card.json"
            path.write_text(json.dumps(card), encoding="utf-8")
            with self.assertRaises(MrliouMRLMeterError):
                Mrliou_MRL_load_rate_card(path)


class ReportHonesty(unittest.TestCase):
    def test_report_never_raises_and_lists_every_failure(self):
        artifacts = [
            {"id": "ok-1", "origin": "MRL"},
            {"id": "unsigned-1"},
            {"id": "foreign-1", "origin": "SomeOtherVendor"},
            {"id": "unsigned-2"},
        ]
        original = deepcopy(artifacts)
        report = Mrliou_MRL_build_commerce_report(artifacts, ENV_SANDBOX)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["failure_count"], 3)
        self.assertEqual(len(report["failures"]), 3)
        self.assertEqual(
            report["grants"],
            {"mrl_granted": 1, "foreign_claimed": 1, "ungranted_pending": 2},
        )
        self.assertEqual(
            report["ungranted_pending_located"], ["unsigned-1", "unsigned-2"]
        )
        self.assertEqual(report["foreign_claimed_located"], ["foreign-1"])
        self.assertFalse(report["global_claim"])
        self.assertEqual(report["origin_signature"], "MrLiouWord")
        self.assertEqual(report["environment"], ENV_SANDBOX)
        self.assertTrue(report["environment_known"])
        self.assertEqual(artifacts, original)  # 只讀不改（LAW-2）
        self.assertIn("違約／失敗", Mrliou_MRL_format_commerce_report(report))

    def test_clean_full_check_claims_globally(self):
        artifacts = [{"id": f"a-{i}", "origin": "Mr.liou"} for i in range(5)]
        report = Mrliou_MRL_build_commerce_report(artifacts, ENV_SANDBOX)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["global_claim"])
        self.assertEqual(report["total_rows"], 5)
        self.assertEqual(report["coverage"], 1.0)
        self.assertFalse(report["sampled"])

    def test_sampling_is_bounded_and_never_claims_a_total_it_did_not_count(self):
        def guarded():
            for i in range(100):
                yield {"id": str(i), "origin": "MrLiouWord"}
            raise AssertionError("read beyond sample")

        report = Mrliou_MRL_build_commerce_report(
            guarded(), ENV_SANDBOX, sample_n=100
        )
        self.assertEqual(report["checked"], 100)
        self.assertIsNone(report["total_rows"])
        self.assertFalse(report["total_rows_known"])
        self.assertIsNone(report["coverage"])
        self.assertTrue(report["sampled"])
        self.assertFalse(report["global_claim"])
        self.assertIn("總數未知", Mrliou_MRL_format_commerce_report(report))

    def test_count_total_reports_real_coverage(self):
        artifacts = [{"id": str(i), "origin": "MRL"} for i in range(250)]
        report = Mrliou_MRL_build_commerce_report(
            artifacts, ENV_SANDBOX, sample_n=100, count_total=True
        )
        self.assertEqual(report["total_rows"], 250)
        self.assertEqual(report["coverage"], 0.4)
        self.assertTrue(report["sampled"])
        self.assertFalse(report["global_claim"])

    def test_unknown_environment_is_passed_through_verbatim(self):
        report = Mrliou_MRL_build_commerce_report([], "my-laptop")
        self.assertEqual(report["environment"], "my-laptop")
        self.assertFalse(report["environment_known"])
        self.assertIn("未知環境名", Mrliou_MRL_format_commerce_report(report))

    def test_usage_without_rate_card_is_counted_not_priced(self):
        report = Mrliou_MRL_build_commerce_report(
            [{"id": "a", "origin": "MRL"}],
            ENV_SANDBOX,
            usage_records=[
                {"axis": AXIS_PARTICLE, "unit": "sdk_call", "qty": 10},
                {"axis": AXIS_PARTICLE, "unit": "sdk_call", "qty": 5},
            ],
        )
        self.assertEqual(report["usage"], [
            {"axis": AXIS_PARTICLE, "unit": "sdk_call", "qty": "15"}
        ])
        self.assertIsNone(report["amount_total"])
        self.assertIsNone(report["currency"])
        self.assertFalse(report["priced"])
        self.assertEqual(report["unpriced"], [])

    def test_unpriced_units_are_listed_and_total_is_not_zeroed(self):
        card = deepcopy(Mrliou_MRL_load_rate_card())
        card["currency"] = "TWD"  # 幣別有了，但單價仍未填
        report = Mrliou_MRL_build_commerce_report(
            [{"id": "a", "origin": "MRL"}],
            ENV_SANDBOX,
            usage_records=[{"axis": AXIS_PARTICLE, "unit": "sdk_call", "qty": 10}],
            rate_card=card,
        )
        self.assertEqual(
            report["unpriced"],
            [{"axis": AXIS_PARTICLE, "unit": "sdk_call", "qty": "10"}],
        )
        self.assertIsNone(report["amount_total"])
        self.assertFalse(report["priced"])
        self.assertIn("無法計價", Mrliou_MRL_format_commerce_report(report))

    def test_priced_usage_totals(self):
        report = Mrliou_MRL_build_commerce_report(
            [{"id": "a", "origin": "MRL"}],
            ENV_SANDBOX,
            usage_records=[{"axis": AXIS_PARTICLE, "unit": "sdk_call", "qty": 10}],
            rate_card=_priced_card(),
        )
        self.assertEqual(report["amount_total"], "5.0")
        self.assertEqual(report["currency"], "TWD")
        self.assertTrue(report["priced"])
        self.assertEqual(report["unpriced"], [])
        self.assertIn("合計 5.0 TWD", Mrliou_MRL_format_commerce_report(report))

    def test_report_never_prices_with_an_unusable_rate_card(self):
        """他方簽名或沒有幣別的費率表：整張不採用，且報告不得丟例外。"""
        foreign = _priced_card()
        foreign["origin_signature"] = "SomeOtherVendor"
        for card, reason in (
            (foreign, "MrliouMRLRateCardAuthorityError"),
            (_priced_card(currency=None), "MrliouMRLUnpricedUnitError"),
        ):
            report = Mrliou_MRL_build_commerce_report(
                [{"id": "a", "origin": "MRL"}], ENV_SANDBOX,
                usage_records=[
                    {"axis": AXIS_PARTICLE, "unit": "sdk_call", "qty": 10}
                ],
                rate_card=card,
            )
            self.assertEqual(report["status"], "FAIL", reason)
            self.assertFalse(report["priced"])
            self.assertIsNone(report["amount_total"])
            self.assertIn(
                reason, [f["reason"] for f in report["failures"]]
            )
            self.assertEqual(
                [f["located"] for f in report["failures"]], ["rate_card"]
            )

    def test_unknown_axis_or_unit_in_ledger_is_reported_in_both_modes(self):
        """已知軸 + 未知單位曾讓『永不丟例外』的報告直接炸掉。"""
        for records in (
            [{"axis": "saas_tier", "unit": "seat", "qty": 1}],
            [{"axis": AXIS_PARTICLE, "unit": "bogus_unit", "qty": 1}],
        ):
            for card in (None, _priced_card()):
                report = Mrliou_MRL_build_commerce_report(
                    [], ENV_SANDBOX, usage_records=records, rate_card=card
                )
                self.assertEqual(report["status"], "FAIL", str(records))
                self.assertIn(
                    "InvalidUsageRecord",
                    [f["reason"] for f in report["failures"]],
                )
                self.assertEqual(report["usage"], [])

    def test_invalid_quantities_are_surfaced_not_dropped(self):
        """qty 缺漏、字串或 bool 的列不得被靜默跳過後報 PASS。"""
        for qty in (None, "10", True, [1]):
            record = {"axis": AXIS_PARTICLE, "unit": "sdk_call"}
            if qty is not None:
                record["qty"] = qty
            report = Mrliou_MRL_build_commerce_report(
                [], ENV_SANDBOX, usage_records=[record]
            )
            self.assertEqual(report["status"], "FAIL", repr(qty))
            self.assertEqual(report["usage"], [], repr(qty))
            self.assertIn(
                "InvalidUsageRecord",
                [f["reason"] for f in report["failures"]],
            )
        self.assertIsNotNone(
            Mrliou_MRL_usage_problem(
                {"axis": AXIS_PARTICLE, "unit": "sdk_call", "qty": "10"}
            )
        )
        self.assertIsNone(
            Mrliou_MRL_usage_problem(
                {"axis": AXIS_PARTICLE, "unit": "sdk_call", "qty": 10}
            )
        )
        self.assertEqual(
            Mrliou_MRL_sum_usage(
                [{"axis": AXIS_PARTICLE, "unit": "sdk_call", "qty": 10}]
            ),
            {(AXIS_PARTICLE, "sdk_call"): Decimal(10)},
        )

    def test_malformed_usage_generator_is_not_silently_dropped(self):
        def records():
            yield {"axis": AXIS_PARTICLE, "unit": "sdk_call", "qty": 1}
            yield {"malformed": True, "located": "usage.jsonl:2", "detail": "x"}

        report = Mrliou_MRL_build_commerce_report(
            [], ENV_SANDBOX, usage_records=records()
        )
        self.assertEqual(
            [f["reason"] for f in report["failures"]], ["InvalidUsageRecord"]
        )
        self.assertEqual(report["failures"][0]["located"], "usage.jsonl:2")
        self.assertEqual(
            Mrliou_MRL_invalid_usage([{"malformed": True, "detail": "x"}]),
            [{"located": "usage-1", "detail": "x"}],
        )


class MotherCorpusAcceptance(unittest.TestCase):
    """驗收語料用母體自己的 core/particle_dict.json，不是自編的例子。"""

    def setUp(self):
        self.corpus = json.loads(
            (REPO_ROOT / "core" / "particle_dict.json").read_text(encoding="utf-8")
        )

    def test_corpus_origin_is_this_authority(self):
        self.assertEqual(
            Mrliou_MRL_normalize_authority(self.corpus["origin"]), "MrLiouWord"
        )
        self.assertEqual(self.corpus["philosophy"], "怎麼過去，就怎麼回來")

    def test_signed_corpus_passes_retention_for_every_alias(self):
        particles = self.corpus["particles"]
        for spelling in AUTHORITY_SPELLINGS:
            rows = [
                {"id": key, "origin": spelling, "particle": body}
                for key, body in particles.items()
            ]
            original = deepcopy(rows)
            report = Mrliou_MRL_build_commerce_report(rows, ENV_SANDBOX)
            self.assertEqual(report["status"], "PASS", spelling)
            self.assertEqual(report["grants"]["mrl_granted"], len(particles))
            self.assertTrue(report["global_claim"], spelling)
            self.assertEqual(rows, original)

    def test_stripped_corpus_is_located_as_breach_not_laundered(self):
        particles = self.corpus["particles"]
        rows = [{"id": key, "particle": body} for key, body in particles.items()]
        report = Mrliou_MRL_build_commerce_report(rows, ENV_SANDBOX)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["grants"]["ungranted_pending"], len(particles))
        self.assertEqual(len(report["ungranted_pending_located"]), len(particles))
        self.assertEqual(report["failure_count"], len(particles))
        self.assertTrue(
            all(f["reason"] == "SignatureNotRetained" for f in report["failures"])
        )

    def test_license_clause_text_matches_what_we_enforce(self):
        clause = (
            REPO_ROOT / "docs" / "references" / "licenses" / "chatserver-license.txt"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "must retain the origin_signature: MrLiouWord in all copies", clause
        )
        report = Mrliou_MRL_build_commerce_report([], ENV_SANDBOX)
        self.assertEqual(
            report["clause"], "chatserver-license.txt GRANT OF LICENSE 1"
        )


if __name__ == "__main__":
    unittest.main()
