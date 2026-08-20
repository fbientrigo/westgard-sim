"""Point-level evidence derivation for the ``student-next`` app.

This module is genuinely new domain code (see decision D4 in
``docs/STUDENT_NEXT_IMPLEMENTATION.md``): :mod:`qc_lab_simulator.rules`
returns booleans only, but the student-facing product needs to say *which*
points are evidence and *why*.

Non-negotiable constraint: this module reproduces **no** rule logic. It
contains no numeric SD threshold, no sign or same-side test and no adjacency
predicate. Every ``triggered`` flag and every ``evidence_runs`` entry is
derived by calling the canonical :mod:`qc_lab_simulator.rules` functions on
the smallest candidate subsets. The single supported-rule registry is
:data:`qc_lab_simulator.metrics._RULES`; this module does not declare a
second one.

Only the standard library, :mod:`qc_lab_simulator.rules` and
:mod:`qc_lab_simulator.metrics` are imported. All three are numpy-free, so
importing this module never imports numpy.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .metrics import _RULES as SUPPORTED_RULES
from . import rules as _rules

# Rule IDs that have no function in qc_lab_simulator.rules / SUPPORTED_RULES.
# These are reference-only: their presence here (and *only* here) is what
# marks them as not evaluable, never an authored flag on content.
REFERENCE_RULES: tuple[str, ...] = ("R_4s", "4_1s", "10x")

# Severity comes from the docstrings in rules.py: 1_2s is documented as the
# warning rule; 1_3s and 2_2s are documented as rejection rules. This mapping
# is presentation metadata about severity *labels*, not a rule predicate.
_SEVERITY: Dict[str, str] = {
    "1_2s": "warning",
    "1_3s": "rejection",
    "2_2s": "rejection",
}

# Tie-break order for governing_rule when multiple rules are triggered:
# a value beyond +-3 SD is the stronger single finding than a same-side pair.
_GOVERNING_PRIORITY: tuple[str, ...] = ("1_3s", "2_2s", "1_2s")


def _evidence_runs_for_rule(rule_id: str, values: List[float], mean: float, sd: float) -> List[int]:
    """Return 1-based run numbers that are evidence for *rule_id*.

    Derived exclusively by calling the canonical rule function on candidate
    subsets, never by re-testing a threshold.
    """
    fn = SUPPORTED_RULES[rule_id]

    if rule_id in ("1_2s", "1_3s"):
        return [i + 1 for i, v in enumerate(values) if fn([v], mean, sd)]

    if rule_id == "2_2s":
        for i in range(len(values) - 1):
            pair = [values[i], values[i + 1]]
            if fn(pair, mean, sd):
                return [i + 1, i + 2]
        return []

    raise ValueError(f"Unknown supported rule id: {rule_id!r}")


def _side_for_runs(evidence_runs: List[int], values: List[float], mean: float) -> Optional[str]:
    """Describe which side of the mean the evidence runs sit on.

    Computed only from the already-identified evidence_runs; never used to
    decide triggering.
    """
    if not evidence_runs:
        return None
    sides = set()
    for run in evidence_runs:
        v = values[run - 1]
        sides.add("positive" if v > mean else "negative")
    if len(sides) > 1:
        return "mixed"
    return sides.pop()


def evaluate_series(values: List[float], mean: float, sd: float) -> Dict[str, Any]:
    """Derive point-level evidence for *values* using the canonical rules.

    Returns the documented shape:

    ``{"rules": [...], "verdict": ..., "governing_rule": ...}``

    ``triggered`` is always the canonical whole-series call
    (``rules.rule_1_2s(values, mean, sd)``, etc.); ``evidence_runs`` is
    derived independently from the same functions on candidate subsets, so
    ``triggered`` is True iff ``evidence_runs`` is non-empty by construction.
    """
    rule_entries: List[Dict[str, Any]] = []
    triggered_by_id: Dict[str, bool] = {}

    for rule_id, fn in SUPPORTED_RULES.items():
        triggered = fn(values, mean, sd)
        evidence_runs = _evidence_runs_for_rule(rule_id, values, mean, sd)
        # By construction (not asserted here as a re-implemented condition):
        # triggered is True iff evidence_runs is non-empty.
        side = _side_for_runs(evidence_runs, values, mean)
        triggered_by_id[rule_id] = triggered
        rule_entries.append(
            {
                "rule": rule_id,
                "triggered": triggered,
                "severity": _SEVERITY[rule_id],
                "evidence_runs": evidence_runs,
                "side": side,
            }
        )

    any_rejection = any(
        entry["triggered"] and entry["severity"] == "rejection" for entry in rule_entries
    )
    warning_triggered = triggered_by_id.get("1_2s", False)

    if any_rejection:
        verdict = "reject"
    elif warning_triggered:
        verdict = "review"
    else:
        verdict = "accept"

    governing_rule: Optional[str] = None
    for candidate in _GOVERNING_PRIORITY:
        if triggered_by_id.get(candidate, False):
            governing_rule = candidate
            break

    return {
        "rules": rule_entries,
        "verdict": verdict,
        "governing_rule": governing_rule,
    }
