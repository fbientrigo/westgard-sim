"""Minimal safe markup renderer shared by HTML preview and Anki CSV export."""

from __future__ import annotations

import html
import re

from .localization import semantic_label

SEMANTIC_KINDS = {"rule", "warning", "rejection", "specimen", "instrument", "qc"}

_SEMANTIC_PATTERN = re.compile(r"\[\[(?P<kind>[a-z]+):(?P<text>[^\]]+)\]\]")
_CODE_PATTERN = re.compile(r"`([^`\n]+)`")
_BOLD_PATTERN = re.compile(r"\*\*([^*\n]+)\*\*")
_ITALIC_PATTERN = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")


def validate_markup_text(text: str) -> list[str]:
    errors: list[str] = []
    if text.count("**") % 2 != 0:
        errors.append("Unbalanced bold marker '**'.")
    italic_markers = re.findall(r"(?<!\*)\*(?!\*)", text)
    if len(italic_markers) % 2 != 0:
        errors.append("Unbalanced italic marker '*'.")
    if text.count("`") % 2 != 0:
        errors.append("Unbalanced monospace marker '`'.")

    if text.count("[[") != text.count("]]"):
        errors.append("Unbalanced semantic token marker '[[' or ']]'.")

    for match in _SEMANTIC_PATTERN.finditer(text):
        kind = match.group("kind")
        token_text = match.group("text").strip()
        if kind not in SEMANTIC_KINDS:
            errors.append(f"Unsupported semantic token '{kind}'.")
        if not token_text:
            errors.append(f"Semantic token '{kind}' cannot be empty.")
    return errors


def render_markup_to_html(text: str, *, language: str = "es") -> str:
    escaped = html.escape(text)

    def semantic_repl(match: re.Match[str]) -> str:
        kind = match.group("kind")
        token_text = html.escape(match.group("text").strip())
        if kind not in SEMANTIC_KINDS:
            return html.escape(match.group(0))
        label = html.escape(semantic_label(kind, language))
        return (
            f'<span class="semantic semantic-{kind}">'
            f'<span class="semantic-label">{label}</span> {token_text}'
            f"</span>"
        )

    rendered = _SEMANTIC_PATTERN.sub(semantic_repl, escaped)
    rendered = _CODE_PATTERN.sub(r"<code>\1</code>", rendered)
    rendered = _BOLD_PATTERN.sub(r"<strong>\1</strong>", rendered)
    rendered = _ITALIC_PATTERN.sub(r"<em>\1</em>", rendered)
    rendered = rendered.replace("\n", "<br>\n")
    return rendered
