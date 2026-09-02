import { zespan, ZespanADKCallbackHandler } from "@zespan/sdk";
import { LlmAgent, InMemoryRunner } from "@google/adk";

zespan.init({ apiKey: process.env.ZESPAN_API_KEY! });

const handler = new ZespanADKCallbackHandler();

const agent = new LlmAgent({
  name: "weather_agent",
  model: "gemini-flash-latest",
  description: "Agent to answer weather questions.",
  instruction: "Use the available tools to find an answer.",
  tools: [getWeather],
  ...handler.callbacks,
});

const runner = new InMemoryRunner({ agent, appName: "weather_app" });

for await (const event of runner.runEphemeral({
  userId: "user",
  newMessage: { parts: [{ text: "What is the weather in New York?" }] },
})) {
  if (event.isFinalResponse()) {
    console.log(event.content.parts[0].text);
  }
}