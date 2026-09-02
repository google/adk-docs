import mlflow
from mlflow.genai.scorers.google_adk import (
    ToolTrajectory,
    ResponseMatch,
    ResponseEvaluation,
)

eval_data = [
    {
        "inputs": {"query": "Find me a flight to Paris next Friday."},
        "outputs": "I found 3 flights to Paris on Friday: AA101, DL202, UA303.",
        "expectations": {
            "expected_tool_calls": [
                {"name": "search_flights", "args": {"destination": "Paris"}},
            ],
            "actual_tool_calls": [
                {"name": "search_flights", "args": {"destination": "Paris"}},
            ],
            "expected_response": "Here are flights to Paris next Friday.",
        },
    },
]

results = mlflow.genai.evaluate(
    data=eval_data,
    scorers=[
        ToolTrajectory(match_type="EXACT", threshold=0.5),
        ResponseMatch(threshold=0.5),
        ResponseEvaluation(threshold=0.6),
    ],
)