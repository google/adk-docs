// Please look at the set of requirements above, consequently export the following in your bashrc file:
// export GOOGLE_CLOUD_PROJECT=my_gcp_project
// export GOOGLE_CLOUD_LOCATION=us-central1
// export GOOGLE_API_KEY=my_api_key

import com.google.adk.sessions.VertexAiSessionService;
import java.util.UUID;

String sessionId = UUID.randomUUID().toString();
String reasoningEngineAppName = "123456789";
String userId = "u_123"; // Example user id
ConcurrentMap<String, Object> initialState = new
    ConcurrentHashMap<>(); // No initial state needed for this example

VertexAiSessionService sessionService = new VertexAiSessionService();
Session mySession =
    sessionService
        .createSession(reasoningEngineAppName, userId, initialState, Optional.of(sessionId))
        .blockingGet();