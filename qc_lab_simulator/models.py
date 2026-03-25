"""Domain models for the QC simulator."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class QCRun:
    """A single quality-control measurement.

    Attributes
    ----------
    run_number : int
        Sequential index of this run (1-based).
    value : float
        Measured analyte value.
    mean : float
        Expected mean used for this run.
    sd : float
        Expected standard deviation used for this run.
    """

    run_number: int
    value: float
    mean: float
    sd: float

    @property
    def z_score(self) -> float:
        """Standardised deviation from the expected mean."""
        return (self.value - self.mean) / self.sd


@dataclass
class ControlSeries:
    """A full sequence of QC runs for one scenario.

    Attributes
    ----------
    analyte : str
        Name of the analyte being measured.
    scenario : str
        Name of the scenario (e.g. 'normal', 'bias').
    runs : list of QCRun
        The individual measurements in order.
    """

    analyte: str
    scenario: str
    runs: List[QCRun] = field(default_factory=list)

    def __len__(self) -> int:  # noqa: D105
        return len(self.runs)

    def values(self) -> List[float]:
        """Return the raw measured values in run order."""
        return [r.value for r in self.runs]

    def z_scores(self) -> List[float]:
        """Return the z-score for every run."""
        return [r.z_score for r in self.runs]
