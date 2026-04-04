"""Export flashcard decks to CSV and standalone HTML preview."""

from __future__ import annotations

import csv
import html
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .io import DEFAULT_THEME_PATH, load_flashcard_deck, load_theme_tokens
from .localization import card_type_label, tag_label
from .markup import render_markup_to_html
from .models import Flashcard, FlashcardDeck
from .theme import build_theme_css
from .validation import validate_flashcard_deck_file


def _ordered_cards(deck: FlashcardDeck) -> list[Flashcard]:
    return sorted(deck.cards, key=lambda card: (card.sort_order or 10**9, card.id))


def _card_tags(deck: FlashcardDeck, card: Flashcard) -> str:
    tags = list(deck.metadata.tags) + list(card.tags)
    unique_tags = list(dict.fromkeys(tags))
    return " ".join(unique_tags)


def _display_tags(tags: tuple[str, ...], language: str) -> list[str]:
    return [tag_label(tag, language) for tag in tags]


def _render_csv(path: Path, deck: FlashcardDeck) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["guid", "anverso", "reverso", "etiquetas"])
        for card in _ordered_cards(deck):
            writer.writerow(
                [
                    card.id,
                    render_markup_to_html(card.front, language=deck.metadata.language),
                    render_markup_to_html(card.back, language=deck.metadata.language),
                    _card_tags(deck, card),
                ]
            )


def _render_card_html(card: Flashcard, language: str) -> str:
    card_id = html.escape(card.id)
    card_type = html.escape(card_type_label(card.card_type, language))
    return f"""
<article class="flashcard">
  <div class="flashcard-header">
    <span class="flashcard-id">{card_id}</span>
    <span class="flashcard-type">{card_type}</span>
  </div>
  <section class="flashcard-face">
    <h3>Anverso</h3>
    <p class="flashcard-text">{render_markup_to_html(card.front, language=language)}</p>
  </section>
  <section class="flashcard-face">
    <h3>Reverso</h3>
    <p class="flashcard-text">{render_markup_to_html(card.back, language=language)}</p>
  </section>
</article>
""".strip()


def _render_preview_html(deck: FlashcardDeck, css_name: str) -> str:
    title = html.escape(deck.metadata.title)
    subtitle = html.escape(deck.metadata.subtitle)
    description = html.escape(deck.metadata.description)
    deck_id = html.escape(deck.deck_id)
    audience = html.escape(deck.metadata.audience)
    author = html.escape(deck.metadata.author)
    tags_html = "\n".join(
        f'      <span class="tag">{html.escape(tag)}</span>'
        for tag in _display_tags(deck.metadata.tags, deck.metadata.language)
    )
    cards_html = "\n".join(_render_card_html(card, deck.metadata.language) for card in _ordered_cards(deck))
    return f"""<!DOCTYPE html>
<html lang="{deck.metadata.language}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="{css_name}">
</head>
<body>
  <main class="page">
    <section class="hero">
      <p class="eyebrow">Flashcards Westgard</p>
      <h1>{title}</h1>
      <p class="subtitle">{subtitle}</p>
      <p class="description">{description}</p>
      <div class="meta">
        <span><strong>ID del deck:</strong> {deck_id}</span>
        <span><strong>Audiencia:</strong> {audience}</span>
        <span><strong>Autoría:</strong> {author}</span>
        <span><strong>Tarjetas:</strong> {len(deck.cards)}</span>
      </div>
      <div class="tag-list">
{tags_html}
      </div>
    </section>
    <section class="card-grid">
{cards_html}
    </section>
  </main>
</body>
</html>
"""


def _render_web_deck(path: Path, deck: FlashcardDeck) -> None:
    payload = {
        "deck_id": deck.deck_id,
        "format_version": deck.format_version,
        "metadata": {
            "title": deck.metadata.title,
            "subtitle": deck.metadata.subtitle,
            "language": deck.metadata.language,
            "audience": deck.metadata.audience,
            "description": deck.metadata.description,
            "author": deck.metadata.author,
            "tags": list(deck.metadata.tags),
            "display_tags": _display_tags(deck.metadata.tags, deck.metadata.language),
            "notes": deck.metadata.notes,
        },
        "cards": [
            {
                "id": card.id,
                "card_type": card.card_type,
                "card_type_label": card_type_label(card.card_type, deck.metadata.language),
                "sort_order": card.sort_order,
                "tags": list(card.tags),
                "display_tags": _display_tags(card.tags, deck.metadata.language),
                "front_html": render_markup_to_html(card.front, language=deck.metadata.language),
                "back_html": render_markup_to_html(card.back, language=deck.metadata.language),
                "front_source": card.front,
                "back_source": card.back,
            }
            for card in _ordered_cards(deck)
        ],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def export_flashcard_deck(
    deck_path: Path,
    output_dir: Path,
    *,
    theme_path: Path | None = None,
) -> dict[str, Any]:
    errors = validate_flashcard_deck_file(deck_path)
    if errors:
        lines = "\n".join(f"  - {error}" for error in errors)
        raise ValueError(f"Flashcard deck validation failed:\n{lines}")

    deck = load_flashcard_deck(deck_path)
    tokens = load_theme_tokens(theme_path or DEFAULT_THEME_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / f"{deck.deck_id}.csv"
    css_path = output_dir / "flashcards.css"
    html_path = output_dir / "preview.html"
    manifest_path = output_dir / "manifest.json"
    web_deck_path = output_dir / "study_deck.json"

    _render_csv(csv_path, deck)
    css_path.write_text(build_theme_css(tokens), encoding="utf-8")
    html_path.write_text(_render_preview_html(deck, css_path.name), encoding="utf-8")
    _render_web_deck(web_deck_path, deck)

    manifest = {
        "deck_id": deck.deck_id,
        "format_version": deck.format_version,
        "card_count": len(deck.cards),
        "source_deck": str(Path(deck_path).as_posix()),
        "theme_path": str(Path(theme_path or DEFAULT_THEME_PATH).as_posix()),
        "outputs": {
            "csv": csv_path.name,
            "html_preview": html_path.name,
            "css": css_path.name,
            "study_deck": web_deck_path.name,
        },
        "cards": [asdict(card) for card in _ordered_cards(deck)],
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {
        "deck_id": deck.deck_id,
        "card_count": len(deck.cards),
        "csv_path": csv_path,
        "html_path": html_path,
        "css_path": css_path,
        "manifest_path": manifest_path,
        "web_deck_path": web_deck_path,
    }
