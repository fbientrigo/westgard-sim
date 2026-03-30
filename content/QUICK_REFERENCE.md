# Quick Reference: Content Editing for Beatriz

## Before You Start

✅ **You can safely edit:** All text in `scenarios.json` and `lessons.json`  
❌ **Never change:** The words `normal`, `bias`, `drift`, `imprecision` (scenario keys)  
❌ **Never change:** Field names like `display_name`, `educational_message`, etc.

---

## Step-by-Step Editing

### 1. Open the File
Use any text editor (VS Code, Notepad++, or even Notepad)

### 2. Make Your Changes
Edit the text between the quotes:

```json
"display_name": "Put your new text here"
```

### 3. Save the File
Save as `.json` (not `.txt`)

### 4. Validate Your Changes
Open Command Prompt or PowerShell:
```bash
cd C:\path\to\westgard\content
python validate_content.py
```

### 5. Check the Output
✅ **Green checkmarks** = You're good!  
❌ **Red X marks** = Fix the errors and try again

---

## Common Edits

### Fixing a Typo

**Before:**
```json
"educational_message": "When the QC proces is working correctly..."
```

**After:**
```json
"educational_message": "When the QC process is working correctly..."
```

### Improving Clarity

**Before:**
```json
"pattern_hint": "Look for scatter"
```

**After:**
```json
"pattern_hint": "Look for random scatter around the mean with most values within ±2SD"
```

### Adding a Question

**Before:**
```json
"guiding_questions": [
  "Question 1?",
  "Question 2?"
]
```

**After:**
```json
"guiding_questions": [
  "Question 1?",
  "Question 2?",
  "Question 3?"
]
```

⚠️ **Remember:** Add a comma after Question 2, but NOT after the last question!

---

## JSON Syntax Reminders

| Rule | Example |
|------|---------|
| Use double quotes | `"text"` not `'text'` |
| Add commas between items | `"field1": "value",` |
| NO comma after last item | Last item has no comma |
| Brackets for lists | `["item1", "item2"]` |
| Braces for objects | `{"key": "value"}` |

---

## What If Something Goes Wrong?

### Error: "Invalid JSON"
- Check for missing quotes, commas, or brackets
- Use https://jsonlint.com/ to find the error
- Compare your file to the original in Git

### Error: "Missing fields"
- Make sure all required fields are present
- Check spelling of field names (exact match required)

### Error: "Field cannot be empty"
- Every field needs text
- Even "TODO" or "placeholder" is better than empty

### Still Stuck?
1. Save your changes somewhere safe
2. Ask the development team
3. Or revert to the last working version: `git checkout content/scenarios.json`

---

## Files You'll Edit

| File | What It Contains |
|------|------------------|
| `scenarios.json` | Main educational descriptions |
| `lessons.json` | Questions, challenges, and explanations |

---

## Quick Validation Check

After editing, always run:
```bash
python validate_content.py
```

Look for:
```
✓ scenarios.json: Valid
✓ lessons.json: Valid

✓ All content files are valid!
```

---

## Tips for Success

1. **Make small changes** - Edit one scenario at a time
2. **Validate often** - Run the validator after each change
3. **Use version control** - Commit working versions
4. **Test before publishing** - Preview in staging environment
5. **Ask for help** - When in doubt, ask the dev team

---

## Scenario Quick Reference

| Key | Display Name | What It Shows |
|-----|--------------|---------------|
| `normal` | Normal Operation | Healthy baseline (no problems) |
| `bias` | Bias Shift | Sudden jump in mean (run 11+) |
| `drift` | Progressive Drift | Gradual upward trend (run 11+) |
| `imprecision` | Imprecision Increase | Wider scatter (run 11+) |

---

## Need Help?

📧 Contact the development team  
📖 Read the full `README.md` for details  
🏗️ See `ARCHITECTURE.md` for technical background

---

**Remember:** The validation script is your friend! Use it every time. 🎯
