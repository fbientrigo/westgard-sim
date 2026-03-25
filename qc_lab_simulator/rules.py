"""Westgard QC detection rules.

Each rule is a pure function with the signature::

    rule_<name>(values: List[float], mean: float, sd: float) -> bool

``True`` means the rule has been violated (alarm triggered).

Rules implemented
-----------------
* **1₂s** – any single value exceeds ±2 SD (warning rule).
* **1₃s** – any single value exceeds ±3 SD (rejection rule).
* **2₂s** – two consecutive values both exceed +2 SD *or* both exceed −2 SD
  (rejection rule).

References
----------
Westgard, J. O., Barry, P. L., Hunt, M. R., & Groth, T. (1981).
A multi-rule Shewhart chart for quality control in clinical chemistry.
*Clinical Chemistry*, 27(3), 493-501.
"""

from __future__ import annotations

from typing import List


def rule_1_2s(values: List[float], mean: float, sd: float) -> bool:
    """Return *True* if any value exceeds mean ± 2 SD (warning rule 1₂s).

    Parameters
    ----------
    values:
        Ordered list of QC measurements.
    mean:
        Expected process mean.
    sd:
        Expected process standard deviation.

    Returns
    -------
    bool
        ``True`` if the rule is violated.
    """
    limit = 2.0 * sd
    return any(abs(v - mean) > limit for v in values)


def rule_1_3s(values: List[float], mean: float, sd: float) -> bool:
    """Return *True* if any value exceeds mean ± 3 SD (rejection rule 1₃s).

    Parameters
    ----------
    values:
        Ordered list of QC measurements.
    mean:
        Expected process mean.
    sd:
        Expected process standard deviation.

    Returns
    -------
    bool
        ``True`` if the rule is violated.
    """
    limit = 3.0 * sd
    return any(abs(v - mean) > limit for v in values)


def rule_2_2s(values: List[float], mean: float, sd: float) -> bool:
    """Return *True* if two consecutive values both exceed +2 SD or −2 SD.

    Both consecutive points must be on the *same* side of the mean (rejection
    rule 2₂s).

    Parameters
    ----------
    values:
        Ordered list of QC measurements.
    mean:
        Expected process mean.
    sd:
        Expected process standard deviation.

    Returns
    -------
    bool
        ``True`` if the rule is violated.
    """
    limit = 2.0 * sd
    for i in range(len(values) - 1):
        a = values[i] - mean
        b = values[i + 1] - mean
        if a > limit and b > limit:
            return True
        if a < -limit and b < -limit:
            return True
    return False


def first_violation(
    values: List[float],
    mean: float,
    sd: float,
    rule_fn,
) -> int | None:
    """Return the 1-based index of the run that first triggers *rule_fn*.

    The rule is re-evaluated after appending each successive value so that the
    returned index is the *earliest* run at which the rule becomes violated.

    Parameters
    ----------
    values:
        Full ordered list of QC measurements.
    mean:
        Expected process mean.
    sd:
        Expected process standard deviation.
    rule_fn:
        One of the rule functions in this module.

    Returns
    -------
    int or None
        1-based run number where the rule first triggers, or ``None`` if the
        rule is never violated.
    """
    for i in range(1, len(values) + 1):
        if rule_fn(values[:i], mean, sd):
            return i
    return None
