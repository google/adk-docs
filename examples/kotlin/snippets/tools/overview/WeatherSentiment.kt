/*
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.google.adk.kt.examples.tools.overview

// --8<-- [start:full_code]

import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.annotations.Param
import com.google.adk.kt.annotations.Tool
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.sessions.InMemorySessionService
import com.google.adk.kt.sessions.SessionKey
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Part
import com.google.adk.kt.types.Role
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking

private const val APP_NAME = "weather_sentiment_agent"
private const val USER_ID = "user1234"
private const val SESSION_ID = "1234"

class WeatherSentimentTools {
    /**
     * Retrieves the current weather report for a specified city.
     *
     * Returns a map with a "status" key ("success" or "error"), plus a "report"
     * with the weather details on success or an "error_message" on failure.
     */
    @Tool
    fun getWeatherReport(
        @Param("The city to retrieve the weather report for.") city: String,
    ): Map<String, String> =
        when (city.lowercase()) {
            "london" ->
                mapOf(
                    "status" to "success",
                    "report" to
                        "The current weather in London is cloudy with a temperature " +
                        "of 18 degrees Celsius and a chance of rain.",
                )
            "paris" ->
                mapOf(
                    "status" to "success",
                    "report" to
                        "The weather in Paris is sunny with a temperature of " +
                        "25 degrees Celsius.",
                )
            else ->
                mapOf(
                    "status" to "error",
                    "error_message" to "Weather information for '$city' is not available.",
                )
        }

    /**
     * Analyzes the sentiment of the given text.
     *
     * Returns a map with a "sentiment" ("positive", "negative" or "neutral") and
     * a "confidence" score.
     */
    @Tool
    fun analyzeSentiment(
        @Param("The text to analyze.") text: String,
    ): Map<String, Any> {
        val lowered = text.lowercase()
        return when {
            "good" in lowered || "sunny" in lowered ->
                mapOf("sentiment" to "positive", "confidence" to 0.8)
            "rain" in lowered || "bad" in lowered ->
                mapOf("sentiment" to "negative", "confidence" to 0.7)
            else -> mapOf("sentiment" to "neutral", "confidence" to 0.6)
        }
    }
}

fun main() =
    runBlocking {
        // The instruction names each tool and says how to handle its return values,
        // including chaining one tool's output into the next.
        val weatherSentimentAgent =
            LlmAgent(
                name = "weather_sentiment_agent",
                model = Gemini(name = "gemini-flash-latest"),
                instruction =
                    Instruction(
                        """
                        You are a helpful assistant that provides weather information
                        and analyzes the sentiment of user feedback.

                        If the user asks about the weather in a specific city, use the
                        getWeatherReport tool. If it returns a "success" status, provide
                        the report to the user. If it returns an "error" status, tell the
                        user the information is unavailable and ask for another city.

                        After providing a weather report, if the user gives feedback on
                        the weather, use the analyzeSentiment tool to understand their
                        sentiment, then briefly acknowledge it.
                        """.trimIndent(),
                    ),
                tools = WeatherSentimentTools().generatedTools(),
            )

        val sessionService = InMemorySessionService()
        val runner =
            InMemoryRunner(
                agent = weatherSentimentAgent,
                appName = APP_NAME,
                sessionService = sessionService,
            )
        sessionService.createSession(SessionKey(APP_NAME, USER_ID, SESSION_ID))

        val query = "weather in london?"
        println("User Query: $query")
        val userContent = Content(role = Role.USER, parts = listOf(Part(text = query)))

        val events =
            runner.runAsync(
                userId = USER_ID,
                sessionId = SESSION_ID,
                newMessage = userContent,
            ).toList()

        for (event in events) {
            if (event.isFinalResponse) {
                println("Agent Response: ${event.content?.parts?.firstOrNull()?.text}")
            }
        }
    }
// --8<-- [end:full_code]
