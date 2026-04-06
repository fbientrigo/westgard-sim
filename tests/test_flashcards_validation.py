from __future__ import annotations

import json
from pathlib import Path

import pytest

from qc_lab_simulator.flashcards.validation import validate_flashcard_deck


def _example_deck() -> dict:
    repo_root = Path(__file__).resolve().parents[1]
    path = repo_root / "content" / "flashcards" / "westgard_qc_basics.deck.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_example_flashcard_deck_validates_when_jsonschema_available() -> None:
    _ = pytest.importorskip("jsonschema")
    errors = validate_flashcard_deck(_example_deck())
    assert errors == []


def test_duplicate_card_ids_produce_friendly_errors_when_jsonschema_available() -> None:
    _ = pytest.importorskip("jsonschema")
    deck = _example_deck()
    deck["cards"].append(dict(deck["cards"][0]))
    errors = validate_flashcard_deck(deck)
    assert any("card id 'qc-purpose' is duplicated" in err for err in errors)


def test_invalid_markup_is_reported_when_jsonschema_available() -> None:
    _ = pytest.importorskip("jsonschema")
    deck = _example_deck()
    deck["cards"][0]["front"] = "What does [[bad:token]] mean?"
    errors = validate_flashcard_deck(deck)
    assert any("Unsupported semantic token 'bad'" in err for err in errors)
