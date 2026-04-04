"""Presentation labels for flashcards."""

from __future__ import annotations

SEMANTIC_LABELS = {
    "es": {
        "rule": "Regla",
        "warning": "Advertencia",
        "rejection": "Rechazo",
        "specimen": "Muestra",
        "instrument": "Instrumento",
        "qc": "Control de calidad",
    }
}

CARD_TYPE_LABELS = {
    "es": {
        "concept": "Concepto",
        "rule_identification": "Identificacion de regla",
        "interpretation": "Interpretacion",
        "lab_context": "Contexto de laboratorio",
    }
}

TAG_LABELS = {
    "es": {
        "westgard": "Westgard",
        "qc": "Control de calidad",
        "laboratorio-clinico": "Laboratorio clinico",
        "educacion": "Educacion",
        "fundamentos": "Fundamentos",
        "estadistica": "Estadistica",
        "reglas-westgard": "Reglas de Westgard",
        "toma-de-decision": "Toma de decision",
        "error-sistematico": "Error sistematico",
        "error-aleatorio": "Error aleatorio",
        "flujo-laboratorio": "Flujo de laboratorio",
        "documentacion": "Documentacion",
    }
}


def _humanize_slug(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").strip().title()


def semantic_label(kind: str, language: str) -> str:
    return SEMANTIC_LABELS.get(language, {}).get(kind, _humanize_slug(kind))


def card_type_label(card_type: str, language: str) -> str:
    return CARD_TYPE_LABELS.get(language, {}).get(card_type, _humanize_slug(card_type))


def tag_label(tag: str, language: str) -> str:
    return TAG_LABELS.get(language, {}).get(tag, _humanize_slug(tag))
