"""Typed models for the flashcard subsystem."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FlashcardDeckMetadata:
    title: str
    subtitle: str
    language: str
    audience: str
    description: str
    author: str
    tags: tuple[str, ...]
    source_url: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class Flashcard:
    id: str
    card_type: str
    front: str
    back: str
    tags: tuple[str, ...] = field(default_factory=tuple)
    sort_order: int | None = None
    notes: str | None = None


@dataclass(frozen=True)
class FlashcardDeck:
    format_version: str
    deck_id: str
    metadata: FlashcardDeckMetadata
    cards: tuple[Flashcard, ...]
