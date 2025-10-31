# Type Annotations for Function Tools

## Overview

When using function tools with ADK and Gemini API, **proper type annotations are critical** for schema generation. Incomplete or incorrect type annotations cause schema validation failures (400 Bad Request errors) that prevent your agents from executing tools.

This guide explains ADK-specific type annotation requirements, common pitfalls, and working patterns validated with Gemini 2.0 Flash.

!!! warning "Common Pain Point"
    The most common issue: using bare `list` or `dict` instead of `List[T]` or `Dict[K, V]`. This causes "missing 'items' field" schema errors and hours of debugging.

## Why Type Annotations Matter

### Schema Generation Process

When you define a function tool, ADK automatically generates an OpenAPI schema for the Gemini API:

```python
from typing import List

def process_items(items: List[str]) -> str:
    """Process a list of item names."""
    return f"Processed {len(items)} items"
```

ADK converts this to an OpenAPI schema:

```json
{
  "name": "process_items",
  "description": "Process a list of item names.",
  "parameters": {
    "type": "object",
    "properties": {
      "items": {
        "type": "array",
        "items": {"type": "string"}
      }
    }
  }
}
```

### What Goes Wrong

**Incomplete type annotations** cause schema generation to fail:

```python
# ❌ Bare list - schema validation fails
def process_items(items: list) -> str:
    pass

# Error: "array missing 'items' field in schema"
```

**Result**: 400 Bad Request from Gemini API, agent execution blocked.

## Required Patterns

### ✅ What Works Today

Use the `typing` module for **all collection types**, even in Python 3.10+:

```python
from typing import List, Dict, Set, Tuple, Optional, Union, Any

# ✅ Correct patterns
def my_tool(
    items: List[str],              # List of strings
    config: Dict[str, Any],        # Dictionary
    unique_ids: Set[int],          # Set of integers
    coords: Tuple[float, float],   # Fixed-size tuple
    optional_param: Optional[str] = None  # Optional string
) -> Dict[str, List[str]]:
    pass
```

### ❌ What Doesn't Work

Avoid these patterns - they cause schema validation failures:

```python
# ❌ Bare collections fail
def bad_tool(
    items: list,        # Missing item type
    config: dict,       # Missing key/value types
    values: set,        # Missing element type
    data: tuple         # Missing element types
) -> list:
    pass

# ❌ Modern union syntax not supported
def broken_tool(
    count: int | None = None  # Fails to parse
) -> str | None:              # Fails to parse
    pass

# ❌ PEP 585 syntax not supported
def wont_work(
    items: list[str]  # Python 3.9+ syntax, but ADK doesn't support it
) -> dict[str, int]:
    pass
```

## Common Errors and Fixes

### Error 1: Missing 'items' Field

**Symptom**: Schema validation fails with "array missing 'items' field"

```python
# ❌ Problem
def process_equipment(equipment: list) -> dict:
    """Parse equipment from P&ID."""
    pass

# Error during schema generation:
# "array missing 'items' field in schema"
```

**Solution**: Specify the list element type

```python
# ✅ Fix
from typing import List, Dict, Any

def process_equipment(equipment: List[dict]) -> Dict[str, Any]:
    """Parse equipment from P&ID."""
    return {"processed": len(equipment)}
```

**Real-world impact**: This exact error cost our team 3+ hours during production development.

### Error 2: Failed to Parse Parameter

**Symptom**: "Failed to parse the parameter name: int | None = None"

```python
# ❌ Problem
def calculate_total(
    discount: int | None = None  # Modern Python 3.10+ syntax
) -> float:
    pass

# Error:
# "ValueError: Failed to parse the parameter name: int | None = None"
```

**Solution**: Use `Optional` from `typing`

```python
# ✅ Fix
from typing import Optional

def calculate_total(
    discount: Optional[int] = None
) -> float:
    base = 100.0
    if discount:
        base -= discount
    return base
```

**Why**: ADK's function parser doesn't yet support PEP 604 union syntax (`X | Y`).

