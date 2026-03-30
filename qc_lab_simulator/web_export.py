"""Web-facing JSON export helpers for scenario payloads."""

from __future__ import annotations

import json
from numbers import Real
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, cast
from uuid import uuid4

from .config import SimConfig
from .metrics import compute_metrics
from .models import ControlSeries
from .scenarios import scenario_bias, scenario_drift, scenario_imprecision, scenario_normal

REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = (
    "scenario_name",
    "scenario_type",
    "description",
    "parameters",
    "control_limits",
    "series",
    "rule_results",
    "summary",
)

SCENARIO_KEYS: tuple[str, ...] = ("normal", "bias", "drift", "imprecision")

DEFAULT_SCENARIO_SPECS: dict[str, dict[str, Any]] = {
    "normal": {
        "scenario_name": "Normal operation",
        "description": "Baseline Gaussian QC process with no injected failure.",
        "parameters": {},
    },
    "bias": {
        "scenario_name": "Bias shift",
        "description": "Sudden mean shift from run 11 onward.",
        "parameters": {"shift_sd": 3.0, "start_run": 11},
    },
    "drift": {
        "scenario_name": "Progressive drift",
        "description": "Gradual linear drift from run 11 to the final run.",
        "parameters": {"total_drift_sd": 4.0, "start_run": 11},
    },
    "imprecision": {
        "scenario_name": "Imprecision increase",
        "description": "Increased random scatter from run 11 onward.",
        "parameters": {"sd_multiplier": 3.0, "start_run": 11},
    },
}


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.parent / f".{path.name}.{uuid4().hex}.tmp"
    temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temp_path.replace(path)


def _control_limits(mean: float, sd: float) -> Dict[str, float]:
    return {
        "mean": float(mean),
        "plus_1s": float(mean + sd),
        "plus_2s": float(mean + 2.0 * sd),
        "plus_3s": float(mean + 3.0 * sd),
        "minus_1s": float(mean - sd),
        "minus_2s": float(mean - 2.0 * sd),
        "minus_3s": float(mean - 3.0 * sd),
    }


def _series_rows(series: ControlSeries) -> List[Dict[str, float | int]]:
    return [
        {
            "run_index": run.run_number,
            "value": run.value,
            "z_score": run.z_score,
        }
        for run in series.runs
    ]


