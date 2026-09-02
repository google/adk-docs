import com.google.adk.sessions.InMemorySessionService;
import com.google.adk.sessions.Session;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.ConcurrentHashMap;

String sessionId = "123";
String appName = "example-app"; // Example app name
String userId = "example-user"; // Example user id
ConcurrentMap<String, Object> initialState = new ConcurrentHashMap<>(Map.of("newKey", "newValue"));
InMemorySessionService exampleSessionService = new InMemorySessionService();

// Create Session
Session exampleSession = exampleSessionService.createSession(
    appName, userId, initialState, Optional.of(sessionId)).blockingGet();
System.out.println("Session created successfully.");

System.out.println("--- Examining Session Properties ---");
System.out.printf("ID (`id`): %s%n", exampleSession.id());
System.out.printf("Application Name (`appName`): %s%n", exampleSession.appName());
System.out.printf("User ID (`userId`): %s%n", exampleSession.userId());
System.out.printf("State (`state`): %s%n", exampleSession.state());
System.out.println("------------------------------------");


// Clean up (optional for this example)
var unused = exampleSessionService.deleteSession(appName, userId, sessionId);