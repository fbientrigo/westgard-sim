# westgard-sim

Reproducible simulator for internal quality control (QC) in clinical laboratory education.

## Overview

`qc-lab-simulator` is a modular Python library that models control runs over time, injects realistic failure scenarios, evaluates Westgard QC detection rules, and generates Levey-Jennings control charts.  It is designed as the scientific core of a future interactive web playground.

## Project structure

```
qc_lab_simulator/
  __init__.py   – package metadata
  config.py     – SimConfig dataclass
  models.py     – QCRun and ControlSeries dataclasses
  simulate.py   – core Gaussian simulation helpers
  scenarios.py  – normal / bias / drift / imprecision scenario generators
  rules.py      – 1_2s, 1_3s, 2_2s Westgard detection rules
  metrics.py    – per-rule summary metrics
  export.py     – JSON and CSV serialisation helpers
  plots.py      – Levey-Jennings control chart plotting

scripts/
  run_demo.py   – end-to-end demo (all four scenarios)

tests/
  test_simulate.py
  test_scenarios.py
  test_rules.py
```

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the demo (saves plots and JSON to outputs/)
python scripts/run_demo.py
```

## Running tests

```bash
pytest
```

## Scenarios

| Scenario | Description |
|---|---|
| `normal` | Baseline Gaussian data – no failure injected |
| `bias` | Sudden mean shift at a chosen run |
| `drift` | Gradual linear drift from a chosen run |
| `imprecision` | Increased SD (wider scatter) from a chosen run |

## Westgard rules implemented

| Rule | Description |
|---|---|
| `1_2s` | Warning: any single value exceeds ±2 SD |
| `1_3s` | Rejection: any single value exceeds ±3 SD |
| `2_2s` | Rejection: two consecutive values both exceed +2 SD or both exceed −2 SD |

## Design principles

- **Pure functions** – no hidden state; results are reproducible given the same seed.
- **Small modules** – each file has a single responsibility.
- **JSON-friendly outputs** – all data can be serialised without a custom encoder.
- **No web framework** – designed for easy embedding into Pyodide / JavaScript later.
