"""Demo script: runs all four scenarios and saves plots + JSON to outputs/.

Usage
-----
    python scripts/run_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running from the repo root without installing the package.
sys.path.insert(0, str(Path(__file__).parent.parent))

from qc_lab_simulator.config import SimConfig
from qc_lab_simulator.export import save_metrics_json, save_series_csv, save_series_json
from qc_lab_simulator.metrics import compute_metrics
from qc_lab_simulator.plots import plot_control_chart, save_figure
from qc_lab_simulator.scenarios import (
    scenario_bias,
    scenario_drift,
    scenario_imprecision,
    scenario_normal,
)

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"


def run_scenario(name: str, series, config: SimConfig) -> None:
    """Run metrics + export for one scenario."""
    print(f"\n{'='*50}")
    print(f"Scenario: {name}")
    metrics = compute_metrics(series)
    for rule, result in metrics["rules"].items():
        status = "TRIGGERED" if result["triggered"] else "ok"
        first = result["first_run"]
        false_alarm = " (false alarm)" if result["false_alarm"] else ""
        print(f"  Rule {rule}: {status}  first_run={first}{false_alarm}")

    # Save data
    save_series_json(series, OUTPUT_DIR / f"{name}_series.json")
    save_series_csv(series, OUTPUT_DIR / f"{name}_series.csv")
    save_metrics_json(metrics, OUTPUT_DIR / f"{name}_metrics.json")

    # Save plot
    fig = plot_control_chart(series)
    save_figure(fig, OUTPUT_DIR / f"{name}_chart.png")
    print(f"  Plot saved → outputs/{name}_chart.png")


def main() -> None:
    config = SimConfig(mean=100.0, sd=2.0, n_runs=30, seed=42, analyte="Glucose")

    scenarios = [
        ("normal", scenario_normal(config)),
        ("bias", scenario_bias(config, shift_sd=3.0, start_run=11)),
        ("drift", scenario_drift(config, total_drift_sd=4.0, start_run=11)),
        ("imprecision", scenario_imprecision(config, sd_multiplier=3.0, start_run=11)),
    ]

    for name, series in scenarios:
        run_scenario(name, series, config)

    print(f"\nAll outputs saved to: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
