"""Summary metrics computed from a :class:`~qc_lab_simulator.models.ControlSeries`.

All functions return plain Python dicts so results are trivially serialisable.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .models import ControlSeries
from .rules import first_violation, rule_1_2s, rule_1_3s, rule_2_2s

_RULES = {
    "1_2s": rule_1_2s,
    "1_3s": rule_1_3s,
    "2_2s": rule_2_2s,
}


def compute_metrics(series: ControlSeries) -> Dict[str, Any]:
    """Compute rule-violation metrics for *series*.

    For every implemented rule this function records:

    * ``triggered`` – whether the rule fired at all.
    * ``first_run`` – 1-based index of the first triggering run (``null`` if
      the rule never fired).

    Additionally it records whether the series is a normal scenario and, if so,
    marks any triggered rule as a ``false_alarm``.

    Parameters
    ----------
    series:
        A :class:`~qc_lab_simulator.models.ControlSeries` to evaluate.

    Returns
    -------
    dict
        Keys: ``analyte``, ``scenario``, ``n_runs``, ``rules``, and for each
        rule entry ``triggered``, ``first_run``, ``false_alarm``.
    """
    values: List[float] = series.values()
    mean = series.runs[0].mean
    sd = series.runs[0].sd
    is_normal = series.scenario == "normal"

    rule_results: Dict[str, Any] = {}
    for name, fn in _RULES.items():
        triggered = fn(values, mean, sd)
        first_run = first_violation(values, mean, sd, fn) if triggered else None
        rule_results[name] = {
            "triggered": triggered,
            "first_run": first_run,
            "false_alarm": triggered and is_normal,
        }

    return {
        "analyte": series.analyte,
        "scenario": series.scenario,
        "n_runs": len(series),
        "rules": rule_results,
    }
