from __future__ import annotations

import json
from pathlib import Path

import pytest

from qc_lab_simulator.config import SimConfig
from qc_lab_simulator.web_export import build_web_scenario_payload
from scripts.authoring_ops import backup_dir_if_exists, backup_file_if_exists, verify_export_output


def _write_payload(path: Path, scenario_key: str = "normal") -> None:
    cfg = SimConfig(mean=100.0, sd=2.0, n_runs=30, seed=42, analyte="Glucose")
    payload = build_web_scenario_payload(scenario_key, cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_verify_export_output_happy_path(tmp_path: Path) -> None:
    export_dir = tmp_path / "web"
    manifest_rel = "experiments/exp_a/manifest.json"
    payload_rel = "experiments/exp_a/scenario_1.json"

    _write_payload(export_dir / payload_rel, "normal")
    manifest = {
        "id": "exp_a",
        "title": "Experiment A",
        "description": "desc",
        "config": {"mean": 100.0, "sd": 2.0, "n_runs": 30, "seed": 42, "analyte": "Glucose"},
        "scenarios": [{"id": "scenario_1", "scenario_key": "normal", "path": payload_rel}],
    }
    (export_dir / manifest_rel).parent.mkdir(parents=True, exist_ok=True)
    (export_dir / manifest_rel).write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    index = {
        "experiments": [
            {
                "id": "exp_a",
                "title": "Experiment A",
                "description": "desc",
                "manifest_path": manifest_rel,
                "scenario_count": 1,
            }
        ]
    }
    (export_dir / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")

    result = verify_export_output(export_dir)
    assert result["experiment_count"] == 1
    assert result["payload_count"] == 1


def test_verify_export_output_fails_when_manifest_missing(tmp_path: Path) -> None:
    export_dir = tmp_path / "web"
    export_dir.mkdir(parents=True, exist_ok=True)
    index = {
        "experiments": [
            {
                "id": "exp_a",
                "title": "Experiment A",
                "description": "desc",
                "manifest_path": "experiments/exp_a/manifest.json",
                "scenario_count": 1,
            }
        ]
    }
    (export_dir / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    with pytest.raises(ValueError) as exc_info:
        _ = verify_export_output(export_dir)
    assert "Missing manifest for experiment 'exp_a'" in str(exc_info.value)


def test_backup_file_if_exists_creates_backup(tmp_path: Path) -> None:
    target = tmp_path / "catalog.json"
    target.write_text('{"a":1}', encoding="utf-8")
    backups = tmp_path / "backups"
    backup = backup_file_if_exists(target, backups, label="technical_catalog")
    assert isinstance(backup, Path)
    assert backup.exists()
    assert backup.suffix == ".json"


def test_backup_dir_if_exists_creates_zip(tmp_path: Path) -> None:
    target = tmp_path / "web_data"
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.json").write_text('{"experiments":[]}', encoding="utf-8")
    backups = tmp_path / "backups"
    archive = backup_dir_if_exists(target, backups, label="web_export")
    assert isinstance(archive, Path)
    assert archive.exists()
    assert archive.suffix == ".zip"
