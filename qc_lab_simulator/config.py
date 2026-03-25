"""Simulation configuration with sensible defaults."""

from dataclasses import dataclass, field


@dataclass
class SimConfig:
    """Parameters that define a single QC simulation run.

    Attributes
    ----------
    mean : float
        Target analyte mean (e.g. 100 mg/dL).
    sd : float
        Target standard deviation under normal conditions.
    n_runs : int
        Number of QC measurements to simulate.
    seed : int
        Random seed for reproducibility.
    analyte : str
        Human-readable label for the analyte.
    """

    mean: float = 100.0
    sd: float = 2.0
    n_runs: int = 30
    seed: int = 42
    analyte: str = "Glucose"


DEFAULT_CONFIG = SimConfig()
