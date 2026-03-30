"""Content validation utility for pedagogical JSON files.

This module validates that scenarios.json and lessons.json conform to their
expected schemas and are safe for non-programmer editing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).parent.parent
CONTENT_DIR = REPO_ROOT / "content"

REQUIRED_SCENARIO_KEYS = (
    "normal",
    "bias",
    "drift",
    "imprecision",
)

REQUIRED_SCENARIO_FIELDS = (
    "display_name",
    "short_description",
    "educational_message",
    "pattern_hint",
    "common_mistake",
)

REQUIRED_LESSON_FIELDS = (
    "guiding_questions",
    "challenge_prompt",
    "reveal_text",
)


def validate_scenarios_json(scenarios_path: Path) -> List[str]:
    """Validate scenarios.json structure and content.
    
    Returns
    -------
    List[str]
        List of validation error messages (empty if valid).
    """
    errors: List[str] = []
    
    try:
        with scenarios_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return [f"File not found: {scenarios_path}"]
    except json.JSONDecodeError as e:
        return [f"Invalid JSON in {scenarios_path}: {e}"]
    
    if not isinstance(data, dict):
        errors.append("scenarios.json root must be an object/dict")
        return errors
    
    # Check all required scenario keys exist
    missing_scenarios = [key for key in REQUIRED_SCENARIO_KEYS if key not in data]
    if missing_scenarios:
        errors.append(f"Missing scenario keys: {missing_scenarios}")
    
    # Check for unexpected extra scenarios
    extra_scenarios = [key for key in data.keys() if key not in REQUIRED_SCENARIO_KEYS]
    if extra_scenarios:
        errors.append(f"Unexpected scenario keys (not in exported web data): {extra_scenarios}")
    
    # Validate each scenario structure
    for scenario_key in REQUIRED_SCENARIO_KEYS:
        if scenario_key not in data:
            continue
        
        scenario = data[scenario_key]
        if not isinstance(scenario, dict):
            errors.append(f"scenarios.{scenario_key} must be an object/dict")
            continue
        
        # Check required fields
        missing_fields = [
            field for field in REQUIRED_SCENARIO_FIELDS
            if field not in scenario
        ]
        if missing_fields:
            errors.append(f"scenarios.{scenario_key} missing fields: {missing_fields}")
        
        # Validate field types
        for field in REQUIRED_SCENARIO_FIELDS:
            if field in scenario:
                value = scenario[field]
                if not isinstance(value, str):
                    errors.append(
                        f"scenarios.{scenario_key}.{field} must be a string, got {type(value).__name__}"
                    )
                elif not value.strip():
                    errors.append(f"scenarios.{scenario_key}.{field} cannot be empty")
    
    return errors


def validate_lessons_json(lessons_path: Path) -> List[str]:
    """Validate lessons.json structure and content.
    
    Returns
    -------
    List[str]
        List of validation error messages (empty if valid).
    """
    errors: List[str] = []
    
    try:
        with lessons_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return [f"File not found: {lessons_path}"]
    except json.JSONDecodeError as e:
        return [f"Invalid JSON in {lessons_path}: {e}"]
    
    if not isinstance(data, dict):
        errors.append("lessons.json root must be an object/dict")
        return errors
    
    # Check all required scenario keys exist
    missing_scenarios = [key for key in REQUIRED_SCENARIO_KEYS if key not in data]
    if missing_scenarios:
        errors.append(f"Missing lesson scenario keys: {missing_scenarios}")
    
    # Check for unexpected extra scenarios
    extra_scenarios = [key for key in data.keys() if key not in REQUIRED_SCENARIO_KEYS]
    if extra_scenarios:
        errors.append(f"Unexpected lesson keys (not in exported web data): {extra_scenarios}")
    
    # Validate each lesson structure
    for scenario_key in REQUIRED_SCENARIO_KEYS:
        if scenario_key not in data:
            continue
        
        lesson = data[scenario_key]
        if not isinstance(lesson, dict):
            errors.append(f"lessons.{scenario_key} must be an object/dict")
            continue
        
        # Check required fields
        missing_fields = [
            field for field in REQUIRED_LESSON_FIELDS
            if field not in lesson
        ]
        if missing_fields:
            errors.append(f"lessons.{scenario_key} missing fields: {missing_fields}")
        
        # Validate guiding_questions
        if "guiding_questions" in lesson:
            questions = lesson["guiding_questions"]
            if not isinstance(questions, list):
                errors.append(
                    f"lessons.{scenario_key}.guiding_questions must be a list"
                )
            elif len(questions) == 0:
                errors.append(
                    f"lessons.{scenario_key}.guiding_questions cannot be empty"
                )
            else:
                for i, question in enumerate(questions):
                    if not isinstance(question, str):
                        errors.append(
                            f"lessons.{scenario_key}.guiding_questions[{i}] must be a string"
                        )
                    elif not question.strip():
                        errors.append(
                            f"lessons.{scenario_key}.guiding_questions[{i}] cannot be empty"
                        )
        
        # Validate string fields
        for field in ["challenge_prompt", "reveal_text"]:
            if field in lesson:
                value = lesson[field]
                if not isinstance(value, str):
                    errors.append(
                        f"lessons.{scenario_key}.{field} must be a string, got {type(value).__name__}"
                    )
                elif not value.strip():
                    errors.append(f"lessons.{scenario_key}.{field} cannot be empty")
    
    return errors


def validate_all_content() -> Dict[str, List[str]]:
    """Validate all content JSON files.
    
    Returns
    -------
    Dict[str, List[str]]
        Dictionary mapping file names to their validation errors.
        Empty lists indicate valid files.
    """
    scenarios_path = CONTENT_DIR / "scenarios.json"
    lessons_path = CONTENT_DIR / "lessons.json"
    
    return {
        "scenarios.json": validate_scenarios_json(scenarios_path),
        "lessons.json": validate_lessons_json(lessons_path),
    }


def print_validation_results(results: Dict[str, List[str]]) -> bool:
    """Print validation results and return True if all valid.
    
    Parameters
    ----------
    results:
        Output from validate_all_content().
    
    Returns
    -------
    bool
        True if all files are valid, False otherwise.
    """
    all_valid = True
    
    for filename, errors in results.items():
        if not errors:
            print(f"✓ {filename}: Valid")
        else:
            print(f"✗ {filename}: {len(errors)} error(s)")
            for error in errors:
                print(f"  - {error}")
            all_valid = False
    
    return all_valid


def main() -> None:
    """Run content validation and exit with appropriate code."""
    print("Validating content files...\n")
    results = validate_all_content()
    all_valid = print_validation_results(results)
    
    if all_valid:
        print("\n✓ All content files are valid!")
        exit(0)
    else:
        print("\n✗ Validation failed. Please fix the errors above.")
        exit(1)


if __name__ == "__main__":
    main()
