from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

from content.authoring_adapter import (
    convert_authoring_to_experiment_catalog,
    load_authoring_catalog,
    write_experiment_catalog,
)
from qc_lab_simulator.web_export import export_experiment_catalog_web_data, load_experiment_catalog


def main() -> None:
    input_path = REPO_ROOT / "content" / "authoring_catalog.example.json"
    technical_path = REPO_ROOT / "outputs" / "smoke" / "experiment_catalog.smoke.json"
    web_output_dir = REPO_ROOT / "outputs" / "smoke" / "web_data"

    authoring = load_authoring_catalog(input_path)
    technical = convert_authoring_to_experiment_catalog(authoring)
    written_technical = write_experiment_catalog(technical, technical_path)

    normalized_experiments = load_experiment_catalog(written_technical)
    result = export_experiment_catalog_web_data(web_output_dir, normalized_experiments)

    experiment_count = int(result["experiment_count"])
    payload_count = int(result["payload_count"])
    index_path = Path(result["index_path"])

    if experiment_count <= 0:
        raise RuntimeError("Smoke flow failed: experiment_count <= 0")
    if payload_count <= 0:
        raise RuntimeError("Smoke flow failed: payload_count <= 0")
    if not index_path.exists():
        raise RuntimeError("Smoke flow failed: index.json was not generated")

    print("Smoke flow OK")
    print(f"  - input: {input_path}")
    print(f"  - technical_catalog: {written_technical}")
    print(f"  - web_output: {web_output_dir}")
    print(f"  - experiments: {experiment_count}")
    print(f"  - payloads: {payload_count}")
    print(f"  - index: {index_path}")


if __name__ == "__main__":
    main()
