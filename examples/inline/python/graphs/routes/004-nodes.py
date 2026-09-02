from google.adk import Event

def my_function_node(node_input: str):
    input_text_modified = node_input.upper()
    return Event(output=input_text_modified)