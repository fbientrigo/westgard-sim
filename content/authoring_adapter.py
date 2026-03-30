"""Adapter from authoring contract to technical experiment catalog."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping
from uuid import uuid4

from content.authoring_validation import validate_catalog, validate_catalog_file

SCENARIO_TYPE_TO_KEY: dict[str, str] = {
    "systematic_error": "bias",
    "trend": "drift",
    "random_error": "imprecision",
}

SCENARIO_TYPE_TO_NAME: dict[str, str] = {
    "systematic_error": "Systematic error",
    "trend": "Trend",
    "random_error": "Random error",
}


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.parent / f".{path.name}.{uuid4().hex}.tmp"
    temp_path.write_text(json.dumps(dict(payload), indent=2), encoding="utf-8")
    temp_path.replace(path)


def _required_str(container: Mapping[str, Any], key: str, where: str) -> str:
    value = container.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing or invalid '{key}' at {where}.")
    return value


def _required_mapping(container: Mapping[str, Any], key: str, where: str) -> Mapping[str, Any]:
    value = container.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"Missing or invalid '{key}' at {where}.")
    return value


def _required_list(container: Mapping[str, Any], key: str, where: str) -> List[Mapping[str, Any]]:
    value = container.get(key)
    if not isinstance(value, list):
        raise ValueError(f"Missing or invalid '{key}' at {where}.")
    if not all(isinstance(item, Mapping) for item in value):
        raise ValueError(f"Invalid list items in '{key}' at {where}.")
    return value  # type: ignore[return-value]


def _required_int_parameter(parameters: Mapping[str, Any], key: str, where: str) -> int:
    if key not in parameters:
        raise ValueError(f"Missing required parameter '{key}' at {where}.")
    value = parameters.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"Invalid parameter '{key}' at {where}. Expected an integer.")
    return value


def _required_number_parameter(parameters: Mapping[str, Any], key: str, where: str) -> float:
    if key not in parameters:
        raise ValueError(f"Missing required parameter '{key}' at {where}.")
    value = parameters.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Invalid parameter '{key}' at {where}. Expected a numeric value.")
    return float(value)


def load_authoring_catalog(path: Path) -> Dict[str, Any]:
    """Load and validate an authoring catalog JSON file."""
    path = Path(path)
    errors = validate_catalog_file(path)
    if errors:
        formatted = "\n".join(f"- {err}" for err in errors)
        raise ValueError(f"Authoring catalog is invalid:\n{formatted}")
    return json.loads(path.read_text(encoding="utf-8"))


def _convert_scenario_parameters(
    scenario: Mapping[str, Any],
    n_runs: int,
    *,
    scenario_index: int,
    experiment_id: str,
) -> Dict[str, Any]:
    where = f"experiment '{experiment_id}', scenario #{scenario_index + 1}"
    scenario_id = _required_str(scenario, "id", where)
    scenario_type = _required_str(scenario, "type", where)
    source_params = dict(_required_mapping(scenario, "parameters", where))
    out: Dict[str, Any] = {}

    if "start_run" in source_params:
        out["start_run"] = _required_int_parameter(source_params, "start_run", where)

    if scenario_type == "systematic_error":
        out["shift_sd"] = _required_number_parameter(source_params, "shift_sd", where)
        return out

    if scenario_type == "random_error":
        out["sd_multiplier"] = _required_number_parameter(source_params, "sd_multiplier", where)
        return out

    if scenario_type == "trend":
        start_run = _required_int_parameter(source_params, "start_run", where)
        drift_per_run = _required_number_parameter(source_params, "drift_per_run", where)
        affected_points = n_runs - (start_run - 1)
        if affected_points <= 1:
            total_drift_sd = 0.0
        else:
            total_drift_sd = drift_per_run * (affected_points - 1)
        out["total_drift_sd"] = total_drift_sd
        out["drift_per_run"] = drift_per_run
        return out

    allowed = ", ".join(sorted(SCENARIO_TYPE_TO_KEY.keys()))
    raise ValueError(
        f"Unsupported scenario type '{scenario_type}' in experiment '{experiment_id}', "
        f"scenario '{scenario_id}'. Allowed values: {allowed}."
    )


def convert_authoring_to_experiment_catalog(
    data: Mapping[str, Any],
    *,
    include_education_metadata: bool = False,
) -> Dict[str, Any]:
    """Convert validated authoring data into technical experiment catalog format."""
    errors = validate_catalog(data)
    if errors:
        formatted = "\n".join(f"- {err}" for err in errors)
        raise ValueError(f"Authoring catalog is invalid:\n{formatted}")

    experiments = data["experiments"]
    converted_experiments: List[Dict[str, Any]] = []
    metadata_experiments: List[Dict[str, Any]] = []

    for exp_index, experiment in enumerate(experiments):
        if not isinstance(experiment, Mapping):
            raise ValueError(f"Invalid experiment object at experiments[{exp_index}].")
        where = f"experiments[{exp_index}]"
        experiment_id = _required_str(experiment, "id", where)
        config = dict(_required_mapping(experiment, "config", where))
        n_runs = int(config["n_runs"])

        technical_experiment: Dict[str, Any] = {
            "id": experiment_id,
            "title": _required_str(experiment, "title", where),
            "description": _required_str(experiment, "description", where),
            "config": {
                "mean": float(config["mean"]),
                "sd": float(config["sd"]),
                "n_runs": n_runs,
                "seed": int(config["seed"]),
                "analyte": _required_str(experiment, "analyte", where),
            },
            "scenarios": [],
        }

        metadata_scenarios: List[Dict[str, Any]] = []
        scenarios = _required_list(experiment, "scenarios", where)
        for sc_index, scenario in enumerate(scenarios):
            scenario_type = _required_str(scenario, "type", f"{where}.scenarios[{sc_index}]")
            scenario_id = _required_str(scenario, "id", f"{where}.scenarios[{sc_index}]")
            if scenario_type not in SCENARIO_TYPE_TO_KEY:
                allowed = ", ".join(sorted(SCENARIO_TYPE_TO_KEY.keys()))
                raise ValueError(
                    f"Unsupported scenario type '{scenario_type}' at "
                    f"{where}.scenarios[{sc_index}]. Allowed values: {allowed}."
                )
            scenario_key = SCENARIO_TYPE_TO_KEY[scenario_type]

            converted_params = _convert_scenario_parameters(
                scenario,
                n_runs,
                scenario_index=sc_index,
                experiment_id=experiment_id,
            )
            converted_scenario: Dict[str, Any] = {
                "id": scenario_id,
                "scenario_key": scenario_key,
                "scenario_name": SCENARIO_TYPE_TO_NAME[scenario_type],
                "parameters": converted_params,
            }
            technical_experiment["scenarios"].append(converted_scenario)

            if include_education_metadata:
                metadata_scenarios.append(
                    {
                        "id": scenario_id,
                        "type": scenario_type,
                        "education": scenario.get("education", {}),
                    }
                )

        converted_experiments.append(technical_experiment)
        if include_education_metadata:
            metadata_experiments.append(
                {
                    "id": experiment_id,
                    "scenarios": metadata_scenarios,
                }
            )

    result: Dict[str, Any] = {"experiments": converted_experiments}
    if include_education_metadata:
        result["authoring_metadata"] = {
            "source_contract": "authoring_catalog.schema.json",
            "experiments": metadata_experiments,
        }
    return result


def write_experiment_catalog(data: Mapping[str, Any], output_path: Path) -> Path:
    """Write technical experiment catalog JSON to disk."""
    output_path = Path(output_path)
    _atomic_write_json(output_path, data)
    return output_path
