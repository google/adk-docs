package com.google.adk.kt.examples.tools

import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.tools.AgentTool
import com.google.adk.kt.tools.GoogleSearchTool

fun main() {
    val modelId = "gemini-flash-latest"

    // --8<-- [start:workaround_1]
    // Define the SearchAgent
    val searchAgent = LlmAgent(
        name = "SearchAgent",
        model = Gemini(name = modelId),
        instruction = Instruction("You're a specialist in Google Search"),
        tools = listOf(GoogleSearchTool())
    )

    // Define another agent (e.g., for specialized tasks)
    val taskAgent = LlmAgent(
        name = "TaskAgent",
        model = Gemini(name = modelId),
        instruction = Instruction("You're a specialist in performing specific tasks.")
    )

    // Define the RootAgent, which uses AgentTool to wrap SearchAgent and TaskAgent
    val rootAgent = LlmAgent(
        name = "RootAgent",
        model = Gemini(name = modelId),
        description = "Root Agent",
        tools = listOf(
            AgentTool(agent = searchAgent),
            AgentTool(agent = taskAgent)
        )
    )
    // --8<-- [end:workaround_1]

    // --8<-- [start:workaround_2]
    val bypassAgent = LlmAgent(
        name = "BypassAgent",
        model = Gemini(name = modelId),
        instruction = Instruction("You can use multiple built-in tools."),
        tools = listOf(
            GoogleSearchTool(bypassMultiToolsLimit = true)
            // other tools can be added here
        )
    )
    // --8<-- [end:workaround_2]
}
