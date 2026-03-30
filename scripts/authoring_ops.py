from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).parent.parent.resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from content.authoring_adapter import (
    convert_authoring_to_experiment_catalog,
    load_authoring_catalog,
    write_experiment_catalog,
)
from content.authoring_validation import AUTHORING_SCHEMA_PATH, validate_catalog_file
from qc_lab_simulator.web_export import (
    export_experiment_catalog_web_data,
    load_experiment_catalog,
    validate_web_payload,
)

DEFAULT_AUTHORING_INPUT = REPO_ROOT / "content" / "authoring_catalog.example.json"
DEFAULT_TECHNICAL_OUTPUT = REPO_ROOT / "content" / "experiment_catalog.generated.json"
DEFAULT_EXPORT_DIR = REPO_ROOT / "outputs" / "web_data"
DEFAULT_BACKUPS_DIR = REPO_ROOT / "outputs" / "backups"


def _now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def _check_module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def backup_file_if_exists(target_file: Path, backups_dir: Path, *, label: str) -> Path | None:
    target_file = Path(target_file)
    if not target_file.exists():
        return None
    backups_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backups_dir / f"{label}_{_now_stamp()}{target_file.suffix}"
    shutil.copy2(target_file, backup_path)
    return backup_path


def backup_dir_if_exists(target_dir: Path, backups_dir: Path, *, label: str) -> Path | None:
    target_dir = Path(target_dir)
    if not target_dir.exists() or not any(target_dir.iterdir()):
        return None
    backups_dir.mkdir(parents=True, exist_ok=True)
    archive_base = backups_dir / f"{label}_{_now_stamp()}"
    archive_path = shutil.make_archive(str(archive_base), "zip", root_dir=target_dir)
    return Path(archive_path)


def run_preflight(authoring_input: Path, *, check_streamlit: bool = True) -> dict[str, Any]:
    authoring_input = Path(authoring_input)
    required_paths = [
        AUTHORING_SCHEMA_PATH,
        authoring_input,
        REPO_ROOT / "scripts" / "build_experiment_catalog.py",
        REPO_ROOT / "scripts" / "export_web_data.py",
    ]

    missing = [path for path in required_paths if not path.exists()]
    if missing:
        rendered = "\n".join(f"- {_display_path(path)}" for path in missing)
        raise ValueError(f"Preflight failed. Missing required files:\n{rendered}")

    deps_missing: list[str] = []
    if not _check_module_available("jsonschema"):
        deps_missing.append("jsonschema")
    if check_streamlit and not _check_module_available("streamlit"):
        deps_missing.append("streamlit")
    if deps_missing:
        rendered = ", ".join(deps_missing)
        raise ValueError(
            f"Preflight failed. Missing Python dependencies: {rendered}. "
            "Instala con: pip install -r requirements.txt"
        )

    errors = validate_catalog_file(authoring_input)
    if errors:
        rendered = "\n".join(f"- {err}" for err in errors)
        raise ValueError(f"Preflight failed. Authoring catalog invalid:\n{rendered}")

    return {
        "authoring_input": authoring_input,
        "catalog_errors": 0,
    }


