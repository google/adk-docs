---
catalog_title: ADK Connector
catalog_description: Expose ADK agents as chatbots on Telegram, Discord, WhatsApp, and more with cross-device session sync
catalog_icon: /integrations/assets/adk-connector.png
catalog_tags: ["connectors"]
---

# ADK Connector

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[ADK Connector](https://github.com/Harshk133/adk-connector) is a plug-and-play
toolkit that wraps any ADK agent and exposes it as a chatbot on popular
messaging channels such as Telegram, Discord, and WhatsApp. A Slack connector
is planned. See the project repository for the current list of supported
channels.

By adding just a few lines of code, you can bridge the gap between local
development, testing, and production messaging platforms, with native support
for database-backed cross-device session synchronization.

## Key features

- **Minimal wrapper**: Deploy any `google-adk` agent (Python or
  JavaScript/TypeScript) to messaging channels with virtually zero code changes.
- **Auto tunnel and webhook server**: Set `tunnel=True` on the Telegram connector
  to automatically spin up a local HTTP server and a Cloudflare Tunnel with zero
  configuration, an automatic precompiled binary downloader, and port-collision
  avoidance.
- **Cross-device session sync**: Chat on Telegram, Discord, or WhatsApp, then
  inspect and continue the exact same conversation inside the ADK Web UI
  (`adk web`).
- **Automatic database engine setup**: Transparently spins up an asynchronous
  SQLite backend to record session states, events, and tool invocations.
- **Local persistent mapping**: Uses a secure, local JSON mapping engine so
  restarting the bot never breaks session IDs or active chats.
- **Unified multi-platform deployment**: Run one agent across Telegram, Discord,
  and WhatsApp concurrently with `ConnectorManager`.
- **Multi-agent support**: Built-in double-import safety and automatic
  resolution of prompt context variables across parent and sub-agents.

## Use cases

- **Multi-channel deployment**: Instantly deploy your ADK agents (written in
  Python or JavaScript/TypeScript) as chatbots on Telegram, Discord, WhatsApp,
  and other supported messaging channels.
- **Cross-device session synchronization**: Seamlessly transition conversations.
  Chat on Telegram, Discord, or WhatsApp, then inspect, debug, and continue the
  exact same conversation inside the local ADK Web UI (`adk web`).
- **Resilient state management**: Automatically configures an asynchronous
  SQLite backend to record session states, tool invocations, and user
  interactions.
- **Production-like local testing**: Use Telegram webhook tunneling for lower
  latency and production parity without manual tunnel setup.
- **Robust multi-agent workflows**: Double-import safety and automatic
  resolution of prompt context variables across parent and sub-agents.

## Prerequisites

- Python 3.10+ or Node.js 18+
- A Gemini API Key (set as `GOOGLE_API_KEY`)
- Messaging channel credentials:
    - **Telegram**: A Telegram account and a Bot Token from
      [BotFather](https://t.me/BotFather)
    - **Discord**: A Discord developer account, a Discord Bot Token, and client
      ID
    - **WhatsApp**: Node.js (>= 18) and npm installed on your system. The
      connector uses a lightweight Node.js child process and sets up its
      internal JavaScript dependencies on first run. No additional Python
      dependencies are required.

## Installation

You can install the connectors for either Python or JavaScript / TypeScript
depending on your ADK project.

=== "Python"

    Install the base package:

    ```bash
    pip install adk-connector
    ```

    Or install specific platform connectors:

    ```bash
    pip install "adk-connector[telegram]"
    pip install "adk-connector[discord]"
    pip install "adk-connector[whatsapp]"
    pip install "adk-connector[all]"
    ```

    To enable database-backed cross-device session synchronization (e.g. `adk
    web` UI), also install the ADK DB components:

    ```bash
    pip install "google-adk[db]"
    ```

=== "JavaScript / TypeScript"

    ```bash
    npm install adk-connector-js
    ```

    Or with pnpm:

    ```bash
    pnpm install adk-connector-js
    ```

## Environment configuration

Create a `.env` file in your project root and configure the required environment
variables:

```env
# Required for agent reasoning
GOOGLE_API_KEY=your_gemini_api_key_here

# Required for Telegram bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_USER_ID=your_telegram_user_id_here

# Required for Discord bot
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_USER_ID=your_discord_user_id_here

# Optional for WhatsApp session sync with adk web
WHATSAPP_USER_ID=your_whatsapp_user_id_here
```

`TELEGRAM_USER_ID`, `DISCORD_USER_ID`, and `WHATSAPP_USER_ID` are required when
using cross-device session synchronization with `adk web`.

## Use with agent

Here is how you can wrap your existing Google ADK agents and launch them on
messaging channels.

=== "Python (Telegram)"

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

    Run the script:

    ```bash
    python agent.py
    ```

=== "Python (Discord)"

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

        # 4. Start the bot
        connector.start()
    ```

    Run the script:

    ```bash
    python agent.py
    ```

=== "Python (WhatsApp)"

    The WhatsApp connector uses a lightweight Node.js child process running the
    `@whiskeysockets/baileys` library. Ensure Node.js (>= 18) and npm are
    installed before running.

    ```python
    from google.adk.agents.llm_agent import Agent
    from adk_connectors.whatsapp import WhatsAppWebConnector

    # 1. Define your standard Google ADK Agent
    assistant = Agent(
        model='gemini-flash-latest',
        name='my_assistant',
        instruction='You are a helpful assistant.'
    )

    if __name__ == "__main__":
        # 2. Bind the connector
        connector = WhatsAppWebConnector(
            agent=assistant
        )

        # 3. Start the bot
        connector.start()
    ```

    Run the script:

    ```bash
    python agent.py
    ```

    On first run, a QR code is printed in your terminal. Open WhatsApp on your
    phone, go to **Settings** > **Linked Devices** > **Link a Device**, and scan
    the QR code. Once paired, test the bot by sending a message like `"hi"` in
    the **Message Yourself** chat or by having a contact message your phone.

=== "JavaScript / TypeScript (Telegram)"

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

    Run the script:

    ```bash
    npx tsx agent.ts
    ```

## Telegram webhook tunneling

By default, the Telegram connector uses long-polling to retrieve messages. For
faster response times, lower latency, and production parity, you can switch to
webhooks using the auto-tunnel feature:

```python
connector = TelegramConnector(
    token=token,
    agent=assistant,
    tunnel=True,  # Spins up HTTP server and Cloudflare tunnel automatically
    webhook_secret="optional-webhook-secret-token"  # Verify Telegram payloads securely
)
```

When `tunnel=True`, the connector:

1. Downloads the `cloudflared` binary automatically if it is not on your PATH
   and caches it in `~/.adk/bin/`.
2. Starts a background HTTP web server (built on `aiohttp`) on your machine.
3. Finds the next free port if the default port (`8000`) is already occupied.
4. Spawns a Cloudflare tunnel (using `trycloudflare.com`) to expose your local
   port securely to the internet.
5. Registers the dynamic HTTPS endpoint with Telegram.
6. Deletes the webhook registration and shuts down tunnel processes cleanly when
   the bot stops.

## Multi-platform deployment

To deploy one agent across multiple platforms simultaneously (for example,
Telegram, Discord, and WhatsApp), use `ConnectorManager` as a central hub.
Initialize platform connectors without an `agent` argument, pass them into
`ConnectorManager`, and run them together with `start_sync()`:

```python
import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from adk_connectors import ConnectorManager
from adk_connectors.telegram import TelegramConnector
from adk_connectors.discord import DiscordConnector
from adk_connectors.whatsapp import WhatsAppConnector

load_dotenv()

assistant = Agent(
    model='gemini-flash-latest',
    name='my_assistant',
    instruction='You are a helpful assistant.'
)

if __name__ == "__main__":
    platforms = []

    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if telegram_token:
        platforms.append(
            TelegramConnector(token=telegram_token, streaming=True, tunnel=True)
        )

    discord_token = os.getenv("DISCORD_BOT_TOKEN")
    if discord_token:
        platforms.append(
            DiscordConnector(token=discord_token, streaming=True)
        )

    platforms.append(
        WhatsAppConnector(port=3001)
    )

    manager = ConnectorManager(
        agent=assistant,
        platforms=platforms,
        session_management_across_device=True,
        dev_user_id=os.getenv("TELEGRAM_USER_ID")
    )

    manager.start_sync()
```

## Session sync with `adk web`

For Python setups, you can sync Telegram, Discord, or WhatsApp chat history
directly with the local ADK Web UI by mapping your provider-specific user ID to
the local development environment.

1. In your code, set `session_management_across_device=True` and pass your user
   ID:

    === "Telegram"

        ```python
        connector = TelegramConnector(
            token=token,
            agent=assistant,
            session_management_across_device=True,
            dev_user_id=os.getenv("TELEGRAM_USER_ID")
        )
        ```

    === "Discord"

        ```python
        connector = DiscordConnector(
            token=token,
            agent=assistant,
            session_management_across_device=True,
            dev_user_id=os.getenv("DISCORD_USER_ID")
        )
        ```

    === "WhatsApp"

        ```python
        connector = WhatsAppWebConnector(
            agent=assistant,
            session_management_across_device=True,
            dev_user_id=os.getenv("WHATSAPP_USER_ID")
        )
        ```

        Set `WHATSAPP_USER_ID` to your account phone number (for example,
        `"919421616978"`) or your account JID/LID JID.

2. Run your bot script:

    ```bash
    python agent.py
    ```

3. Run the ADK Web UI in a separate terminal:

    ```bash
    adk web .
    ```

4. Access `http://127.0.0.1:8000` to view active conversations and tool
   execution logs directly in the browser. You can chat from either your
   messaging client or the Web UI.

## Multi-agent and sub-agent support

`adk-connector` supports complex agents that delegate tasks to sub-agents (for
example, using `sub_agents=[...]` or `tools=[AgentTool(agent=...)]`).

- **No extra launcher files**: Integrate `adk-connector` directly inside your
  main `agent.py` file under `if __name__ == "__main__":`. You do not need a
  separate script such as `run_telegram.py`.
- **Auto-resolution of missing state variables**: Sub-agents often expect prompt
  context variables (for example, `{seminal_paper}`) populated by parent outputs
  from previous turns. `adk-connector` scans parent and sub-agent instructions
  for curly-brace placeholders and pre-populates them dynamically before
  executing the runner, preventing `KeyError: 'Context variable not found'`
  crashes.
- **Double-import safety**: Running multi-agent code as a script
  (`python -m package.module`) can trigger Python double-import cycles. When an
  ADK agent is instantiated twice in this cycle, Pydantic throws a validation
  error because sub-agents are assigned a parent twice. `adk-connector`
  overrides ADK parent-validation checks to allow safe duplicate parent
  resolution under import cycles.

## Supported channels

| Channel | Status |
| ------- | ------ |
| Telegram | Available |
| Discord | Available |
| WhatsApp | Available |
| Slack | Planned |

## Additional resources

- [ADK Connector GitHub Repository](https://github.com/Harshk133/adk-connector)
- [ADK Connector Python Package (PyPI)](https://pypi.org/project/adk-connector/)
- [ADK Connector JS/TS Package (NPM)](https://www.npmjs.com/package/adk-connector-js)
- [blog-writer setup demo](https://github.com/google/adk-samples/tree/main/python/agents/blog-writer)
