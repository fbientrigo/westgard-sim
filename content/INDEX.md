# Content Folder Index

This folder contains the **editable content layer** for the Westgard QC Simulator.

## Files Overview

### 📋 Data Files (Edit These!)

| File | Purpose | Who Edits |
|------|---------|-----------|
| `scenarios.json` | Educational descriptions for each QC failure pattern | Domain experts (Beatriz) |
| `lessons.json` | Teaching materials: questions, challenges, answers | Domain experts (Beatriz) |

### 📖 Documentation

| File | Purpose | Audience |
|------|---------|----------|
| `README.md` | Comprehensive editing guide with JSON tips | Non-programmers |
| `QUICK_REFERENCE.md` | Quick cheat sheet for common edits | Non-programmers |
| `ARCHITECTURE.md` | Technical design and integration guide | Developers |
| `INDEX.md` | This file - navigation guide | Everyone |

### 🛠️ Utilities

| File | Purpose | Usage |
|------|---------|-------|
| `validate_content.py` | Schema validation script | Run after editing: `python validate_content.py` |
| `load_content.py` | Python loader for content integration | Import in Python/web code |

## Quick Navigation

**"I want to edit educational content"**  
→ Start with `QUICK_REFERENCE.md`, then edit `scenarios.json` or `lessons.json`

**"I want to understand the content structure"**  
→ Read `README.md`

**"I want to integrate content into code"**  
→ See `ARCHITECTURE.md` and use `load_content.py`

**"I want to validate my edits"**  
→ Run `python validate_content.py`

## Content Schema

### scenarios.json
Each scenario has 5 fields:
- `display_name` - Title shown in UI
- `short_description` - Brief summary
- `educational_message` - Main learning objective
- `pattern_hint` - Visual pattern description
- `common_mistake` - Typical misconception

### lessons.json
Each lesson has 3 fields:
- `guiding_questions` - List of pre-exploration questions
- `challenge_prompt` - Active learning task
- `reveal_text` - Detailed explanation

## Scenario Keys

The content layer covers these four scenarios (aligned with web exports):

| Key | Display Name | Export File |
|-----|--------------|-------------|
| `normal` | Normal Operation | `outputs/web_data/normal.json` |
| `bias` | Bias Shift | `outputs/web_data/bias.json` |
| `drift` | Progressive Drift | `outputs/web_data/drift.json` |
| `imprecision` | Imprecision Increase | `outputs/web_data/imprecision.json` |

## Validation Status

✅ All files created  
✅ JSON syntax valid  
✅ All scenario keys present  
✅ All required fields populated  
✅ Aligned with web exports

## Need Help?

1. **For editing questions**: See `README.md` or `QUICK_REFERENCE.md`
2. **For validation errors**: Run `python validate_content.py` and read error messages
3. **For technical questions**: See `ARCHITECTURE.md` or contact dev team
4. **For educational content**: Consult domain experts

---

**Last Updated**: Content layer created with 4 scenarios (normal, bias, drift, imprecision)  
**Maintained By**: Domain experts (content) + Development team (structure)
