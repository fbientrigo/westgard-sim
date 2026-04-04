"""I/O helpers for flashcard decks and theme tokens."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from .models import Flashcard, FlashcardDeck, FlashcardDeckMetadata

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = REPO_ROOT / "content" / "flashcards"
DEFAULT_SCHEMA_PATH = CONTENT_DIR / "flashcard_deck.schema.json"
DEFAULT_THEME_PATH = CONTENT_DIR / "theme_tokens.json"
DEFAULT_DECK_PATH = CONTENT_DIR / "westgard_qc_basics.deck.json"


def load_json_file(path: Path) -> Mapping[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ValueError(f"Expected JSON object at {path}")
    return cast(Mapping[str, Any], raw)


def load_flashcard_deck(path: Path) -> FlashcardDeck:
    data = load_json_file(path)
    metadata_raw = cast(Mapping[str, Any], data["metadata"])
    metadata = FlashcardDeckMetadata(
        title=str(metadata_raw["title"]),
        subtitle=str(metadata_raw["subtitle"]),
        language=str(metadata_raw["language"]),
        audience=str(metadata_raw["audience"]),
        description=str(metadata_raw["description"]),
        author=str(metadata_raw["author"]),
        tags=tuple(str(item) for item in metadata_raw.get("tags", [])),
        source_url=str(metadata_raw["source_url"]) if "source_url" in metadata_raw else None,
        notes=str(metadata_raw["notes"]) if "notes" in metadata_raw else None,
    )
    cards = tuple(
        Flashcard(
            id=str(card["id"]),
            card_type=str(card["card_type"]),
            front=str(card["front"]),
            back=str(card["back"]),
            tags=tuple(str(item) for item in card.get("tags", [])),
            sort_order=int(card["sort_order"]) if "sort_order" in card else None,
            notes=str(card["notes"]) if "notes" in card else None,
        )
        for card in cast(list[Mapping[str, Any]], data["cards"])
    )
    return FlashcardDeck(
        format_version=str(data["format_version"]),
        deck_id=str(data["deck_id"]),
        metadata=metadata,
        cards=cards,
    )


def load_theme_tokens(path: Path | None = None) -> Mapping[str, Any]:
    return load_json_file(path or DEFAULT_THEME_PATH)
