"""Contract tests for web-facing scenario export payloads."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from qc_lab_simulator.config import SimConfig
from qc_lab_simulator.web_export import (
    REQUIRED_TOP_LEVEL_KEYS,
    SCENARIO_KEYS,
    build_web_scenario_payload,
    export_experiment_catalog_web_data,
    export_all_web_data,
    load_experiment_catalog,
    save_web_payload,
    validate_web_payload,
)


def make_config(**kwargs) -> SimConfig:
    defaults = dict(mean=100.0, sd=2.0, n_runs=30, seed=42, analyte="Glucose")
    defaults.update(kwargs)
    return SimConfig(
        mean=float(defaults["mean"]),
        sd=float(defaults["sd"]),
        n_runs=int(defaults["n_runs"]),
        seed=int(defaults["seed"]),
        analyte=str(defaults["analyte"]),
    )


@pytest.mark.parametrize("scenario_key", SCENARIO_KEYS)
def test_schema_completeness(scenario_key: str):
    payload = build_web_scenario_payload(scenario_key, make_config())
    assert set(payload.keys()) == set(REQUIRED_TOP_LEVEL_KEYS)


@pytest.mark.parametrize("scenario_key", SCENARIO_KEYS)
def test_series_consistency(scenario_key: str):
    payload = build_web_scenario_payload(scenario_key, make_config())
    series = payload["series"]
    run_indices = [row["run_index"] for row in series]
    values = [row["value"] for row in series]
    assert run_indices == sorted(run_indices)
    assert run_indices == list(range(1, len(series) + 1))
    assert all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values)


@pytest.mark.parametrize("scenario_key", SCENARIO_KEYS)
def test_control_limit_consistency(scenario_key: str):
    payload = build_web_scenario_payload(scenario_key, make_config())
    limits = payload["control_limits"]
    mean = limits["mean"]

    assert limits["plus_1s"] > mean > limits["minus_1s"]
    assert limits["plus_2s"] > limits["plus_1s"]
    assert limits["plus_3s"] > limits["plus_2s"]
    assert limits["minus_1s"] > limits["minus_2s"] > limits["minus_3s"]

    assert (limits["plus_1s"] - mean) == pytest.approx(mean - limits["minus_1s"])
    assert (limits["plus_2s"] - mean) == pytest.approx(mean - limits["minus_2s"])
    assert (limits["plus_3s"] - mean) == pytest.approx(mean - limits["minus_3s"])


@pytest.mark.parametrize("scenario_key", SCENARIO_KEYS)
def test_rule_result_consistency(scenario_key: str):
    payload = build_web_scenario_payload(scenario_key, make_config())
    n_runs = len(payload["series"])

    for result in payload["rule_results"].values():
        triggered = result["triggered"]
        first_trigger_run = result["first_trigger_run"]
        if triggered:
            assert isinstance(first_trigger_run, int)
            assert 1 <= first_trigger_run <= n_runs
        else:
            assert first_trigger_run is None


def test_reproducibility_same_seed_same_series():
    cfg = make_config(seed=77)
    first = build_web_scenario_payload("drift", cfg)
    second = build_web_scenario_payload("drift", cfg)
    assert first["series"] == second["series"]


def test_scenario_independence_same_schema():
    cfg = make_config()
    key_sets = {scenario: set(build_web_scenario_payload(scenario, cfg).keys()) for scenario in SCENARIO_KEYS}
    assert len({frozenset(keys) for keys in key_sets.values()}) == 1


def test_validator_accepts_generated_payloads():
    cfg = make_config()
    for scenario in SCENARIO_KEYS:
        payload = build_web_scenario_payload(scenario, cfg)
        assert validate_web_payload(payload) == []


def test_validator_rejects_non_consecutive_run_indices():
    cfg = make_config()
    payload = build_web_scenario_payload("normal", cfg)
    mutated = copy.deepcopy(payload)
    mutated["series"][1]["run_index"] = mutated["series"][2]["run_index"]
    errors = validate_web_payload(mutated)
    assert errors
    assert any("1..N" in err for err in errors)


def test_validator_rejects_out_of_range_trigger_runs():
    cfg = make_config()
    payload = build_web_scenario_payload("normal", cfg)
    n_runs = len(payload["series"])

    invalid_runs = [0, n_runs + 1]
    for invalid in invalid_runs:
        mutated = copy.deepcopy(payload)
        _, rule_result = next(iter(mutated["rule_results"].items()))
        rule_result["triggered"] = True
        rule_result["first_trigger_run"] = invalid
        errors = validate_web_payload(mutated)
        assert errors
        assert any(
            "first_trigger_run must be int within run range" in err for err in errors
        )


def test_validator_rejects_non_bool_triggered():
    cfg = make_config()
    payload = build_web_scenario_payload("normal", cfg)
    mutated = copy.deepcopy(payload)
    rule_name, rule_result = next(iter(mutated["rule_results"].items()))
    rule_result["triggered"] = 1
    errors = validate_web_payload(mutated)
    assert errors
    assert any(
        f"rule_results.{rule_name}.triggered must be bool" in err for err in errors
    )


def test_validator_rejects_non_numeric_z_score():
    cfg = make_config()
    payload = build_web_scenario_payload("normal", cfg)
    mutated = copy.deepcopy(payload)
    mutated["series"][0]["z_score"] = "nan"
    errors = validate_web_payload(mutated)
    assert errors
    assert any("series.z_score must be numeric" in err for err in errors)


def test_export_all_writes_four_json_files(tmp_path: Path):
    cfg = make_config()
    written = export_all_web_data(tmp_path, cfg)
    assert set(written.keys()) == set(SCENARIO_KEYS)

    for scenario, file_path in written.items():
        assert file_path.exists()
        with file_path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        assert payload["scenario_type"] == scenario
        assert validate_web_payload(payload) == []


def test_build_web_payload_supports_parameter_overrides():
    cfg = make_config()
    payload = build_web_scenario_payload(
        "bias",
        cfg,
        scenario_name="Bias custom",
        description="Custom description",
        parameters={"shift_sd": 5.0, "start_run": 5},
    )
    assert payload["scenario_name"] == "Bias custom"
    assert payload["description"] == "Custom description"
    assert payload["parameters"]["shift_sd"] == 5.0
    assert payload["parameters"]["start_run"] == 5
    assert validate_web_payload(payload) == []


def test_load_catalog_and_export_static_index(tmp_path: Path):
    catalog_path = Path(__file__).resolve().parents[1] / "content" / "experiment_catalog.json"
    experiments = load_experiment_catalog(catalog_path)
    result = export_experiment_catalog_web_data(tmp_path, experiments)
    index_path = result["index_path"]
    assert index_path.exists()

    with index_path.open("r", encoding="utf-8") as fh:
        index = json.load(fh)
    assert "experiments" in index
    assert len(index["experiments"]) == len(experiments)

    first_manifest_path = tmp_path / index["experiments"][0]["manifest_path"]
    with first_manifest_path.open("r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    assert manifest["scenarios"]

    first_payload_path = tmp_path / manifest["scenarios"][0]["path"]
    with first_payload_path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    assert set(payload.keys()) == set(REQUIRED_TOP_LEVEL_KEYS)
    assert validate_web_payload(payload) == []


def test_save_web_payload_does_not_leave_temp_files(tmp_path: Path):
    cfg = make_config()
    payload = build_web_scenario_payload("normal", cfg)
    target_path = tmp_path / "normal.json"
    save_web_payload(payload, target_path)

    assert target_path.exists()
    leftover_temps = [p for p in tmp_path.rglob("*.tmp")]
    assert leftover_temps == []
