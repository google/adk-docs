import com.google.adk.kt.sessions.SessionKey
import com.google.adk.kt.sessions.VertexAiSessionService
import kotlinx.coroutines.runBlocking

// The reasoning engine is pinned here, at construction. In the other tabs
// the engine is chosen per call, through `app_name`; in Kotlin `appName`
// is never parsed for it and is only a label on the session.
val sessionService =
    VertexAiSessionService(
        project = "your-gcp-project-id",
        location = "us-central1",
        // The bare numeric engine id. A full
        // "projects/.../reasoningEngines/..." resource name is rejected;
        // project and location are separate arguments.
        reasoningEngineId = "1234567890",
    )

// Session methods are suspend functions; `runBlocking` here is the
// counterpart of the Java tab's `.blockingGet()`.
val mySession = runBlocking {
    // A null id lets the service assign one.
    sessionService.createSession(SessionKey("example-app", "u_123", id = null))
}