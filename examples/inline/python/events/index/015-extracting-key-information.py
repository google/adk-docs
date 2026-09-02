responses = event.get_function_responses()
if responses:
    for response in responses:
        tool_name = response.name
        result_dict = response.response # The dictionary returned by the tool
        print(f"  Tool Result: {tool_name} -> {result_dict}")