def verify_export_output(export_dir: Path) -> dict[str, Any]:
    export_dir = Path(export_dir)
    index_path = export_dir / "index.json"
    errors: list[str] = []

    if not export_dir.exists():
        raise ValueError(f"Export directory not found: {_display_path(export_dir)}")
    if not index_path.exists():
        raise ValueError(f"Missing index.json in {_display_path(export_dir)}")

    try:
        index_data = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid index.json: {exc}") from exc

    experiments = index_data.get("experiments")
    if not isinstance(experiments, list):
        raise ValueError("Invalid index.json: 'experiments' must be a list.")
    if not experiments:
        raise ValueError("Invalid index.json: 'experiments' is empty.")

    total_manifest_scenarios = 0
    total_payload_files = 0

    for exp_index, exp in enumerate(experiments):
        location = f"index.experiments[{exp_index}]"
        if not isinstance(exp, Mapping):
            errors.append(f"{location} must be an object.")
            continue
        exp_id = exp.get("id")
        if not isinstance(exp_id, str) or not exp_id.strip():
            errors.append(f"{location}.id must be non-empty string.")
            continue

        manifest_rel = exp.get("manifest_path")
        if not isinstance(manifest_rel, str) or not manifest_rel.strip():
            errors.append(f"{location}.manifest_path must be non-empty string.")
            continue

        manifest_path = export_dir / manifest_rel
        if not manifest_path.exists():
            errors.append(f"Missing manifest for experiment '{exp_id}': {manifest_rel}")
            continue

        if Path(manifest_rel).parts[:2] != ("experiments", exp_id):
            errors.append(
                f"Experiment '{exp_id}' has manifest_path outside expected structure: {manifest_rel}"
            )

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid manifest for '{exp_id}': {exc}")
            continue

        scenarios = manifest.get("scenarios")
        if not isinstance(scenarios, list):
            errors.append(f"Manifest '{manifest_rel}' has invalid 'scenarios'.")
            continue

        declared_count = exp.get("scenario_count")
        if isinstance(declared_count, int) and declared_count != len(scenarios):
            errors.append(
                f"Scenario count mismatch for '{exp_id}': index={declared_count}, manifest={len(scenarios)}."
            )

        total_manifest_scenarios += len(scenarios)
        for sc_index, scenario in enumerate(scenarios):
            sc_loc = f"{manifest_rel}.scenarios[{sc_index}]"
            if not isinstance(scenario, Mapping):
                errors.append(f"{sc_loc} must be an object.")
                continue
            payload_rel = scenario.get("path")
            if not isinstance(payload_rel, str) or not payload_rel.strip():
                errors.append(f"{sc_loc}.path must be non-empty string.")
                continue

            payload_path = export_dir / payload_rel
            if not payload_path.exists():
                errors.append(f"Missing payload file: {payload_rel}")
                continue

            expected_prefix = ("experiments", exp_id)
            if Path(payload_rel).parts[:2] != expected_prefix:
                errors.append(
                    f"Payload path for '{exp_id}' outside expected structure: {payload_rel}"
                )

            try:
                payload_data = json.loads(payload_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"Invalid payload JSON '{payload_rel}': {exc}")
                continue
            payload_errors = validate_web_payload(payload_data)
            if payload_errors:
                errors.append(
                    f"Invalid payload content '{payload_rel}': {', '.join(payload_errors[:2])}"
                )
                continue
            total_payload_files += 1

    if total_manifest_scenarios != total_payload_files:
        errors.append(
            "Payload count mismatch between manifests and valid payload files: "
            f"{total_manifest_scenarios} vs {total_payload_files}."
        )

    if errors:
        rendered = "\n".join(f"- {err}" for err in errors)
        raise ValueError(f"Export verification failed:\n{rendered}")

    return {
        "export_dir": export_dir,
        "index_path": index_path,
        "experiment_count": len(experiments),
        "manifest_scenarios": total_manifest_scenarios,
        "payload_count": total_payload_files,
    }


