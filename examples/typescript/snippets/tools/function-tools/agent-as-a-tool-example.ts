/**
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import {
  AgentTool,
  InMemoryRunner,
  LlmAgent,
} from '@google/adk';
import {Part, createUserContent} from '@google/genai';

/**
 * This example demonstrates how to use an agent as a tool.
 */
async function main() {
  // Define the summarization agent that will be used as a tool
  const summaryAgent = new LlmAgent({
    name: 'summary_agent',
    model: 'gemini-2.5-flash',
    description: 'Agent to summarize text',
    instruction:
      'You are an expert summarizer. Please read the following text and provide a concise summary.',
  });

  // Define the main agent that uses the summarization agent as a tool.
  // skipSummarization is set to true, so the main_agent will directly output
  // the result from the summary_agent without further processing.
  const mainAgent = new LlmAgent({
    name: 'main_agent',
    model: 'gemini-2.5-flash',
    instruction:
      "You are a helpful assistant. When the user provides a text, use the 'summary_agent' tool to generate a summary. Always forward the user's message exactly as received to the 'summary_agent' tool, without modifying or summarizing it yourself. Present the response from the tool to the user.",
    tools: [new AgentTool({agent: summaryAgent, skipSummarization: true})],
  });

  const appName = 'agent-as-a-tool-app';
  const runner = new InMemoryRunner({agent: mainAgent, appName});

  const longText = `Quantum computing represents a fundamentally different approach to computation, 
leveraging the bizarre principles of quantum mechanics to process information. Unlike classical computers 
that rely on bits representing either 0 or 1, quantum computers use qubits which can exist in a state of superposition - effectively 
being 0, 1, or a combination of both simultaneously. Furthermore, qubits can become entangled, 
meaning their fates are intertwined regardless of distance, allowing for complex correlations. This parallelism and 
interconnectedness grant quantum computers the potential to solve specific types of incredibly complex problems - such 
as drug discovery, materials science, complex system optimization, and breaking certain types of cryptography - far 
faster than even the most powerful classical supercomputers could ever achieve, although the technology is still largely in its developmental stages.`;

  // Create the session before running the agent
  await runner.sessionService.createSession({
    appName,
    userId: 'user1',
    sessionId: 'session1',
  });

  // Run the agent with the long text to summarize
  const events = runner.runAsync({
    userId: 'user1',
    sessionId: 'session1',
    newMessage: createUserContent(longText),
  });

  // Print the final response from the agent
  console.log('Agent Response:');
  for await (const event of events) {
    if (event.content?.parts?.length) {
      const responsePart = event.content.parts.find((p: Part) => p.functionResponse);
      if (responsePart && responsePart.functionResponse) {
        console.log(responsePart.functionResponse.response);
      }
    }
  }
}

main();