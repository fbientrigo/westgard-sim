"""Plotting helpers for QC control charts.

All functions return a ``matplotlib.figure.Figure`` so callers decide whether
to display or save the figure.  Domain logic is kept entirely out of this
module.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt

from .models import ControlSeries


def plot_control_chart(
    series: ControlSeries,
    *,
    title: Optional[str] = None,
    figsize: tuple[float, float] = (12, 5),
) -> plt.Figure:
    """Draw a Levey-Jennings control chart for *series*.

    The chart shows:

    * individual QC values connected by a line,
    * horizontal reference lines at mean ± 1 SD, ± 2 SD, and ± 3 SD.

    Parameters
    ----------
    series:
        The control series to plot.
    title:
        Figure title.  Defaults to ``"<analyte> – <scenario> scenario"``.
    figsize:
        Width × height of the figure in inches.

    Returns
    -------
    matplotlib.figure.Figure
    """
    mean = series.runs[0].mean
    sd = series.runs[0].sd
    run_numbers = [r.run_number for r in series.runs]
    values = series.values()

    fig, ax = plt.subplots(figsize=figsize)

    # QC values
    ax.plot(run_numbers, values, marker="o", linewidth=1.5, color="#2166ac", label="QC value")

    # Control limit lines
    _add_limit_line(ax, mean, label="Mean", color="black", linestyle="-")
    _add_limit_line(ax, mean + sd, label="+1 SD", color="#4dac26", linestyle="--")
    _add_limit_line(ax, mean - sd, label="-1 SD", color="#4dac26", linestyle="--")
    _add_limit_line(ax, mean + 2 * sd, label="+2 SD", color="#f1a340", linestyle="-.")
    _add_limit_line(ax, mean - 2 * sd, label="-2 SD", color="#f1a340", linestyle="-.")
    _add_limit_line(ax, mean + 3 * sd, label="+3 SD", color="#d7191c", linestyle=":")
    _add_limit_line(ax, mean - 3 * sd, label="-3 SD", color="#d7191c", linestyle=":")

    ax.set_xlabel("Run number")
    ax.set_ylabel(series.analyte)
    ax.set_title(title or f"{series.analyte} – {series.scenario} scenario")
    ax.legend(loc="upper right", fontsize="small", ncol=2)
    ax.set_xticks(run_numbers)
    fig.tight_layout()
    return fig


def _add_limit_line(ax: plt.Axes, y: float, *, label: str, color: str, linestyle: str) -> None:
    """Draw a single horizontal reference line on *ax*."""
    ax.axhline(y=y, color=color, linestyle=linestyle, linewidth=1.0, label=label)


def save_figure(fig: plt.Figure, path: Path) -> None:
    """Save *fig* to *path*, creating parent directories as needed.

    Parameters
    ----------
    fig:
        The figure to save.
    path:
        Destination file path.  The format is inferred from the extension
        (e.g. ``.png``, ``.svg``).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
