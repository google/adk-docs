---
catalog_title: ADK Connector
catalog_description: Expose ADK agents as chatbots on popular messaging channels with cross-device session sync
catalog_icon: /integrations/assets/adk-connector.png
catalog_tags: ["connectors"]
---

# ADK Connector

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[ADK Connector](https://github.com/Harshk133/adk-connector) is a plug-and-play
toolkit that wraps any ADK agent and exposes it as a chatbot on popular
messaging channels such as Telegram and Discord. See the project repository for
the current list of supported channels.

By adding just a few lines of code, you can bridge the gap between local
development, testing, and production messaging platforms, with native support
for database-backed cross-device session synchronization.

## Use cases

- **Multi-Channel Deployment**: Instantly deploy your ADK agents (written in
  Python or JavaScript/TypeScript) as chatbots on supported messaging channels
  like Telegram and Discord.
- **Cross-Device Session Synchronization**: Seamlessly transition conversations.
  Chat on Telegram or Discord, then inspect, debug, and continue the exact same
  conversation inside the local ADK Web UI (`adk web`).
- **Resilient State Management**: Automatically configures an asynchronous
  SQLite backend to record session states, tool invocations, and user
  interactions.
- **Robust Multi-Agent Workflows**: Double-import safety and automatic
  resolution of prompt context variables across parent and sub-agents.

## Prerequisites

- Python 3.10+ or Node.js 18+
- A Gemini API Key (set as `GOOGLE_API_KEY`)
- Messaging channel credentials:
    - **Telegram**: A Telegram account and a Bot Token from BotFather
    - **Discord**: A Discord developer account, a Discord Bot Token, and client ID

## Installation

You can install the connectors for either Python or JavaScript / TypeScript
depending on your ADK project.

=== "Python"

    ```bash
    pip install adk-connector
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

## Use with agent

Here is how you can wrap your existing Google ADK agents and launch them on
messaging channels.

=== "Python (Telegram)"

    ```python
    --8<-- "examples/inline/python/integrations/adk-connector/001-use-with-agent.py"
    ```

=== "Python (Discord)"

    ```python
    --8<-- "examples/inline/python/integrations/adk-connector/002-use-with-agent.py"
    ```

=== "JavaScript / TypeScript (Telegram)"

    ```typescript
    --8<-- "examples/inline/typescript/integrations/adk-connector/003-use-with-agent.ts"
    ```

## Session sync with `adk web`

For Python setups, you can sync Telegram or Discord chat history directly with
the local ADK Web UI by mapping your provider-specific user ID to the local
development environment.

1. In your code, set `session_management_across_device=True` and pass your user ID:

    === "Telegram"

        ```python
        --8<-- "examples/inline/python/integrations/adk-connector/004-session-sync-with-adk-web.py"
        ```

    === "Discord"

        ```python
        --8<-- "examples/inline/python/integrations/adk-connector/005-session-sync-with-adk-web.py"
        ```

2. Run your bot script:
   ```bash
   python agent.py
   ```
3. Run the ADK Web UI in a separate terminal:
   ```bash
   adk web .
   ```
4. Access `http://127.0.0.1:8000` to view active conversations and tool
   execution logs directly in the browser.

## Additional resources

- [ADK Connector GitHub Repository](https://github.com/Harshk133/adk-connector)
- [ADK Connector Python Package (PyPI)](https://pypi.org/project/adk-connector/)
- [ADK Connector JS/TS Package (NPM)](https://www.npmjs.com/package/adk-connector-js)
