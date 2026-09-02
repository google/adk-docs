import { zespan, instrumentADK } from "@zespan/sdk";
import { LlmAgent, InMemoryRunner } from "@google/adk";

zespan.init({ apiKey: process.env.ZESPAN_API_KEY! });

function getWeather(city: string): object {
  if (city.toLowerCase() === "new york") {
    return {
      status: "success",
      report: "The weather in New York is sunny with a temperature of 25°C.",
    };
  }
  return {
    status: "error",
    error_message: `Weather information for '${city}' is not available.`,
  };
}

const coordinator = new LlmAgent({
  name: "weather_agent",
  model: "gemini-flash-latest",
  description: "Agent to answer weather questions.",
  instruction: "Use the available tools to find an answer.",
  tools: [getWeather],
});

const runner = new InMemoryRunner({
  agent: coordinator,
  appName: "weather_app",
});

const { runner: tracedRunner } = instrumentADK({ coordinator, runner });

for await (const event of tracedRunner.runEphemeral({
  userId: "user",
  newMessage: { parts: [{ text: "What is the weather in New York?" }] },
})) {
  if (event.isFinalResponse()) {
    console.log(event.content.parts[0].text);
  }
}