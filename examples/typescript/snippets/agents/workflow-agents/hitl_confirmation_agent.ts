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

/**
 * A custom policy engine that enforces a confirmation step for tool calls.
 * The `evaluate` method is called by the `SecurityPlugin` before any tool is
 * executed. By returning `PolicyOutcome.CONFIRM`, we instruct the plugin to
 * pause execution and request user confirmation. In a real application, this
 * method could contain logic to decide which tools need confirmation.
 */
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
  // The SecurityPlugin is added to the runner's plugins. It intercepts tool
  // calls and uses the provided `policyEngine` to evaluate them.
  const runner = new InMemoryRunner({
    agent: rootAgent,
    appName,
    plugins: [new SecurityPlugin({policyEngine: new CustomPolicyEngine()})]
  });

  const session = await runner.sessionService.createSession({
    appName,
    userId,
  });

  const content = createUserContent('What is the weather in New York? And the time?');

  let confirmationCalls: FunctionCall[] = [];
  // First run: The agent will decide to call one or more tools. The
  // `SecurityPlugin` intercepts these calls, consults our `CustomPolicyEngine`,
  // and sees the `CONFIRM` outcome. It then generates a special function call
  // instead of executing the actual tool.
  for await (const e of runner.runAsync({
    userId,
    sessionId: session.id,
    newMessage: content,
  })) {
    if (e.content?.parts?.[0]?.text) {
      console.log(`${e.author}: ${JSON.stringify(e.content, null, 2)}`);
    }
    // We use this helper to extract any confirmation requests from the event.
    const newConfirmationCalls = getAskUserConfirmationFunctionCalls(e);
    if (newConfirmationCalls.length > 0) {
      confirmationCalls.push(...newConfirmationCalls);
    }
  }

  // This loop represents the application's logic for handling confirmation
  // requests. It iterates through each request, simulates user approval, and
  // sends the confirmation back to the agent. This allows the `SecurityPlugin`
  // to proceed with the originally intended tool call.
  while (confirmationCalls.length > 0) {
    console.log(SEPARATOR);
    console.log(
      `Confirmation requested for: ${confirmationCalls[0].name}(${JSON.stringify(confirmationCalls[0].args)})`
    );

    const call = confirmationCalls.shift();
    if (!call) {
      break;
    }
    // To approve the request, we create a FunctionResponse for the special confirmation request.
    // The `name` of this response must match the constant `REQUEST_CONFIRMATION_FUNCTION_CALL_NAME`
    // and the response must indicate confirmation.
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

    // Second run: We send the confirmation response back to the agent. The
    // `SecurityPlugin` receives this, recognizes it as an approval for the
    // pending tool call, and proceeds to execute the original tool.
    // The agent then gets the real tool result and continues.
    for await (const e of runner.runAsync({
      userId,
      sessionId: session.id,
      newMessage: contentWithConfirmation,
    })) {
      if (e.content?.parts?.[0]?.text) {
        console.log(`${e.author}: ${JSON.stringify(e.content, null, 4)}`);
      }
      // Check if this second run resulted in another confirmation request (for
      // the next tool in a sequence).
      const newConfirmationCalls = getAskUserConfirmationFunctionCalls(e);
      if (newConfirmationCalls.length > 0) {
        confirmationCalls.push(...newConfirmationCalls);
      }
    }
  }
}

main().catch(console.error);