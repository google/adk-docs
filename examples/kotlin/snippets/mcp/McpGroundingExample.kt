package com.google.adk.kt.examples.mcp

import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.tools.mcp.McpConnectionParameters
import com.google.adk.kt.tools.mcp.McpToolset

// --8<-- [start:maps_grounding]
/**
 * Creating an agent that uses Google Maps Grounding Lite via Streamable HTTP.
 */
fun createMapsGroundingAgent(apiKey: String) {
    val mapsToolset =
        McpToolset.McpToolsetConfig(
            streamableHttpConnectionParams =
                McpConnectionParameters.StreamableHttp(
                    url = "https://mapstools.googleapis.com/mcp",
                    headers =
                        mapOf(
                            "X-Goog-Api-Key" to apiKey,
                            "Content-Type" to "application/json",
                            "Accept" to "application/json, text/event-stream",
                        ),
                ),
        ).toToolset()

    val travelAgent =
        LlmAgent(
            name = "travel_planner_agent",
            model = Gemini(name = "gemini-flash-latest"),
            description = "A helpful assistant for planning travel routes.",
            instruction = Instruction("Help the user plan their travel routes."),
            toolsets = listOf(mapsToolset),
        )
}
// --8<-- [end:maps_grounding]