def _rule_results(metrics: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    rules = metrics["rules"]
    return {
        rule_name: {
            "triggered": bool(result["triggered"]),
            "first_trigger_run": result["first_run"],
            "false_alarm": bool(result["false_alarm"]),
        }
        for rule_name, result in rules.items()
    }


def _summary(series: ControlSeries, rule_results: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    triggered_rules = [name for name, result in rule_results.items() if result["triggered"]]
    return {
        "analyte": series.analyte,
        "n_runs": len(series.runs),
        "triggered_rule_count": len(triggered_rules),
        "triggered_rules": triggered_rules,
    }


def _scenario_series(
    scenario_key: str,
    config: SimConfig,
    parameters: Mapping[str, Any],
) -> ControlSeries:
    if scenario_key == "normal":
        return scenario_normal(config)
    if scenario_key == "bias":
        return scenario_bias(
            config,
            shift_sd=float(parameters["shift_sd"]),
            start_run=int(parameters["start_run"]),
        )
    if scenario_key == "drift":
        return scenario_drift(
            config,
            total_drift_sd=float(parameters["total_drift_sd"]),
            start_run=int(parameters["start_run"]),
        )
    if scenario_key == "imprecision":
        return scenario_imprecision(
            config,
            sd_multiplier=float(parameters["sd_multiplier"]),
            start_run=int(parameters["start_run"]),
        )
    raise ValueError(f"Unsupported scenario_key: {scenario_key}")


def _merged_scenario_parameters(
    scenario_key: str,
    parameters: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    if scenario_key not in DEFAULT_SCENARIO_SPECS:
        raise ValueError(f"Unsupported scenario_key: {scenario_key}")
    defaults = cast(dict[str, Any], DEFAULT_SCENARIO_SPECS[scenario_key]["parameters"])
    merged = dict(defaults)
    if parameters is not None:
        merged.update(dict(parameters))
    return merged


def build_web_scenario_payload(
    scenario_key: str,
    config: SimConfig,
    *,
    scenario_name: str | None = None,
    description: str | None = None,
    parameters: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Build one web-facing JSON payload for the selected scenario."""
    if scenario_key not in DEFAULT_SCENARIO_SPECS:
        raise ValueError(f"Unsupported scenario_key: {scenario_key}")

    base_spec = DEFAULT_SCENARIO_SPECS[scenario_key]
    resolved_name = scenario_name or cast(str, base_spec["scenario_name"])
    resolved_description = description or cast(str, base_spec["description"])
    resolved_parameters = _merged_scenario_parameters(scenario_key, parameters)
    series = _scenario_series(scenario_key, config, resolved_parameters)

    metrics = compute_metrics(series)
    rules = _rule_results(metrics)
    payload: Dict[str, Any] = {
        "scenario_name": resolved_name,
        "scenario_type": scenario_key,
        "description": resolved_description,
        "parameters": resolved_parameters,
        "control_limits": _control_limits(config.mean, config.sd),
        "series": _series_rows(series),
        "rule_results": rules,
        "summary": _summary(series, rules),
    }
    return payload


def validate_web_payload(payload: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []

    missing = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in payload]
    if missing:
        errors.append(f"Missing top-level keys: {missing}")
        return errors

    series_value = payload["series"]
    series_list: List[Mapping[str, Any]] | None = None
    if not isinstance(series_value, list):
        errors.append("series must be a list")
    else:
        run_indices: List[int] = []
        for row in series_value:
            if not isinstance(row, Mapping):
                errors.append("series items must be dict-like objects")
                continue
            run_index = row.get("run_index")
            value = row.get("value")
            z_score = row.get("z_score")
            if not isinstance(run_index, int):
                errors.append("series.run_index must be int")
            else:
                run_indices.append(run_index)
            if isinstance(value, bool) or not isinstance(value, Real):
                errors.append("series.value must be numeric")
            if isinstance(z_score, bool) or not isinstance(z_score, Real):
                errors.append("series.z_score must be numeric")
        expected_indices = list(range(1, len(series_value) + 1))
        if run_indices != expected_indices:
            errors.append("series run_index values must exactly be 1..N with no gaps or duplicates")
        series_list = series_value

    limits = payload["control_limits"]
    if not isinstance(limits, Mapping):
        errors.append("control_limits must be a mapping")
    else:
        required_limits = (
            "mean",
            "plus_1s",
            "plus_2s",
            "plus_3s",
            "minus_1s",
            "minus_2s",
            "minus_3s",
        )
        if not all(name in limits for name in required_limits):
            errors.append("control_limits is missing required keys")
        else:
            mean_value = limits["mean"]
            plus_1s_value = limits["plus_1s"]
            plus_2s_value = limits["plus_2s"]
            plus_3s_value = limits["plus_3s"]
            minus_1s_value = limits["minus_1s"]
            minus_2s_value = limits["minus_2s"]
            minus_3s_value = limits["minus_3s"]
            if (
                not isinstance(mean_value, Real)
                or not isinstance(plus_1s_value, Real)
                or not isinstance(plus_2s_value, Real)
                or not isinstance(plus_3s_value, Real)
                or not isinstance(minus_1s_value, Real)
                or not isinstance(minus_2s_value, Real)
                or not isinstance(minus_3s_value, Real)
            ):
                errors.append("control_limits values must be numeric")
            else:
                mean = float(mean_value)
                plus_1s = float(plus_1s_value)
                plus_2s = float(plus_2s_value)
                plus_3s = float(plus_3s_value)
                minus_1s = float(minus_1s_value)
                minus_2s = float(minus_2s_value)
                minus_3s = float(minus_3s_value)

                if not (plus_1s > mean > minus_1s):
                    errors.append("control limit order invalid around mean")
                if not (plus_2s > plus_1s and plus_3s > plus_2s):
                    errors.append("upper control limits must be strictly increasing")
                if not (minus_1s > minus_2s and minus_2s > minus_3s):
                    errors.append("lower control limits must be strictly decreasing")

                tolerance = 1e-12
                if abs((plus_1s - mean) - (mean - minus_1s)) > tolerance:
                    errors.append("+-1s limits are not symmetric")
                if abs((plus_2s - mean) - (mean - minus_2s)) > tolerance:
                    errors.append("+-2s limits are not symmetric")
                if abs((plus_3s - mean) - (mean - minus_3s)) > tolerance:
                    errors.append("+-3s limits are not symmetric")

    rule_results = payload["rule_results"]
    if not isinstance(rule_results, Mapping):
        errors.append("rule_results must be a mapping")
    else:
        n_runs = len(series_list) if series_list is not None else 0
        for rule_name, result in rule_results.items():
            if not isinstance(result, Mapping):
                errors.append(f"rule_results.{rule_name} must be a mapping")
                continue
            triggered = result.get("triggered")
            triggered_is_bool = isinstance(triggered, bool)
            if not triggered_is_bool:
                errors.append(f"rule_results.{rule_name}.triggered must be bool")
            first_trigger_run = result.get("first_trigger_run")
            if triggered_is_bool and triggered is False and first_trigger_run is not None:
                errors.append(
                    f"rule_results.{rule_name}: first_trigger_run must be null when triggered is false"
                )
            if triggered_is_bool and triggered is True:
                in_range = isinstance(first_trigger_run, int) and 1 <= first_trigger_run <= n_runs
                if not in_range:
                    errors.append(
                        f"rule_results.{rule_name}: first_trigger_run must be int within run range"
                    )

    return errors


def save_web_payload(payload: Mapping[str, Any], path: Path) -> None:
    _atomic_write_json(Path(path), payload)


def export_all_web_data(
    output_dir: Path,
    config: SimConfig,
) -> Dict[str, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    exported_paths: Dict[str, Path] = {}
    for scenario_key in SCENARIO_KEYS:
        payload = build_web_scenario_payload(scenario_key, config)
        errors = validate_web_payload(payload)
        if errors:
            raise ValueError(f"Validation failed for scenario '{scenario_key}': {errors}")
        out_path = output_dir / f"{scenario_key}.json"
        save_web_payload(payload, out_path)
        exported_paths[scenario_key] = out_path

    return exported_paths


def load_experiment_catalog(path: Path) -> List[Dict[str, Any]]:
    """Load a JSON catalog for static experiment exports."""
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, Mapping):
        experiments_raw = raw.get("experiments")
    else:
        experiments_raw = raw
    if not isinstance(experiments_raw, list):
        raise ValueError("Catalog must be a list or an object with an 'experiments' list.")

    normalized: List[Dict[str, Any]] = []
    for i, item in enumerate(experiments_raw):
        if not isinstance(item, Mapping):
            raise ValueError(f"Catalog item #{i + 1} must be an object.")
        experiment_id = item.get("id")
        if not isinstance(experiment_id, str) or not experiment_id.strip():
            raise ValueError(f"Catalog item #{i + 1} must contain a non-empty string 'id'.")

        title = item.get("title", experiment_id)
        description = item.get("description", "")
        if not isinstance(title, str):
            raise ValueError(f"Catalog item '{experiment_id}' has invalid 'title'.")
        if not isinstance(description, str):
            raise ValueError(f"Catalog item '{experiment_id}' has invalid 'description'.")

        config_input = item.get("config", {})
        if not isinstance(config_input, Mapping):
            raise ValueError(f"Catalog item '{experiment_id}' has invalid 'config'.")
        sim_config = SimConfig(
            mean=float(config_input.get("mean", 100.0)),
            sd=float(config_input.get("sd", 2.0)),
            n_runs=int(config_input.get("n_runs", 30)),
            seed=int(config_input.get("seed", 42)),
            analyte=str(config_input.get("analyte", "Glucose")),
        )

        scenario_entries = item.get("scenarios", [{"scenario_key": k} for k in SCENARIO_KEYS])
        if not isinstance(scenario_entries, Sequence) or isinstance(scenario_entries, (str, bytes)):
            raise ValueError(f"Catalog item '{experiment_id}' has invalid 'scenarios'.")

        normalized_scenarios: List[Dict[str, Any]] = []
        scenario_ids: set[str] = set()
        for scenario_item in scenario_entries:
            if not isinstance(scenario_item, Mapping):
                raise ValueError(f"Catalog item '{experiment_id}' has a scenario that is not an object.")
            scenario_key = scenario_item.get("scenario_key")
            if not isinstance(scenario_key, str) or scenario_key not in SCENARIO_KEYS:
                raise ValueError(
                    f"Catalog item '{experiment_id}' has invalid scenario_key '{scenario_key}'."
                )
            scenario_id = scenario_item.get("id", scenario_key)
            if not isinstance(scenario_id, str) or not scenario_id.strip():
                raise ValueError(
                    f"Catalog item '{experiment_id}' has invalid scenario 'id' for key '{scenario_key}'."
                )
            if scenario_id in scenario_ids:
                raise ValueError(
                    f"Catalog item '{experiment_id}' repeats scenario id '{scenario_id}'."
                )
            scenario_ids.add(scenario_id)

            scenario_name = scenario_item.get("scenario_name")
            scenario_description = scenario_item.get("description")
            parameters = scenario_item.get("parameters")
            if scenario_name is not None and not isinstance(scenario_name, str):
                raise ValueError(
                    f"Catalog item '{experiment_id}' scenario '{scenario_id}' has invalid scenario_name."
                )
            if scenario_description is not None and not isinstance(scenario_description, str):
                raise ValueError(
                    f"Catalog item '{experiment_id}' scenario '{scenario_id}' has invalid description."
                )
            if parameters is not None and not isinstance(parameters, Mapping):
                raise ValueError(
                    f"Catalog item '{experiment_id}' scenario '{scenario_id}' has invalid parameters."
                )

            normalized_scenarios.append(
                {
                    "id": scenario_id,
                    "scenario_key": scenario_key,
                    "scenario_name": scenario_name,
                    "description": scenario_description,
                    "parameters": dict(parameters) if parameters is not None else None,
                }
            )

        normalized.append(
            {
                "id": experiment_id,
                "title": title,
                "description": description,
                "config": sim_config,
                "scenarios": normalized_scenarios,
            }
        )

    return normalized


def export_experiment_catalog_web_data(
    output_dir: Path,
    experiments: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Export a catalog of experiments as static files for web hosting."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    experiments_dir = output_dir / "experiments"
    experiments_dir.mkdir(parents=True, exist_ok=True)

    index_records: List[Dict[str, Any]] = []
    total_payloads = 0
    for experiment in experiments:
        experiment_id = cast(str, experiment["id"])
        title = cast(str, experiment["title"])
        description = cast(str, experiment["description"])
        config = cast(SimConfig, experiment["config"])
        scenarios = cast(Sequence[Mapping[str, Any]], experiment["scenarios"])

        experiment_dir = experiments_dir / experiment_id
        experiment_dir.mkdir(parents=True, exist_ok=True)

        scenario_records: List[Dict[str, str]] = []
        for scenario in scenarios:
            scenario_id = cast(str, scenario["id"])
            scenario_key = cast(str, scenario["scenario_key"])
            payload = build_web_scenario_payload(
                scenario_key,
                config,
                scenario_name=cast(str | None, scenario["scenario_name"]),
                description=cast(str | None, scenario["description"]),
                parameters=cast(Mapping[str, Any] | None, scenario["parameters"]),
            )
            errors = validate_web_payload(payload)
            if errors:
                raise ValueError(
                    f"Validation failed for experiment '{experiment_id}' scenario '{scenario_id}': {errors}"
                )
            out_path = experiment_dir / f"{scenario_id}.json"
            save_web_payload(payload, out_path)
            total_payloads += 1
            scenario_records.append(
                {
                    "id": scenario_id,
                    "scenario_key": scenario_key,
                    "path": str(out_path.relative_to(output_dir)).replace("\\", "/"),
                }
            )

        experiment_manifest = {
            "id": experiment_id,
            "title": title,
            "description": description,
            "config": {
                "mean": config.mean,
                "sd": config.sd,
                "n_runs": config.n_runs,
                "seed": config.seed,
                "analyte": config.analyte,
            },
            "scenarios": scenario_records,
        }
        manifest_path = experiment_dir / "manifest.json"
        _atomic_write_json(manifest_path, experiment_manifest)

        index_records.append(
            {
                "id": experiment_id,
                "title": title,
                "description": description,
                "manifest_path": str(manifest_path.relative_to(output_dir)).replace("\\", "/"),
                "scenario_count": len(scenario_records),
            }
        )

    index_payload = {"experiments": index_records}
    index_path = output_dir / "index.json"
    _atomic_write_json(index_path, index_payload)
    return {
        "index_path": index_path,
        "experiment_count": len(index_records),
        "payload_count": total_payloads,
    }
