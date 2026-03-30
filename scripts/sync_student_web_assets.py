from __future__ import annotations

import argparse
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_SOURCE = REPO_ROOT / "outputs" / "web_data"
DEFAULT_DATASET_TARGET = REPO_ROOT / "apps" / "student-web" / "public" / "web_data"
DEFAULT_EDUCATIONAL_TARGET = REPO_ROOT / "apps" / "student-web" / "public" / "educational"
DEFAULT_SCENARIOS_SOURCE = REPO_ROOT / "content" / "scenarios.json"
DEFAULT_LESSONS_SOURCE = REPO_ROOT / "content" / "lessons.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync static dataset and educational assets for apps/student-web.",
    )
    parser.add_argument(
        "--dataset-source",
        type=Path,
        default=DEFAULT_DATASET_SOURCE,
        help="Source directory with exported web_data (default: outputs/web_data).",
    )
    parser.add_argument(
        "--dataset-target",
        type=Path,
        default=DEFAULT_DATASET_TARGET,
        help="Target directory inside student web public assets.",
    )
    parser.add_argument(
        "--skip-educational",
        action="store_true",
        help="Skip optional educational content copy.",
    )
    parser.add_argument(
        "--clean-target",
        action="store_true",
        help="Delete target directories before copying.",
    )
    return parser.parse_args()


def _clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def _copy_dataset(source: Path, target: Path, clean_target: bool) -> None:
    if not source.exists():
        raise FileNotFoundError(
            f"Dataset source not found: {source}. Run export first (westgard_ops.ps1 -Action release)."
        )
    if clean_target:
        _clean_dir(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True)


def _copy_optional_file(source: Path, target: Path) -> bool:
    if not source.exists():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return True


def main() -> None:
    args = parse_args()

    dataset_source = Path(args.dataset_source).resolve()
    dataset_target = Path(args.dataset_target).resolve()
    include_educational = not bool(args.skip_educational)

    _copy_dataset(dataset_source, dataset_target, clean_target=bool(args.clean_target))
    print(f"[sync] dataset copied: {dataset_source} -> {dataset_target}")

    if include_educational:
        educational_target = DEFAULT_EDUCATIONAL_TARGET.resolve()
        if args.clean_target:
            _clean_dir(educational_target)
        copied_scenarios = _copy_optional_file(
            DEFAULT_SCENARIOS_SOURCE.resolve(),
            educational_target / "scenarios.json",
        )
        copied_lessons = _copy_optional_file(
            DEFAULT_LESSONS_SOURCE.resolve(),
            educational_target / "lessons.json",
        )
        print(
            "[sync] educational files: "
            f"scenarios={'ok' if copied_scenarios else 'missing'}, "
            f"lessons={'ok' if copied_lessons else 'missing'}"
        )
    else:
        print("[sync] educational copy skipped")


if __name__ == "__main__":
    main()
