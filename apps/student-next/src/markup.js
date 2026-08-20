// src/markup.js
// Renders exactly the four canonical constructs from
// qc_lab_simulator/flashcards/markup.py: [[kind:text]], **bold**, *italic*,
// `code`. This is a renderer, not a new content model — do not add syntax.

const SEMANTIC_KINDS = new Set(["rule", "warning", "rejection", "specimen", "instrument", "qc"]);
const SEMANTIC_LABEL_ES = {
  rule: "Regla",
  warning: "Advertencia",
  rejection: "Rechazo",
  specimen: "Muestra",
  instrument: "Instrumento",
  qc: "Control de calidad",
};

const SEMANTIC_PATTERN = /\[\[([a-z]+):([^\]]+)\]\]/g;
const CODE_PATTERN = /`([^`\n]+)`/g;
const BOLD_PATTERN = /\*\*([^*\n]+)\*\*/g;
const ITALIC_PATTERN = /(?<!\*)\*([^*\n]+)\*(?!\*)/g;

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function renderCardMarkup(text) {
  let escaped = escapeHtml(text);

  escaped = escaped.replace(SEMANTIC_PATTERN, (match, kind, body) => {
    const trimmed = body.trim();
    if (!SEMANTIC_KINDS.has(kind)) return match;
    const label = SEMANTIC_LABEL_ES[kind] || kind;
    return `<span class="semantic semantic-${kind}"><span class="semantic-label">${label}</span> ${trimmed}</span>`;
  });

  escaped = escaped.replace(CODE_PATTERN, "<code>$1</code>");
  escaped = escaped.replace(BOLD_PATTERN, "<strong>$1</strong>");
  escaped = escaped.replace(ITALIC_PATTERN, "<em>$1</em>");
  escaped = escaped.replaceAll("\n", "<br>\n");

  return escaped;
}
