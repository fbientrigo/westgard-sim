# Graph Report - westgard-sim  (2026-06-19)

## Corpus Check
- 129 files · ~41,179 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1198 nodes · 2113 edges · 75 communities (70 shown, 5 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 65 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9c27e1bc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 72|Community 72]]

## God Nodes (most connected - your core abstractions)
1. `SimConfig` - 42 edges
2. `ControlSeries` - 32 edges
3. `build_web_scenario_payload()` - 29 edges
4. `convert_authoring_to_experiment_catalog()` - 24 edges
5. `compilerOptions` - 19 edges
6. `export_flashcard_deck()` - 19 edges
7. `scenario_normal()` - 18 edges
8. `export_experiment_catalog_web_data()` - 18 edges
9. `make_config()` - 18 edges
10. `generate_control_series()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `Namespace` --uses--> `SimConfig`  [INFERRED]
  scripts/export_web_data.py → qc_lab_simulator/config.py
- `SimConfig` --uses--> `SimConfig`  [INFERRED]
  tests/test_scenarios.py → qc_lab_simulator/config.py
- `SimConfig` --uses--> `SimConfig`  [INFERRED]
  tests/test_simulate.py → qc_lab_simulator/config.py
- `SimConfig` --uses--> `SimConfig`  [INFERRED]
  tests/test_web_export.py → qc_lab_simulator/config.py
- `Path` --uses--> `SimConfig`  [INFERRED]
  scripts/export_web_data.py → qc_lab_simulator/config.py

## Import Cycles
- None detected.

## Communities (75 total, 5 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (68): ArgumentParser, _atomic_write_json(), convert_authoring_to_experiment_catalog(), _convert_scenario_parameters(), load_authoring_catalog(), Any, Path, Adapter from authoring contract to technical experiment catalog. (+60 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (60): Flashcard, _card_tags(), _display_tags(), export_flashcard_deck(), _ordered_cards(), Export flashcard decks to CSV and standalone HTML preview., _render_card_html(), _render_csv() (+52 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (32): Summary metrics computed from a :class:`~qc_lab_simulator.models.ControlSeries`., first_violation(), Westgard QC detection rules.  Each rule is a pure function with the signature::, Return the 1-based index of the run that first triggers *rule_fn*.      The rule, Return *True* if any value exceeds mean ± 2 SD (warning rule 1₂s).      Paramete, Return *True* if any value exceeds mean ± 3 SD (rejection rule 1₃s).      Parame, Return *True* if two consecutive values both exceed +2 SD or −2 SD.      Both co, rule_1_2s() (+24 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (39): App(), AppLayout(), AppRouter(), AuthPanel(), AuthContext, AuthContextValue, AuthProvider(), disabledAuthContext (+31 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (43): _atomic_write_json(), build_web_scenario_payload(), _control_limits(), export_all_web_data(), export_experiment_catalog_web_data(), _merged_scenario_parameters(), Any, Path (+35 more)

### Community 5 - "Community 5"
Cohesion: 0.15
Nodes (42): _atomic_write_json(), _build_technical_catalog(), _copy_tree(), _count_catalog(), _count_flashcards(), _default_experiment(), _default_flashcard(), _default_flashcard_deck() (+34 more)

### Community 6 - "Community 6"
Cohesion: 0.11
Nodes (23): ControlSeries, SimConfig, Increased imprecision from *start_run* onward.      The standard deviation is mu, Baseline scenario: all runs follow *Normal(mean, sd)*.      Parameters     -----, Sudden bias shift at *start_run*.      From *start_run* onward the process mean, Gradual linear drift from *start_run* to the last run.      The mean shifts line, scenario_bias(), scenario_drift() (+15 more)

### Community 7 - "Community 7"
Cohesion: 0.05
Nodes (35): `config`, Crear Experimento (authoring catalog), `education`, Errores comunes, Estructura minima, Flujo recomendado para crear/subir experimentos, Nivel catalogo, Nivel escenario (+27 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (25): ExperimentDetail, ExperimentListItem, RuleResultEntry, ScenarioLimits, ScenarioManifestItem, ScenarioPoint, ScenarioStats, buildTriggerDetailsByRun() (+17 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (33): dependencies, react, react-dom, react-router-dom, recharts, @supabase/supabase-js, zod, devDependencies (+25 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (29): Automated Testing, Automated Validation, Can Change Freely, Cannot Change, Constraints and Limitations, Content Layer Architecture, Design Principles, Export Pipeline Integration (+21 more)

### Community 11 - "Community 11"
Cohesion: 0.13
Nodes (20): DataFrame, ndarray, Simulation configuration with sensible defaults., ControlSeries, QCRun, Domain models for the QC simulator., Standardised deviation from the expected mean., A full sequence of QC runs for one scenario.      Attributes     ---------- (+12 more)

### Community 12 - "Community 12"
Cohesion: 0.07
Nodes (26): 1. `scenarios.json`, 2. `lessons.json`, 3. `validate_content.py`, 4. `README.md`, Basic Structure, Common Errors, Content Editing Guide for Non-Programmers, ❌ Do NOT Edit (+18 more)

### Community 13 - "Community 13"
Cohesion: 0.20
Nodes (16): translateExperimentTitle(), AsyncResource, AsyncState, useAsyncResource(), getTriggerRuns(), ExperimentPage(), FlashcardsPage(), HomePage() (+8 more)

### Community 14 - "Community 14"
Cohesion: 0.14
Nodes (19): ANALYTE_ES, EDUCATIONAL_CONTENT_ES, EXPERIMENT_TITLE_ES, SCENARIO_DESCRIPTION_ES, SCENARIO_ID_ES, SCENARIO_NAME_ES, SCENARIO_TYPE_LABEL_ES, translateAnalyte() (+11 more)

### Community 15 - "Community 15"
Cohesion: 0.08
Nodes (23): 1. Open the File, 2. Make Your Changes, 3. Save the File, 4. Validate Your Changes, 5. Check the Output, Adding a Question, Before You Start, Common Edits (+15 more)

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (21): 1. Folder Structure, 2. Data Files, 3. Validation Infrastructure, 4. Integration Utilities, 5. Documentation, 6. Main README Update, ✅ Completed Tasks, Content Layer Implementation Summary (+13 more)

### Community 17 - "Community 17"
Cohesion: 0.09
Nodes (21): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleResolution (+13 more)

### Community 18 - "Community 18"
Cohesion: 0.17
Nodes (19): Parameters that define a single QC simulation run.      Attributes     ---------, SimConfig, Any, ControlSeries, Path, Serialisation helpers – convert simulator objects to JSON-friendly dicts.  The f, Convert a :class:`~qc_lab_simulator.models.ControlSeries` to a dict.      Parame, Write a :class:`~qc_lab_simulator.models.ControlSeries` as JSON.      Parameters (+11 more)

### Community 19 - "Community 19"
Cohesion: 0.20
Nodes (7): Generate a baseline Gaussian control series.      Parameters     ----------, simulate_normal(), make_config(), SimConfig, TestGenerateControlSeries, TestSeriesToDataframe, TestSimulateNormal

### Community 20 - "Community 20"
Cohesion: 0.13
Nodes (14): experimentIndexSchema, experimentManifestSchema, flashcardStudyDeckSchema, lessonEducationMapSchema, lessonEducationSchema, scenarioEducationMapSchema, scenarioEducationSchema, scenarioPayloadSchema (+6 more)

### Community 21 - "Community 21"
Cohesion: 0.25
Nodes (13): parseExperimentIndex(), parseExperimentManifest(), parseFlashcardStudyDeck(), parseScenarioPayload(), ApiError, fetchJson(), getExperimentManifest(), getFlashcardStudyDeck() (+5 more)

### Community 22 - "Community 22"
Cohesion: 0.12
Nodes (17): properties, maximum, minimum, type, maximum, minimum, type, mean (+9 more)

### Community 23 - "Community 23"
Cohesion: 0.12
Nodes (13): args, cleanTarget, datasetSource, datasetTarget, __dirname, educationalTarget, __filename, flashcardsSource (+5 more)

### Community 24 - "Community 24"
Cohesion: 0.22
Nodes (14): export_for_web(), get_combined_content(), get_lesson_content(), get_scenario_content(), load_lessons(), load_scenarios(), Any, Content loader utility for web applications.  This module provides simple functi (+6 more)

### Community 25 - "Community 25"
Cohesion: 0.13
Nodes (14): 1. Activar el entorno, 2. Editar o agregar tarjetas, 3. Exportar el deck, 4. Revisar el resultado, Deck actual de ejemplo, Donde estan los decks, Flujo operativo recomendado, Formato soportado dentro de las tarjetas (+6 more)

### Community 26 - "Community 26"
Cohesion: 0.13
Nodes (15): minLength, type, enum, type, minLength, type, properties, type (+7 more)

### Community 27 - "Community 27"
Cohesion: 0.15
Nodes (13): $ref, $ref, experiment, additionalProperties, properties, required, type, $ref (+5 more)

### Community 28 - "Community 28"
Cohesion: 0.15
Nodes (13): maximum, minimum, type, properties, drift_per_run, sd_multiplier, shift_sd, exclusiveMinimum (+5 more)

### Community 29 - "Community 29"
Cohesion: 0.15
Nodes (12): Content Folder Index, Content Schema, 📋 Data Files (Edit These!), 📖 Documentation, Files Overview, lessons.json, Need Help?, Quick Navigation (+4 more)

### Community 30 - "Community 30"
Cohesion: 0.22
Nodes (12): main(), print_validation_results(), Path, Content validation utility for pedagogical JSON files.  This module validates th, Validate lessons.json structure and content.          Returns     -------     Li, Validate all content JSON files.          Returns     -------     Dict[str, List, Print validation results and return True if all valid.          Parameters     -, Run content validation and exit with appropriate code. (+4 more)

### Community 31 - "Community 31"
Cohesion: 0.15
Nodes (12): 1) Requisitos, 2) Iniciar la interfaz, 3) Abrir un catalogo de autora, 4) Editar experimentos y escenarios, 5) Validar y guardar, 6) Generar catalogo tecnico, 7) Exportar datos estaticos web, 8) Resultado final (+4 more)

### Community 32 - "Community 32"
Cohesion: 0.15
Nodes (13): minLength, type, minLength, type, minLength, type, properties, audience (+5 more)

### Community 33 - "Community 33"
Cohesion: 0.20
Nodes (11): Axes, Figure, _add_limit_line(), plot_control_chart(), ControlSeries, Path, Plotting helpers for QC control charts.  All functions return a ``matplotlib.fig, Draw a Levey-Jennings control chart for *series*.      The chart shows:      * i (+3 more)

### Community 34 - "Community 34"
Cohesion: 0.17
Nodes (12): additionalProperties, required, type, $defs, config, nonEmptyString, parameters, minLength (+4 more)

### Community 35 - "Community 35"
Cohesion: 0.17
Nodes (12): scenario, $ref, $ref, education, parameters, type, additionalProperties, properties (+4 more)

### Community 36 - "Community 36"
Cohesion: 0.17
Nodes (11): Barra lateral, Entrada recomendada, Estructura de la UI, Flujo recomendado para experimentos, Flujo recomendado para flashcards, Guia de Uso: Authoring Studio, Limitaciones actuales, Objetivo (+3 more)

### Community 37 - "Community 37"
Cohesion: 0.17
Nodes (12): minLength, pattern, type, const, type, additionalProperties, required, type (+4 more)

### Community 38 - "Community 38"
Cohesion: 0.17
Nodes (11): card_count, cards, deck_id, format_version, outputs, css, csv, html_preview (+3 more)

### Community 39 - "Community 39"
Cohesion: 0.18
Nodes (10): additionalProperties, minItems, type, $id, properties, experiments, required, $schema (+2 more)

### Community 40 - "Community 40"
Cohesion: 0.18
Nodes (11): education, $ref, additionalProperties, properties, required, type, $ref, $ref (+3 more)

### Community 41 - "Community 41"
Cohesion: 0.22
Nodes (10): compute_metrics(), Any, ControlSeries, Compute rule-violation metrics for *series*.      For every implemented rule thi, ControlSeries, SimConfig, Web-facing JSON export helpers for scenario payloads., _scenario_series() (+2 more)

### Community 42 - "Community 42"
Cohesion: 0.18
Nodes (10): Arquitectura, Comandos, Contenido educativo, Datos y contrato, Deploy a GitHub Pages, Deploy a Vercel, Flashcards interactivas, Requisitos (+2 more)

### Community 43 - "Community 43"
Cohesion: 0.18
Nodes (10): compilerOptions, allowSyntheticDefaultImports, composite, module, moduleResolution, noEmit, skipLibCheck, strict (+2 more)

### Community 44 - "Community 44"
Cohesion: 0.20
Nodes (10): items, $ref, questions, scenarios, items, minItems, type, items (+2 more)

### Community 45 - "Community 45"
Cohesion: 0.22
Nodes (8): 1) Abrir terminal en la raiz del repo, 2) Preflight (30-60s), 3) Abrir UI de autora, 4) Build + Export + Verify (release local), 5) Verificacion independiente (opcional), Rutas por defecto, Salida minima esperada, Westgard Pilot Quickstart (5 minutos)

### Community 46 - "Community 46"
Cohesion: 0.22
Nodes (8): 1) Identificar ultimo backup, 2) Restaurar catalogo tecnico (si aplica), 3) Restaurar export web, Donde quedan los backups, Recovery rapido (3 pasos), Si no hay backup util, Verificar recuperacion, Westgard Pilot Recovery Guide

### Community 47 - "Community 47"
Cohesion: 0.22
Nodes (8): Contenido educativo, Deploy en GitHub Pages, Estrategia de integracion de datos, Flujo operativo completo, Limitaciones abiertas, Objetivo, Student Frontend Guide, Tradeoffs tecnicos

### Community 48 - "Community 48"
Cohesion: 0.54
Nodes (7): _clean_dir(), _copy_dataset(), _copy_optional_file(), main(), parse_args(), Namespace, Path

### Community 49 - "Community 49"
Cohesion: 0.29
Nodes (6): Checklist de Piloto con Bea (usuaria no tecnica), Criterio de exito minimo para piloto, Errores a registrar, Preparacion (5 min), Que observar durante la prueba, Tareas de Bea (sin ayuda tecnica)

### Community 50 - "Community 50"
Cohesion: 0.29
Nodes (6): 1) `Preflight failed. Missing Python dependencies`, 2) `Authoring catalog invalid`, 3) `Export verification failed`, 4) No abre la UI, 5) Quiero usar rutas personalizadas, Westgard Pilot Troubleshooting

### Community 51 - "Community 51"
Cohesion: 0.29
Nodes (6): additionalProperties, $id, required, $schema, title, type

### Community 52 - "Community 52"
Cohesion: 0.29
Nodes (7): minLength, type, tags, default, items, minItems, type

### Community 53 - "Community 53"
Cohesion: 0.33
Nodes (5): Decisions, Incremental Deliverables, Risks and Mitigations, Scope, Student Frontend Plan

### Community 54 - "Community 54"
Cohesion: 0.33
Nodes (6): items, minItems, type, additionalProperties, required, cards

### Community 55 - "Community 55"
Cohesion: 0.40
Nodes (4): Documentacion Authoring MVP, Mapa de documentos, Nota importante, Punto de entrada recomendado

### Community 56 - "Community 56"
Cohesion: 0.40
Nodes (4): Archivos, Decks de Flashcards, Flujo seguro de edición, Formato inline soportado

### Community 57 - "Community 57"
Cohesion: 0.40
Nodes (3): __dirname, __filename, repoRoot

### Community 58 - "Community 58"
Cohesion: 0.50
Nodes (4): start_run, maximum, minimum, type

### Community 59 - "Community 59"
Cohesion: 0.50
Nodes (4): minLength, pattern, type, id

### Community 60 - "Community 60"
Cohesion: 0.50
Nodes (3): Path, Use a repo-local tmp directory to avoid host TEMP permission issues., tmp_path()

### Community 61 - "Community 61"
Cohesion: 0.67
Nodes (3): minLength, type, language

### Community 62 - "Community 62"
Cohesion: 0.67
Nodes (3): subtitle, minLength, type

### Community 63 - "Community 63"
Cohesion: 0.67
Nodes (3): title, minLength, type

## Knowledge Gaps
- **448 isolated node(s):** `name`, `version`, `private`, `type`, `dev` (+443 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `export_flashcard_deck()` connect `Community 1` to `Community 5`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `validate_flashcard_deck()` connect `Community 1` to `Community 5`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `SimConfig` connect `Community 18` to `Community 0`, `Community 4`, `Community 6`, `Community 41`, `Community 11`, `Community 19`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `SimConfig` (e.g. with `DataFrame` and `ndarray`) actually correct?**
  _`SimConfig` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `ControlSeries` (e.g. with `Axes` and `DataFrame`) actually correct?**
  _`ControlSeries` has 19 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `version`, `private` to the rest of the system?**
  _540 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06842105263157895 - nodes in this community are weakly interconnected._