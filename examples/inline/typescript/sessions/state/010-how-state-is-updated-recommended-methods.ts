import { LlmAgent, Runner, InMemorySessionService, isFinalResponse } from "@google/adk";
import { Content } from "@google/genai";

// Define agent with outputKey
const greetingAgent = new LlmAgent({
    name: "Greeter",
    model: "gemini-flash-latest",
    instruction: "Generate a short, friendly greeting.",
    outputKey: "last_greeting" // Save response to state['last_greeting']
});

// --- Setup Runner and Session ---
const appName = "state_app";
const userId = "user1";
const sessionId = "session1";
const sessionService = new InMemorySessionService();
const runner = new Runner({
    agent: greetingAgent,
    appName: appName,
    sessionService: sessionService
});
const session = await sessionService.createSession({
    appName,
    userId,
    sessionId
});
console.log(`Initial state: ${JSON.stringify(session.state)}`);

// --- Run the Agent ---
// Runner handles calling appendEvent, which uses the outputKey
// to automatically create the stateDelta.
const userMessage: Content = { parts: [{ text: "Hello" }] };
for await (const event of runner.runAsync({
    userId,
    sessionId,
    newMessage: userMessage
})) {
    if (isFinalResponse(event)) {
      console.log("Agent responded."); // Response text is also in event.content
    }
}

// --- Check Updated State ---
const updatedSession = await sessionService.getSession({ appName, userId, sessionId });
console.log(`State after agent run: ${JSON.stringify(updatedSession?.state)}`);
// Expected output might include: {"last_greeting":"Hello there! How can I help you today?"}