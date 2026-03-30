# Content Editing Guide for Non-Programmers

## Overview

This folder contains **educational content** for the Westgard QC simulator. The files here are designed to be edited by domain experts (like Beatriz) who understand the educational goals but may not be Python programmers.

**Key principle**: You can safely edit the text in these JSON files without breaking the simulation logic.

---

## Files in This Folder

### 1. `scenarios.json`
Contains educational descriptions for each QC failure pattern.

### 2. `lessons.json`
Contains teaching materials: guiding questions, challenges, and reveal text for learners.

### 3. `validate_content.py`
A helper script to check that your edits are valid. Run this after making changes!

### 4. `README.md`
This file—your guide to editing content safely.

---

## What You CAN Edit Safely

### ✅ Safe to Edit

1. **All text content** in `scenarios.json` and `lessons.json`
   - Display names
   - Descriptions
   - Educational messages
   - Pattern hints
   - Common mistakes
   - Guiding questions
   - Challenge prompts
   - Reveal text

2. **Wording and phrasing**
   - Fix typos
   - Improve clarity
   - Add domain expertise
   - Update educational explanations
   - Adjust reading level

3. **Question lists**
   - Add or remove guiding questions
   - Reorder questions
   - Rewrite questions for clarity

### ❌ Do NOT Edit

1. **Scenario keys** (`normal`, `bias`, `drift`, `imprecision`)
   - These MUST match the exported web data
   - Changing these will break the web application

2. **Field names** (like `display_name`, `educational_message`, etc.)
   - These are used by the web application code
   - Only edit the *values*, not the field names

3. **JSON syntax**
   - Keep the quotes, commas, brackets, and braces intact
   - See "JSON Editing Tips" below if unsure

4. **Python simulation code**
   - Do NOT edit files in `qc_lab_simulator/` folder
   - That's where the scientific logic lives

---

## JSON Editing Tips

### Basic Structure

JSON files use this pattern:
```json
{
  "key": "value",
  "another_key": "another value"
}
```

### Rules to Remember

1. **Strings use double quotes**: `"text"` not `'text'`
2. **Commas between items**: Except after the last item
3. **No trailing commas**: The last item in a list or object shouldn't have a comma
4. **Lists use square brackets**: `["item1", "item2", "item3"]`
5. **Objects use curly braces**: `{"field": "value"}`

### Example Edit

**Before:**
```json
{
  "display_name": "Normal Operation",
  "short_description": "Baseline scenario with no failures"
}
```

**After (safe edit):**
```json
{
  "display_name": "Normal Operation",
  "short_description": "Baseline scenario showing a healthy QC process"
}
```

**WRONG (breaks JSON):**
```json
{
  "display_name": "Normal Operation",
  "short_description": "Missing closing quote
}
```

---

## How to Validate Your Changes

After editing, always run the validation script to check for errors:

### On Windows (PowerShell or Command Prompt)
```bash
cd C:\path\to\westgard\content
python validate_content.py
```

### Expected Output

**If valid:**
```
Validating content files...

✓ scenarios.json: Valid
✓ lessons.json: Valid

✓ All content files are valid!
```

**If errors:**
```
Validating content files...

✗ scenarios.json: 2 error(s)
  - scenarios.normal.display_name cannot be empty
  - scenarios.bias missing fields: ['common_mistake']

✗ Validation failed. Please fix the errors above.
```

Fix the errors and run validation again until you see all green checkmarks.

---

## Scenario Structure Reference

Each scenario in `scenarios.json` must have these five fields:

```json
{
  "scenario_key": {
    "display_name": "Short title shown to users",
    "short_description": "One-sentence summary",
    "educational_message": "Main learning point (2-3 sentences)",
    "pattern_hint": "What to look for in the chart",
    "common_mistake": "Typical student misunderstanding"
  }
}
```

### Field Descriptions

| Field | Purpose | Example |
|-------|---------|---------|
| `display_name` | UI heading | "Normal Operation" |
| `short_description` | Subtitle or preview | "Baseline scenario with no QC failures" |
| `educational_message` | Core teaching point | "When the QC process is working correctly..." |
| `pattern_hint` | What the chart looks like | "Look for random scatter around the mean..." |
| `common_mistake` | Anticipated misconception | "Students often expect perfectly symmetric patterns..." |

---

## Lesson Structure Reference

Each lesson in `lessons.json` must have these three fields:

```json
{
  "scenario_key": {
    "guiding_questions": [
      "Question 1?",
      "Question 2?",
      "Question 3?"
    ],
    "challenge_prompt": "Active learning task for the student",
    "reveal_text": "Detailed explanation revealed after attempt"
  }
}
```

### Field Descriptions

| Field | Purpose | Type |
|-------|---------|------|
| `guiding_questions` | Pre-exploration questions | List of strings |
| `challenge_prompt` | Active learning task | String |
| `reveal_text` | Full explanation with answer | String |

---

## Scenario Keys Reference

These four keys align with the exported web data and **must not be changed**:

| Key | Display Name | Pattern Type |
|-----|--------------|--------------|
| `normal` | Normal Operation | Baseline (no failure) |
| `bias` | Bias Shift | Sudden mean shift |
| `drift` | Progressive Drift | Gradual linear drift |
| `imprecision` | Imprecision Increase | Increased scatter |

---

## Workflow for Making Changes

1. **Edit** the JSON files in a text editor
   - VS Code, Notepad++, or even Notepad work fine
   - Keep the JSON structure intact

2. **Validate** your changes
   ```bash
   python validate_content.py
   ```

3. **Fix** any reported errors

4. **Test** in the web application (if available)

5. **Commit** your changes to version control
   ```bash
   git add content/scenarios.json content/lessons.json
   git commit -m "Update educational content for bias scenario"
   ```

---

## Getting Help

### Common Errors

**"Invalid JSON"**
- Check for missing quotes, commas, or brackets
- Use a JSON validator: https://jsonlint.com/

**"Missing fields"**
- Make sure all five scenario fields are present
- Make sure all three lesson fields are present

**"Field cannot be empty"**
- Every text field needs actual content
- Even placeholders like "TODO" are better than empty strings

**"Unexpected scenario keys"**
- You may have added a new scenario key
- Only `normal`, `bias`, `drift`, `imprecision` are allowed
- Contact the development team if you need a new scenario

---

## Questions?

If you're unsure about an edit:
1. Run `validate_content.py` first
2. Check this README
3. Ask the development team
4. Test in a non-production environment

**Remember**: When in doubt, validate! The validation script will catch most problems before they reach users.
