import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini

// --- Example using a stable Gemini Flash model ---
val agentGeminiFlash = LlmAgent(
    // Use the latest stable Flash model identifier
    name = "gemini_flash_agent",
    model = Gemini(name = "gemini-flash-latest"),
    instruction = Instruction("You are a fast and helpful Gemini assistant."),
    // ... other agent parameters
)