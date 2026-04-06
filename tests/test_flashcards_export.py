from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from qc_lab_simulator.flashcards.export import export_flashcard_deck


def test_export_flashcard_deck_writes_expected_outputs(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    deck_path = repo_root / "content" / "flashcards" / "westgard_qc_basics.deck.json"

    result = export_flashcard_deck(deck_path, tmp_path)

    csv_path = Path(result["csv_path"])
    html_path = Path(result["html_path"])
    css_path = Path(result["css_path"])
    manifest_path = Path(result["manifest_path"])
    web_deck_path = Path(result["web_deck_path"])

    assert csv_path.exists()
    assert html_path.exists()
    assert css_path.exists()
    assert manifest_path.exists()
    assert web_deck_path.exists()

    rows = list(csv.reader(csv_path.open(encoding="utf-8", newline="")))
    assert rows[0] == ["guid", "anverso", "reverso", "etiquetas"]
    assert rows[1][0] == "qc-purpose"
    assert "<span class=\"semantic semantic-qc\">" in rows[1][1]

    html_text = html_path.read_text(encoding="utf-8")
    assert "Fundamentos del control de calidad Westgard" in html_text
    assert "flashcards.css" in html_text
    assert "Concepto" in html_text
    assert "Control de calidad" in html_text

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["deck_id"] == "westgard_qc_basics"
    assert manifest["card_count"] == 20
    assert manifest["outputs"]["study_deck"] == "study_deck.json"

    web_deck = json.loads(web_deck_path.read_text(encoding="utf-8"))
    assert web_deck["metadata"]["display_tags"][1] == "Control de calidad"
    assert web_deck["cards"][0]["card_type_label"] == "Concepto"
    assert "Control de calidad" in web_deck["cards"][0]["front_html"]


def test_flashcard_export_is_deterministic(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    deck_path = repo_root / "content" / "flashcards" / "westgard_qc_basics.deck.json"
    output_one = tmp_path / "run_one"
    output_two = tmp_path / "run_two"

    export_flashcard_deck(deck_path, output_one)
    export_flashcard_deck(deck_path, output_two)

    digests_one = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(output_one.iterdir())
        if path.is_file()
    }
    digests_two = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(output_two.iterdir())
        if path.is_file()
    }
    assert digests_one == digests_two


def test_export_flashcards_script(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "export_flashcards.py"
    deck_path = repo_root / "content" / "flashcards" / "westgard_qc_basics.deck.json"
    _ = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--deck",
            str(deck_path),
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
    )

    assert (tmp_path / "westgard_qc_basics.csv").exists()
    assert (tmp_path / "preview.html").exists()
    assert (tmp_path / "flashcards.css").exists()
    assert (tmp_path / "study_deck.json").exists()
