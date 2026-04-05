from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Mapping
from uuid import uuid4

import streamlit as st

REPO_ROOT = Path(__file__).parent.parent.resolve()

from content.authoring_adapter import convert_authoring_to_experiment_catalog, write_experiment_catalog
from content.authoring_validation import validate_catalog
from qc_lab_simulator.flashcards.export import export_flashcard_deck
from qc_lab_simulator.flashcards.localization import card_type_label
from qc_lab_simulator.flashcards.markup import render_markup_to_html
from qc_lab_simulator.flashcards.validation import validate_flashcard_deck
from qc_lab_simulator.web_export import export_experiment_catalog_web_data, load_experiment_catalog

DEFAULT_INPUT_PATH = REPO_ROOT / "content" / "authoring_catalog.example.json"
DEFAULT_SAVE_PATH = REPO_ROOT / "content" / "authoring_catalog.example.json"
DEFAULT_TECHNICAL_PATH = REPO_ROOT / "content" / "experiment_catalog.generated.json"
DEFAULT_EXPORT_DIR = REPO_ROOT / "outputs" / "web_data_from_authoring_ui"

DEFAULT_DECK_INPUT_PATH = REPO_ROOT / "content" / "flashcards" / "westgard_qc_basics.deck.json"
DEFAULT_DECK_SAVE_PATH = REPO_ROOT / "content" / "flashcards" / "westgard_qc_basics.deck.json"
DEFAULT_FLASHCARDS_EXPORT_DIR = REPO_ROOT / "outputs" / "flashcards" / "westgard_qc_basics"

DEFAULT_STUDENT_WEB_DATA_DIR = REPO_ROOT / "apps" / "student-web" / "public" / "web_data"
DEFAULT_STUDENT_FLASHCARDS_DIR = REPO_ROOT / "apps" / "student-web" / "public" / "flashcards"

CARD_TYPES = ["concept", "rule_identification", "interpretation", "lab_context"]


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.parent / f".{path.name}.{uuid4().hex}.tmp"
    temp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp_path.replace(path)


