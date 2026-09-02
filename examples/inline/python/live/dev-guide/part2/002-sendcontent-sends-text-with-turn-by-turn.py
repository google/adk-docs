content = types.Content(parts=[types.Part(text=json_message["text"])])
live_request_queue.send_content(content)