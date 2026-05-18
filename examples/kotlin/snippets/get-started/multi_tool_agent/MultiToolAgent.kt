package agents.multitool

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
import java.text.Normalizer
import java.time.ZoneId
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.util.Scanner

class MultiToolService {
    @Tool
    fun getCurrentTime(
        @Param("The name of the city for which to retrieve the current time") city: String,
    ): Map<String, String> {
        val normalizedCity =
            Normalizer.normalize(city, Normalizer.Form.NFD)
                .trim()
                .lowercase()
                .replace(Regex("(\\p{IsM}+|\\p{IsP}+)"), "")
                .replace(Regex("\\s+"), "_")

        val zoneId =
            ZoneId.getAvailableZoneIds()
                .firstOrNull { it.lowercase().endsWith("/$normalizedCity") }

        return if (zoneId != null) {
            val time =
                ZonedDateTime.now(ZoneId.of(zoneId))
                    .format(DateTimeFormatter.ofPattern("HH:mm"))
            mapOf(
                "status" to "success",
                "report" to "The current time in $city is $time.",
            )
        } else {
            mapOf(
                "status" to "error",
                "report" to "Sorry, I don't have timezone information for $city.",
            )
        }
    }

    @Tool
    fun getWeather(
        @Param("The name of the city for which to retrieve the weather report") city: String,
    ): Map<String, String> {
        return if (city.lowercase() == "new york") {
            mapOf(
                "status" to "success",
                "report" to "The weather in New York is sunny with a temperature of " +
                    "25 degrees Celsius (77 degrees Fahrenheit).",
            )
        } else {
            mapOf(
                "status" to "error",
                "report" to "Weather information for $city is not available.",
            )
        }
    }
}

fun main() =
    runBlocking {
        val model = Gemini(apiKey = "YOUR_API_KEY", name = "gemini-2.5-flash")

        val agent =
            LlmAgent(
                name = "multi_tool_agent",
                model = model,
                description = "Agent to answer questions about the time and weather in a city.",
                instruction =
                    Instruction(
                        "You are a helpful agent who can answer user questions about the " +
                            "time and weather in a city.",
                    ),
                tools = MultiToolService().generatedTools(),
            )

        val sessionService = InMemorySessionService()
        val runner =
            InMemoryRunner(
                agent = agent,
                appName = "multi_tool_app",
                sessionService = sessionService,
            )

        val userId = "student"
        val sessionId = "session_1"

        sessionService.createSession(SessionKey("multi_tool_app", userId, sessionId))

        val scanner = Scanner(System.`in`)
        while (true) {
            print("\nYou > ")
            val userInput = scanner.nextLine()
            if (userInput.lowercase() == "quit") break

            val userContent = Content(role = Role.USER, parts = listOf(Part(text = userInput)))
            val events = runner.runAsync(userId, sessionId, newMessage = userContent).toList()

            print("\nAgent > ")
            for (event in events) {
                event.content?.parts?.forEach { part ->
                    part.text?.let { print(it) }
                }
            }
            println()
        }
    }
