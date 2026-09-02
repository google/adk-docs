import { InMemorySessionService } from "@google/adk";

// Create a simple session to examine its properties
const tempService = new InMemorySessionService();
const exampleSession = await tempService.createSession({
    appName: "my_app",
    userId: "example_user",
    state: {"initial_key": "initial_value"} // State can be initialized
});

console.log("--- Examining Session Properties ---");
console.log(`ID ('id'):                ${exampleSession.id}`);
console.log(`Application Name ('appName'): ${exampleSession.appName}`);
console.log(`User ID ('userId'):         ${exampleSession.userId}`);
console.log(`State ('state'):           ${JSON.stringify(exampleSession.state)}`); // Note: Only shows initial state here
console.log(`Events ('events'):         ${JSON.stringify(exampleSession.events)}`); // Initially empty
console.log(`Last Update ('lastUpdateTime'): ${exampleSession.lastUpdateTime}`);
console.log("---------------------------------");

// Clean up (optional for this example)
const finalStatus = await tempService.deleteSession({
    appName: exampleSession.appName,
    userId: exampleSession.userId,
    sessionId: exampleSession.id
});
console.log("The final status of temp_service - ", finalStatus);