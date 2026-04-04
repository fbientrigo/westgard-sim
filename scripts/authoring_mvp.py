from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping
from uuid import uuid4

import streamlit as st

REPO_ROOT = Path(__file__).parent.parent.resolve()

from content.authoring_adapter import convert_authoring_to_experiment_catalog, write_experiment_catalog
from content.authoring_validation import validate_catalog
from qc_lab_simulator.web_export import export_experiment_catalog_web_data, load_experiment_catalog

DEFAULT_INPUT_PATH = REPO_ROOT / "content" / "authoring_catalog.example.json"
DEFAULT_SAVE_PATH = REPO_ROOT / "content" / "authoring_catalog.example.json"
DEFAULT_TECHNICAL_PATH = REPO_ROOT / "content" / "experiment_catalog.generated.json"
DEFAULT_EXPORT_DIR = REPO_ROOT / "outputs" / "web_data_from_authoring_ui"


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.parent / f".{path.name}.{uuid4().hex}.tmp"
    temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temp_path.replace(path)


def _default_scenario(index: int) -> Dict[str, Any]:
    return {
        "id": f"scenario_{index}",
        "type": "systematic_error",
        "parameters": {"start_run": 10, "shift_sd": 3.0},
        "education": {
            "description": "Describe el patron que deberian observar los estudiantes.",
            "learning_objective": "Indicar el objetivo pedagogico principal.",
            "questions": ["Que patron observas en la grafica?"],
            "explanation": "Explica la respuesta esperada de forma clara.",
        },
    }


def _default_experiment(index: int) -> Dict[str, Any]:
    return {
        "id": f"experiment_{index}",
        "title": f"Experimento {index}",
        "description": "Describe que quieres demostrar con este experimento.",
        "analyte": "Glucose",
        "config": {"mean": 100.0, "sd": 2.0, "n_runs": 30, "seed": 42},
        "scenarios": [_default_scenario(1)],
    }


def _move_item(items: List[Any], index: int, direction: int) -> int:
    target = index + direction
    if target < 0 or target >= len(items):
        return index
    items[index], items[target] = items[target], items[index]
    return target


def _safe_selected_index(total: int, key: str, default: int = 0) -> int:
    if total <= 0:
        st.session_state[key] = 0
        return 0
    current = int(st.session_state.get(key, default))
    current = max(0, min(current, total - 1))
    st.session_state[key] = current
    return current


def _count_catalog(data: Mapping[str, Any]) -> tuple[int, int]:
    experiments = data.get("experiments", [])
    if not isinstance(experiments, list):
        return (0, 0)
    scenario_count = 0
    for exp in experiments:
        if isinstance(exp, Mapping):
            scenarios = exp.get("scenarios", [])
            if isinstance(scenarios, list):
                scenario_count += len(scenarios)
    return (len(experiments), scenario_count)


def _ensure_state() -> None:
    if "authoring_data" not in st.session_state:
        st.session_state.authoring_data = None
    if "validation_errors" not in st.session_state:
        st.session_state.validation_errors = []
    if "generated_catalog" not in st.session_state:
        st.session_state.generated_catalog = None
    if "selected_experiment_index" not in st.session_state:
        st.session_state.selected_experiment_index = 0
    if "selected_scenario_index" not in st.session_state:
        st.session_state.selected_scenario_index = 0
    if "loaded_catalog_path" not in st.session_state:
        st.session_state.loaded_catalog_path = ""
    if "last_saved_path" not in st.session_state:
        st.session_state.last_saved_path = ""
    if "last_technical_path" not in st.session_state:
        st.session_state.last_technical_path = ""
    if "last_export_summary" not in st.session_state:
        st.session_state.last_export_summary = None
    if "last_action_message" not in st.session_state:
        st.session_state.last_action_message = ""


