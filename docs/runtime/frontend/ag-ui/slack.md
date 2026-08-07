# Slack

<div class="language-support-tag">
  <span class="lst-supported">Messaging platform</span>
</div>

Use CopilotKit Slack when Slack conversations should connect to an ADK agent
through AG-UI. Slack is not a browser chat surface: the Slack adapter owns
Socket Mode, message formatting, Block Kit rendering, interactions, and thread
routing.

## Install

Complete the [AG-UI backend setup](index.md) first, then install the Slack bot
packages:

```shell
npm install @copilotkit/bot @copilotkit/bot-slack @copilotkit/bot-ui
```

## Connect Slack to the ADK AG-UI endpoint

The Slack adapter can run in the same Node process as the rest of your backend.
Create an AG-UI agent per Slack thread and point it at the `ag-ui-adk` endpoint.
For Slack, CopilotKit Bot is the CopilotKit surface; it does not use the same
browser `/api/copilotkit` route as React, Angular, or Vue.

```ts title="slack-bot.ts"
import { createBot } from "@copilotkit/bot";
import {
  defaultSlackContext,
  defaultSlackTools,
  SanitizingHttpAgent,
  slack,
} from "@copilotkit/bot-slack";

function makeAgent(threadId: string) {
  const agent = new SanitizingHttpAgent({
    url: process.env.ADK_AG_UI_URL ?? "http://localhost:8000/ag-ui",
  });
  agent.threadId = threadId;
  return agent;
}

const bot = createBot({
  adapters: [
    slack({
      botToken: process.env.SLACK_BOT_TOKEN!,
      appToken: process.env.SLACK_APP_TOKEN!,
    }),
  ],
  agent: (threadId) => makeAgent(threadId),
  tools: [...defaultSlackTools],
  context: [...defaultSlackContext],
});

bot.onMention(({ thread }) => thread.runAgent());

await bot.start();
```

Use Socket Mode for local development. It requires an app-level token and does
not require a public inbound URL.

## Slack app settings

Create a Slack app with:

- a bot token in `SLACK_BOT_TOKEN`
- a Socket Mode app token in `SLACK_APP_TOKEN`
- app mention events for channel mentions
- direct message events if the bot should answer in DMs

Keep ADK credentials, session lookup, and tool execution policy behind the
`ag-ui-adk` endpoint. The Slack adapter should translate Slack threads and
interactions into agent runs; it should not call ADK Runtime endpoints such as
`/run_sse` directly.

## Use this for

- Internal support, operations, or workflow assistants in Slack.
- Agent responses that need Slack-native cards, buttons, threaded replies, or
  approvals.
- The same ADK agent behavior across web, mobile, and Slack surfaces.
