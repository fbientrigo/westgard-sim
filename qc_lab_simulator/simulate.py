"""Core simulation helpers.

All functions are pure: they take parameters, return data, and have no side
effects beyond creating ``numpy`` random state objects.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import SimConfig
from .models import ControlSeries, QCRun


def generate_control_series(
    config: SimConfig,
    values: np.ndarray,
    *,
    scenario: str = "normal",
) -> ControlSeries:
    """Wrap a pre-generated value array into a :class:`ControlSeries`.

    Parameters
    ----------
    config:
        Simulation configuration (provides mean, sd, analyte name).
    values:
        Array of measured QC values, one per run.
    scenario:
        Human-readable scenario label stored on the result.

    Returns
    -------
    ControlSeries
        Object containing one :class:`QCRun` per value.
    """
    runs = [
        QCRun(run_number=i + 1, value=float(v), mean=config.mean, sd=config.sd)
        for i, v in enumerate(values)
    ]
    return ControlSeries(analyte=config.analyte, scenario=scenario, runs=runs)


def simulate_normal(config: SimConfig) -> ControlSeries:
    """Generate a baseline Gaussian control series.

    Parameters
    ----------
    config:
        Simulation parameters (mean, sd, n_runs, seed).

    Returns
    -------
    ControlSeries
        A series with *n_runs* values drawn from
        ``Normal(config.mean, config.sd)``.
    """
    rng = np.random.default_rng(config.seed)
    values = rng.normal(loc=config.mean, scale=config.sd, size=config.n_runs)
    return generate_control_series(config, values, scenario="normal")


def series_to_dataframe(series: ControlSeries) -> pd.DataFrame:
    """Convert a :class:`ControlSeries` to a tidy :class:`pandas.DataFrame`.

    Columns
    -------
    run_number, value, mean, sd, z_score, analyte, scenario

    Parameters
    ----------
    series:
        The control series to convert.

    Returns
    -------
    pandas.DataFrame
    """
    rows = [
        {
            "run_number": r.run_number,
            "value": r.value,
            "mean": r.mean,
            "sd": r.sd,
            "z_score": r.z_score,
        }
        for r in series.runs
    ]
    df = pd.DataFrame(rows)
    df["analyte"] = series.analyte
    df["scenario"] = series.scenario
    return df
