import {Content, Part} from '@google/genai';
import {
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

  // Define the schema for the tool's return value using Zod
  const getStockPriceResponseSchema = z.object({
      price: z.string().describe('The stock price.'),
  });

  // Create a FunctionTool from the function and schema
  const stockPriceTool = new FunctionTool({
    name: 'getStockPrice',
    description: 'Gets the current price of a stock.',
    parameters: getStockPriceSchema,
    returnType: getStockPriceResponseSchema,
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

  const userContent: Content = {
    role: 'user',
    parts: [{text: 'What is the stock price of GOOG?'},],
  };

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
  if (finalResponse?.content?.parts) {
    console.log(finalResponse.content.parts.map((part: Part) => part.text).join(''));
  }
}

main();