def _safe_path(path_text: str) -> Path:
    path = Path(path_text).expanduser()
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def _normalize_authoring_data(raw: Dict[str, Any]) -> Dict[str, Any]:
    if "experiments" not in raw or not isinstance(raw["experiments"], list):
        raw["experiments"] = []

    normalized_experiments: List[Dict[str, Any]] = []
    for i, experiment in enumerate(raw["experiments"], start=1):
        if not isinstance(experiment, dict):
            continue

        exp = _default_experiment(i)
        exp.update({k: v for k, v in experiment.items() if k != "scenarios" and k != "config"})

        config = exp["config"]
        if isinstance(experiment.get("config"), dict):
            config.update(experiment["config"])
        exp["config"] = config

        scenarios_raw = experiment.get("scenarios", [])
        if not isinstance(scenarios_raw, list):
            scenarios_raw = []
        normalized_scenarios: List[Dict[str, Any]] = []
        for j, scenario in enumerate(scenarios_raw, start=1):
            if not isinstance(scenario, dict):
                continue
            sc = _default_scenario(j)
            sc.update({k: v for k, v in scenario.items() if k not in ("parameters", "education")})
            if isinstance(scenario.get("parameters"), dict):
                sc["parameters"].update(scenario["parameters"])
            if isinstance(scenario.get("education"), dict):
                sc["education"].update(scenario["education"])
            if not isinstance(sc["education"].get("questions"), list):
                sc["education"]["questions"] = []
            normalized_scenarios.append(sc)
        exp["scenarios"] = normalized_scenarios
        normalized_experiments.append(exp)

    raw["experiments"] = normalized_experiments
    return raw


def _load_json_file(path: Path) -> Dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("El archivo debe contener un objeto JSON.")
    return _normalize_authoring_data(raw)


def _validate_current_data() -> List[str]:
    data = st.session_state.authoring_data
    if not isinstance(data, Mapping):
        return ["No hay catalogo cargado."]
    errors = validate_catalog(data)
    st.session_state.validation_errors = errors
    return errors


def _build_technical_catalog(output_path: Path) -> Dict[str, Any]:
    data = st.session_state.authoring_data
    technical = convert_authoring_to_experiment_catalog(data)
    write_experiment_catalog(technical, output_path)
    st.session_state.generated_catalog = technical
    st.session_state.last_technical_path = str(output_path)
    return technical


def _ensure_required_parameters(scenario: Dict[str, Any]) -> None:
    scenario_type = scenario.get("type")
    params = scenario.setdefault("parameters", {})
    if not isinstance(params, dict):
        params = {}
        scenario["parameters"] = params
    if "start_run" not in params:
        params["start_run"] = 10
    if scenario_type == "systematic_error":
        params.pop("drift_per_run", None)
        params.pop("sd_multiplier", None)
        params.setdefault("shift_sd", 3.0)
    elif scenario_type == "trend":
        params.pop("shift_sd", None)
        params.pop("sd_multiplier", None)
        params.setdefault("drift_per_run", 0.25)
    elif scenario_type == "random_error":
        params.pop("shift_sd", None)
        params.pop("drift_per_run", None)
        params.setdefault("sd_multiplier", 2.5)


def _errors_for_experiment(errors: List[str], exp_index: int) -> List[str]:
    token = f"experiments[{exp_index}]"
    return [err for err in errors if token in err]


def _errors_for_scenario(errors: List[str], exp_index: int, sc_index: int) -> List[str]:
    token = f"experiments[{exp_index}].scenarios[{sc_index}]"
    return [err for err in errors if token in err]


def _show_action_feedback() -> None:
    if st.session_state.last_action_message:
        st.info(st.session_state.last_action_message)

    loaded_path = st.session_state.loaded_catalog_path
    saved_path = st.session_state.last_saved_path
    technical_path = st.session_state.last_technical_path

    c1, c2, c3 = st.columns(3)
    c1.metric("Catalogo cargado", "Si" if loaded_path else "No")
    c2.metric("Ultimo guardado", "Si" if saved_path else "No")
    c3.metric("Catalogo tecnico", "Generado" if technical_path else "Pendiente")

    if loaded_path:
        st.caption(f"Archivo cargado: {loaded_path}")
    if saved_path:
        st.caption(f"Ultimo guardado: {saved_path}")


def _experiment_manager(experiments: List[Dict[str, Any]]) -> None:
    st.subheader("Gestion de experimentos")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Nuevo experimento"):
            experiments.append(_default_experiment(len(experiments) + 1))
            st.session_state.selected_experiment_index = len(experiments) - 1
            st.session_state.selected_scenario_index = 0
            st.rerun()
    with c2:
        if st.button("Eliminar experimento"):
            if experiments:
                idx = _safe_selected_index(len(experiments), "selected_experiment_index")
                experiments.pop(idx)
                st.session_state.selected_experiment_index = max(0, idx - 1)
                st.session_state.selected_scenario_index = 0
                st.rerun()
    with c3:
        if st.button("Subir experimento"):
            if experiments:
                idx = _safe_selected_index(len(experiments), "selected_experiment_index")
                st.session_state.selected_experiment_index = _move_item(experiments, idx, -1)
                st.rerun()
    with c4:
        if st.button("Bajar experimento"):
            if experiments:
                idx = _safe_selected_index(len(experiments), "selected_experiment_index")
                st.session_state.selected_experiment_index = _move_item(experiments, idx, 1)
                st.rerun()


