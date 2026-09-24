# ADK Connector

Supported in ADKPythonTypeScript

[ADK Connector](https://github.com/Harshk133/adk-connector) is a plug-and-play toolkit that wraps any ADK agent and exposes it as a chatbot on popular messaging channels such as Telegram and Discord. See the project repository for the current list of supported channels.

By adding just a few lines of code, you can bridge the gap between local development, testing, and production messaging platforms, with native support for database-backed cross-device session synchronization.

## Use cases

- **Multi-Channel Deployment**: Instantly deploy your ADK agents (written in Python or JavaScript/TypeScript) as chatbots on supported messaging channels like Telegram and Discord.
- **Cross-Device Session Synchronization**: Seamlessly transition conversations. Chat on Telegram or Discord, then inspect, debug, and continue the exact same conversation inside the local ADK Web UI (`adk web`).
- **Resilient State Management**: Automatically configures an asynchronous SQLite backend to record session states, tool invocations, and user interactions.
- **Robust Multi-Agent Workflows**: Double-import safety and automatic resolution of prompt context variables across parent and sub-agents.

## Prerequisites

- Python 3.10+ or Node.js 18+
- A Gemini API Key (set as `GOOGLE_API_KEY`)
- Messaging channel credentials:
  - **Telegram**: A Telegram account and a Bot Token from BotFather
  - **Discord**: A Discord developer account, a Discord Bot Token, and client ID

## Installation

You can install the connectors for either Python or JavaScript / TypeScript depending on your ADK project.

```bash
pip install adk-connector
```

To enable database-backed cross-device session synchronization (e.g. `adk web` UI), also install the ADK DB components:

```bash
pip install "google-adk[db]"
```

```bash
npm install adk-connector-js
```

## Use with agent

Here is how you can wrap your existing Google ADK agents and launch them on messaging channels.

```python
import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from adk_connectors.telegram import TelegramConnector

# Load environment variables
load_dotenv()

# 1. Define your standard Google ADK Agent
assistant = Agent(
    model='gemini-flash-latest',
    name='my_assistant',
    instruction='You are a helpful assistant.'
)

if __name__ == "__main__":
    # 2. Retrieve your Telegram Bot Token
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    # 3. Bind the connector
    connector = TelegramConnector(
        token=token,
        agent=assistant
    )

    # 4. Start polling
    connector.start()
```

```python
import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from adk_connectors.discord import DiscordConnector

# Load environment variables
load_dotenv()

# 1. Define your standard Google ADK Agent
assistant = Agent(
    model='gemini-flash-latest',
    name='my_assistant',
    instruction='You are a helpful assistant.'
)

if __name__ == "__main__":
    # 2. Retrieve your Discord Bot Token
    token = os.getenv("DISCORD_BOT_TOKEN")

    # 3. Bind the connector
    connector = DiscordConnector(
        token=token,
        agent=assistant
    )

    # 4. Start the bot!
    connector.start()
```

```typescript
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
```

## Session sync with `adk web`

For Python setups, you can sync Telegram or Discord chat history directly with the local ADK Web UI by mapping your provider-specific user ID to the local development environment.

1. In your code, set `session_management_across_device=True` and pass your user ID:

   ```python
   connector = TelegramConnector(
       token=token,
       agent=assistant,
       session_management_across_device=True,  # Spin up DB & mapping persistence
       dev_user_id=os.getenv("TELEGRAM_USER_ID") # Syncs this ID to the "user" Web UI namespace
   )
   ```

   ```python
   connector = DiscordConnector(
       token=token,
       agent=assistant,
       session_management_across_device=True,  # Spin up DB & mapping persistence
       dev_user_id=os.getenv("DISCORD_USER_ID")  # Syncs this ID to the "user" Web UI namespace
   )
   ```

1. Run your bot script:

   ```bash
   python agent.py
   ```

1. Run the ADK Web UI in a separate terminal:

   ```bash
   adk web .
   ```

1. Access `http://127.0.0.1:8000` to view active conversations and tool execution logs directly in the browser.

## Additional resources

- [ADK Connector GitHub Repository](https://github.com/Harshk133/adk-connector)
- [ADK Connector Python Package (PyPI)](https://pypi.org/project/adk-connector/)
- [ADK Connector JS/TS Package (NPM)](https://www.npmjs.com/package/adk-connector-js)
