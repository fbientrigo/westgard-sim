from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.authoring_validation import validate_catalog


def _example_catalog() -> dict:
    repo_root = Path(__file__).resolve().parents[1]
    path = repo_root / "content" / "authoring_catalog.example.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_example_catalog_validates_when_jsonschema_available():
    _ = pytest.importorskip("jsonschema")
    errors = validate_catalog(_example_catalog())
    assert errors == []


def test_duplicate_ids_produce_user_friendly_errors_when_jsonschema_available():
    _ = pytest.importorskip("jsonschema")
    data = _example_catalog()
    data["experiments"].append(data["experiments"][0])
    errors = validate_catalog(data)
    assert any("id 'glucose_intro_course' esta repetido" in err for err in errors)