def _scenario_manager(scenarios: List[Dict[str, Any]]) -> None:
    st.subheader("Gestion de escenarios")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Nuevo escenario"):
            scenarios.append(_default_scenario(len(scenarios) + 1))
            st.session_state.selected_scenario_index = len(scenarios) - 1
            st.rerun()
    with c2:
        if st.button("Eliminar escenario"):
            if scenarios:
                idx = _safe_selected_index(len(scenarios), "selected_scenario_index")
                scenarios.pop(idx)
                st.session_state.selected_scenario_index = max(0, idx - 1)
                st.rerun()
    with c3:
        if st.button("Subir escenario"):
            if scenarios:
                idx = _safe_selected_index(len(scenarios), "selected_scenario_index")
                st.session_state.selected_scenario_index = _move_item(scenarios, idx, -1)
                st.rerun()
    with c4:
        if st.button("Bajar escenario"):
            if scenarios:
                idx = _safe_selected_index(len(scenarios), "selected_scenario_index")
                st.session_state.selected_scenario_index = _move_item(scenarios, idx, 1)
                st.rerun()


def _editor(data: Dict[str, Any]) -> None:
    experiments = data.get("experiments", [])
    if not isinstance(experiments, list):
        data["experiments"] = []
        experiments = data["experiments"]

    _experiment_manager(experiments)
    if not experiments:
        st.warning(
            "No hay experimentos. Usa 'Nuevo experimento' para comenzar. "
            "Sin experimentos no se puede validar ni exportar."
        )
        return

    exp_index = _safe_selected_index(len(experiments), "selected_experiment_index")
    exp_options = [f"{i + 1}. {exp.get('id', 'sin-id')}" for i, exp in enumerate(experiments)]
    selected_label = st.selectbox("Experimento", exp_options, index=exp_index)
    exp_index = exp_options.index(selected_label)
    st.session_state.selected_experiment_index = exp_index
    experiment = experiments[exp_index]

    st.subheader("Datos del experimento")
    experiment["id"] = st.text_input("ID del experimento", value=experiment.get("id", ""))
    experiment["title"] = st.text_input("Titulo", value=experiment.get("title", ""))
    experiment["description"] = st.text_area(
        "Descripcion (explica para que sirve este experimento)",
        value=experiment.get("description", ""),
        height=90,
    )
    experiment["analyte"] = st.text_input(
        "Analito",
        value=experiment.get("analyte", ""),
        help="Ejemplo: Glucose, Creatinine, Urea.",
    )

    config = experiment.setdefault("config", {})
    c1, c2 = st.columns(2)
    with c1:
        config["mean"] = float(st.number_input("Media (mean)", value=float(config.get("mean", 100.0))))
        config["sd"] = float(
            st.number_input("Desviacion estandar (sd)", value=float(config.get("sd", 2.0)), min_value=0.0001)
        )
    with c2:
        config["n_runs"] = int(
            st.number_input("Cantidad de ejecuciones (n_runs)", value=int(config.get("n_runs", 30)), min_value=5)
        )
        config["seed"] = int(st.number_input("Semilla (seed)", value=int(config.get("seed", 42)), min_value=0))

    scenarios = experiment.get("scenarios", [])
    if not isinstance(scenarios, list):
        experiment["scenarios"] = []
        scenarios = experiment["scenarios"]

    _scenario_manager(scenarios)
    if not scenarios:
        st.warning(
            "No hay escenarios en este experimento. "
            "Usa 'Nuevo escenario'."
        )
        return

    sc_index = _safe_selected_index(len(scenarios), "selected_scenario_index")
    sc_options = [f"{i + 1}. {sc.get('id', 'sin-id')}" for i, sc in enumerate(scenarios)]
    sc_label = st.selectbox("Escenario", sc_options, index=sc_index)
    sc_index = sc_options.index(sc_label)
    st.session_state.selected_scenario_index = sc_index
    scenario = scenarios[sc_index]

    scenario["id"] = st.text_input("ID del escenario", value=scenario.get("id", ""))
    types = ["systematic_error", "trend", "random_error"]
    current_type = scenario.get("type", "systematic_error")
    if current_type not in types:
        current_type = "systematic_error"
    scenario["type"] = st.selectbox(
        "Tipo de escenario",
        types,
        index=types.index(current_type),
        help="systematic_error = sesgo, trend = tendencia, random_error = imprecision.",
    )
    _ensure_required_parameters(scenario)

    params = scenario["parameters"]
    params["start_run"] = int(
        st.number_input(
            "Inicio del problema (start_run)",
            value=int(params.get("start_run", 10)),
            min_value=1,
            max_value=max(int(config.get("n_runs", 30)), 1),
            help="Run donde comienza el comportamiento anormal.",
        )
    )
    if scenario["type"] == "systematic_error":
        params["shift_sd"] = float(
            st.number_input(
                "Magnitud del sesgo (shift_sd)",
                value=float(params.get("shift_sd", 3.0)),
                help="Cuantas SD se mueve la media.",
            )
        )
    elif scenario["type"] == "trend":
        params["drift_per_run"] = float(
            st.number_input(
                "Cambio por ejecucion (drift_per_run)",
                value=float(params.get("drift_per_run", 0.25)),
                help="Pendiente por run en unidades de SD.",
            )
        )
    elif scenario["type"] == "random_error":
        params["sd_multiplier"] = float(
            st.number_input(
                "Multiplicador de dispersion (sd_multiplier)",
                value=float(params.get("sd_multiplier", 2.5)),
                min_value=0.0001,
                help="Cuanto aumenta la variabilidad.",
            )
        )

    st.subheader("Bloque educativo")
    education = scenario.setdefault("education", {})
    if not isinstance(education, dict):
        education = {}
        scenario["education"] = education
    education["description"] = st.text_area(
        "Descripcion pedagogica",
        value=education.get("description", ""),
        height=80,
    )
    education["learning_objective"] = st.text_area(
        "Objetivo de aprendizaje",
        value=education.get("learning_objective", ""),
        height=80,
    )
    questions = education.get("questions", [])
    if not isinstance(questions, list):
        questions = []
    questions_text = "\n".join(str(q) for q in questions)
    edited_questions = st.text_area(
        "Preguntas (una por linea)",
        value=questions_text,
        height=120,
    )
    education["questions"] = [line.strip() for line in edited_questions.splitlines() if line.strip()]
    education["explanation"] = st.text_area(
        "Explicacion para revelar a estudiantes",
        value=education.get("explanation", ""),
        height=100,
    )

    errors = st.session_state.validation_errors
    if errors:
        with st.expander("Errores del experimento seleccionado", expanded=True):
            scoped = _errors_for_experiment(errors, exp_index)
            if scoped:
                for err in scoped:
                    st.error(err)
            else:
                st.success("Sin errores en este experimento.")
        with st.expander("Errores del escenario seleccionado", expanded=False):
            scoped = _errors_for_scenario(errors, exp_index, sc_index)
            if scoped:
                for err in scoped:
                    st.error(err)
            else:
                st.success("Sin errores en este escenario.")


