#!/usr/bin/env python3
"""Build-time exporter for the ``apps/student-next`` static data bundle.

Stdlib only. Must not import numpy, ``simulate.py``, ``scenarios.py`` or
``web_export.py`` so CI needs no ``pip install`` to run this script.

Writes exactly three files to ``--output-dir``:

- ``cards.json``  — byte-identical copy of the canonical flashcard deck.
- ``rules.json``  — authored rule reference + engine-derived capability flag.
- ``practice.json`` — authored scenarios + fully derived evidence/expected
  answers/counterfactual table/point zones.

Usage::

    python scripts/export_student_next_data.py --output-dir apps/student-next/data
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from qc_lab_simulator import evidence as evidence_mod  # noqa: E402
from qc_lab_simulator import rules as rules_mod  # noqa: E402
from qc_lab_simulator.metrics import _RULES as SUPPORTED_RULES  # noqa: E402

GENERATED_BY = "scripts/export_student_next_data.py"
FORMAT_VERSION = "1.0"

CARDS_SOURCE = REPO_ROOT / "content" / "flashcards" / "westgard_qc_basics.deck.json"
RULES_REFERENCE_SOURCE = REPO_ROOT / "content" / "rules_reference.json"
PRACTICE_SCENARIOS_SOURCE = REPO_ROOT / "content" / "practice_scenarios.json"

GRID_MIN = -4.0
GRID_MAX = 4.0
GRID_STEP = 0.2

# Consequence text templates. This mapping lives only here; the frontend
# performs lookup of the precomputed `consequence` string, never arithmetic.
_RULE_DISPLAY = {"1_2s": "1₂s", "1_3s": "1₃s", "2_2s": "2₂s"}
_ACTION_LABEL = {"accept": "Aceptar", "review": "Revisar", "reject": "Rechazar"}


class ExportError(Exception):
    """Raised with a message naming the offending id; causes exit(1)."""


def _fail(message: str) -> None:
    raise ExportError(message)


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _z_grid() -> List[float]:
    """41 entries, indices 0..40, from -4.0 to +4.0 step 0.2."""
    grid = []
    steps = round((GRID_MAX - GRID_MIN) / GRID_STEP)
    for i in range(steps + 1):
        z = round(GRID_MIN + i * GRID_STEP, 1)
        grid.append(z)
    return grid


def _zone_for_point(value: float, mean: float, sd: float) -> str:
    """Categorical zone derived from the canonical rule functions only.

    No numeric threshold comparison happens outside rules.py.
    """
    if rules_mod.rule_1_3s([value], mean, sd):
        return "beyond_3sd"
    if rules_mod.rule_1_2s([value], mean, sd):
        return "beyond_2sd"
    return "within_2sd"


def build_cards_payload() -> Dict[str, Any]:
    if not CARDS_SOURCE.exists():
        _fail(f"missing canonical deck at {CARDS_SOURCE}")
    return _load_json(CARDS_SOURCE)


def _cards_source_bytes() -> bytes:
    return CARDS_SOURCE.read_bytes()


def build_rules_payload() -> Dict[str, Any]:
    authored = _load_json(RULES_REFERENCE_SOURCE)
    rules_authored = authored.get("rules", [])

    seen_ids = set()
    output_rules = []
    for entry in rules_authored:
        rule_id = entry.get("id")
        if rule_id in seen_ids:
            _fail(f"duplicate rule id in rules_reference.json: {rule_id}")
        seen_ids.add(rule_id)

        if "evaluation" in entry:
            _fail(
                f"content/rules_reference.json must not author 'evaluation' "
                f"(found on rule id={rule_id!r}); it is derived from the engine registry"
            )

        evaluation = "interactive" if rule_id in SUPPORTED_RULES else "reference"
        if evaluation == "interactive" and rule_id not in SUPPORTED_RULES:
            _fail(f"rule {rule_id!r} marked interactive but absent from engine registry")
        if rule_id not in SUPPORTED_RULES and rule_id not in evidence_mod.REFERENCE_RULES:
            _fail(
                f"rule {rule_id!r} is neither in the engine registry nor in "
                f"REFERENCE_RULES; cannot classify"
            )

        output_entry = dict(entry)
        output_entry["evaluation"] = evaluation
        output_rules.append(output_entry)

    return {
        "format_version": FORMAT_VERSION,
        "generated_by": GENERATED_BY,
        "engine": {
            "supported_rules": sorted(SUPPORTED_RULES.keys()),
            "reference_rules": list(evidence_mod.REFERENCE_RULES),
            "control_levels": 1,
            "boundary_semantics": "strict_greater_than",
        },
        "rules": output_rules,
    }


def _validate_card_ids_exist(rules_payload: Dict[str, Any], card_ids: set) -> None:
    for rule in rules_payload["rules"]:
        for card_id in rule.get("card_ids", []):
            if card_id not in card_ids:
                _fail(
                    f"rule {rule['id']!r} references unknown card_id {card_id!r}"
                )


def _validate_z_value(z: float, scenario_id: str, run: int) -> None:
    if z < -4.0 or z > 4.0:
        _fail(f"scenario {scenario_id!r} run {run}: z-value {z} outside [-4.0, 4.0]")
    # multiple of 0.1, tolerant of float error
    scaled = round(z * 10)
    if abs(scaled - z * 10) > 1e-6:
        _fail(f"scenario {scenario_id!r} run {run}: z-value {z} is not a multiple of 0.1")


def _consequence_text(baseline: Dict[str, Any], candidate: Dict[str, Any]) -> str:
    baseline_triggered = {r["rule"] for r in baseline["rules"] if r["triggered"]}
    candidate_triggered = {r["rule"] for r in candidate["rules"] if r["triggered"]}

    stopped = sorted(baseline_triggered - candidate_triggered, key=list(_RULE_DISPLAY).index)
    started = sorted(candidate_triggered - baseline_triggered, key=list(_RULE_DISPLAY).index)

    stopped_names = [_RULE_DISPLAY[r] for r in stopped]
    started_names = [_RULE_DISPLAY[r] for r in started]

    parts: List[str] = []
    if stopped_names and started_names:
        parts.append(
            f"Con este valor, {', '.join(stopped_names)} ya no se cumple y "
            f"{', '.join(started_names)} empieza a cumplirse."
        )
    elif stopped_names:
        parts.append(f"Con este valor, {', '.join(stopped_names)} ya no se cumple.")
    elif started_names:
        parts.append(f"Con este valor, {', '.join(started_names)} empieza a cumplirse.")
    else:
        parts.append("Sin cambios: las mismas reglas se cumplen.")

    if baseline["verdict"] != candidate["verdict"]:
        parts.append(
            f"La decisión pasa de {_ACTION_LABEL[baseline['verdict']]} a "
            f"{_ACTION_LABEL[candidate['verdict']]}."
        )

    return " ".join(parts)


def build_practice_payload() -> Dict[str, Any]:
    authored = _load_json(PRACTICE_SCENARIOS_SOURCE)
    mean = authored["mean"]
    sd = authored["sd"]
    scenarios_authored = authored.get("scenarios", [])

    seen_ids = set()
    grid = _z_grid()
    output_scenarios = []

    for scenario in scenarios_authored:
        scenario_id = scenario["id"]
        if scenario_id in seen_ids:
            _fail(f"duplicate scenario id: {scenario_id}")
        seen_ids.add(scenario_id)

        z_values = scenario["z_values"]
        if len(z_values) != 10:
            _fail(f"scenario {scenario_id!r} has {len(z_values)} z-values, expected 10")

        editable_run = scenario["editable_run"]
        if not (1 <= editable_run <= 10):
            _fail(f"scenario {scenario_id!r}: editable_run {editable_run} out of range [1,10]")

        for i, z in enumerate(z_values):
            _validate_z_value(z, scenario_id, i + 1)

        values = [mean + z * sd for z in z_values]
        evaluation = evidence_mod.evaluate_series(values, mean, sd)

        points = []
        for i, (z, value) in enumerate(zip(z_values, values)):
            zone = _zone_for_point(value, mean, sd)
            points.append({"run": i + 1, "value": value, "z": z, "zone": zone})

        governing_rule = evaluation["governing_rule"]
        if governing_rule is None:
            expected_evidence_runs: List[int] = []
        else:
            governing_entry = next(
                r for r in evaluation["rules"] if r["rule"] == governing_rule
            )
            expected_evidence_runs = governing_entry["evidence_runs"]

        expected = {
            "action": evaluation["verdict"],
            "rule": governing_rule,
            "evidence_runs": expected_evidence_runs,
        }

        # Error type interpretation, restricted to the two permitted cases.
        rules_by_id = {r["rule"]: r for r in evaluation["rules"]}
        error_type = None
        if rules_by_id["2_2s"]["triggered"]:
            error_type = "Compatible con error sistemático (desplazamiento en un solo sentido)."
        elif (
            rules_by_id["1_3s"]["triggered"]
            and len(rules_by_id["1_3s"]["evidence_runs"]) == 1
            and not rules_by_id["2_2s"]["triggered"]
        ):
            error_type = "Compatible con error aleatorio o un error grosero puntual."

        capability_note = None
        triggered_ids = {r["rule"] for r in evaluation["rules"] if r["triggered"]}
        if triggered_ids == {"1_2s"}:
            capability_note = (
                "Este simulador solo evalúa 1₂s, 1₃s y 2₂s. En el laboratorio, una "
                "advertencia 1₂s obliga a revisar también R₄s, 4₁s y 10x antes de decidir."
            )

        # Counterfactual table over the full grid for the editable run.
        cf_results = []
        for z_candidate in grid:
            candidate_values = list(values)
            candidate_values[editable_run - 1] = mean + z_candidate * sd
            candidate_eval = evidence_mod.evaluate_series(candidate_values, mean, sd)
            consequence = _consequence_text(evaluation, candidate_eval)
            cf_results.append(
                {
                    "z": z_candidate,
                    "evaluation": candidate_eval,
                    "consequence": consequence,
                }
            )

        output_scenarios.append(
            {
                "id": scenario_id,
                "label": scenario["label"],
                "family": scenario["family"],
                "mean": mean,
                "sd": sd,
                "points": points,
                "editable_run": editable_run,
                "evaluation": evaluation,
                "expected": expected,
                "counterfactuals": {
                    "run": editable_run,
                    "z_values": grid,
                    "results": cf_results,
                },
                "teaching": {
                    "pattern": scenario["teaching"]["pattern"],
                    "why": scenario["teaching"]["why"],
                    "action_text": scenario["teaching"]["action_text"],
                    "error_type": error_type,
                    "capability_note": capability_note,
                },
            }
        )

    return {
        "format_version": FORMAT_VERSION,
        "generated_by": GENERATED_BY,
        "engine": {
            "supported_rules": sorted(SUPPORTED_RULES.keys()),
            "reference_rules": list(evidence_mod.REFERENCE_RULES),
            "control_levels": 1,
            "boundary_semantics": "strict_greater_than",
        },
        "scenarios": output_scenarios,
    }


def export(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    cards_payload = build_cards_payload()
    rules_payload = build_rules_payload()
    practice_payload = build_practice_payload()

    card_ids = {c["id"] for c in cards_payload.get("cards", [])}
    _validate_card_ids_exist(rules_payload, card_ids)

    (output_dir / "cards.json").write_bytes(_cards_source_bytes())
    (output_dir / "rules.json").write_text(
        json.dumps(rules_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "practice.json").write_text(
        json.dumps(practice_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write cards.json, rules.json, practice.json into.",
    )
    args = parser.parse_args(argv)

    try:
        export(Path(args.output_dir))
    except ExportError as exc:
        print(f"export failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
