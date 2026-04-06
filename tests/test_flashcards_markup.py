from __future__ import annotations

from qc_lab_simulator.flashcards.markup import render_markup_to_html, validate_markup_text


def test_render_markup_to_html_supports_core_tokens() -> None:
    rendered = render_markup_to_html("**Bold** *italic* `code` [[rule:1-3s]]")
    assert "<strong>Bold</strong>" in rendered
    assert "<em>italic</em>" in rendered
    assert "<code>code</code>" in rendered
    assert 'class="semantic semantic-rule"' in rendered
    assert "Regla" in rendered
    assert "1-3s" in rendered


def test_render_markup_to_html_escapes_html() -> None:
    rendered = render_markup_to_html("<script>alert(1)</script>")
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered


def test_validate_markup_detects_unbalanced_markers() -> None:
    errors = validate_markup_text("**broken* [[rule:test]")
    assert any("Unbalanced bold marker" in err for err in errors)
    assert any("Unbalanced semantic token" in err for err in errors)
