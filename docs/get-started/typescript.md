# TypeScript Quickstart for ADK

This guide shows you how to get up and running with Agent Development Kit
(ADK) for TypeScript. Before you start, make sure you have the following installed:

*   Node.js (LTS version recommended)
*   `npm` for installing packages

## Installation and Project Setup

Run the following commands to create a new project directory, install the necessary packages, and create the initial files.

```shell
mkdir my_agent
cd my_agent
npm init -y
npm install @google/adk @google/adk-devtools
npm install -D typescript
```

Next, create a `tsconfig.json` file with the following content. This configuration ensures your project correctly handles modern Node.js modules.

```json title="tsconfig.json"
{
  "compilerOptions": {
    "target": "es2020",
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true
  }
}
```

Now, create the `agent.ts` and `.env` files.

=== "OS X &amp; Linux"
    ```shell
    touch agent.ts
    touch .env
    ```

=== "Windows"
    ```shell
    type nul > agent.ts
    type nul > .env
    ```

### Explore the agent project

The created agent project has the following structure, with the `agent.ts`
file containing the main control code for the agent.

```none
my_agent/
    agent.ts      # main agent code
    .env          # API key or project ID
    package.json
    tsconfig.json
```

## Update your agent project

The `agent.ts` file should export a `rootAgent` which is the only
required element of an ADK agent. You can also define tools for the agent to
use. Update the generated `agent.ts` code to include a `get_current_time` tool
for use by the agent, as shown in the following code:

```typescript
import 'dotenv/config';
import { LlmAgent, FunctionTool } from '@google/adk';
import { z } from 'zod';

// Mock tool implementation
const getCurrentTime = new FunctionTool({
  name: 'get_current_time',
  description: 'Returns the current time in a specified city.',
  parameters: z.object({
    city: z.string(),
  }),
  execute: ({ city }: { city: string }) => {
    return { status: 'success', city: city, time: '10:30 AM' };
  },
});

export const rootAgent = new LlmAgent({
    model: 'gemini-2.5-flash',
    name: 'root_agent',
    description: "Tells the current time in a specified city.",
    instruction: "You are a helpful assistant that tells the current time in cities. Use the 'get_current_time' tool for this purpose.",
    tools: [getCurrentTime],
});
```

### Set your API key

This project uses the Gemini API, which requires an API key. If you
don't already have Gemini API key, create a key in Google AI Studio on the
[API Keys](https://aistudio.google.com/app/apikey) page.

In a terminal window, write your API key into the `.env` file as an environment variable:

```console title="Update: my_agent/.env"
echo 'GOOGLE_GENAI_API_KEY="YOUR_API_KEY"' > .env
```

??? tip "Using other AI models with ADK"
    ADK supports the use of many generative AI models. For more
    information on configuring other models in ADK agents, see
    [Models & Authentication](/adk-docs/agents/models).

## Run your agent

You can run your ADK agent with an interactive command-line interface using the
`npx adk run` command or the ADK web user interface provided by the ADK using the
`npx adk web` command. Both these options allow you to test and interact with your
agent.

### Run with command-line interface

Run your agent using the `npx adk run` command-line tool.

```console
npx adk run agent.ts
```

![adk-run.png](/adk-docs/assets/adk-run.png)

### Run with web interface

The ADK framework provides a web interface you can use to test and interact with
your agent. You can start the web interface using the following command:

```console
npx adk web agent.ts
```

This command starts a web server with a chat interface for your agent. You can
access the web interface at (http://localhost:8000). Select the agent at the
upper right corner and type a request.

![adk-web-dev-ui-chat.png](/adk-docs/assets/adk-web-dev-ui-chat.png)

## Next: Build your agent

Now that you have ADK installed and your first agent running, try building
your own agent with our build guides:

*  [Build your agent](/adk-docs/tutorials/)