**Status**: This is a [known limitation](https://github.com/google/adk-python/issues/1634). Use `Optional` and `Union` until support is added.

### Error 3: 400 INVALID_ARGUMENT from Gemini

**Symptom**: 400 Bad Request with "INVALID_ARGUMENT" after tool execution

```python
# ❌ Problem
def analyze_data(
    config: dict  # Bare dict causes schema issues
) -> dict:
    pass

# Error from Gemini API:
# "400 INVALID_ARGUMENT: Please ensure function call turn comes
#  immediately after a user turn or function response turn"
```

**Solution**: Use fully-typed `Dict`

```python
# ✅ Fix
from typing import Dict, Any

def analyze_data(
    config: Dict[str, Any]
) -> Dict[str, Any]:
    return {"status": "analyzed", "config": config}
```

**Why**: Bare `dict` creates incomplete schemas that confuse the LLM's conversation flow.

## Python Version Compatibility

### Python 3.9-3.10

**Must use `typing` module** for all generic types:

```python
from typing import List, Dict, Set, Tuple, Optional, Union

def my_tool(items: List[str]) -> Dict[str, Any]:
    pass
```

**Note**: While Python 3.9+ supports `list[str]` syntax (PEP 585), **ADK does not yet support it** for schema generation.

### Python 3.11+

**Still use `typing` module** for ADK tools:

```python
# ✅ Recommended for ADK
from typing import List, Dict
def my_tool(items: List[str]) -> Dict[str, int]:
    pass

# ❌ Works in pure Python, fails in ADK
def broken_tool(items: list[str]) -> dict[str, int]:
    pass
```

**Why**: ADK schema generation hasn't migrated to PEP 585 built-in generics yet.

## Complex Type Patterns

### Nested Structures

```python
from typing import List, Dict, Any

def process_hierarchical_data(
    equipment: List[Dict[str, Any]],      # List of dictionaries
    categories: Dict[str, List[str]]      # Dict mapping to lists
) -> Dict[str, List[Dict[str, Any]]]:
    """
    equipment: List of equipment dictionaries with any structure
    categories: Dictionary mapping category names to equipment IDs
    returns: Dictionary grouping equipment by category
    """
    grouped = {}
    for category, ids in categories.items():
        grouped[category] = [e for e in equipment if e.get('id') in ids]
    return grouped
```

### Union Types (Multiple Allowed Types)

```python
from typing import Union, List

def flexible_search(
    query: Union[str, int, List[str]]  # Accept multiple types
) -> List[Dict[str, Any]]:
    """Search by text query, ID, or list of keywords."""
    if isinstance(query, list):
        # Handle list of keywords
        return search_by_keywords(query)
    elif isinstance(query, int):
        # Handle ID lookup
        return [lookup_by_id(query)]
    else:
        # Handle text search
        return search_by_text(query)
```

### Optional Parameters with Defaults

```python
from typing import Optional, List, Dict, Any

def search_equipment(
    query: str,                           # Required parameter
    filters: Optional[List[str]] = None,  # Optional list
    max_results: Optional[int] = 10,      # Optional with default
    include_metadata: bool = False        # Boolean with default
) -> List[Dict[str, Any]]:
    """
    query: Required search term
    filters: Optional list of filter criteria
    max_results: Maximum number of results (default 10)
    include_metadata: Whether to include full metadata (default False)
    """
    if filters is None:
        filters = []

    results = perform_search(query, filters)
    results = results[:max_results]

    if not include_metadata:
        results = [strip_metadata(r) for r in results]

    return results
```

## Enum Support

### Current Limitation

Native Python `Enum` types are [not yet fully supported](https://github.com/google/adk-python/issues/2733) in ADK function tool schemas.

### Workaround: Use Literal

Use `typing.Literal` for constrained string values:

```python
from typing import Literal, Dict, Any

def set_priority(
    task_id: str,
    priority: Literal["low", "medium", "high", "critical"]
) -> Dict[str, Any]:
    """
    Set task priority to one of the allowed values.

    Args:
        task_id: Task identifier
        priority: Must be one of: low, medium, high, critical
    """
    return {
        "task_id": task_id,
        "priority": priority,
        "updated": True
    }
```

**Benefits**:
- Type checkers validate the literal values
- Schema generation includes the enum constraint
- Clear API contract for LLM

**Status**: Track [#2733](https://github.com/google/adk-python/issues/2733) and [#398](https://github.com/google/adk-python/issues/398) for native Enum support.

## Validation and Testing

### Type Checker Integration

Use `mypy` to catch type errors during development:

```bash
# Install mypy
pip install mypy

# Run type checking
mypy your_agent.py
```

**Example**:

```python
from typing import List

def process_items(items: List[str]) -> str:
    return ", ".join(items)

# mypy catches type mismatches:
process_items([1, 2, 3])  # Error: List[int] incompatible with List[str]
process_items(["a", "b"])  # ✅ OK
```

### Testing Tool Schema Generation

Verify schemas generate correctly:

```python
import pytest
from google.adk.agents import LlmAgent
from typing import List, Dict, Any

def test_tool_schema_generation():
    """Verify tool schema generates without errors."""

    def my_tool(items: List[str], config: Dict[str, Any]) -> str:
        return f"Processed {len(items)} items"

    # Agent instantiation fails if schema generation fails
    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="test_agent",
        tools=[my_tool]
    )

    assert agent is not None

    # Optionally verify tool is registered
    tool_names = [t.name for t in agent.tools]
    assert "my_tool" in tool_names
```

### Runtime Testing

Test with actual LLM calls:

```python
from google.adk.agents import LlmAgent
from typing import List

def calculate_sum(numbers: List[int]) -> int:
    """Calculate the sum of numbers."""
    return sum(numbers)

agent = LlmAgent(
    model="gemini-2.0-flash",
    name="calculator",
    instruction="You calculate sums using the calculate_sum tool.",
    tools=[calculate_sum]
)

# Test with a prompt that should trigger the tool
response = agent.run("What is the sum of 5, 10, and 15?")

# Verify tool was called and response is correct
assert "30" in response.content
```

## Migration Checklist

When updating existing tools with incomplete annotations:

- [ ] **Import typing module**: Add `from typing import List, Dict, Optional, Any, Union`
- [ ] **Replace bare `list`**: Change all `list` to `List[T]` with appropriate type parameter
- [ ] **Replace bare `dict`**: Change all `dict` to `Dict[K, V]`
- [ ] **Replace bare `set`**: Change all `set` to `Set[T]`
- [ ] **Replace bare `tuple`**: Change all `tuple` to `Tuple[T, ...]`
- [ ] **Fix union syntax**: Replace `X | None` with `Optional[X]`
- [ ] **Fix union types**: Replace `X | Y` with `Union[X, Y]`
- [ ] **Add Any for unknown types**: Use `Any` for truly dynamic values
- [ ] **Update docstrings**: Document the expected types
- [ ] **Run type checker**: Execute `mypy` to verify correctness
- [ ] **Test with Gemini**: Verify schema generation works
- [ ] **Update tests**: Ensure unit tests reflect type changes

### Migration Example

**Before**:
```python
def analyze_document(
    doc_path: str,
    options: dict = None
) -> dict:
    """Analyze a document with options."""
    if options is None:
        options = {}
    return {"status": "analyzed", "path": doc_path}
```

**After**:
```python
from typing import Optional, Dict, Any

def analyze_document(
    doc_path: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze a document with optional configuration.

    Args:
        doc_path: Path to document file
        options: Optional dictionary of analysis options

    Returns:
        Dictionary with analysis results
    """
    if options is None:
        options = {}
    return {"status": "analyzed", "path": doc_path, "options": options}
```

## Quick Reference Card

```python
# ====================================================================
# ADK Function Tool Type Annotation Cheat Sheet
# ====================================================================

from typing import List, Dict, Set, Tuple, Optional, Union, Any, Literal

# BASIC TYPES (built-in types work fine)
def tool_basic(
    text: str,              # ✅ String
    count: int,             # ✅ Integer
    value: float,           # ✅ Float
    flag: bool              # ✅ Boolean
) -> str:
    pass

# CONTAINER TYPES (MUST use typing module)
def tool_containers(
    items: List[str],                  # ✅ List of strings
    config: Dict[str, Any],            # ✅ Dictionary (flexible values)
    unique_ids: Set[int],              # ✅ Set of integers
    coords: Tuple[float, float],       # ✅ Fixed 2-element tuple
    nested: List[Dict[str, Any]]       # ✅ Nested structures
) -> Dict[str, List[str]]:
    pass

# OPTIONAL PARAMETERS
def tool_optional(
    required: str,                         # ✅ Required parameter
    optional: Optional[str] = None,        # ✅ Optional string
    optional_list: Optional[List[str]] = None,  # ✅ Optional list
    with_default: Optional[int] = 10       # ✅ Optional with default
) -> Optional[Dict[str, Any]]:             # ✅ Optional return
    pass

# MULTIPLE ALLOWED TYPES
def tool_union(
    flexible: Union[str, int],                # ✅ String OR integer
    multi: Union[str, int, List[str]]         # ✅ Multiple alternatives
) -> Union[str, Dict[str, Any]]:
    pass

# CONSTRAINED VALUES (Enum workaround)
def tool_literal(
    priority: Literal["low", "medium", "high"],  # ✅ Limited choices
    status: Literal["pending", "active", "done"] # ✅ Predefined values
) -> Dict[str, str]:
    pass

# COMMON MISTAKES - DON'T DO THESE
def tool_mistakes(
    items: list,                 # ❌ Bare list fails
    config: dict,                # ❌ Bare dict fails
    optional: int | None,        # ❌ Modern union syntax not supported
    values: list[str],           # ❌ PEP 585 syntax not supported
    data: set                    # ❌ Bare set fails
) -> tuple:                      # ❌ Bare tuple fails
    pass
```

## Troubleshooting

### Schema Validation Fails

**Symptom**: "array missing 'items' field" or similar schema errors

**Check**:
1. Are you using bare `list`, `dict`, `set`, or `tuple`?
2. Have you imported from `typing`?
3. Did you specify type parameters like `List[str]`?

**Fix**: Add proper type annotations with `typing` module.

### Parameter Parsing Fails

**Symptom**: "Failed to parse the parameter name: X | None"

**Check**:
1. Are you using modern union syntax (`|`) instead of `Union` or `Optional`?
2. Is your Python version 3.10+ but ADK doesn't support the syntax yet?

**Fix**: Use `Optional[X]` instead of `X | None`.

### 400 Errors from Gemini

**Symptom**: "400 INVALID_ARGUMENT" during or after tool execution

**Check**:
1. Are your type annotations complete and correct?
2. Does the tool return the type specified in the return annotation?
3. Are you using bare `dict` or `list` in return types?

**Fix**: Ensure all types are fully specified with `typing` module.

## Additional Resources

- [Function Tools Overview](../tools/function-tools.md) - Core function tool documentation
- [ADK GitHub Issues](https://github.com/google/adk-python/issues) - Known limitations and feature requests

## Related Issues

- [#1634](https://github.com/google/adk-python/issues/1634) - Modern union syntax not supported
- [#2925](https://github.com/google/adk-python/issues/2925) - Documentation/implementation mismatch for `| None`
- [#2733](https://github.com/google/adk-python/issues/2733) - Native Enum support
- [#398](https://github.com/google/adk-python/issues/398) - Enum types in function parameters

---

**Last Updated**: 2025-10-18
**Validated With**: Gemini 2.0 Flash, Python 3.9-3.12
**Status**: Active workarounds documented, tracking issues for native support
