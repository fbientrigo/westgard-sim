from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.authoring_adapter import (
    convert_authoring_to_experiment_catalog,
    load_authoring_catalog,
    write_experiment_catalog,
)


def _load_example() -> dict:
    repo_root = Path(__file__).resolve().parents[1]
    path = repo_root / "content" / "authoring_catalog.example.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_convert_maps_core_fields_and_parameters():
    data = _load_example()
    converted = convert_authoring_to_experiment_catalog(data)

    assert "experiments" in converted
    exp = converted["experiments"][0]
    assert exp["id"] == "glucose_intro_course"
    assert exp["config"]["analyte"] == "Glucose"

    by_id = {s["id"]: s for s in exp["scenarios"]}
    assert by_id["syst_bias_early"]["scenario_key"] == "bias"
    assert by_id["syst_bias_early"]["parameters"]["shift_sd"] == 3.0
    assert by_id["rand_precision_loss"]["scenario_key"] == "imprecision"
    assert by_id["rand_precision_loss"]["parameters"]["sd_multiplier"] == 2.8
    assert by_id["trend_progressive"]["scenario_key"] == "drift"
    assert by_id["trend_progressive"]["parameters"]["total_drift_sd"] == pytest.approx(5.5)


def test_convert_omits_education_by_default():
    converted = convert_authoring_to_experiment_catalog(_load_example())
    assert "authoring_metadata" not in converted
    first_scenario = converted["experiments"][0]["scenarios"][0]
    assert "education" not in first_scenario


def test_convert_can_include_education_metadata():
    converted = convert_authoring_to_experiment_catalog(
        _load_example(),
        include_education_metadata=True,
    )
    assert "authoring_metadata" in converted
    scenarios = converted["authoring_metadata"]["experiments"][0]["scenarios"]
    assert scenarios[0]["education"]["questions"]


def test_load_and_write_roundtrip():
    repo_root = Path(__file__).resolve().parents[1]
    input_path = repo_root / "content" / "authoring_catalog.example.json"
    loaded = load_authoring_catalog(input_path)
    converted = convert_authoring_to_experiment_catalog(loaded)
    output_path = repo_root / "outputs" / "test_authoring_adapter_roundtrip.json"
    written = write_experiment_catalog(converted, output_path)
    assert written.exists()
    persisted = json.loads(written.read_text(encoding="utf-8"))
    assert persisted["experiments"][0]["id"] == "glucose_intro_course"


def test_invalid_catalog_raises_clear_error():
    data = _load_example()
    del data["experiments"][0]["title"]
    with pytest.raises(ValueError) as exc_info:
        _ = convert_authoring_to_experiment_catalog(data)
    assert "Authoring catalog is invalid" in str(exc_info.value)


def test_convert_defensive_error_for_unsupported_scenario_type(monkeypatch: pytest.MonkeyPatch):
    data = _load_example()
    data["experiments"][0]["scenarios"][0]["type"] = "unknown_type"
    monkeypatch.setattr("content.authoring_adapter.validate_catalog", lambda _: [])
    with pytest.raises(ValueError) as exc_info:
        _ = convert_authoring_to_experiment_catalog(data)
    msg = str(exc_info.value)
    assert "Unsupported scenario type 'unknown_type'" in msg
    assert "experiments[0].scenarios[0]" in msg


def test_convert_defensive_error_for_missing_required_parameter(monkeypatch: pytest.MonkeyPatch):
    data = _load_example()
    data["experiments"][0]["scenarios"][0]["type"] = "systematic_error"
    del data["experiments"][0]["scenarios"][0]["parameters"]["shift_sd"]
    monkeypatch.setattr("content.authoring_adapter.validate_catalog", lambda _: [])
    with pytest.raises(ValueError) as exc_info:
        _ = convert_authoring_to_experiment_catalog(data)
    assert "Missing required parameter 'shift_sd'" in str(exc_info.value)
