import com.google.adk.kt.sessions.InMemorySessionService
import com.google.adk.kt.sessions.SessionKey

val sessionId = "123"
val appName = "example-app"
val userId = "example-user"
val initialState = mapOf("newKey" to "newValue")
val sessionService = InMemorySessionService()

// Create Session
val exampleSession = sessionService.createSession(
    key = SessionKey(appName, userId, sessionId),
    state = initialState
)
println("Session created successfully.")

println("--- Examining Session Properties ---")
println("ID (`id`):                ${exampleSession.key.id}")
println("Application Name (`appName`): ${exampleSession.key.appName}")
println("User ID (`userId`):         ${exampleSession.key.userId}")
println("State (`state`):           ${exampleSession.state}")
println("------------------------------------")

// Clean up (optional for this example)
sessionService.deleteSession(exampleSession.key)