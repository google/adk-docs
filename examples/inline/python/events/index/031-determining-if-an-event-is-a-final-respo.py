# Pseudocode: Handling final responses in application (Python)
# full_response_text = ""
# async for event in runner.run_async(...):
#     # Accumulate streaming text if needed...
#     if event.partial and event.content and event.content.parts and event.content.parts[0].text:
#         full_response_text += event.content.parts[0].text
#
#     # Check if it's a final, displayable event
#     if event.is_final_response():
#         print("\n--- Final Output Detected ---")
#         if event.content and event.content.parts and event.content.parts[0].text:
#              # If it's the final part of a stream, use accumulated text
#              final_text = full_response_text + (event.content.parts[0].text if not event.partial else "")
#              print(f"Display to user: {final_text.strip()}")
#              full_response_text = "" # Reset accumulator
#         elif event.actions and event.actions.skip_summarization and event.get_function_responses():
#              # Handle displaying the raw tool result if needed
#              response_data = event.get_function_responses()[0].response
#              print(f"Display raw tool result: {response_data}")
#         elif hasattr(event, 'long_running_tool_ids') and event.long_running_tool_ids:
#              print("Display message: Tool is running in background...")
#         else:
#              # Handle other types of final responses if applicable
#              print("Display: Final non-textual response or signal.")