def _copy_tree(source: Path, target: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"No se encontró la carpeta origen: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True)


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


def _default_flashcard(index: int) -> Dict[str, Any]:
    return {
        "id": f"nueva_tarjeta_{index}",
        "card_type": "concept",
        "sort_order": index,
        "tags": [],
        "front": "Escribe aqui la pregunta o recordatorio clave.",
        "back": "Escribe aqui la respuesta esperada.",
        "notes": "",
    }


def _default_flashcard_deck() -> Dict[str, Any]:
    return {
        "format_version": "1.0",
        "deck_id": "nuevo_deck",
        "metadata": {
            "title": "Nuevo deck de flashcards",
            "subtitle": "Subtitulo breve para la autora",
            "language": "es",
            "audience": "Estudiantes y profesionales en formacion",
            "description": "Describe el objetivo de aprendizaje del deck.",
            "author": "Westgard Sim",
            "tags": ["westgard", "qc"],
            "notes": "",
        },
        "cards": [_default_flashcard(1)],
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


def _safe_path(path_text: str) -> Path:
    path = Path(path_text).expanduser()
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def _parse_tag_text(raw_text: str) -> list[str]:
    tags: list[str] = []
    for chunk in raw_text.replace("\n", ",").split(","):
        cleaned = chunk.strip()
        if cleaned and cleaned not in tags:
            tags.append(cleaned)
    return tags


def _display_path(path: Path | str | None) -> str:
    if path is None:
        return ""
    rendered = Path(path).resolve()
    try:
        return str(rendered.relative_to(REPO_ROOT))
    except ValueError:
        return str(rendered)


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


def _count_flashcards(deck: Mapping[str, Any]) -> tuple[int, int]:
    cards = deck.get("cards", [])
    if not isinstance(cards, list):
        return (0, 0)
    tag_count = 0
    for card in cards:
        if isinstance(card, Mapping) and isinstance(card.get("tags"), list):
            tag_count += len(card["tags"])
    return (len(cards), tag_count)


def _normalize_authoring_data(raw: Dict[str, Any]) -> Dict[str, Any]:
    if "experiments" not in raw or not isinstance(raw["experiments"], list):
        raw["experiments"] = []

    normalized_experiments: List[Dict[str, Any]] = []
    for i, experiment in enumerate(raw["experiments"], start=1):
        if not isinstance(experiment, dict):
            continue

        exp = _default_experiment(i)
        exp.update({k: v for k, v in experiment.items() if k not in ("scenarios", "config")})

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


def _normalize_flashcard_deck(raw: Dict[str, Any]) -> Dict[str, Any]:
    base = _default_flashcard_deck()
    base.update({k: v for k, v in raw.items() if k not in ("metadata", "cards")})

    metadata = dict(base["metadata"])
    if isinstance(raw.get("metadata"), dict):
        metadata.update(raw["metadata"])
    metadata["tags"] = list(metadata.get("tags", [])) if isinstance(metadata.get("tags"), list) else []
    base["metadata"] = metadata

    cards_raw = raw.get("cards", [])
    if not isinstance(cards_raw, list):
        cards_raw = []

    normalized_cards: list[Dict[str, Any]] = []
    for i, card in enumerate(cards_raw, start=1):
        if not isinstance(card, dict):
            continue
        current = _default_flashcard(i)
        current.update({k: v for k, v in card.items() if k != "tags"})
        current["tags"] = list(card.get("tags", [])) if isinstance(card.get("tags"), list) else []
        if not current.get("sort_order"):
            current["sort_order"] = i
        normalized_cards.append(current)

    if not normalized_cards:
        normalized_cards = [_default_flashcard(1)]
    base["cards"] = normalized_cards
    return base


def _load_json_file(path: Path) -> Dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("El archivo debe contener un objeto JSON.")
    return raw


def _load_authoring_catalog(path: Path) -> Dict[str, Any]:
    return _normalize_authoring_data(_load_json_file(path))


def _load_flashcard_deck(path: Path) -> Dict[str, Any]:
    return _normalize_flashcard_deck(_load_json_file(path))


def _validate_current_data() -> List[str]:
    data = st.session_state.authoring_data
    if not isinstance(data, Mapping):
        return ["No hay catalogo cargado."]
    errors = validate_catalog(data)
    st.session_state.validation_errors = errors
    return errors


def _validate_current_flashcards() -> List[str]:
    deck = st.session_state.flashcard_data
    if not isinstance(deck, Mapping):
        return ["No hay deck cargado."]
    errors = validate_flashcard_deck(deck)
    st.session_state.flashcard_validation_errors = errors
    return errors


def _build_technical_catalog(output_path: Path) -> Dict[str, Any]:
    data = st.session_state.authoring_data
    technical = convert_authoring_to_experiment_catalog(data)
    write_experiment_catalog(technical, output_path)
    st.session_state.generated_catalog = technical
    st.session_state.last_technical_path = str(output_path)
    return technical


def _export_flashcards(deck_path: Path, output_dir: Path) -> Dict[str, Any]:
    result = export_flashcard_deck(deck_path, output_dir)
    summary = {
        "deck_id": result["deck_id"],
        "card_count": int(result["card_count"]),
        "csv_path": str(result["csv_path"]),
        "html_path": str(result["html_path"]),
        "manifest_path": str(result["manifest_path"]),
        "web_deck_path": str(result["web_deck_path"]),
        "output_dir": str(output_dir),
    }
    st.session_state.last_flashcard_export_summary = summary
    return summary


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


def _errors_for_card(errors: List[str], card_index: int) -> List[str]:
    token = f"cards[{card_index}]"
    return [err for err in errors if token in err]


def _refresh_flashcard_sort_orders(cards: List[Dict[str, Any]]) -> None:
    for index, card in enumerate(cards, start=1):
        card["sort_order"] = index


def _ensure_state() -> None:
    defaults = {
        "authoring_data": None,
        "validation_errors": [],
        "generated_catalog": None,
        "selected_experiment_index": 0,
        "selected_scenario_index": 0,
        "loaded_catalog_path": "",
        "last_saved_path": "",
        "last_technical_path": "",
        "last_export_summary": None,
        "flashcard_data": None,
        "flashcard_validation_errors": [],
        "selected_card_index": 0,
        "loaded_flashcard_path": "",
        "last_flashcard_saved_path": "",
        "last_flashcard_export_summary": None,
        "last_published_dataset_path": "",
        "last_published_flashcards_path": "",
        "last_action_message": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _status_banner() -> None:
    if st.session_state.last_action_message:
        st.info(st.session_state.last_action_message)

    authoring_data = st.session_state.authoring_data
    flashcard_data = st.session_state.flashcard_data

    exp_count, sc_count = _count_catalog(authoring_data) if isinstance(authoring_data, Mapping) else (0, 0)
    card_count, tag_count = _count_flashcards(flashcard_data) if isinstance(flashcard_data, Mapping) else (0, 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Experimentos", exp_count)
    c2.metric("Escenarios", sc_count)
    c3.metric("Tarjetas", card_count)
    c4.metric("Tags de tarjetas", tag_count)

    if st.session_state.loaded_catalog_path:
        st.caption(f"Catalogo de experimentos: {st.session_state.loaded_catalog_path}")
    if st.session_state.loaded_flashcard_path:
        st.caption(f"Deck de flashcards: {st.session_state.loaded_flashcard_path}")


def _render_workspace_sidebar() -> dict[str, str]:
    with st.sidebar:
        st.header("Archivos de trabajo")
        input_path_text = st.text_input("Catalogo de experimentos", value=str(DEFAULT_INPUT_PATH))
        save_path_text = st.text_input("Guardar experimentos en", value=str(DEFAULT_SAVE_PATH))
        technical_path_text = st.text_input("Catalogo tecnico", value=str(DEFAULT_TECHNICAL_PATH))
        export_dir_text = st.text_input("Salida web de experimentos", value=str(DEFAULT_EXPORT_DIR))

        st.divider()
        deck_input_path_text = st.text_input("Deck de flashcards", value=str(DEFAULT_DECK_INPUT_PATH))
        deck_save_path_text = st.text_input("Guardar deck en", value=str(DEFAULT_DECK_SAVE_PATH))
        flashcards_export_dir_text = st.text_input(
            "Salida export de flashcards",
            value=str(DEFAULT_FLASHCARDS_EXPORT_DIR),
        )

        st.divider()
        student_web_data_dir_text = st.text_input(
            "Publicar dataset en",
            value=str(DEFAULT_STUDENT_WEB_DATA_DIR),
        )
        student_web_flashcards_dir_text = st.text_input(
            "Publicar flashcards en",
            value=str(DEFAULT_STUDENT_FLASHCARDS_DIR),
        )

        if st.button("Abrir catalogo de experimentos", use_container_width=True):
            try:
                source_path = _safe_path(input_path_text)
                loaded = _load_authoring_catalog(source_path)
                st.session_state.authoring_data = loaded
                st.session_state.validation_errors = []
                st.session_state.generated_catalog = None
                st.session_state.selected_experiment_index = 0
                st.session_state.selected_scenario_index = 0
                st.session_state.loaded_catalog_path = str(source_path)
                exp_count, sc_count = _count_catalog(loaded)
                st.session_state.last_action_message = (
                    f"Catalogo de experimentos cargado ({exp_count} experimentos, {sc_count} escenarios)."
                )
            except FileNotFoundError:
                st.error("No se encontro el archivo de experimentos.")
            except json.JSONDecodeError as exc:
                st.error(f"JSON invalido en catalogo de experimentos: {exc}")
            except Exception as exc:  # noqa: BLE001
                st.error(f"No se pudo abrir el catalogo de experimentos: {exc}")

        if st.button("Abrir deck de flashcards", use_container_width=True):
            try:
                source_path = _safe_path(deck_input_path_text)
                loaded = _load_flashcard_deck(source_path)
                st.session_state.flashcard_data = loaded
                st.session_state.flashcard_validation_errors = []
                st.session_state.selected_card_index = 0
                st.session_state.loaded_flashcard_path = str(source_path)
                card_count, _ = _count_flashcards(loaded)
                st.session_state.last_action_message = f"Deck cargado ({card_count} tarjetas)."
            except FileNotFoundError:
                st.error("No se encontro el deck de flashcards.")
            except json.JSONDecodeError as exc:
                st.error(f"JSON invalido en deck de flashcards: {exc}")
            except Exception as exc:  # noqa: BLE001
                st.error(f"No se pudo abrir el deck de flashcards: {exc}")

    return {
        "input_path_text": input_path_text,
        "save_path_text": save_path_text,
        "technical_path_text": technical_path_text,
        "export_dir_text": export_dir_text,
        "deck_input_path_text": deck_input_path_text,
        "deck_save_path_text": deck_save_path_text,
        "flashcards_export_dir_text": flashcards_export_dir_text,
        "student_web_data_dir_text": student_web_data_dir_text,
        "student_web_flashcards_dir_text": student_web_flashcards_dir_text,
    }


def _render_home_tab(paths: Mapping[str, str]) -> None:
    st.subheader("Flujo recomendado para Beatriz")
    st.markdown(
        """
1. Abre el catalogo de experimentos y/o el deck de flashcards desde la barra lateral.
2. Edita el contenido en las pestañas `Experimentos` y `Flashcards`.
3. Revisa validaciones antes de guardar.
4. Usa `Publicar` para generar carpetas listas para compartir o copiar a la web local.
"""
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Salida para compartir experimentos**")
        st.code(_display_path(_safe_path(paths["export_dir_text"])))
        st.markdown("**Salida para compartir flashcards**")
        st.code(_display_path(_safe_path(paths["flashcards_export_dir_text"])))
    with c2:
        st.markdown("**Publicacion en web local de estudiantes**")
        st.code(_display_path(_safe_path(paths["student_web_data_dir_text"])))
        st.code(_display_path(_safe_path(paths["student_web_flashcards_dir_text"])))

    st.caption(
        "La carpeta de salida en outputs sirve para revisar y compartir. "
        "La carpeta apps/student-web/public sirve para dejar la web local actualizada."
    )


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
        if st.button("Eliminar experimento") and experiments:
            idx = _safe_selected_index(len(experiments), "selected_experiment_index")
            experiments.pop(idx)
            st.session_state.selected_experiment_index = max(0, idx - 1)
            st.session_state.selected_scenario_index = 0
            st.rerun()
    with c3:
        if st.button("Subir experimento") and experiments:
            idx = _safe_selected_index(len(experiments), "selected_experiment_index")
            st.session_state.selected_experiment_index = _move_item(experiments, idx, -1)
            st.rerun()
    with c4:
        if st.button("Bajar experimento") and experiments:
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
        if st.button("Eliminar escenario") and scenarios:
            idx = _safe_selected_index(len(scenarios), "selected_scenario_index")
            scenarios.pop(idx)
            st.session_state.selected_scenario_index = max(0, idx - 1)
            st.rerun()
    with c3:
        if st.button("Subir escenario") and scenarios:
            idx = _safe_selected_index(len(scenarios), "selected_scenario_index")
            st.session_state.selected_scenario_index = _move_item(scenarios, idx, -1)
            st.rerun()
    with c4:
        if st.button("Bajar escenario") and scenarios:
            idx = _safe_selected_index(len(scenarios), "selected_scenario_index")
            st.session_state.selected_scenario_index = _move_item(scenarios, idx, 1)
            st.rerun()


def _render_experiments_tab() -> None:
    data = st.session_state.authoring_data
    if data is None:
        st.info("Carga un catalogo de experimentos para empezar a editar.")
        return

    experiments = data.get("experiments", [])
    if not isinstance(experiments, list):
        data["experiments"] = []
        experiments = data["experiments"]

    _experiment_manager(experiments)
    if not experiments:
        st.warning("No hay experimentos. Usa `Nuevo experimento` para comenzar.")
        return

    exp_index = _safe_selected_index(len(experiments), "selected_experiment_index")
    exp_options = [f"{i + 1}. {exp.get('title', exp.get('id', 'sin-id'))}" for i, exp in enumerate(experiments)]
    selected_label = st.selectbox("Selecciona experimento", exp_options, index=exp_index)
    exp_index = exp_options.index(selected_label)
    st.session_state.selected_experiment_index = exp_index
    experiment = experiments[exp_index]

    st.subheader("Ficha del experimento")
    experiment["id"] = st.text_input("ID interno", value=experiment.get("id", ""))
    experiment["title"] = st.text_input("Titulo visible", value=experiment.get("title", ""))
    experiment["description"] = st.text_area(
        "Descripcion para la autora",
        value=experiment.get("description", ""),
        height=90,
        help="Explica que deberia demostrar el experimento cuando se comparta.",
    )
    experiment["analyte"] = st.text_input(
        "Analito",
        value=experiment.get("analyte", ""),
        help="Ejemplo: Glucose, Creatinine, Urea.",
    )

    config = experiment.setdefault("config", {})
    c1, c2 = st.columns(2)
    with c1:
        config["mean"] = float(st.number_input("Media objetivo", value=float(config.get("mean", 100.0))))
        config["sd"] = float(
            st.number_input("Desviacion estandar", value=float(config.get("sd", 2.0)), min_value=0.0001)
        )
    with c2:
        config["n_runs"] = int(
            st.number_input("Cantidad de corridas", value=int(config.get("n_runs", 30)), min_value=5)
        )
        config["seed"] = int(st.number_input("Semilla", value=int(config.get("seed", 42)), min_value=0))

    scenarios = experiment.get("scenarios", [])
    if not isinstance(scenarios, list):
        experiment["scenarios"] = []
        scenarios = experiment["scenarios"]

    _scenario_manager(scenarios)
    if not scenarios:
        st.warning("Este experimento no tiene escenarios todavia.")
        return

    sc_index = _safe_selected_index(len(scenarios), "selected_scenario_index")
    sc_options = [f"{i + 1}. {sc.get('id', 'sin-id')}" for i, sc in enumerate(scenarios)]
    sc_label = st.selectbox("Selecciona escenario", sc_options, index=sc_index)
    sc_index = sc_options.index(sc_label)
    st.session_state.selected_scenario_index = sc_index
    scenario = scenarios[sc_index]

    st.subheader("Escenario seleccionado")
    scenario["id"] = st.text_input("ID del escenario", value=scenario.get("id", ""))
    types = ["systematic_error", "trend", "random_error"]
    current_type = scenario.get("type", "systematic_error")
    if current_type not in types:
        current_type = "systematic_error"
    scenario["type"] = st.selectbox(
        "Tipo de problema",
        types,
        index=types.index(current_type),
        help="systematic_error = sesgo, trend = tendencia, random_error = imprecision.",
    )
    _ensure_required_parameters(scenario)

    params = scenario["parameters"]
    params["start_run"] = int(
        st.number_input(
            "Run donde inicia el problema",
            value=int(params.get("start_run", 10)),
            min_value=1,
            max_value=max(int(config.get("n_runs", 30)), 1),
        )
    )
    if scenario["type"] == "systematic_error":
        params["shift_sd"] = float(st.number_input("Magnitud del sesgo", value=float(params.get("shift_sd", 3.0))))
    elif scenario["type"] == "trend":
        params["drift_per_run"] = float(
            st.number_input("Pendiente por corrida", value=float(params.get("drift_per_run", 0.25)))
        )
    else:
        params["sd_multiplier"] = float(
            st.number_input(
                "Multiplicador de dispersion",
                value=float(params.get("sd_multiplier", 2.5)),
                min_value=0.0001,
            )
        )

    st.subheader("Bloque educativo")
    education = scenario.setdefault("education", {})
    if not isinstance(education, dict):
        education = {}
        scenario["education"] = education
    education["description"] = st.text_area(
        "Que deben observar",
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
    edited_questions = st.text_area(
        "Preguntas al estudiante (una por linea)",
        value="\n".join(str(q) for q in questions),
        height=110,
    )
    education["questions"] = [line.strip() for line in edited_questions.splitlines() if line.strip()]
    education["explanation"] = st.text_area(
        "Explicacion que se revelara",
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


def _flashcard_manager(cards: List[Dict[str, Any]]) -> None:
    st.subheader("Gestion de tarjetas")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Nueva tarjeta"):
            cards.append(_default_flashcard(len(cards) + 1))
            _refresh_flashcard_sort_orders(cards)
            st.session_state.selected_card_index = len(cards) - 1
            st.rerun()
    with c2:
        if st.button("Eliminar tarjeta") and cards:
            idx = _safe_selected_index(len(cards), "selected_card_index")
            cards.pop(idx)
            if not cards:
                cards.append(_default_flashcard(1))
            _refresh_flashcard_sort_orders(cards)
            st.session_state.selected_card_index = max(0, idx - 1)
            st.rerun()
    with c3:
        if st.button("Subir tarjeta") and cards:
            idx = _safe_selected_index(len(cards), "selected_card_index")
            st.session_state.selected_card_index = _move_item(cards, idx, -1)
            _refresh_flashcard_sort_orders(cards)
            st.rerun()
    with c4:
        if st.button("Bajar tarjeta") and cards:
            idx = _safe_selected_index(len(cards), "selected_card_index")
            st.session_state.selected_card_index = _move_item(cards, idx, 1)
            _refresh_flashcard_sort_orders(cards)
            st.rerun()


def _render_flashcards_tab() -> None:
    deck = st.session_state.flashcard_data
    if deck is None:
        st.info("Carga un deck de flashcards para empezar a editar.")
        return

    st.subheader("Deck")
    metadata = deck.setdefault("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
        deck["metadata"] = metadata

    deck["deck_id"] = st.text_input("ID del deck", value=deck.get("deck_id", ""))
    c1, c2 = st.columns(2)
    with c1:
        metadata["title"] = st.text_input("Titulo del deck", value=metadata.get("title", ""))
        metadata["subtitle"] = st.text_input("Subtitulo", value=metadata.get("subtitle", ""))
        metadata["author"] = st.text_input("Autoria", value=metadata.get("author", ""))
        metadata["language"] = st.text_input("Idioma", value=metadata.get("language", "es"))
    with c2:
        metadata["audience"] = st.text_input("Audiencia", value=metadata.get("audience", ""))
        metadata["description"] = st.text_area(
            "Descripcion",
            value=metadata.get("description", ""),
            height=110,
        )
        metadata["notes"] = st.text_area(
            "Notas del deck",
            value=metadata.get("notes", "") or "",
            height=70,
        )

    metadata["tags"] = _parse_tag_text(
        st.text_input(
            "Tags generales del deck (separados por coma)",
            value=", ".join(str(tag) for tag in metadata.get("tags", [])),
        )
    )

    cards = deck.get("cards", [])
    if not isinstance(cards, list):
        deck["cards"] = []
        cards = deck["cards"]
    _refresh_flashcard_sort_orders(cards)
    _flashcard_manager(cards)

    card_index = _safe_selected_index(len(cards), "selected_card_index")
    labels = [f"{i + 1}. {card.get('id', 'sin-id')}" for i, card in enumerate(cards)]
    selected = st.selectbox("Selecciona tarjeta", labels, index=card_index)
    card_index = labels.index(selected)
    st.session_state.selected_card_index = card_index
    card = cards[card_index]

    st.subheader("Tarjeta seleccionada")
    c1, c2 = st.columns(2)
    with c1:
        card["id"] = st.text_input("ID estable de la tarjeta", value=card.get("id", ""))
        card_type = card.get("card_type", "concept")
        if card_type not in CARD_TYPES:
            card_type = "concept"
        card["card_type"] = st.selectbox(
            "Tipo de tarjeta",
            CARD_TYPES,
            index=CARD_TYPES.index(card_type),
            format_func=lambda value: card_type_label(value, metadata.get("language", "es")),
        )
        card["tags"] = _parse_tag_text(
            st.text_input(
                "Tags de la tarjeta (separados por coma)",
                value=", ".join(str(tag) for tag in card.get("tags", [])),
            )
        )
        card["notes"] = st.text_area(
            "Notas internas",
            value=card.get("notes", "") or "",
            height=80,
        )
        st.caption(f"Orden actual: {card.get('sort_order', card_index + 1)}")
    with c2:
        card["front"] = st.text_area(
            "Anverso",
            value=card.get("front", ""),
            height=140,
            help="Puedes usar **negrita**, *cursiva* y tokens como [[rule:1-2s]].",
        )
        card["back"] = st.text_area(
            "Reverso",
            value=card.get("back", ""),
            height=140,
        )

    st.subheader("Vista previa rapida")
    p1, p2 = st.columns(2)
    language = metadata.get("language", "es")
    with p1:
        st.markdown("**Anverso renderizado**")
        st.markdown(render_markup_to_html(card.get("front", ""), language=language), unsafe_allow_html=True)
    with p2:
        st.markdown("**Reverso renderizado**")
        st.markdown(render_markup_to_html(card.get("back", ""), language=language), unsafe_allow_html=True)

    errors = st.session_state.flashcard_validation_errors
    if errors:
        with st.expander("Errores de esta tarjeta", expanded=True):
            scoped = _errors_for_card(errors, card_index)
            if scoped:
                for err in scoped:
                    st.error(err)
            else:
                st.success("Sin errores en esta tarjeta.")


def _publish_experiments(paths: Mapping[str, str]) -> None:
    st.markdown("**Experimentos y escenarios**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Validar experimentos", use_container_width=True):
            errors = _validate_current_data()
            if errors:
                st.error(f"Se encontraron {len(errors)} errores en experimentos.")
            else:
                exp_count, sc_count = _count_catalog(st.session_state.authoring_data)
                st.success(f"Catalogo valido ({exp_count} experimentos, {sc_count} escenarios).")
    with c2:
        if st.button("Guardar experimentos", use_container_width=True):
            try:
                save_path = _safe_path(paths["save_path_text"])
                _atomic_write_json(save_path, st.session_state.authoring_data)
                st.session_state.last_saved_path = str(save_path)
                st.success(f"Catalogo guardado en {_display_path(save_path)}.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"No se pudo guardar el catalogo: {exc}")
    with c3:
        if st.button("Generar y exportar dataset", use_container_width=True):
            errors = _validate_current_data()
            if errors:
                st.error("Corrige los errores de experimentos antes de exportar.")
            else:
                try:
                    technical_path = _safe_path(paths["technical_path_text"])
                    export_dir = _safe_path(paths["export_dir_text"])
                    _build_technical_catalog(technical_path)
                    experiments = load_experiment_catalog(technical_path)
                    result = export_experiment_catalog_web_data(export_dir, experiments)
                    summary = {
                        "experiment_count": int(result["experiment_count"]),
                        "payload_count": int(result["payload_count"]),
                        "index_path": str(result["index_path"]),
                        "output_dir": str(export_dir),
                    }
                    st.session_state.last_export_summary = summary
                    st.success(
                        f"Dataset generado en {_display_path(export_dir)} "
                        f"con {summary['experiment_count']} experimentos."
                    )
                except Exception as exc:  # noqa: BLE001
                    st.error(f"No se pudo exportar el dataset: {exc}")

    if st.button("Publicar experimentos en student-web", use_container_width=True):
        summary = st.session_state.last_export_summary
        if not summary:
            st.error("Primero genera el dataset de experimentos.")
        else:
            try:
                source_dir = _safe_path(summary["output_dir"])
                target_dir = _safe_path(paths["student_web_data_dir_text"])
                _copy_tree(source_dir, target_dir)
                st.session_state.last_published_dataset_path = str(target_dir)
                st.success(f"Dataset copiado a {_display_path(target_dir)}.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"No se pudo publicar el dataset: {exc}")

    summary = st.session_state.last_export_summary
    if summary:
        st.caption(f"Carpeta para compartir: {_display_path(summary['output_dir'])}")
        st.caption(f"Indice generado: {_display_path(summary['index_path'])}")
    if st.session_state.last_published_dataset_path:
        st.caption(f"Publicacion local lista en: {st.session_state.last_published_dataset_path}")


def _publish_flashcards(paths: Mapping[str, str]) -> None:
    st.markdown("**Flashcards**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Validar flashcards", use_container_width=True):
            errors = _validate_current_flashcards()
            if errors:
                st.error(f"Se encontraron {len(errors)} errores en el deck.")
            else:
                deck = st.session_state.flashcard_data
                card_count, _ = _count_flashcards(deck)
                st.success(f"Deck valido ({card_count} tarjetas).")
    with c2:
        if st.button("Guardar deck", use_container_width=True):
            try:
                deck_path = _safe_path(paths["deck_save_path_text"])
                _atomic_write_json(deck_path, st.session_state.flashcard_data)
                st.session_state.last_flashcard_saved_path = str(deck_path)
                st.success(f"Deck guardado en {_display_path(deck_path)}.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"No se pudo guardar el deck: {exc}")
    with c3:
        if st.button("Exportar flashcards", use_container_width=True):
            errors = _validate_current_flashcards()
            if errors:
                st.error("Corrige los errores del deck antes de exportar.")
            else:
                try:
                    deck_path = _safe_path(paths["deck_save_path_text"])
                    _atomic_write_json(deck_path, st.session_state.flashcard_data)
                    st.session_state.last_flashcard_saved_path = str(deck_path)
                    export_dir = _safe_path(paths["flashcards_export_dir_text"])
                    summary = _export_flashcards(deck_path, export_dir)
                    st.success(
                        f"Flashcards exportadas en {_display_path(export_dir)} "
                        f"({summary['card_count']} tarjetas)."
                    )
                except Exception as exc:  # noqa: BLE001
                    st.error(f"No se pudo exportar el deck: {exc}")

    if st.button("Publicar flashcards en student-web", use_container_width=True):
        summary = st.session_state.last_flashcard_export_summary
        if not summary:
            st.error("Primero exporta las flashcards.")
        else:
            try:
                source_dir = _safe_path(summary["output_dir"])
                target_root = _safe_path(paths["student_web_flashcards_dir_text"])
                target_dir = target_root / summary["deck_id"]
                _copy_tree(source_dir, target_dir)
                st.session_state.last_published_flashcards_path = str(target_dir)
                st.success(f"Flashcards copiadas a {_display_path(target_dir)}.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"No se pudo publicar las flashcards: {exc}")

    summary = st.session_state.last_flashcard_export_summary
    if summary:
        st.caption(f"Carpeta para compartir: {_display_path(summary['output_dir'])}")
        st.caption(f"Vista previa HTML: {_display_path(summary['html_path'])}")
        st.caption(f"CSV Anki: {_display_path(summary['csv_path'])}")
    if st.session_state.last_published_flashcards_path:
        st.caption(f"Publicacion local lista en: {st.session_state.last_published_flashcards_path}")


def _render_publish_tab(paths: Mapping[str, str]) -> None:
    st.subheader("Publicar y compartir")
    st.caption(
        "Este panel separa dos destinos: `outputs/` para revisar o compartir carpetas, "
        "y `apps/student-web/public/` para dejar la web local actualizada."
    )
    _publish_experiments(paths)
    st.divider()
    _publish_flashcards(paths)

    st.divider()
    st.markdown("**Checklist rapida**")
    st.markdown(
        """
- `Guardar` antes de exportar si hiciste cambios relevantes.
- `Validar` cuando aparezcan dudas sobre estructura o tags.
- Comparte la carpeta dentro de `outputs/` si otra persona solo necesita los archivos generados.
- Copia a `apps/student-web/public/` si quieres que la web local quede actualizada.
"""
    )


def main() -> None:
    st.set_page_config(page_title="Westgard Authoring Studio", layout="wide")
    st.title("Westgard Authoring Studio")
    st.caption(
        "UI local para Beatriz: editar experimentos, crear flashcards, validar y preparar archivos listos para compartir."
    )
    _ensure_state()
    paths = _render_workspace_sidebar()
    _status_banner()

    home_tab, experiments_tab, flashcards_tab, publish_tab = st.tabs(
        ["Inicio", "Experimentos", "Flashcards", "Publicar"]
    )

    with home_tab:
        _render_home_tab(paths)
    with experiments_tab:
        _render_experiments_tab()
    with flashcards_tab:
        _render_flashcards_tab()
    with publish_tab:
        _render_publish_tab(paths)

    if st.session_state.validation_errors:
        with st.expander("Errores globales de experimentos", expanded=False):
            for err in st.session_state.validation_errors:
                st.error(err)

    if st.session_state.flashcard_validation_errors:
        with st.expander("Errores globales de flashcards", expanded=False):
            for err in st.session_state.flashcard_validation_errors:
                st.error(err)

    st.subheader("Vista previa del catalogo tecnico")
    if st.session_state.generated_catalog is None:
        st.info("Todavia no se ha generado el catalogo tecnico de experimentos.")
    else:
        st.json(st.session_state.generated_catalog)


if __name__ == "__main__":
    main()
