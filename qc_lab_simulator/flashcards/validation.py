"""Validation helpers for flashcard decks."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from .io import DEFAULT_SCHEMA_PATH
from .markup import validate_markup_text


def _path_to_text(path_parts: Iterable[Any]) -> str:
    parts = list(path_parts)
    if not parts:
        return "deck"
    out: list[str] = []
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
        return f"At {location}: missing required field '{missing}'."
    if validator == "additionalProperties":
        extra = error.message.split("'")[1] if "'" in error.message else error.message
        return f"At {location}: field '{extra}' is not allowed."
    if validator == "minLength":
        return f"At {location}: text cannot be empty."
    if validator == "enum":
        allowed = ", ".join(repr(v) for v in error.validator_value)
        return f"At {location}: invalid value. Allowed values: {allowed}."
    if validator == "pattern":
        return f"At {location}: use lowercase letters, numbers, dots, underscores, or hyphens."
    if validator == "minItems":
        return f"At {location}: include at least one item."
    if validator == "type":
        return f"At {location}: invalid type."
    if validator == "const":
        return f"At {location}: unsupported format version."
    return f"At {location}: {error.message}"


def _custom_rules(data: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    card_ids: set[str] = set()
    sort_orders: set[int] = set()
    cards = data.get("cards", [])
    if not isinstance(cards, list):
        return errors

    for index, card in enumerate(cards):
        if not isinstance(card, Mapping):
            continue
        path = f"cards[{index}]"
        card_id = card.get("id")
        if isinstance(card_id, str):
            if card_id in card_ids:
                errors.append(f"At {path}.id: card id '{card_id}' is duplicated.")
            card_ids.add(card_id)
        sort_order = card.get("sort_order")
        if isinstance(sort_order, int):
            if sort_order in sort_orders:
                errors.append(f"At {path}.sort_order: value '{sort_order}' is duplicated.")
            sort_orders.add(sort_order)

        for field_name in ("front", "back"):
            value = card.get(field_name)
            if isinstance(value, str):
                for markup_error in validate_markup_text(value):
                    errors.append(f"At {path}.{field_name}: {markup_error}")

    return errors


def validate_flashcard_deck(data: Mapping[str, Any]) -> list[str]:
    try:
        from jsonschema import Draft202012Validator
    except ModuleNotFoundError:
        return ["Missing dependency: install 'jsonschema' to validate flashcard decks."]

    schema = json.loads(DEFAULT_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    schema_errors = sorted(validator.iter_errors(data), key=lambda err: list(err.absolute_path))
    errors = [_friendly_schema_error(err) for err in schema_errors]
    errors.extend(_custom_rules(data))
    return errors


def validate_flashcard_deck_file(path: Path) -> list[str]:
    deck_path = Path(path)
    try:
        raw = json.loads(deck_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"Deck file not found: {deck_path}"]
    except json.JSONDecodeError as exc:
        return [f"Invalid JSON in {deck_path}: {exc}"]

    if not isinstance(raw, Mapping):
        return ["Flashcard deck must be a JSON object."]
    return validate_flashcard_deck(raw)
