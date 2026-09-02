import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.tools.VertexAiSearchTool

// Configuration
val DATASTORE_ID =
    "projects/YOUR_PROJECT_ID/locations/global/collections/default_collection/dataStores/YOUR_DATASTORE_ID"

val rootAgent =
    LlmAgent(
        name = "vertex_search_agent",
        model = Gemini(name = "gemini-flash-latest"),
        instruction =
            Instruction(
                "Answer questions using Agent Search to find information from internal " +
                    "documents. Always cite sources when available.",
            ),
        description = "Enterprise document search assistant with Agent Search capabilities",
        tools = listOf(VertexAiSearchTool(dataStoreId = DATASTORE_ID)),
    )