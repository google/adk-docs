async for event in runner.run_async(user_id='u_123', session_id='s_abc',
    invocation_id='invocation-123'):
  print(event)

# When new_message is set to a function response,
# we are trying to resume a long running function.