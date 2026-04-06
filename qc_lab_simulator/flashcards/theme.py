"""Shared token loading and CSS generation for flashcard exports."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def build_theme_css(tokens: Mapping[str, Any]) -> str:
    palette = tokens["palette"]
    typography = tokens["typography"]
    variables = {
        "--color-page-background": palette["page_background"],
        "--color-surface": palette["surface"],
        "--color-surface-muted": palette["surface_muted"],
        "--color-text-primary": palette["text_primary"],
        "--color-text-secondary": palette["text_secondary"],
        "--color-border": palette["border"],
        "--color-accent": palette["accent"],
        "--color-accent-soft": palette["accent_soft"],
        "--color-rule": palette["rule"],
        "--color-warning": palette["warning"],
        "--color-rejection": palette["rejection"],
        "--color-specimen": palette["specimen"],
        "--color-instrument": palette["instrument"],
        "--color-qc": palette["qc"],
        "--font-body": typography["font_body"],
        "--font-heading": typography["font_heading"],
        "--font-mono": typography["font_mono"],
        "--font-size-base": f"{typography['base_size_px']}px",
        "--line-height-base": str(typography["line_height"]),
        "--card-radius": f"{typography['card_radius_px']}px",
        "--card-shadow": typography["card_shadow"],
    }
    vars_block = "\n".join(f"  {name}: {value};" for name, value in variables.items())
    return f"""
:root {{
{vars_block}
}}

* {{
  box-sizing: border-box;
}}

body {{
  margin: 0;
  font-family: var(--font-body);
  font-size: var(--font-size-base);
  line-height: var(--line-height-base);
  background:
    radial-gradient(circle at top left, rgba(143, 74, 43, 0.12), transparent 28rem),
    linear-gradient(180deg, var(--color-page-background), #f8f4ee 60%, #f1eadf);
  color: var(--color-text-primary);
}}

.page {{
  max-width: 1080px;
  margin: 0 auto;
  padding: 40px 20px 64px;
}}

.hero {{
  padding: 28px;
  border: 1px solid var(--color-border);
  border-radius: calc(var(--card-radius) + 6px);
  background: linear-gradient(135deg, var(--color-surface), var(--color-surface-muted));
  box-shadow: var(--card-shadow);
}}

.eyebrow {{
  margin: 0 0 10px;
  font-family: var(--font-heading);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-accent);
  font-size: 0.84rem;
}}

h1,
h2,
h3 {{
  font-family: var(--font-heading);
}}

h1 {{
  margin: 0;
  font-size: clamp(2rem, 4vw, 3.4rem);
  line-height: 1.05;
}}

.subtitle,
.description,
.meta {{
  color: var(--color-text-secondary);
}}

.meta {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  margin-top: 16px;
  font-size: 0.95rem;
}}

.tag-list {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}}

.tag {{
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(143, 74, 43, 0.12);
  color: var(--color-accent);
  font-family: var(--font-heading);
  font-size: 0.82rem;
}}

.card-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 18px;
  margin-top: 28px;
}}

.flashcard {{
  display: grid;
  gap: 16px;
  padding: 22px;
  border: 1px solid var(--color-border);
  border-radius: var(--card-radius);
  background: var(--color-surface);
  box-shadow: var(--card-shadow);
}}

.flashcard-header {{
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: baseline;
}}

.flashcard-id,
.flashcard-type {{
  font-size: 0.82rem;
  font-family: var(--font-heading);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}}

.flashcard-face {{
  display: grid;
  gap: 8px;
}}

.flashcard-face h3 {{
  margin: 0;
  font-size: 1rem;
}}

.flashcard-text {{
  margin: 0;
}}

code {{
  font-family: var(--font-mono);
  padding: 0.1em 0.35em;
  border-radius: 0.35em;
  background: rgba(31, 26, 22, 0.08);
}}

.semantic {{
  display: inline-flex;
  align-items: center;
  gap: 0.35em;
  padding: 0.12em 0.55em;
  border-radius: 999px;
  border: 1px solid currentColor;
  font-size: 0.95em;
  white-space: nowrap;
}}

.semantic-label {{
  font-family: var(--font-heading);
  font-size: 0.72em;
  letter-spacing: 0.08em;
}}

.semantic-rule {{
  color: var(--color-rule);
  background: rgba(122, 46, 31, 0.12);
}}

.semantic-warning {{
  color: var(--color-warning);
  background: rgba(156, 106, 17, 0.12);
}}

.semantic-rejection {{
  color: var(--color-rejection);
  background: rgba(138, 28, 28, 0.12);
}}

.semantic-specimen {{
  color: var(--color-specimen);
  background: rgba(54, 101, 109, 0.12);
}}

.semantic-instrument {{
  color: var(--color-instrument);
  background: rgba(77, 79, 143, 0.12);
}}

.semantic-qc {{
  color: var(--color-qc);
  background: rgba(36, 97, 62, 0.12);
}}

@media (max-width: 720px) {{
  .page {{
    padding: 24px 14px 40px;
  }}

  .hero,
  .flashcard {{
    padding: 18px;
  }}
}}
""".strip() + "\n"
