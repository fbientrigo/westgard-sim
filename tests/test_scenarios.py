"""Tests for scenarios.py – scenario generators."""

import pytest

from qc_lab_simulator.config import SimConfig
from qc_lab_simulator.scenarios import (
    scenario_bias,
    scenario_drift,
    scenario_imprecision,
    scenario_normal,
)


def make_config(**kwargs) -> SimConfig:
    defaults = dict(mean=100.0, sd=2.0, n_runs=30, seed=42)
    defaults.update(kwargs)
    return SimConfig(**defaults)


class TestScenarioNormal:
    def test_label(self):
        assert scenario_normal(make_config()).scenario == "normal"

    def test_length(self):
        cfg = make_config(n_runs=20)
        assert len(scenario_normal(cfg)) == 20

    def test_reproducibility(self):
        cfg = make_config(seed=7)
        assert scenario_normal(cfg).values() == scenario_normal(cfg).values()


class TestScenarioBias:
    def test_label(self):
        assert scenario_bias(make_config()).scenario == "bias"

    def test_pre_shift_runs_unchanged(self):
        """Runs before start_run should match the normal scenario values."""
        cfg = make_config(seed=0, n_runs=30)
        normal = scenario_normal(cfg)
        biased = scenario_bias(cfg, shift_sd=3.0, start_run=11)
        # First 10 runs (indices 0-9) should be identical
        assert normal.values()[:10] == pytest.approx(biased.values()[:10])

    def test_shifted_runs_are_higher(self):
        """After shift (positive shift_sd) all affected values should be higher."""
        cfg = make_config(seed=0, n_runs=30)
        normal = scenario_normal(cfg)
        biased = scenario_bias(cfg, shift_sd=3.0, start_run=11)
        shift = 3.0 * cfg.sd
        for i in range(10, cfg.n_runs):
            assert biased.values()[i] == pytest.approx(normal.values()[i] + shift)

    def test_large_shift_triggers_1_3s(self):
        """A 4 SD shift should reliably trigger the 1_3s rule."""
        from qc_lab_simulator.rules import rule_1_3s

        cfg = make_config(sd=2.0, n_runs=30, seed=42)
        series = scenario_bias(cfg, shift_sd=4.0, start_run=11)
        assert rule_1_3s(series.values(), cfg.mean, cfg.sd)


class TestScenarioDrift:
    def test_label(self):
        assert scenario_drift(make_config()).scenario == "drift"

    def test_first_affected_run_has_small_offset(self):
        """The very first affected run should have only a tiny drift offset."""
        cfg = make_config(seed=0, n_runs=30)
        normal = scenario_normal(cfg)
        drifted = scenario_drift(cfg, total_drift_sd=4.0, start_run=11)
        # linspace starts at 0 so first affected value equals the normal value
        assert drifted.values()[10] == pytest.approx(normal.values()[10])

    def test_last_run_has_full_drift(self):
        """The final run should have the full drift applied."""
        cfg = make_config(seed=0, n_runs=30)
        normal = scenario_normal(cfg)
        total_drift = 4.0 * cfg.sd
        drifted = scenario_drift(cfg, total_drift_sd=4.0, start_run=11)
        assert drifted.values()[-1] == pytest.approx(normal.values()[-1] + total_drift)

    def test_length(self):
        cfg = make_config(n_runs=20)
        assert len(scenario_drift(cfg)) == 20


class TestScenarioImprecision:
    def test_label(self):
        assert scenario_imprecision(make_config()).scenario == "imprecision"

    def test_length(self):
        cfg = make_config(n_runs=20)
        assert len(scenario_imprecision(cfg)) == 20

    def test_pre_affected_runs_normal(self):
        """Runs before start_run should be identical to the normal scenario."""
        cfg = make_config(seed=0, n_runs=30)
        normal = scenario_normal(cfg)
        imprecise = scenario_imprecision(cfg, sd_multiplier=3.0, start_run=11)
        # The first 10 runs use the same RNG state so they match.
        assert normal.values()[:10] == pytest.approx(imprecise.values()[:10])

    def test_reproducibility(self):
        cfg = make_config(seed=13)
        a = scenario_imprecision(cfg)
        b = scenario_imprecision(cfg)
        assert a.values() == b.values()
