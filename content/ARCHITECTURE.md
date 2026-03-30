# Content Layer Architecture

## Purpose

This content layer separates **educational/pedagogical text** from **scientific simulation logic**, enabling domain experts to modify teaching materials without touching Python code.

## Design Principles

1. **Separation of Concerns**: Educational content lives in JSON, simulation logic stays in Python
2. **Domain Expert Friendly**: JSON files are human-readable and editable without programming knowledge
3. **Validated**: Schema validation prevents structural errors
4. **Aligned**: Scenario keys match exported web data exactly

## File Structure

```
content/
├── README.md                 # Non-programmer editing guide
├── ARCHITECTURE.md          # This file - technical overview
├── scenarios.json           # Educational content for each scenario
├── lessons.json             # Teaching materials (questions, challenges)
├── validate_content.py      # Schema validation utility
└── load_content.py          # Loader utility for web/Python integration
```

## Schema Design

### scenarios.json

Each scenario has 5 required fields:

```json
{
  "scenario_key": {
    "display_name": "Human-readable title",
    "short_description": "Brief summary (1 sentence)",
    "educational_message": "Main learning objective (2-3 sentences)",
    "pattern_hint": "What to look for in the data visualization",
    "common_mistake": "Typical student misconception"
  }
}
```

**Design rationale:**
- `display_name`: UI heading
- `short_description`: Subtitle/preview text
- `educational_message`: Core pedagogical point
- `pattern_hint`: Guides visual pattern recognition
- `common_mistake`: Addresses known misconceptions

### lessons.json

Each lesson has 3 required fields:

```json
{
  "scenario_key": {
    "guiding_questions": ["Question 1?", "Question 2?", "Question 3?"],
    "challenge_prompt": "Active learning task description",
    "reveal_text": "Detailed explanation with answer key"
  }
}
```

**Design rationale:**
- `guiding_questions`: Pre-exploration to activate prior knowledge
- `challenge_prompt`: Active learning engagement
- `reveal_text`: Complete explanation after student attempt

## Scenario Keys

Four scenario keys are hard-coded to match simulation exports:

| Key | Export File | Python Function | Web Scenario Type |
|-----|-------------|-----------------|-------------------|
| `normal` | `normal.json` | `scenario_normal()` | "normal" |
| `bias` | `bias.json` | `scenario_bias()` | "bias" |
| `drift` | `drift.json` | `scenario_drift()` | "drift" |
| `imprecision` | `imprecision.json` | `scenario_imprecision()` | "imprecision" |

**Critical constraint**: These keys cannot be changed without modifying:
1. `qc_lab_simulator/web_export.py` (SCENARIO_KEYS constant)
2. `qc_lab_simulator/scenarios.py` (function names)
3. Web application code (if already deployed)

## Validation Strategy

### Automated Validation

`validate_content.py` enforces:

1. **Structural validity**
   - Valid JSON syntax
   - Required keys present
   - Correct field types

2. **Content completeness**
   - No empty strings
   - Required fields populated
   - Scenario key alignment

3. **Schema adherence**
   - `guiding_questions` is a list of strings
   - Text fields are non-empty strings
   - No unexpected extra fields

### Manual Validation

Domain experts should:
1. Run `python validate_content.py` after every edit
2. Check educational accuracy (validator only checks structure)
3. Test in staging environment before production

## Integration Points

### Python Integration

```python
from content.load_content import get_combined_content

# Get all educational content for a scenario
content = get_combined_content('bias')
print(content['display_name'])  # "Bias Shift"
print(content['guiding_questions'])  # List of questions
```

### Web/JavaScript Integration

```python
from content.load_content import export_for_web
import json

# Export all content for web consumption
web_content = export_for_web()
with open('web_content.json', 'w') as f:
    json.dump(web_content, f, indent=2)
```

```javascript
// In JavaScript/TypeScript
fetch('web_content.json')
  .then(res => res.json())
  .then(content => {
    const biasContent = content.bias;
    document.querySelector('.scenario-title').textContent = 
      biasContent.display_name;
    // etc.
  });
```

### Export Pipeline Integration

Future enhancement: Merge content with web export:

```python
# In scripts/export_web_data.py (future)
from content.load_content import get_scenario_content

def build_web_scenario_payload(scenario_key, config):
    # ... existing export logic ...
    
    # Merge educational content
    educational_content = get_scenario_content(scenario_key)
    payload['educational_content'] = educational_content
    
    return payload
```

## Workflow

### For Domain Experts (Beatriz)

1. Edit `scenarios.json` or `lessons.json` in any text editor
2. Run `python validate_content.py`
3. Fix any reported errors
4. Commit changes to version control
5. (Optional) Test in staging environment

### For Developers

1. Do NOT modify JSON schema without team discussion
2. Use `load_content.py` functions to access content
3. Keep simulation logic separate from content
4. Update `validate_content.py` if schema changes

## Future Enhancements

### Potential Additions

1. **Internationalization**
   - `content/en/scenarios.json`
   - `content/es/scenarios.json`
   - `content/pt/scenarios.json`

2. **Versioning**
   - Track content version separately from code
   - Support A/B testing of educational messages

3. **Rich Media**
   - Add image references
   - Support embedded videos
   - Link to external resources

4. **Auto-merge with exports**
   - Integrate content directly into web export pipeline
   - Single unified JSON per scenario

5. **Content Analytics**
   - Track which messages are most effective
   - Iterate based on student outcomes

### Schema Evolution

If the schema needs to change:

1. Update `validate_content.py` with new requirements
2. Update `README.md` with new field descriptions
3. Migrate existing JSON files
4. Update `load_content.py` if necessary
5. Test thoroughly before deployment

## Testing

### Manual Testing Checklist

- [ ] JSON files parse without errors
- [ ] Validation script passes
- [ ] All scenario keys present
- [ ] All required fields populated
- [ ] Text is grammatically correct
- [ ] Educational content is accurate
- [ ] No broken references or placeholders

### Automated Testing

Future work: Add pytest tests for content validation

```python
# tests/test_content.py (future)
def test_scenarios_valid():
    from content.validate_content import validate_scenarios_json
    errors = validate_scenarios_json(CONTENT_DIR / "scenarios.json")
    assert len(errors) == 0

def test_all_scenarios_present():
    from content.load_content import load_scenarios
    scenarios = load_scenarios()
    assert set(scenarios.keys()) == {'normal', 'bias', 'drift', 'imprecision'}
```

## Constraints and Limitations

### Cannot Change

- Scenario keys (`normal`, `bias`, `drift`, `imprecision`)
- Field names in JSON schema
- JSON file names

### Can Change Freely

- All text content
- Wording and phrasing
- Number of guiding questions
- Educational approaches

### Requires Coordination

- Adding new scenarios (needs Python simulation code)
- Removing scenarios (affects web exports)
- Changing schema structure (affects all consumers)

## Questions?

For architectural questions or schema changes, consult the development team.
For content questions or educational accuracy, consult domain experts (Beatriz).
