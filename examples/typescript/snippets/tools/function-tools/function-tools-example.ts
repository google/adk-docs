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
import {Content, Part, createUserContent} from '@google/genai';
import {
  stringifyContent,
  FunctionTool,
  InMemoryRunner,
  LlmAgent,
} from '@google/adk';
import {z} from 'zod';

// Define the function to get the stock price
async function getStockPrice({ticker}: {ticker: string}): Promise<Record<string, unknown>> {
  console.log(`Getting stock price for ${ticker}`);
  // In a real-world scenario, you would fetch the stock price from an API
  const price = (Math.random() * 1000).toFixed(2);
  return {price: `$${price}`};
}

async function main() {
  // Define the schema for the tool's parameters using Zod
  const getStockPriceSchema = z.object({
    ticker: z.string().describe('The stock ticker symbol to look up.'),
  });

  // Create a FunctionTool from the function and schema
  const stockPriceTool = new FunctionTool({
    name: 'getStockPrice',
    description: 'Gets the current price of a stock.',
    parameters: getStockPriceSchema,
    execute: getStockPrice,
  });

  // Define the agent that will use the tool
  const stockAgent = new LlmAgent({
    name: 'stock_agent',
    model: 'gemini-2.5-flash',
    instruction: 'You can get the stock price of a company.',
    tools: [stockPriceTool],
  });

  // Create a runner for the agent
  const runner = new InMemoryRunner({agent: stockAgent});

  // Create a new session
  const session = await runner.sessionService.createSession({
    appName: runner.appName,
    userId: 'test-user',
  });

  const userContent: Content = createUserContent('What is the stock price of GOOG?');

  // Run the agent and get the response
  const response = [];
  for await (const event of runner.runAsync({
    userId: session.userId,
    sessionId: session.id,
    newMessage: userContent,
  })) {
    response.push(event);
  }

  // Print the final response from the agent
  const finalResponse = response[response.length - 1];
  if (finalResponse?.content?.parts?.length) {
    console.log(stringifyContent(finalResponse));
  }
}

main();

