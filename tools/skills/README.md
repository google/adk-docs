# Skills Validation Tools

This directory contains validation tools for ADK skills documentation to ensure accuracy and prevent drift from the actual ADK API.

## Tools Overview

### 1. `validate_snippets.py` (Existing)
**Purpose**: Syntax and import validation for Python/Bash code snippets

**What it validates**:
- ✅ Python syntax via `ast.parse()`
- ✅ Import statements resolve correctly
- ✅ Bash `adk` commands are valid

**What it doesn't validate**:
- ❌ API signatures match actual ADK
- ❌ Code actually runs
- ❌ Runtime behavior

### 2. `validate_callback_signatures.py` (New)
**Purpose**: Validate callback function signatures against actual ADK API

**What it validates**:
- ✅ Callback parameter names and types
- ✅ Return type annotations
- ✅ Parameter order matches ADK source

**Example**:
```bash
# Validate all skills
python tools/skills/validate_callback_signatures.py

# Validate specific file
python tools/skills/validate_callback_signatures.py skills/adk-cheatsheet/references/python.md
```

**Expected signatures** (extracted from ADK source):
```python
# Agent lifecycle
def before_agent_callback(callback_context: CallbackContext) -> None
def after_agent_callback(callback_context: CallbackContext) -> genai_types.Content | None

# Model interaction
def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> LlmResponse | None
def after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> LlmResponse | None

# Tool execution
def before_tool_callback(tool: BaseTool, args: dict, tool_context: ToolContext) -> dict | None
def after_tool_callback(tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict) -> dict | None
```

### 3. `test_callback_snippets.py` (New)
**Purpose**: Integration test - actually runs callbacks against ADK

**What it validates**:
- ✅ Callbacks execute without signature errors
- ✅ ADK runtime accepts the signatures
- ✅ Full integration with actual ADK library

**Example**:
```bash
python tools/skills/test_callback_snippets.py
```

### 4. `validate_links.py` (Existing)
**Purpose**: Validate hyperlinks in skills documentation

## CI/CD Integration

The validation runs automatically via `.github/workflows/skills-check.yaml`:

### On Pull Requests
- Validates changed `skills/**/*.md` files
- Runs all validators on modified files only
- Blocks merge if validation fails

### On Schedule (Weekly)
- Validates ALL skills documentation
- Runs every Wednesday at 3 AM UTC
- Catches drift as ADK evolves

## Common Issues and Fixes

### Issue: Callback signature mismatch
**Symptom**: `validate_callback_signatures.py` fails
**Cause**: Documentation shows incorrect parameter names/types
**Fix**: Update markdown with correct signatures from ADK source

**Example Fix**:
```diff
# WRONG ❌
-async def before_tool_callback(ctx: CallbackContext, tool_name: str, args: dict)

# CORRECT ✅
+async def before_tool_callback(tool: BaseTool, args: dict, tool_context: ToolContext)
```

### Issue: Import errors in CI
**Symptom**: `validate_snippets.py` fails on imports
**Cause**: Missing dependency or typo in import path
**Fix**: Check `requirements.txt` and import paths

### Issue: Integration test skipped
**Symptom**: `test_callback_snippets.py` shows `[SKIP]`
**Cause**: API credentials not available (expected in CI)
**Fix**: No action needed - this is normal in CI environment

## How the Validation Prevents API Drift

### The Problem (Before)
```
┌─────────────────────────┐
│ ADK Source (CORRECT)    │  Changes in ADK releases
│ /google/adk/            │
└─────────────────────────┘
         ↓
         ↓  No validation
         ↓
┌─────────────────────────┐
│ Skills Docs (OUTDATED)  │  Manual docs drift over time
│ skills/*.md             │
└─────────────────────────┘
```

### The Solution (After)
```
┌─────────────────────────┐
│ ADK Source (CORRECT)    │
│ /google/adk/            │
└─────────────────────────┘
         ↓
         ↓  ✅ validate_callback_signatures.py
         ↓  ✅ test_callback_snippets.py
         ↓
┌─────────────────────────┐
│ Skills Docs (VALIDATED) │  Weekly checks catch drift
│ skills/*.md             │
└─────────────────────────┘
```

## Maintenance

### When ADK API Changes
1. ADK releases new version with API changes
2. Weekly CI run detects signature mismatches
3. Update skills documentation to match new API
4. Validation passes ✅

### When Adding New Callbacks
1. Add callback to `EXPECTED_SIGNATURES` in `validate_callback_signatures.py`
2. Add test case to `test_callback_snippets.py`
3. Document in skills markdown
4. Validation ensures consistency ✅

## Local Development

```bash
# Install dependencies
pip install -r tools/skills/requirements.txt

# Run all validators
python tools/skills/validate_snippets.py
python tools/skills/validate_callback_signatures.py
python tools/skills/test_callback_snippets.py
python tools/skills/validate_links.py

# Run on specific file
python tools/skills/validate_callback_signatures.py skills/adk-cheatsheet/references/python.md
```