def run_release(
    authoring_input: Path,
    technical_output: Path,
    export_dir: Path,
    backups_dir: Path,
    *,
    skip_backup: bool = False,
) -> dict[str, Any]:
    preflight = run_preflight(authoring_input, check_streamlit=False)
    backup_technical = None
    backup_export = None
    if not skip_backup:
        backup_technical = backup_file_if_exists(
            Path(technical_output), Path(backups_dir), label="technical_catalog"
        )
        backup_export = backup_dir_if_exists(
            Path(export_dir), Path(backups_dir), label="web_export"
        )

    authoring = load_authoring_catalog(Path(authoring_input))
    technical = convert_authoring_to_experiment_catalog(authoring)
    technical_written = write_experiment_catalog(technical, Path(technical_output))

    experiments = load_experiment_catalog(technical_written)
    export_result = export_experiment_catalog_web_data(Path(export_dir), experiments)
    verification = verify_export_output(Path(export_dir))

    scenario_count = sum(len(exp["scenarios"]) for exp in technical["experiments"])
    return {
        "preflight": preflight,
        "technical_output": technical_written,
        "export_dir": Path(export_dir),
        "index_path": Path(export_result["index_path"]),
        "experiment_count": len(technical["experiments"]),
        "scenario_count": scenario_count,
        "payload_count": int(export_result["payload_count"]),
        "backup_technical": backup_technical,
        "backup_export_zip": backup_export,
        "verification": verification,
    }


def run_smoke() -> None:
    script_path = REPO_ROOT / "scripts" / "smoke_authoring_flow.py"
    subprocess.run([sys.executable, str(script_path)], check=True)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Operational commands for Westgard authoring pilot pipeline."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight", help="Validate environment and authoring input.")
    _ = preflight.add_argument("--input", type=Path, default=DEFAULT_AUTHORING_INPUT)
    _ = preflight.add_argument(
        "--skip-streamlit-check",
        action="store_true",
        help="Skip streamlit dependency check (for headless build/export environments).",
    )

    release = subparsers.add_parser(
        "release", help="Preflight + optional backup + build + export + verify."
    )
    _ = release.add_argument("--input", type=Path, default=DEFAULT_AUTHORING_INPUT)
    _ = release.add_argument("--technical-output", type=Path, default=DEFAULT_TECHNICAL_OUTPUT)
    _ = release.add_argument("--export-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    _ = release.add_argument("--backups-dir", type=Path, default=DEFAULT_BACKUPS_DIR)
    _ = release.add_argument("--skip-backup", action="store_true")

    verify = subparsers.add_parser("verify", help="Verify an exported static dataset.")
    _ = verify.add_argument("--export-dir", type=Path, default=DEFAULT_EXPORT_DIR)

    _ = subparsers.add_parser("smoke", help="Run smoke_authoring_flow.py end-to-end.")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "preflight":
        result = run_preflight(args.input, check_streamlit=not bool(args.skip_streamlit_check))
        print("Preflight OK")
        print(f"  - input: {_display_path(result['authoring_input'])}")
        return

    if args.command == "release":
        result = run_release(
            args.input,
            args.technical_output,
            args.export_dir,
            args.backups_dir,
            skip_backup=bool(args.skip_backup),
        )
        print("Release pipeline OK")
        print(f"  - input: {_display_path(Path(args.input))}")
        print(f"  - technical_output: {_display_path(result['technical_output'])}")
        print(f"  - export_dir: {_display_path(result['export_dir'])}")
        print(f"  - index_path: {_display_path(result['index_path'])}")
        print(f"  - experiments: {result['experiment_count']}")
        print(f"  - scenarios: {result['scenario_count']}")
        print(f"  - payloads: {result['payload_count']}")
        backup_technical = result["backup_technical"]
        backup_export = result["backup_export_zip"]
        print(
            "  - backup_technical: "
            f"{_display_path(backup_technical) if isinstance(backup_technical, Path) else 'none'}"
        )
        print(
            "  - backup_export_zip: "
            f"{_display_path(backup_export) if isinstance(backup_export, Path) else 'none'}"
        )
        return

    if args.command == "verify":
        result = verify_export_output(args.export_dir)
        print("Verification OK")
        print(f"  - export_dir: {_display_path(result['export_dir'])}")
        print(f"  - index_path: {_display_path(result['index_path'])}")
        print(f"  - experiments: {result['experiment_count']}")
        print(f"  - payloads: {result['payload_count']}")
        return

    if args.command == "smoke":
        run_smoke()
        return

    raise RuntimeError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
