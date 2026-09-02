# Exclude None values for smaller payloads (with camelCase field names)
event_json = event.model_dump_json(exclude_none=True, by_alias=True)

# Custom exclusions (e.g., skip large binary audio)
event_json = event.model_dump_json(
    exclude={'content': {'parts': {'__all__': {'inline_data'}}}},
    by_alias=True
)

# Include only specific fields
event_json = event.model_dump_json(
    include={'content', 'author', 'turn_complete', 'interrupted'},
    by_alias=True
)

# Pretty-printed JSON (for debugging)
event_json = event.model_dump_json(indent=2, by_alias=True)