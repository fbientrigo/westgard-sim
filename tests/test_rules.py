"""Tests for rules.py – Westgard QC detection rules."""

import pytest

from qc_lab_simulator.rules import first_violation, rule_1_2s, rule_1_3s, rule_2_2s

MEAN = 100.0
SD = 2.0


# ---------------------------------------------------------------------------
# Helper builders
# ---------------------------------------------------------------------------

def values_all_normal(n: int = 10) -> list[float]:
    """Values at exactly the mean – should never trigger any rule."""
    return [MEAN] * n


def values_one_above_2sd() -> list[float]:
    """One value just above 2 SD; no consecutive pair."""
    return [MEAN, MEAN, MEAN + 2.1 * SD, MEAN, MEAN]


def values_one_above_3sd() -> list[float]:
    """One value above 3 SD."""
    return [MEAN, MEAN, MEAN + 3.1 * SD, MEAN]


def values_two_consecutive_above_2sd() -> list[float]:
    """Two consecutive values both above +2 SD."""
    return [MEAN, MEAN + 2.1 * SD, MEAN + 2.1 * SD, MEAN]


def values_two_consecutive_below_2sd() -> list[float]:
    """Two consecutive values both below -2 SD."""
    return [MEAN, MEAN - 2.1 * SD, MEAN - 2.1 * SD, MEAN]


def values_two_consecutive_different_sides() -> list[float]:
    """Two consecutive values outside 2 SD but on opposite sides – no 2_2s."""
    return [MEAN + 2.1 * SD, MEAN - 2.1 * SD]


# ---------------------------------------------------------------------------
# rule_1_2s
# ---------------------------------------------------------------------------

class TestRule1_2s:
    def test_no_trigger_when_all_within_2sd(self):
        assert rule_1_2s(values_all_normal(), MEAN, SD) is False

    def test_triggers_on_value_above_2sd(self):
        assert rule_1_2s(values_one_above_2sd(), MEAN, SD) is True

    def test_triggers_on_value_below_2sd(self):
        vals = [MEAN, MEAN - 2.1 * SD, MEAN]
        assert rule_1_2s(vals, MEAN, SD) is True

    def test_boundary_exactly_2sd_does_not_trigger(self):
        """Values at exactly ±2 SD (not strictly greater) should NOT trigger."""
        vals = [MEAN + 2.0 * SD]
        assert rule_1_2s(vals, MEAN, SD) is False

    def test_single_normal_value(self):
        assert rule_1_2s([MEAN], MEAN, SD) is False

    def test_triggers_on_3sd_value(self):
        """A value beyond 3 SD also exceeds 2 SD."""
        assert rule_1_2s(values_one_above_3sd(), MEAN, SD) is True


# ---------------------------------------------------------------------------
# rule_1_3s
# ---------------------------------------------------------------------------

class TestRule1_3s:
    def test_no_trigger_when_all_within_3sd(self):
        assert rule_1_3s(values_all_normal(), MEAN, SD) is False

    def test_no_trigger_on_2sd_violation_only(self):
        """A 2 SD violation should NOT trigger the 3 SD rule."""
        assert rule_1_3s(values_one_above_2sd(), MEAN, SD) is False

    def test_triggers_on_value_above_3sd(self):
        assert rule_1_3s(values_one_above_3sd(), MEAN, SD) is True

    def test_triggers_on_value_below_3sd(self):
        vals = [MEAN, MEAN - 3.1 * SD]
        assert rule_1_3s(vals, MEAN, SD) is True

    def test_boundary_exactly_3sd_does_not_trigger(self):
        vals = [MEAN + 3.0 * SD]
        assert rule_1_3s(vals, MEAN, SD) is False


# ---------------------------------------------------------------------------
# rule_2_2s
# ---------------------------------------------------------------------------

class TestRule2_2s:
    def test_no_trigger_when_all_normal(self):
        assert rule_2_2s(values_all_normal(), MEAN, SD) is False

    def test_triggers_two_consecutive_above_2sd(self):
        assert rule_2_2s(values_two_consecutive_above_2sd(), MEAN, SD) is True

    def test_triggers_two_consecutive_below_2sd(self):
        assert rule_2_2s(values_two_consecutive_below_2sd(), MEAN, SD) is True

    def test_no_trigger_opposite_sides(self):
        """Consecutive values on opposite sides should NOT trigger 2_2s."""
        assert rule_2_2s(values_two_consecutive_different_sides(), MEAN, SD) is False

    def test_no_trigger_single_2sd_violation(self):
        assert rule_2_2s(values_one_above_2sd(), MEAN, SD) is False

    def test_non_consecutive_pair_does_not_trigger(self):
        vals = [MEAN + 2.1 * SD, MEAN, MEAN + 2.1 * SD]
        assert rule_2_2s(vals, MEAN, SD) is False


# ---------------------------------------------------------------------------
# first_violation
# ---------------------------------------------------------------------------

class TestFirstViolation:
    def test_returns_none_when_no_violation(self):
        result = first_violation(values_all_normal(), MEAN, SD, rule_1_3s)
        assert result is None

    def test_returns_correct_run_index(self):
        # Third value exceeds 2 SD → first violation at run 3
        vals = [MEAN, MEAN, MEAN + 2.5 * SD, MEAN]
        result = first_violation(vals, MEAN, SD, rule_1_2s)
        assert result == 3

    def test_first_run_violation(self):
        vals = [MEAN + 3.5 * SD, MEAN]
        result = first_violation(vals, MEAN, SD, rule_1_3s)
        assert result == 1

    def test_2_2s_needs_two_runs(self):
        """2_2s requires at least two values, so earliest is run 2."""
        vals = [MEAN + 2.5 * SD, MEAN + 2.5 * SD, MEAN]
        result = first_violation(vals, MEAN, SD, rule_2_2s)
        assert result == 2
