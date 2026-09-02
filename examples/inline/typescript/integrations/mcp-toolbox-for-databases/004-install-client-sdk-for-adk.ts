import {InMemoryRunner, LlmAgent} from '@google/adk';
import {Content} from '@google/genai';
import {ToolboxClient} from '@toolbox-sdk/adk'

const toolboxClient = new ToolboxClient("http://127.0.0.1:5000");
const loadedTools = await toolboxClient.loadToolset();

export const rootAgent = new LlmAgent({
  name: 'weather_time_agent',
  model: 'gemini-flash-latest',
  description:
    'Agent to answer questions about the time and weather in a city.',
  instruction:
    'You are a helpful agent who can answer user questions about the time and weather in a city.',
  tools: loadedTools,
});

async function main() {
  const userId = 'test_user';
  const appName = rootAgent.name;
  const runner = new InMemoryRunner({agent: rootAgent, appName});
  const session = await runner.sessionService.createSession({
    appName,
    userId,
  });

  const prompt = 'What is the weather in New York? And the time?';
  const content: Content = {
    role: 'user',
    parts: [{text: prompt}],
  };
  console.log(content);
  for await (const e of runner.runAsync({
    userId,
    sessionId: session.id,
    newMessage: content,
  })) {
    if (e.content?.parts?.[0]?.text) {
      console.log(`${e.author}: ${JSON.stringify(e.content, null, 2)}`);
    }
  }
}

main().catch(console.error);