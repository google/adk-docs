from google.adk.agents import LlmAgent
from google.adk.tools.load_artifacts_tool import LoadArtifactsTool

root_agent = LlmAgent(
    name="artifact_reader",
    model="gemini-flash-latest",
    instruction=(
        "Answer questions about available user files. "
        "Call load_artifacts before answering when you need file contents."
    ),
    tools=[
        LoadArtifactsTool(),
    ],
)