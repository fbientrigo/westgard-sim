"""Scenario generators.

Each function accepts a :class:`~qc_lab_simulator.config.SimConfig` and
returns a :class:`~qc_lab_simulator.models.ControlSeries` whose values
simulate a specific failure mode.

Design notes
------------
* All scenarios begin with the same Gaussian baseline so that early runs look
  normal.
* The failure is injected from a configurable start run onward.
* Functions are pure – they do not mutate the config.
"""

from __future__ import annotations

import numpy as np

from .config import SimConfig
from .models import ControlSeries
from .simulate import generate_control_series


def scenario_normal(config: SimConfig) -> ControlSeries:
    """Baseline scenario: all runs follow *Normal(mean, sd)*.

    Parameters
    ----------
    config:
        Simulation parameters.

    Returns
    -------
    ControlSeries
        Label ``"normal"``.
    """
    rng = np.random.default_rng(config.seed)
    values = rng.normal(loc=config.mean, scale=config.sd, size=config.n_runs)
    return generate_control_series(config, values, scenario="normal")


def scenario_bias(
    config: SimConfig,
    *,
    shift_sd: float = 3.0,
    start_run: int = 11,
) -> ControlSeries:
    """Sudden bias shift at *start_run*.

    From *start_run* onward the process mean jumps by ``shift_sd * config.sd``.

    Parameters
    ----------
    config:
        Simulation parameters.
    shift_sd:
        Magnitude of the shift expressed as multiples of ``config.sd``.
    start_run:
        1-based index of the first affected run.

    Returns
    -------
    ControlSeries
        Label ``"bias"``.
    """
    rng = np.random.default_rng(config.seed)
    values = rng.normal(loc=config.mean, scale=config.sd, size=config.n_runs)
    shift = shift_sd * config.sd
    values[start_run - 1 :] += shift
    return generate_control_series(config, values, scenario="bias")


def scenario_drift(
    config: SimConfig,
    *,
    total_drift_sd: float = 4.0,
    start_run: int = 11,
) -> ControlSeries:
    """Gradual linear drift from *start_run* to the last run.

    The mean shifts linearly from 0 to ``total_drift_sd * config.sd`` over the
    affected runs.

    Parameters
    ----------
    config:
        Simulation parameters.
    total_drift_sd:
        Total magnitude of the drift at the last run, in multiples of
        ``config.sd``.
    start_run:
        1-based index where the drift begins.

    Returns
    -------
    ControlSeries
        Label ``"drift"``.
    """
    rng = np.random.default_rng(config.seed)
    values = rng.normal(loc=config.mean, scale=config.sd, size=config.n_runs)
    n_affected = config.n_runs - (start_run - 1)
    if n_affected > 0:
        drift = np.linspace(0.0, total_drift_sd * config.sd, n_affected)
        values[start_run - 1 :] += drift
    return generate_control_series(config, values, scenario="drift")


def scenario_imprecision(
    config: SimConfig,
    *,
    sd_multiplier: float = 3.0,
    start_run: int = 11,
) -> ControlSeries:
    """Increased imprecision from *start_run* onward.

    The standard deviation is multiplied by *sd_multiplier* for affected runs
    while the mean stays at ``config.mean``.

    Parameters
    ----------
    config:
        Simulation parameters.
    sd_multiplier:
        Factor by which ``config.sd`` is increased for affected runs.
    start_run:
        1-based index of the first affected run.

    Returns
    -------
    ControlSeries
        Label ``"imprecision"``.
    """
    rng = np.random.default_rng(config.seed)
    n_normal = start_run - 1
    n_affected = config.n_runs - n_normal

    normal_vals = rng.normal(loc=config.mean, scale=config.sd, size=n_normal)
    affected_vals = rng.normal(
        loc=config.mean, scale=config.sd * sd_multiplier, size=n_affected
    )
    values = np.concatenate([normal_vals, affected_vals])
    return generate_control_series(config, values, scenario="imprecision")
