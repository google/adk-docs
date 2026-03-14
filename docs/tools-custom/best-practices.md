# Best Practices for Function Tools

This guide provides best practices and common patterns for building robust and user-friendly function tools in ADK.

## Handling File Uploads

When building agents that process files, you often need to handle both:

1. Files uploaded directly through the chat interface
2. File paths provided as text by the user

### Problem

Without explicit handling, agents may:

- Ask for file paths even when files are already uploaded
- Fail to recognize uploaded files as attachments
- Pass incorrect parameters to parsing tools

### Solution: Flexible File Path Handling

Design your tools to accept both display names (from uploaded files) and full file paths.

???+ example "File Upload Tool Pattern"
    === "Python"
        ```python
        import os

        def parse_document(doc_path: str = "uploaded_document") -> str:
          """Parses a document (uploaded file or file path).

          Args:
            doc_path: Display name of uploaded file or full file path.

          Returns:
            Success message with output path.
          """
          # Handle both uploaded file identifiers and full paths
          if '/' in doc_path:
            # Full path provided
            run_id = os.path.basename(os.path.dirname(doc_path))
          else:
            # Uploaded file display name or simple identifier
            run_id = doc_path.replace('.', '_')

          output_path = f"output/{run_id}.xml"
          os.makedirs(os.path.dirname(output_path), exist_ok=True)

          # ... your parsing logic here

          return f"Successfully parsed document to {output_path}"
        ```

### Agent Instructions

Your agent instructions should explicitly guide the LLM on how to handle both upload methods:

???+ example "Agent Instructions for File Handling"
    === "Python"
        ```python
        from google.adk import Agent

        agent = Agent(
          name="DocumentParser",
          model="gemini-2.0-flash",
          instruction="""
          You are a document parsing agent.

          When the user provides files:
          1. If files are uploaded directly in the chat:
             - Acknowledge them by their display names
             - Call parsing tools with their display names or identifiers
             - You can identify uploaded files by their presence as attachments
          2. If file paths are provided in text:
             - Call parsing tools with the exact paths provided

          Do not ask for file paths if files are already uploaded.
          """,
          tools=[parse_document]
        )
        ```

### Why This Matters

This pattern ensures your agent gracefully handles both upload methods, providing a better user experience.

#### Example Usage

**Uploaded File**:
```
User: [Uploads: report.pdf]
      Parse this document

Agent: [Calls parse_document("report.pdf")]
```

**File Path**:
```
User: Parse the document at /path/to/reports/quarterly_report.pdf

Agent: [Calls parse_document("/path/to/reports/quarterly_report.pdf")]
```

## Type Annotations

Always use explicit type annotations for function tool parameters to ensure proper schema generation.

!!! warning "Use Explicit Types"
    Bare `list` and `dict` types can cause schema validation errors. Always specify item types.

???+ example "Proper Type Annotations"
    === "❌ Invalid"
        ```python
        def process_items(items: list) -> str:
            """This causes Gemini schema validation errors."""
            pass
        ```
    === "✅ Valid"
        ```python
        from typing import List

        def process_items(items: List[str]) -> str:
            """Properly typed for Gemini schema generation."""
            pass
        ```

## Tool Naming

Use clear, descriptive names for your tools that indicate their purpose:

- ✅ `get_weather_forecast`
- ✅ `parse_pdf_document`
- ✅ `calculate_tax_liability`
- ❌ `tool1`
- ❌ `process`
- ❌ `do_thing`

## Docstrings

Provide comprehensive docstrings with `Args` and `Returns` sections. The LLM uses these to understand when and how to use your tool.

???+ example "Well-Documented Tool"
    === "Python"
        ```python
        def get_weather(city: str, unit: str = "celsius") -> dict:
          """Retrieves current weather for a specified city.

          This function fetches real-time weather data including temperature,
          humidity, and conditions for the requested city.

          Args:
            city: The name of the city (e.g., "London", "New York").
            unit: Temperature unit, either "celsius" or "fahrenheit".
                  Defaults to "celsius".

          Returns:
            A dictionary containing:
              - temperature: Current temperature as a float
              - humidity: Humidity percentage as an integer
              - conditions: Weather conditions as a string
              - timestamp: UTC timestamp of the reading

          Example:
            >>> get_weather("Paris", "celsius")
            {
              "temperature": 18.5,
              "humidity": 65,
              "conditions": "Partly cloudy",
              "timestamp": "2025-10-18T10:30:00Z"
            }
          """
          # ... implementation
        ```

## Error Handling

Return clear, actionable error messages that help the LLM understand what went wrong and how to fix it.

???+ example "Error Handling"
    === "❌ Poor Error Handling"
        ```python
        def validate_email(email: str) -> bool:
            if "@" not in email:
                raise ValueError("Invalid")
            return True
        ```
    === "✅ Good Error Handling"
        ```python
        def validate_email(email: str) -> dict:
            """Validates an email address format.

            Args:
              email: The email address to validate.

            Returns:
              A dictionary with 'valid' (bool) and 'message' (str) fields.
            """
            if "@" not in email:
                return {
                    "valid": False,
                    "message": f"Email '{email}' is missing '@' symbol. "
                               "Expected format: user@domain.com"
                }

            if "." not in email.split("@")[1]:
                return {
                    "valid": False,
                    "message": f"Email '{email}' domain is missing a TLD. "
                               "Expected format: user@domain.com"
                }

            return {
                "valid": True,
                "message": f"Email '{email}' is valid."
            }
        ```

## Return Values

Structure return values consistently and include enough context for the LLM to provide useful responses to the user.

???+ tip "Structured Returns"
    Return dictionaries with clear field names rather than plain strings or tuples when you have multiple pieces of information to convey.

    === "❌ Unclear Return"
        ```python
        def search_products(query: str) -> str:
            return "Found 3 items: item1, item2, item3"
        ```
    === "✅ Structured Return"
        ```python
        def search_products(query: str) -> dict:
            """Searches for products matching the query.

            Returns:
              A dictionary containing:
                - count: Number of products found
                - products: List of product dictionaries
                - query: The original search query
            """
            return {
                "count": 3,
                "products": [
                    {"id": 1, "name": "item1", "price": 19.99},
                    {"id": 2, "name": "item2", "price": 29.99},
                    {"id": 3, "name": "item3", "price": 39.99}
                ],
                "query": query
            }
        ```

## See Also

- [Function Tools](function-tools.md) - Learn how to create function tools
- [Long Running Tools](function-tools.md#long-run-tool) - Handle tools that take time to execute
- [Tool Performance](performance.md) - Optimize tool execution
