"""Validation helpers for the authoring catalog contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, List, Mapping

REPO_ROOT = Path(__file__).parent.parent
CONTENT_DIR = REPO_ROOT / "content"
AUTHORING_SCHEMA_PATH = CONTENT_DIR / "authoring_catalog.schema.json"


def _path_to_text(path_parts: Iterable[Any]) -> str:
    parts = list(path_parts)
    if not parts:
        return "catalogo"
    out: List[str] = []
    for part in parts:
        if isinstance(part, int):
            out[-1] = f"{out[-1]}[{part}]"
        else:
            out.append(str(part))
    return ".".join(out)


def _friendly_schema_error(error: Any) -> str:
    location = _path_to_text(error.absolute_path)
    validator = getattr(error, "validator", "")
    if validator == "required":
        missing = error.message.split("'")[1] if "'" in error.message else error.message
        return f"En {location}: falta el campo obligatorio '{missing}'."
    if validator == "additionalProperties":
        extra = error.message.split("'")[1] if "'" in error.message else error.message
        return f"En {location}: el campo '{extra}' no esta permitido."
    if validator == "minLength":
        return f"En {location}: el texto no puede estar vacio."
    if validator == "enum":
        allowed = ", ".join(repr(v) for v in error.validator_value)
        return f"En {location}: valor invalido. Valores permitidos: {allowed}."
    if validator in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"):
        return f"En {location}: valor fuera de rango permitido."
    if validator == "minItems":
        return f"En {location}: debes incluir al menos un elemento."
    if validator == "minProperties":
        return f"En {location}: debes activar al menos un parametro."
    if validator == "type":
        expected = error.validator_value
        return f"En {location}: tipo invalido, se esperaba '{expected}'."
    return f"En {location}: {error.message}"


def _custom_rules(data: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    experiments = data.get("experiments", [])
    if not isinstance(experiments, list):
        return errors

    experiment_ids: set[str] = set()
    for exp_index, experiment in enumerate(experiments):
        if not isinstance(experiment, Mapping):
            continue
        experiment_path = f"experiments[{exp_index}]"
        experiment_id = experiment.get("id")
        if isinstance(experiment_id, str):
            if experiment_id in experiment_ids:
                errors.append(
                    f"En {experiment_path}.id: el id '{experiment_id}' esta repetido. Debe ser unico."
                )
            experiment_ids.add(experiment_id)

        config = experiment.get("config", {})
        n_runs = config.get("n_runs") if isinstance(config, Mapping) else None
        scenarios = experiment.get("scenarios", [])
        if not isinstance(scenarios, list):
            continue

        scenario_ids: set[str] = set()
        for sc_index, scenario in enumerate(scenarios):
            if not isinstance(scenario, Mapping):
                continue
            scenario_path = f"{experiment_path}.scenarios[{sc_index}]"
            scenario_id = scenario.get("id")
            scenario_type = scenario.get("type")
            parameters = scenario.get("parameters")

            if isinstance(scenario_id, str):
                if scenario_id in scenario_ids:
                    errors.append(
                        f"En {scenario_path}.id: el id '{scenario_id}' esta repetido dentro del experimento."
                    )
                scenario_ids.add(scenario_id)

            if not isinstance(parameters, Mapping):
                continue

            if len(parameters) == 0:
                errors.append(f"En {scenario_path}.parameters: activa al menos un parametro.")

            start_run = parameters.get("start_run")
            if isinstance(start_run, int) and isinstance(n_runs, int) and start_run > n_runs:
                errors.append(
                    f"En {scenario_path}.parameters.start_run: no puede ser mayor que n_runs ({n_runs})."
                )

            if scenario_type == "systematic_error":
                if "shift_sd" not in parameters:
                    errors.append(
                        f"En {scenario_path}.parameters: para 'systematic_error' falta 'shift_sd'."
                    )
                if "start_run" not in parameters:
                    errors.append(
                        f"En {scenario_path}.parameters: para 'systematic_error' falta 'start_run'."
                    )

            if scenario_type == "trend":
                if "drift_per_run" not in parameters:
                    errors.append(
                        f"En {scenario_path}.parameters: para 'trend' falta 'drift_per_run'."
                    )
                if "start_run" not in parameters:
                    errors.append(
                        f"En {scenario_path}.parameters: para 'trend' falta 'start_run'."
                    )

            if scenario_type == "random_error":
                if "sd_multiplier" not in parameters:
                    errors.append(
                        f"En {scenario_path}.parameters: para 'random_error' falta 'sd_multiplier'."
                    )
                if "start_run" not in parameters:
                    errors.append(
                        f"En {scenario_path}.parameters: para 'random_error' falta 'start_run'."
                    )

    return errors


def validate_catalog(data: Mapping[str, Any]) -> List[str]:
    """Validate authoring catalog data against JSON Schema and business rules.

    Returns a list of user-friendly errors. An empty list means valid.
    """
    try:
        from jsonschema import Draft202012Validator
    except ModuleNotFoundError:
        return [
            "Dependencia faltante: instala 'jsonschema' para validar el catalogo de autora."
        ]

    schema = json.loads(AUTHORING_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    schema_errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    errors = [_friendly_schema_error(err) for err in schema_errors]
    errors.extend(_custom_rules(data))
    return errors


def validate_catalog_file(path: Path) -> List[str]:
    """Validate a catalog JSON file path and return user-oriented errors."""
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"No se encontro el archivo: {path}"]
    except json.JSONDecodeError as exc:
        return [f"JSON invalido en {path}: {exc}"]

    if not isinstance(raw, Mapping):
        return ["El catalogo debe ser un objeto JSON con la clave 'experiments'."]
    return validate_catalog(raw)


def main() -> None:
    """CLI helper for local authoring validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate authoring catalog JSON.")
    _ = parser.add_argument(
        "--file",
        type=Path,
        default=CONTENT_DIR / "authoring_catalog.example.json",
        help="Path to authoring catalog JSON file.",
    )
    args = parser.parse_args()
    errors = validate_catalog_file(args.file)
    if errors:
        print("Catalog validation failed:")
        for err in errors:
            print(f"  - {err}")
        raise SystemExit(1)
    print("Catalog is valid.")


if __name__ == "__main__":
    main()
