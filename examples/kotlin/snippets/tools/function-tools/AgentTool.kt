package com.google.adk.kt.examples.tools

// --8<-- [start:agent_tool]
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.tools.AgentTool
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Part
import kotlinx.coroutines.runBlocking

fun main() = runBlocking {
    val appName = "summary_agent"
    val userId = "user1234"

    // Define a specialized agent to be used as a tool
    val summaryAgent = LlmAgent(
        name = "summary_agent",
        model = Gemini(name = "gemini-flash-latest"),
        description = "Agent to summarize text",
        instruction = Instruction("You are an expert summarizer. Please read the following text and provide a concise summary.")
    )

    // Wrap the agent in an AgentTool with skipSummarization = true
    val summaryTool = AgentTool(
        agent = summaryAgent,
        skipSummarization = true
    )

    // Define the root agent that uses the summary tool
    val rootAgent = LlmAgent(
        name = "root_agent",
        model = Gemini(name = "gemini-flash-latest"),
        instruction = Instruction("You are a helpful assistant. When the user provides a text, use the 'summary_agent' tool to generate a summary. Always forward the user's message exactly as received to the 'summary_agent' tool. Present the response from the tool to the user."),
        tools = listOf(summaryTool)
    )

    // Create an InMemoryRunner
    val runner = InMemoryRunner(agent = rootAgent, appName = appName)

    val sessionId = "session_001"

    val longText = """
        Quantum computing represents a fundamentally different approach to computation, 
        leveraging the bizarre principles of quantum mechanics to process information. Unlike classical computers 
        that rely on bits representing either 0 or 1, quantum computers use qubits which can exist in a state of superposition - effectively 
        being 0, 1, or a combination of both simultaneously. Furthermore, qubits can become entangled, 
        meaning their fates are intertwined regardless of distance, allowing for complex correlations. This parallelism and 
        interconnectedness grant quantum computers the potential to solve specific types of incredibly complex problems - such 
        as drug discovery, materials science, complex system optimization, and breaking certain types of cryptography - far 
        faster than even the most powerful classical supercomputers could ever achieve, although the technology is still largely in its developmental stages.
    """.trimIndent()

    val userMessage = Content(parts = listOf(Part(text = longText)))

    // Run the agent and collect events
    runner.runAsync(userId = userId, sessionId = sessionId, newMessage = userMessage).collect { event ->
        if (event.isFinalResponse) {
            val finalResponse = event.content?.parts?.firstOrNull()?.text
            println("Agent Response: $finalResponse")
        }
    }
}
// --8<-- [end:agent_tool]
