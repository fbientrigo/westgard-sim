from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

from qc_lab_simulator.flashcards.export import export_flashcard_deck
from qc_lab_simulator.flashcards.io import DEFAULT_DECK_PATH

DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "flashcards" / DEFAULT_DECK_PATH.stem.replace(".deck", "")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and export a flashcard deck.")
    _ = parser.add_argument(
        "--deck",
        type=Path,
        default=DEFAULT_DECK_PATH,
        help="Path to a flashcard deck JSON file.",
    )
    _ = parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Target folder for CSV, preview HTML, and CSS output.",
    )
    _ = parser.add_argument(
        "--theme",
        type=Path,
        default=None,
        help="Optional theme token JSON override.",
    )
    return parser.parse_args()


def _display_relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def main() -> None:
    args = parse_args()
    result = export_flashcard_deck(args.deck, args.output_dir, theme_path=args.theme)
    print("Deck de flashcards exportado:")
    print(f"  - deck: {result['deck_id']}")
    print(f"  - tarjetas: {result['card_count']}")
    print(f"  - csv: {_display_relative_path(result['csv_path'])}")
    print(f"  - vista_previa: {_display_relative_path(result['html_path'])}")
    print(f"  - css: {_display_relative_path(result['css_path'])}")


if __name__ == "__main__":
    main()
