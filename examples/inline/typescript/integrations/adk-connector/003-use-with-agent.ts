import { LlmAgent } from '@google/adk';
import { TelegramConnector } from 'adk-connector-js';
import dotenv from 'dotenv';

dotenv.config();

// 1. Define your standard Google ADK Agent
export const rootAgent = new LlmAgent({
  name: 'my_assistant',
  model: 'gemini-flash-latest',
  instruction: 'You are a helpful assistant.'
});

// 2. Launch the Telegram Connector under script entrypoint
if (import.meta.url === `file://${process.argv[1]}` || process.argv[1]?.endsWith('agent.ts')) {
  const connector = new TelegramConnector({
    token: process.env.TELEGRAM_BOT_TOKEN!,
    agent: rootAgent
  });

  connector.start();
}