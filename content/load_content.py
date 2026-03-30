"""Content loader utility for web applications.

This module provides simple functions to load pedagogical content
from the content/ folder for use in web interfaces or educational tools.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).parent.parent
CONTENT_DIR = REPO_ROOT / "content"


def load_scenarios() -> Dict[str, Dict[str, str]]:
    """Load all scenario educational content.
    
    Returns
    -------
    Dict[str, Dict[str, str]]
        Nested dictionary with scenario keys mapping to their fields:
        - display_name
        - short_description
        - educational_message
        - pattern_hint
        - common_mistake
    
    Examples
    --------
    >>> scenarios = load_scenarios()
    >>> print(scenarios['normal']['display_name'])
    'Normal Operation'
    >>> print(scenarios['bias']['pattern_hint'])
    'The first 10 runs cluster around the original mean...'
    """
    scenarios_path = CONTENT_DIR / "scenarios.json"
    with scenarios_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_lessons() -> Dict[str, Dict[str, Any]]:
    """Load all lesson educational content.
    
    Returns
    -------
    Dict[str, Dict[str, Any]]
        Nested dictionary with scenario keys mapping to their lesson fields:
        - guiding_questions (List[str])
        - challenge_prompt (str)
        - reveal_text (str)
    
    Examples
    --------
    >>> lessons = load_lessons()
    >>> print(lessons['drift']['guiding_questions'][0])
    'How is this pattern different from the bias scenario?'
    >>> print(lessons['imprecision']['challenge_prompt'])
    'Calculate the standard deviation...'
    """
    lessons_path = CONTENT_DIR / "lessons.json"
    with lessons_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_scenario_content(scenario_key: str) -> Dict[str, str]:
    """Get educational content for a specific scenario.
    
    Parameters
    ----------
    scenario_key
        One of: 'normal', 'bias', 'drift', 'imprecision'
    
    Returns
    -------
    Dict[str, str]
        Educational content fields for the scenario.
    
    Raises
    ------
    KeyError
        If scenario_key is not recognized.
    
    Examples
    --------
    >>> content = get_scenario_content('bias')
    >>> print(content['display_name'])
    'Bias Shift'
    """
    scenarios = load_scenarios()
    return scenarios[scenario_key]


def get_lesson_content(scenario_key: str) -> Dict[str, Any]:
    """Get lesson content for a specific scenario.
    
    Parameters
    ----------
    scenario_key
        One of: 'normal', 'bias', 'drift', 'imprecision'
    
    Returns
    -------
    Dict[str, Any]
        Lesson content fields for the scenario.
    
    Raises
    ------
    KeyError
        If scenario_key is not recognized.
    
    Examples
    --------
    >>> lesson = get_lesson_content('drift')
    >>> print(len(lesson['guiding_questions']))
    3
    """
    lessons = load_lessons()
    return lessons[scenario_key]


def get_combined_content(scenario_key: str) -> Dict[str, Any]:
    """Get both scenario and lesson content for a specific scenario.
    
    Convenient function that merges scenario educational content
    with lesson content for a complete pedagogical package.
    
    Parameters
    ----------
    scenario_key
        One of: 'normal', 'bias', 'drift', 'imprecision'
    
    Returns
    -------
    Dict[str, Any]
        Combined dictionary containing all educational fields.
    
    Examples
    --------
    >>> content = get_combined_content('normal')
    >>> print(content['display_name'])  # from scenarios
    'Normal Operation'
    >>> print(len(content['guiding_questions']))  # from lessons
    3
    """
    scenario_content = get_scenario_content(scenario_key)
    lesson_content = get_lesson_content(scenario_key)
    
    return {**scenario_content, **lesson_content}


# Example usage for JavaScript/web integration
def export_for_web() -> Dict[str, Dict[str, Any]]:
    """Export all content in a web-friendly format.
    
    This function combines scenarios and lessons into a single
    dictionary that can be easily converted to JSON for web use.
    
    Returns
    -------
    Dict[str, Dict[str, Any]]
        Complete educational content for all scenarios.
    
    Examples
    --------
    To export to a JSON file for web use:
    >>> import json
    >>> content = export_for_web()
    >>> with open('web_content.json', 'w') as f:
    ...     json.dump(content, f, indent=2)
    """
    scenarios = load_scenarios()
    lessons = load_lessons()
    
    combined = {}
    for scenario_key in scenarios.keys():
        combined[scenario_key] = {
            **scenarios[scenario_key],
            **lessons[scenario_key]
        }
    
    return combined


if __name__ == "__main__":
    # Demo: print all content
    print("=== Westgard QC Content Loader Demo ===\n")
    
    scenarios = load_scenarios()
    print(f"Loaded {len(scenarios)} scenarios:")
    for key in scenarios.keys():
        print(f"  - {key}: {scenarios[key]['display_name']}")
    
    print("\nExample usage:")
    content = get_combined_content('bias')
    print(f"\nScenario: {content['display_name']}")
    print(f"Description: {content['short_description']}")
    print(f"Number of guiding questions: {len(content['guiding_questions'])}")
