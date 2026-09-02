from mlflow.genai.scorers.google_adk import Hallucination, ResponseEvaluation

response_eval = ResponseEvaluation(
    model="gemini-flash-latest",
    threshold=0.5,
    num_samples=5,
)

hallucination = Hallucination(model="gemini-flash-latest", threshold=0.5)