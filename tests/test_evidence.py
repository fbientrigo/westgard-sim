"""Tests for qc_lab_simulator/evidence.py.

Defense-in-depth: evidence.py already derives everything from rules.py, so
these tests assert parity with the canonical functions and the documented
shape/semantics, rather than re-implementing rule predicates.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from qc_lab_simulator import evidence
from qc_lab_simulator import rules

MEAN = 100.0
SD = 2.0

# The six MVP fixtures from docs/STUDENT_NEXT_IMPLEMENTATION.md, exact z arrays.
FIXTURES = {
    "in-control-01": {
        "z_values": [0.4, -0.6, 0.9, -0.3, 0.7, -1.1, 0.2, 1.4, -0.8, 0.5],
        "verdict": "accept",
        "governing_rule": None,
        "evidence_runs": [],
    },
    "warning-1-2s-01": {
        "z_values": [-0.5, 0.6, -0.2, 1.1, -0.9, 0.3, 1.6, -0.4, 2.4, -0.7],
        "verdict": "review",
        "governing_rule": "1_2s",
        "evidence_runs": [9],
        "side": "positive",
    },
    "reject-1-3s-01": {
        "z_values": [0.3, -0.7, 0.5, -1.2, 0.8, -0.4, 1.0, -3.3, 0.6, -0.5],
        "verdict": "reject",
        "governing_rule": "1_3s",
        "evidence_runs": [8],
        "side": "negative",
    },
    "reject-2-2s-01": {
        "z_values": [0.5, -0.4, 0.7, -0.6, 0.9, 1.2, 2.3, 2.6, 1.8, 0.4],
        "verdict": "reject",
        "governing_rule": "2_2s",
        "evidence_runs": [7, 8],
        "side": "positive",
    },
    "boundary-exact-2s-01": {
        "z_values": [-0.3, 0.8, -0.6, 1.3, -0.9, 0.4, 1.7, 2.0, -0.5, 0.7],
        "verdict": "accept",
        "governing_rule": None,
        "evidence_runs": [],
    },
    "distractor-opposite-01": {
        "z_values": [0.4, -0.8, 0.6, -0.5, 1.1, -0.7, 2.3, -2.4, 0.9, -0.3],
        "verdict": "review",
        "governing_rule": "1_2s",
        "evidence_runs": [7, 8],
        "side": "mixed",
    },
}


def to_values(z_values):
    return [MEAN + z * SD for z in z_values]


def z_grid():
    """41 entries, -4.0 .. +4.0 step 0.2 (as used for counterfactuals)."""
    grid = []
    for i in range(41):
        grid.append(round(-4.0 + i * 0.2, 1))
    return grid


class TestFixtureGoldenOutcomes:
    @pytest.mark.parametrize("fixture_id", FIXTURES.keys())
    def test_verdict_and_governing_rule(self, fixture_id):
        fixture = FIXTURES[fixture_id]
        values = to_values(fixture["z_values"])
        result = evidence.evaluate_series(values, MEAN, SD)
        assert result["verdict"] == fixture["verdict"], fixture_id
        assert result["governing_rule"] == fixture["governing_rule"], fixture_id

    @pytest.mark.parametrize("fixture_id", FIXTURES.keys())
    def test_governing_evidence_runs(self, fixture_id):
        fixture = FIXTURES[fixture_id]
        values = to_values(fixture["z_values"])
        result = evidence.evaluate_series(values, MEAN, SD)
        governing = result["governing_rule"]
        if governing is None:
            assert fixture["evidence_runs"] == []
            return
        entry = next(r for r in result["rules"] if r["rule"] == governing)
        assert entry["evidence_runs"] == fixture["evidence_runs"], fixture_id
        if "side" in fixture:
            assert entry["side"] == fixture["side"], fixture_id


class TestParityWithCanonicalRules:
    """evaluate_series' triggered flags must equal direct calls to rules.py."""

    @pytest.mark.parametrize("fixture_id", FIXTURES.keys())
    def test_triggered_matches_rules_module(self, fixture_id):
        values = to_values(FIXTURES[fixture_id]["z_values"])
        result = evidence.evaluate_series(values, MEAN, SD)
        by_id = {r["rule"]: r for r in result["rules"]}
        assert by_id["1_2s"]["triggered"] == rules.rule_1_2s(values, MEAN, SD)
        assert by_id["1_3s"]["triggered"] == rules.rule_1_3s(values, MEAN, SD)
        assert by_id["2_2s"]["triggered"] == rules.rule_2_2s(values, MEAN, SD)

    @pytest.mark.parametrize("fixture_id", FIXTURES.keys())
    def test_counterfactual_parity_all_grid_values(self, fixture_id):
        """Parity for all 41 counterfactual values of the editable run (246 series x 3 rules)."""
        editable_run_index = {
            "in-control-01": 7,
            "warning-1-2s-01": 8,
            "reject-1-3s-01": 7,
            "reject-2-2s-01": 7,
            "boundary-exact-2s-01": 7,
            "distractor-opposite-01": 7,
        }[fixture_id]
        z_values = list(FIXTURES[fixture_id]["z_values"])
        for z_candidate in z_grid():
            candidate_z = list(z_values)
            candidate_z[editable_run_index] = z_candidate
            values = to_values(candidate_z)
            result = evidence.evaluate_series(values, MEAN, SD)
            by_id = {r["rule"]: r for r in result["rules"]}
            assert by_id["1_2s"]["triggered"] == rules.rule_1_2s(values, MEAN, SD)
            assert by_id["1_3s"]["triggered"] == rules.rule_1_3s(values, MEAN, SD)
            assert by_id["2_2s"]["triggered"] == rules.rule_2_2s(values, MEAN, SD)


