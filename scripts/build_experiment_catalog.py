from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

from content.authoring_adapter import (
    convert_authoring_to_experiment_catalog,
    load_authoring_catalog,
    write_experiment_catalog,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build technical experiment catalog from authoring contract."
    )
    _ = parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Authoring contract JSON path.",
    )
    _ = parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output path for generated technical experiment catalog JSON.",
    )
    _ = parser.add_argument(
        "--include-education-metadata",
        action="store_true",
        help="Copy educational data into a separate 'authoring_metadata' block.",
    )
    return parser.parse_args()


def _display_relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def main() -> None:
    args = parse_args()
    authoring = load_authoring_catalog(args.input)
    technical = convert_authoring_to_experiment_catalog(
        authoring,
        include_education_metadata=bool(args.include_education_metadata),
    )
    written = write_experiment_catalog(technical, args.output)
    print("\nTechnical catalog generated:")
    print(f"  - input: {_display_relative_path(args.input)}")
    print(f"  - output: {_display_relative_path(written)}")
    print(f"  - experiments: {len(technical['experiments'])}")
    print(f"  - include_education_metadata: {bool(args.include_education_metadata)}")


if __name__ == "__main__":
    main()
