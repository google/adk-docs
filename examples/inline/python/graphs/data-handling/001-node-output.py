from google.adk import Event

def my_function_node(node_input: str):
    output_value = node_input.upper()
    return Event(output=output_value) # "THE RESULT"