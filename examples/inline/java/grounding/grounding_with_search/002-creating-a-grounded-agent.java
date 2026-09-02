import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.VertexAiSearchTool;

// Configuration
String DATASTORE_ID = "projects/YOUR_PROJECT_ID/locations/global/collections/default_collection/dataStores/YOUR_DATASTORE_ID";

LlmAgent rootAgent = LlmAgent.builder()
    .name("vertex_search_agent")
    .model("gemini-flash-latest")
    .instruction("Answer questions using Agent Search to find information from internal documents. Always cite sources when available.")
    .description("Enterprise document search assistant with Agent Search capabilities")
    .tools(VertexAiSearchTool.builder().dataStoreId(DATASTORE_ID).build())
    .build();