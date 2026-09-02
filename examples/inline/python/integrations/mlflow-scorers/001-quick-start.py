from mlflow.genai.scorers.google_adk import ToolTrajectory

scorer = ToolTrajectory(match_type="EXACT", threshold=0.5)
feedback = scorer(
    inputs="Book a flight to Paris",
    outputs="Booked flight AA123 to Paris",
    expectations={
        "expected_tool_calls": [
            {"name": "search_flights", "args": {"destination": "Paris"}},
            {"name": "book_flight", "args": {"flight_id": "AA123"}},
        ],
        "actual_tool_calls": [
            {"name": "search_flights", "args": {"destination": "Paris"}},
            {"name": "book_flight", "args": {"flight_id": "AA123"}},
        ],
    },
)

print(feedback.value)            # "yes" or "no"
print(feedback.metadata["score"]) # 1.0 on a full match