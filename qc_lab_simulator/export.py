"""Serialisation helpers – convert simulator objects to JSON-friendly dicts.

The functions here produce plain Python structures (dicts and lists) that can
be passed to ``json.dumps`` without any custom encoder.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from .models import ControlSeries
from .simulate import series_to_dataframe


def series_to_dict(series: ControlSeries) -> Dict[str, Any]:
    """Convert a :class:`~qc_lab_simulator.models.ControlSeries` to a dict.

    Parameters
    ----------
    series:
        The control series to serialise.

    Returns
    -------
    dict
        Plain Python dict with keys ``analyte``, ``scenario``, and ``runs``.
        Each run is itself a dict with ``run_number``, ``value``, ``mean``,
        ``sd``, and ``z_score``.
    """
    return {
        "analyte": series.analyte,
        "scenario": series.scenario,
        "runs": [
            {
                "run_number": r.run_number,
                "value": r.value,
                "mean": r.mean,
                "sd": r.sd,
                "z_score": r.z_score,
            }
            for r in series.runs
        ],
    }


def save_series_json(series: ControlSeries, path: Path) -> None:
    """Write a :class:`~qc_lab_simulator.models.ControlSeries` as JSON.

    Parameters
    ----------
    series:
        Series to save.
    path:
        Destination file path (created or overwritten).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(series_to_dict(series), fh, indent=2)


def save_metrics_json(metrics: Dict[str, Any], path: Path) -> None:
    """Write a metrics dict (from :func:`~qc_lab_simulator.metrics.compute_metrics`) as JSON.

    Parameters
    ----------
    metrics:
        Metrics dictionary to serialise.
    path:
        Destination file path (created or overwritten).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)


def save_series_csv(series: ControlSeries, path: Path) -> None:
    """Write a :class:`~qc_lab_simulator.models.ControlSeries` as a CSV file.

    Parameters
    ----------
    series:
        Series to save.
    path:
        Destination file path (created or overwritten).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df: pd.DataFrame = series_to_dataframe(series)
    df.to_csv(path, index=False)
