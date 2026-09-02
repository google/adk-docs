from a2ui.core.parser.parser import parse_response
from a2ui.a2a import parse_response_to_parts

# Get the active catalog's validator
selected_catalog = schema_manager.get_selected_catalog()

# Option A: Manual parse + validate
response_parts = parse_response(llm_output_text)
for part in response_parts:
    if part.a2ui_json:
        selected_catalog.validator.validate(part.a2ui_json)

# Option B: One-liner that returns A2A Parts
parts = parse_response_to_parts(
    llm_output_text,
    validator=selected_catalog.validator,
    fallback_text="Here's what I found.",
)