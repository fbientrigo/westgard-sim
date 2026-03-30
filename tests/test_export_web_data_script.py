"""Verification that the export web data CLI stays contract-compliant."""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import cast

from qc_lab_simulator.web_export import REQUIRED_TOP_LEVEL_KEYS, validate_web_payload


def test_export_web_data_script(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "export_web_data.py"
    _ = subprocess.run(
        [sys.executable, str(script_path), "--output-dir", str(tmp_path)],
        check=True,
    )

    expected_files = [
        "normal.json",
        "bias.json",
        "drift.json",
        "imprecision.json",
    ]

    for file_name in expected_files:
        output_path = tmp_path / file_name
        assert output_path.exists(), f"{file_name} was not created"
        payload = cast(Mapping[str, object], json.loads(output_path.read_text(encoding="utf-8")))
        assert set(payload.keys()) == set(REQUIRED_TOP_LEVEL_KEYS)
        assert payload["scenario_type"] == Path(file_name).stem
        assert validate_web_payload(payload) == []


def test_export_web_data_script_with_catalog(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "export_web_data.py"
    catalog_path = repo_root / "content" / "experiment_catalog.json"
    _ = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--output-dir",
            str(tmp_path),
            "--catalog",
            str(catalog_path),
        ],
        check=True,
    )

    index_path = tmp_path / "index.json"
    assert index_path.exists()
    index = cast(Mapping[str, object], json.loads(index_path.read_text(encoding="utf-8")))
    experiments = cast(list[Mapping[str, object]], index["experiments"])
    assert len(experiments) > 0

    manifest_rel = cast(str, experiments[0]["manifest_path"])
    manifest_path = tmp_path / manifest_rel
    assert manifest_path.exists()