def main() -> None:
    st.set_page_config(page_title="Westgard Authoring MVP", layout="wide")
    st.title("Westgard Authoring MVP (Local)")
    st.caption("Editar catalogo de autora, validar, construir catalogo tecnico y exportar datos estaticos.")
    _ensure_state()

    with st.sidebar:
        st.header("Archivos")
        input_path_text = st.text_input("Catalogo de autora", value=str(DEFAULT_INPUT_PATH))
        save_path_text = st.text_input("Guardar cambios en", value=str(DEFAULT_SAVE_PATH))
        technical_path_text = st.text_input("Catalogo tecnico salida", value=str(DEFAULT_TECHNICAL_PATH))
        export_dir_text = st.text_input("Directorio web estatico", value=str(DEFAULT_EXPORT_DIR))

        if st.button("Abrir catalogo"):
            try:
                source_path = _safe_path(input_path_text)
                loaded = _load_json_file(source_path)
                st.session_state.authoring_data = loaded
                st.session_state.validation_errors = []
                st.session_state.generated_catalog = None
                st.session_state.selected_experiment_index = 0
                st.session_state.selected_scenario_index = 0
                st.session_state.loaded_catalog_path = str(source_path)
                exp_count, sc_count = _count_catalog(loaded)
                st.session_state.last_action_message = (
                    f"Catalogo cargado correctamente ({exp_count} experimentos, {sc_count} escenarios)."
                )
            except FileNotFoundError:
                st.error("No se encontro el archivo indicado.")
            except json.JSONDecodeError as exc:
                st.error(f"JSON invalido: {exc}")
            except Exception as exc:  # noqa: BLE001
                st.error(f"No se pudo abrir el archivo: {exc}")

    _show_action_feedback()

    if st.session_state.authoring_data is None:
        st.info("Carga un archivo de catalogo para comenzar.")
        return

    data = st.session_state.authoring_data
    _editor(data)

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Validar catalogo"):
            errors = _validate_current_data()
            if errors:
                sample = "\n".join(errors[:3])
                st.error(
                    f"Se encontraron {len(errors)} errores. "
                    "Revisa el detalle abajo y corrige primero esos campos.\n\n"
                    f"{sample}"
                )
            else:
                exp_count, sc_count = _count_catalog(data)
                st.success(f"Catalogo valido ({exp_count} experimentos, {sc_count} escenarios).")

    with c2:
        if st.button("Guardar cambios"):
            try:
                save_path = _safe_path(save_path_text)
                _atomic_write_json(save_path, data)
                st.session_state.last_saved_path = str(save_path)
                exp_count, sc_count = _count_catalog(data)
                st.success(
                    f"Cambios guardados en {save_path}. "
                    f"Total actual: {exp_count} experimentos, {sc_count} escenarios."
                )
            except Exception as exc:  # noqa: BLE001
                st.error(f"No se pudo guardar: {exc}")

    with c3:
        if st.button("Build technical catalog"):
            errors = _validate_current_data()
            if errors:
                st.error("No se puede construir el catalogo tecnico: primero corrige los errores de validacion.")
            else:
                try:
                    technical_path = _safe_path(technical_path_text)
                    technical = _build_technical_catalog(technical_path)
                    scenario_count = sum(len(exp["scenarios"]) for exp in technical["experiments"])
                    st.success(
                        f"Catalogo tecnico generado en {technical_path}. "
                        f"Experimentos: {len(technical['experiments'])}, escenarios: {scenario_count}."
                    )
                    st.session_state.generated_catalog = technical
                except Exception as exc:  # noqa: BLE001
                    st.error(f"No se pudo construir catalogo tecnico: {exc}")

    with c4:
        if st.button("Export static web data"):
            errors = _validate_current_data()
            if errors:
                st.error("No se puede exportar: primero corrige los errores de validacion.")
            else:
                try:
                    technical_path = _safe_path(technical_path_text)
                    _ = _build_technical_catalog(technical_path)
                    experiments = load_experiment_catalog(technical_path)
                    export_dir = _safe_path(export_dir_text)
                    result = export_experiment_catalog_web_data(export_dir, experiments)
                    summary = {
                        "experiment_count": int(result["experiment_count"]),
                        "payload_count": int(result["payload_count"]),
                        "index_path": str(result["index_path"]),
                        "output_dir": str(export_dir),
                    }
                    st.session_state.last_export_summary = summary
                    st.success(
                        f"Export completado. Experimentos: {summary['experiment_count']}, "
                        f"escenarios exportados: {summary['payload_count']}."
                    )
                except Exception as exc:  # noqa: BLE001
                    st.error(f"No se pudo exportar datos web: {exc}")

    errors = st.session_state.validation_errors
    if errors:
        st.subheader("Errores de validacion")
        for err in errors:
            st.error(err)

    if st.session_state.last_export_summary:
        summary = st.session_state.last_export_summary
        st.subheader("Resumen de ultimo export")
        st.write(
            f"Experimentos: {summary['experiment_count']}  |  "
            f"Escenarios exportados: {summary['payload_count']}"
        )
        st.caption(f"Directorio de salida: {summary['output_dir']}")
        st.caption(f"Indice generado: {summary['index_path']}")

    st.subheader("Vista previa: catalogo tecnico generado")
    if st.session_state.generated_catalog is None:
        st.info("Todavia no se genero catalogo tecnico.")
    else:
        st.json(st.session_state.generated_catalog)


if __name__ == "__main__":
    main()
