// Copyright 2025 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import {BasePolicyEngine, FunctionTool, getAskUserConfirmationFunctionCalls, InMemoryRunner, LlmAgent, PolicyCheckResult, PolicyOutcome, REQUEST_CONFIRMATION_FUNCTION_CALL_NAME, SecurityPlugin, ToolCallPolicyContext} from '@google/adk';
import {Content, createUserContent, FunctionCall, FunctionResponse} from '@google/genai';
import {z} from 'zod';

interface ToolResult {
  status: 'success'|'error';
  report?: string;
  error_message?: string;
}

/**
 * Retrieves the current weather report for a specified city.
 *
 * @param city The name of the city for which to retrieve the weather
 report.
 * @returns status and result or error msg.
 */
async function get_weather({city}: {city: string}): Promise<ToolResult> {
  if (city.toLowerCase() === 'new york') {
    return {
      'status': 'success',
      'report':
          'The weather in New York is sunny with a temperature of 25 degrees Celsius (77 degrees Fahrenheit).',
    };
  } else {
    return {
      'status': 'error',
      'error_message': `Weather information for '${city}' is not available.`,
    };
  }
}

/**
 * Returns the current time in a specified city.
 *
 * @param city The name of the city for which to retrieve the current time.
 * @returns status and result or error msg.
 */
async function get_current_time({city}: {city: string}): Promise<ToolResult> {
  if (city.toLowerCase() === 'new york') {
    const tzIdentifier = 'America/New_York';
    try {
      const now = new Date();
      const report =
          `The current time in ${city} is ${now.toLocaleString('en-US', {
            timeZone: tzIdentifier
          })} ${tzIdentifier}`;
      return {'status': 'success', 'report': report};
    } catch (e) {
      return {
        'status': 'error',
        'error_message': `Error getting time for ${city}: ${e}`,
      };
    }
  } else {
    return {
      'status': 'error',
      'error_message': `Sorry, I don't have timezone information for ${city}.`,
    };
  }
}

const getWeatherTool = new FunctionTool({
  name: 'get_weather',
  description: 'Retrieves the current weather report for a specified city.',
  parameters: z.object({
    city: z.string().describe('The name of the city.'),
  }),
  execute: get_weather,
});

const getCurrentTimeTool = new FunctionTool({
  name: 'get_current_time',
  description: 'Returns the current time in a specified city.',
  parameters: z.object({
    city: z.string().describe('The name of the city.'),
  }),
  execute: get_current_time,
});

export const rootAgent = new LlmAgent({
  name: 'weather_time_agent',
  model: 'gemini-2.5-flash',
  description:
      'Agent to answer questions about the time and weather in a city.',
  instruction:
      'You are a helpful agent who can answer user questions about the time and weather in a city.',
  tools: [getWeatherTool, getCurrentTimeTool],
});

export class CustomPolicyEngine implements BasePolicyEngine {
  async evaluate(_context: ToolCallPolicyContext): Promise<PolicyCheckResult> {
    // Default permissive implementation
    return Promise.resolve({
      outcome: PolicyOutcome.CONFIRM,
      reason: 'Needs confirmation for tool call',
    });
  }
}

async function main() {
  const SEPARATOR = '-'.repeat(60);
  const userId = 'test_user';
  const appName = rootAgent.name;
  const runner = new InMemoryRunner({
    agent: rootAgent,
    appName,
    plugins: [new SecurityPlugin({policyEngine: new CustomPolicyEngine()})]
  });

  const session = await runner.sessionService.createSession({
    appName,
    userId,
  });

  const content =
      createUserContent('What is the weather in New York? And the time?');
  console.log(content);

  let confirmationCalls: FunctionCall[] = [];
  for await (const e of runner.runAsync({
    userId,
    sessionId: session.id,
    newMessage: content,
  })) {
    if (e.content?.parts?.[0]?.text) {
      console.log(`${e.author}: ${JSON.stringify(e.content, null, 2)}`);
    }
    const newConfirmationCalls = getAskUserConfirmationFunctionCalls(e);
    if (newConfirmationCalls.length > 0) {
      confirmationCalls.push(...newConfirmationCalls);
    }
  }

  while (confirmationCalls.length > 0) {
    console.log(SEPARATOR);
    console.log(
      `Confirmation requested for: ${confirmationCalls[0].name}(${JSON.stringify(confirmationCalls[0].args)})`
    );
    console.log('Simulating a user thinking for 3 seconds...');
    // Simulate a user taking time to respond before confirming.
    await new Promise((resolve) => setTimeout(resolve, 3000));

    const call = confirmationCalls.shift();
    if (!call) {
      break;
    }
    const functionResponse = new FunctionResponse();
    functionResponse.name = REQUEST_CONFIRMATION_FUNCTION_CALL_NAME;
    functionResponse.response = {
      confirmed: true,
    };
    functionResponse.id = call.id;

    const contentWithConfirmation: Content = {
      role: 'user',
      parts: [{functionResponse: functionResponse}],
    };

    console.log(
      'User has approved. Sending confirmation response:',
      JSON.stringify(contentWithConfirmation, null, 4)
    );
    console.log(SEPARATOR);

    for await (const e of runner.runAsync({
      userId,
      sessionId: session.id,
      newMessage: contentWithConfirmation,
    })) {
      if (e.content?.parts?.[0]?.text) {
        console.log(`${e.author}: ${JSON.stringify(e.content, null, 4)}`);
      }
      const newConfirmationCalls = getAskUserConfirmationFunctionCalls(e);
      if (newConfirmationCalls.length > 0) {
        confirmationCalls.push(...newConfirmationCalls);
      }
    }
  }
}

main().catch(console.error);