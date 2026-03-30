from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

from qc_lab_simulator.config import SimConfig
from qc_lab_simulator.web_export import (
    export_all_web_data,
    export_experiment_catalog_web_data,
    load_experiment_catalog,
)

DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "web_data"
FIXED_CONFIG = SimConfig(mean=100.0, sd=2.0, n_runs=30, seed=42, analyte="Glucose")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export web-ready QC scenarios to JSON files.")
    _ = parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Target folder for exported JSON files (default: outputs/web_data).",
    )
    _ = parser.add_argument(
        "--catalog",
        type=Path,
        default=None,
        help=(
            "Optional experiment catalog JSON. If provided, exports a full static dataset "
            "for GitHub Pages under output-dir/index.json and output-dir/experiments/*."
        ),
    )
    return parser.parse_args()


def _display_relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _run_default_export(output_dir: Path) -> None:
    exported = export_all_web_data(output_dir, FIXED_CONFIG)
    print("\nExported scenario payloads:")
    for scenario_name in sorted(exported):
        written_path = exported[scenario_name]
        print(f"  - {scenario_name}: {_display_relative_path(written_path)}")


def _run_catalog_export(output_dir: Path, catalog_path: Path) -> None:
    experiments = load_experiment_catalog(catalog_path)
    result = export_experiment_catalog_web_data(output_dir, experiments)
    index_path = Path(result["index_path"])
    experiment_count = int(result["experiment_count"])
    payload_count = int(result["payload_count"])
    print("\nExported experiment catalog:")
    print(f"  - catalog: {_display_relative_path(catalog_path)}")
    print(f"  - index: {_display_relative_path(index_path)}")
    print(f"  - experiments: {experiment_count}")
    print(f"  - payloads: {payload_count}")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    catalog_arg = args.catalog

    if catalog_arg is not None:
        _run_catalog_export(output_dir, Path(catalog_arg))
        return

    _run_default_export(output_dir)


if __name__ == "__main__":
    main()
