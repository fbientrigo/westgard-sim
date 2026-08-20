"""Tests for scripts/export_student_next_data.py.

Covers: golden expected answers for the six fixtures, per-point zone
consistency with the canonical rule functions, card_ids integrity, deck
byte-identity, numpy-free import, and the derived (never authored)
evaluation flag guard.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_SCRIPT = REPO_ROOT / "scripts" / "export_student_next_data.py"


def _load_export_module():
    spec = importlib.util.spec_from_file_location(
        "export_student_next_data", EXPORT_SCRIPT
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def export_module():
    return _load_export_module()


@pytest.fixture(scope="module")
def exported(tmp_path_factory, export_module):
    out_dir = tmp_path_factory.mktemp("student_next_export")
    export_module.export(out_dir)
    cards = json.loads((out_dir / "cards.json").read_text(encoding="utf-8"))
    rules_payload = json.loads((out_dir / "rules.json").read_text(encoding="utf-8"))
    practice = json.loads((out_dir / "practice.json").read_text(encoding="utf-8"))
    return {"dir": out_dir, "cards": cards, "rules": rules_payload, "practice": practice}


GOLDEN_EXPECTED = {
    "in-control-01": {"action": "accept", "rule": None, "evidence_runs": []},
    "warning-1-2s-01": {"action": "review", "rule": "1_2s", "evidence_runs": [9]},
    "reject-1-3s-01": {"action": "reject", "rule": "1_3s", "evidence_runs": [8]},
    "reject-2-2s-01": {"action": "reject", "rule": "2_2s", "evidence_runs": [7, 8]},
    "boundary-exact-2s-01": {"action": "accept", "rule": None, "evidence_runs": []},
    "distractor-opposite-01": {"action": "review", "rule": "1_2s", "evidence_runs": [7, 8]},
}


class TestGoldenExpectedAnswers:
    @pytest.mark.parametrize("scenario_id", GOLDEN_EXPECTED.keys())
    def test_expected_matches_golden(self, exported, scenario_id):
        scenarios = {s["id"]: s for s in exported["practice"]["scenarios"]}
        assert scenario_id in scenarios
        assert scenarios[scenario_id]["expected"] == GOLDEN_EXPECTED[scenario_id]


class TestPointZones:
    def test_every_point_has_valid_zone(self, exported):
        valid_zones = {"within_2sd", "beyond_2sd", "beyond_3sd"}
        for scenario in exported["practice"]["scenarios"]:
            for point in scenario["points"]:
                assert point["zone"] in valid_zones

    def test_exact_boundary_stays_inner_shape(self, exported):
        scenarios = {s["id"]: s for s in exported["practice"]["scenarios"]}
        boundary = scenarios["boundary-exact-2s-01"]
        run_8 = next(p for p in boundary["points"] if p["run"] == 8)
        assert abs(run_8["z"] - 2.0) < 1e-9
        assert run_8["zone"] == "within_2sd"

    def test_zone_consistent_with_canonical_rules(self, exported):
        from qc_lab_simulator import rules as rules_mod

        for scenario in exported["practice"]["scenarios"]:
            mean = scenario["mean"]
            sd = scenario["sd"]
            for point in scenario["points"]:
                value = point["value"]
                if rules_mod.rule_1_3s([value], mean, sd):
                    expected_zone = "beyond_3sd"
                elif rules_mod.rule_1_2s([value], mean, sd):
                    expected_zone = "beyond_2sd"
                else:
                    expected_zone = "within_2sd"
                assert point["zone"] == expected_zone


class TestCardIdsIntegrity:
    def test_all_card_ids_exist_in_deck(self, exported):
        card_ids = {c["id"] for c in exported["cards"]["cards"]}
        for rule in exported["rules"]["rules"]:
            for card_id in rule["card_ids"]:
                assert card_id in card_ids, f"missing card_id {card_id!r} for rule {rule['id']!r}"

    def test_generated_cards_match_canonical_source(self, exported):
        canonical = json.loads(
            (REPO_ROOT / "content" / "flashcards" / "westgard_qc_basics.deck.json").read_text(
                encoding="utf-8"
            )
        )
        assert exported["cards"] == canonical

    def test_cards_json_is_byte_identical_to_source(self, exported):
        source_bytes = (
            REPO_ROOT / "content" / "flashcards" / "westgard_qc_basics.deck.json"
        ).read_bytes()
        generated_bytes = (exported["dir"] / "cards.json").read_bytes()
        assert generated_bytes == source_bytes


class TestRuleCapabilityDerivation:
    def test_interactive_rules_are_exactly_the_engine_registry(self, exported):
        from qc_lab_simulator.metrics import _RULES

        interactive_ids = {
            r["id"] for r in exported["rules"]["rules"] if r["evaluation"] == "interactive"
        }
        assert interactive_ids == set(_RULES.keys())

    def test_reference_rules_never_become_interactive(self, exported):
        from qc_lab_simulator import evidence as evidence_mod

        for rule in exported["rules"]["rules"]:
            if rule["id"] in evidence_mod.REFERENCE_RULES:
                assert rule["evaluation"] == "reference"

    def test_export_rejects_authored_evaluation_field(self, export_module, tmp_path, monkeypatch):
        # Point RULES_REFERENCE_SOURCE at a temp file with an authored 'evaluation'.
        bad_reference = json.loads(export_module.RULES_REFERENCE_SOURCE.read_text(encoding="utf-8"))
        bad_reference["rules"][0]["evaluation"] = "interactive"
        bad_path = tmp_path / "rules_reference_bad.json"
        bad_path.write_text(json.dumps(bad_reference), encoding="utf-8")

        monkeypatch.setattr(export_module, "RULES_REFERENCE_SOURCE", bad_path)
        with pytest.raises(export_module.ExportError):
            export_module.build_rules_payload()


class TestExporterHasNoNumpyDependency:
    def test_export_script_module_does_not_import_numpy(self):
        """Run in a subprocess for the same isolation reason as evidence.py's check."""
        import subprocess

        code = (
            "import sys, runpy; "
            "runpy.run_path(r'" + str(EXPORT_SCRIPT) + "', run_name='__not_main__'); "
            "print('numpy' in sys.modules)"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "False"


class TestExporterCLI:
    def test_export_exits_zero_and_writes_three_files(self, export_module, tmp_path):
        exit_code = export_module.main(["--output-dir", str(tmp_path)])
        assert exit_code == 0
        assert (tmp_path / "cards.json").exists()
        assert (tmp_path / "rules.json").exists()
        assert (tmp_path / "practice.json").exists()

    def test_duplicate_scenario_id_fails_export(self, export_module, tmp_path, monkeypatch):
        scenarios_payload = json.loads(
            export_module.PRACTICE_SCENARIOS_SOURCE.read_text(encoding="utf-8")
        )
        scenarios_payload["scenarios"].append(scenarios_payload["scenarios"][0])
        bad_path = tmp_path / "practice_scenarios_bad.json"
        bad_path.write_text(json.dumps(scenarios_payload), encoding="utf-8")

        monkeypatch.setattr(export_module, "PRACTICE_SCENARIOS_SOURCE", bad_path)
        with pytest.raises(export_module.ExportError):
            export_module.build_practice_payload()
