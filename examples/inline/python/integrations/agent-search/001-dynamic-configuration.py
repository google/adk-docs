from google.genai import types
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import VertexAiSearchTool

class MyVertexAISearchTool(VertexAiSearchTool):
    def _build_vertex_ai_search_config(
        self, readonly_context: ReadonlyContext
    ) -> types.VertexAISearch:
        """Builds the VertexAISearch configuration, adding a user-specific filter."""
        config = super()._build_vertex_ai_search_config(readonly_context)
        if "user_id" in readonly_context.state:
            user_id = readonly_context.state["user_id"]
            config.filter = f'user_id: ANY("{user_id}")'
        return config