class TestTriggeredEvidenceRunsEquivalence:
    @pytest.mark.parametrize("fixture_id", FIXTURES.keys())
    def test_triggered_iff_evidence_runs_nonempty(self, fixture_id):
        values = to_values(FIXTURES[fixture_id]["z_values"])
        result = evidence.evaluate_series(values, MEAN, SD)
        for entry in result["rules"]:
            assert entry["triggered"] == (len(entry["evidence_runs"]) > 0)


class TestBoundaries:
    def test_exact_2sd_does_not_trigger_1_2s(self):
        values = [MEAN + 2.0 * SD]
        result = evidence.evaluate_series(values, MEAN, SD)
        by_id = {r["rule"]: r for r in result["rules"]}
        assert by_id["1_2s"]["triggered"] is False
        assert by_id["1_2s"]["evidence_runs"] == []

    def test_exact_3sd_does_not_trigger_1_3s(self):
        values = [MEAN + 3.0 * SD, MEAN - 3.0 * SD]
        result = evidence.evaluate_series(values, MEAN, SD)
        by_id = {r["rule"]: r for r in result["rules"]}
        assert by_id["1_3s"]["triggered"] is False
        assert by_id["1_3s"]["evidence_runs"] == []

    def test_beyond_2sd_triggers(self):
        values = [MEAN + 2.2 * SD]
        result = evidence.evaluate_series(values, MEAN, SD)
        by_id = {r["rule"]: r for r in result["rules"]}
        assert by_id["1_2s"]["triggered"] is True
        assert by_id["1_2s"]["evidence_runs"] == [1]


class TestOppositeSidePair:
    def test_opposite_side_pair_does_not_trigger_2_2s(self):
        values = [MEAN + 2.4 * SD, MEAN - 2.6 * SD]
        result = evidence.evaluate_series(values, MEAN, SD)
        by_id = {r["rule"]: r for r in result["rules"]}
        assert by_id["2_2s"]["triggered"] is False
        assert by_id["1_2s"]["triggered"] is True
        assert by_id["1_2s"]["evidence_runs"] == [1, 2]
        assert by_id["1_2s"]["side"] == "mixed"


class TestSameSideConsecutivePair:
    def test_same_side_pair_triggers_2_2s_and_reports_both_points(self):
        values = [MEAN, MEAN + 2.3 * SD, MEAN + 2.6 * SD, MEAN]
        result = evidence.evaluate_series(values, MEAN, SD)
        by_id = {r["rule"]: r for r in result["rules"]}
        assert by_id["2_2s"]["triggered"] is True
        assert by_id["2_2s"]["evidence_runs"] == [2, 3]
        assert by_id["2_2s"]["side"] == "positive"


class TestEarliestQualifying2_2sPair:
    def test_returns_earliest_pair_only(self):
        # Two qualifying pairs exist; only the earliest is reported.
        values = [
            MEAN + 2.1 * SD,
            MEAN + 2.1 * SD,
            MEAN,
            MEAN + 2.5 * SD,
            MEAN + 2.5 * SD,
        ]
        result = evidence.evaluate_series(values, MEAN, SD)
        by_id = {r["rule"]: r for r in result["rules"]}
        assert by_id["2_2s"]["evidence_runs"] == [1, 2]


class TestVerdictAndGoverningRule:
    def test_1_3s_implies_1_2s_but_1_3s_governs(self):
        values = [MEAN + 3.4 * SD]
        result = evidence.evaluate_series(values, MEAN, SD)
        by_id = {r["rule"]: r for r in result["rules"]}
        assert by_id["1_2s"]["triggered"] is True
        assert by_id["1_3s"]["triggered"] is True
        assert result["governing_rule"] == "1_3s"
        assert result["verdict"] == "reject"

    def test_nothing_triggered_is_accept(self):
        values = [MEAN] * 10
        result = evidence.evaluate_series(values, MEAN, SD)
        assert result["verdict"] == "accept"
        assert result["governing_rule"] is None

    def test_only_warning_is_review(self):
        values = [MEAN + 2.2 * SD]
        result = evidence.evaluate_series(values, MEAN, SD)
        assert result["verdict"] == "review"
        assert result["governing_rule"] == "1_2s"


class TestModuleBoundaries:
    def test_evidence_module_imports_no_numpy(self):
        """Importing evidence.py in a clean subprocess must not import numpy.

        Run in a subprocess because the shared test-session sys.modules may
        already contain numpy from unrelated test files (e.g. simulate.py /
        web_export.py) that import it independently. That pollution is a
        test-isolation artifact, not evidence that evidence.py itself
        depends on numpy.
        """
        import subprocess

        code = (
            "import sys; "
            "import qc_lab_simulator.evidence; "
            "print('numpy' in sys.modules)"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(Path(__file__).resolve().parent.parent),
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.stdout.strip() == "False"

    def test_reference_rules_are_exactly_three_and_absent_from_supported(self):
        assert evidence.REFERENCE_RULES == ("R_4s", "4_1s", "10x")
        for rule_id in evidence.REFERENCE_RULES:
            assert rule_id not in evidence.SUPPORTED_RULES

    def test_supported_rules_is_the_engine_registry(self):
        from qc_lab_simulator.metrics import _RULES

        assert evidence.SUPPORTED_RULES is _RULES
