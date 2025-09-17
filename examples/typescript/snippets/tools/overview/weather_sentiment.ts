import { LlmAgent, FunctionTool, InMemoryRunner, isFinalResponse } from "@google/adk";
import { z } from "zod";
import { Content } from "@google/genai";

/**
 * Retrieves the current weather report for a specified city.
 */
function getWeatherReport(params: { city: string }): Record<string, any> {
    if (params.city.toLowerCase().includes("london")) {
        return {
            "status": "success",
            "report": "The current weather in London is cloudy with a " +
                "temperature of 18 degrees Celsius and a chance of rain.",
        };
    }
    if (params.city.toLowerCase().includes("paris")) {
        return {
            "status": "success",
            "report": "The weather in Paris is sunny with a temperature of 25 " +
                "degrees Celsius.",
        };
    }
    return {
        "status": "error",
        "error_message": `Weather information for '${params.city}' is not available.`,
    };
}

/**
 * Analyzes the sentiment of a given text.
 */
function analyzeSentiment(params: { text: string }): Record<string, any> {
    if (params.text.includes("cloudy") || params.text.includes("rain")) {
        return { "status": "success", "sentiment": "negative" };
    }
    if (params.text.includes("sunny")) {
        return { "status": "success", "sentiment": "positive" };
    }
    return { "status": "success", "sentiment": "neutral" };
}

async function main() {
    const weatherTool = new FunctionTool({
        name: "get_weather_report",
        description: "Retrieves the current weather report for a specified city.",
        parameters: z.object({
            city: z.string().describe("The city to get the weather for."),
        }),
        execute: getWeatherReport,
    });

    const sentimentTool = new FunctionTool({
        name: "analyze_sentiment",
        description: "Analyzes the sentiment of a given text.",
        parameters: z.object({
            text: z.string().describe("The text to analyze the sentiment of."),
        }),
        execute: analyzeSentiment,
    });

    const instruction = `
    You are a helpful assistant that first checks the weather and then analyzes
    its sentiment.

    Follow these steps:
    1. Use the ​get_weather_report​ tool to get the weather for the requested
       city.
    2. If the ​get_weather_report​ tool returns an error, inform the user about
       the error and stop.
    3. If the weather report is available, use the ​analyze_sentiment​ tool to
       determine the sentiment of the weather report.
    4. Finally, provide a summary to the user, including the weather report and
       its sentiment.
    `;

    const agent = new LlmAgent({
        name: "weather_sentiment_agent",
        instruction: instruction,
        tools: [weatherTool, sentimentTool],
        model: "gemini-2.5-flash"
    });

    const runner = new InMemoryRunner({ agent: agent, appName: "weather_sentiment_app" });

    await runner.sessionService.createSession({
        appName: "weather_sentiment_app",
        userId: "user1",
        sessionId: "session1"
    });

    const newMessage: Content = {
        role: "user",
        parts: [{ text: "What is the weather in London?" }],
    };

    for await (const event of runner.run({
        userId: "user1",
        sessionId: "session1",
        newMessage: newMessage,
    })) {
        if (isFinalResponse(event) && event.content?.parts) {
            const text = event.content.parts.map(p => p.text).join('').trim();
            if (text) {
                console.log(text);
            }
        }
    }
}

main();