from google.genai import types

run_config = RunConfig(
    session_resumption=types.SessionResumptionConfig()
)