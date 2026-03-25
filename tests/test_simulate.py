"""Tests for simulate.py – core simulation helpers."""

import numpy as np
import pandas as pd
import pytest

from qc_lab_simulator.config import SimConfig
from qc_lab_simulator.models import ControlSeries, QCRun
from qc_lab_simulator.simulate import generate_control_series, series_to_dataframe, simulate_normal


def make_config(**kwargs) -> SimConfig:
    defaults = dict(mean=100.0, sd=2.0, n_runs=20, seed=0)
    defaults.update(kwargs)
    return SimConfig(**defaults)


class TestSimulateNormal:
    def test_returns_control_series(self):
        cfg = make_config()
        result = simulate_normal(cfg)
        assert isinstance(result, ControlSeries)

    def test_correct_number_of_runs(self):
        cfg = make_config(n_runs=25)
        result = simulate_normal(cfg)
        assert len(result) == 25

    def test_scenario_label(self):
        cfg = make_config()
        result = simulate_normal(cfg)
        assert result.scenario == "normal"

    def test_analyte_label(self):
        cfg = make_config()
        cfg.analyte = "Calcium"
        result = simulate_normal(cfg)
        assert result.analyte == "Calcium"

    def test_reproducibility(self):
        cfg = make_config(seed=99)
        a = simulate_normal(cfg)
        b = simulate_normal(cfg)
        assert a.values() == b.values()

    def test_different_seeds_differ(self):
        a = simulate_normal(make_config(seed=1))
        b = simulate_normal(make_config(seed=2))
        assert a.values() != b.values()

    def test_run_numbers_are_1_based(self):
        cfg = make_config(n_runs=5)
        result = simulate_normal(cfg)
        assert [r.run_number for r in result.runs] == [1, 2, 3, 4, 5]


class TestGenerateControlSeries:
    def test_values_stored_correctly(self):
        cfg = make_config()
        arr = np.array([100.0, 101.0, 99.0])
        series = generate_control_series(cfg, arr, scenario="test")
        assert series.values() == pytest.approx([100.0, 101.0, 99.0])

    def test_mean_and_sd_from_config(self):
        cfg = make_config(mean=50.0, sd=5.0)
        arr = np.array([50.0, 55.0])
        series = generate_control_series(cfg, arr)
        assert series.runs[0].mean == 50.0
        assert series.runs[0].sd == 5.0

    def test_z_score_calculation(self):
        cfg = make_config(mean=100.0, sd=2.0)
        arr = np.array([102.0])  # z = (102 - 100) / 2 = 1.0
        series = generate_control_series(cfg, arr)
        assert series.runs[0].z_score == pytest.approx(1.0)


class TestSeriesToDataframe:
    def test_returns_dataframe(self):
        cfg = make_config(n_runs=5)
        series = simulate_normal(cfg)
        df = series_to_dataframe(series)
        assert isinstance(df, pd.DataFrame)

    def test_correct_columns(self):
        cfg = make_config(n_runs=5)
        series = simulate_normal(cfg)
        df = series_to_dataframe(series)
        assert set(df.columns) >= {"run_number", "value", "mean", "sd", "z_score", "analyte", "scenario"}

    def test_correct_row_count(self):
        cfg = make_config(n_runs=10)
        series = simulate_normal(cfg)
        df = series_to_dataframe(series)
        assert len(df) == 10
