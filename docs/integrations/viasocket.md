---
catalog_title: viaSocket
catalog_description: Act in 2,300+ apps your users connected, on their own accounts
catalog_icon: /integrations/assets/viasocket.svg
catalog_tags: ["connectors"]
---

# viaSocket plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [viaSocket](https://viasocket.com) Python package connects your ADK agent
to the apps your end users connected through viaSocket. That covers 2,300+ apps
such as Slack, Google Sheets, HubSpot, Notion and GitHub. Each action of an app
becomes one tool, and each call runs on that user's own connection. Your team
does not build connectors or handle OAuth.

## Use cases

- **Act in your users' apps**: Post a Slack message, add a row to a Google
  Sheet or create a HubSpot deal for the user who asked, with their own account.
- **Offer integrations without building them**: Let each user of your product
  connect the apps they use through viaSocket's hosted sign-in. Your agent gets
  the tools for those apps.
- **Fill fields from real data**: An app with a field that holds an id (a
  channel, a spreadsheet) also gets a list-options tool. The agent reads the
  real values from the user's account instead of guessing.

## Prerequisites

- A [viaSocket account](https://flow.viasocket.com)
- Three values from the viaSocket dashboard (**Integrations > Create embed >
  Install Code**): `VIASOCKET_ORG_ID`, `VIASOCKET_PROJECT_ID` and
  `VIASOCKET_EMBED_SECRET`. With Node.js, `npx viasocket-apps setup` writes them
  to `.env` after one sign-in.
- At least one app connected for the user. Your users connect apps through
  viaSocket's connect popup in your product. To try it, connect an app for
  yourself from the terminal: `npx viasocket-apps connect slack --user me`.

## Installation

```bash
pip install "viasocket[adk]"
```

## Use with agent

```python
import os

from google.adk.agents import Agent
from viasocket import ViaSocket
from viasocket.adk import viasocket_tools

viasocket = ViaSocket(
    org_id=os.environ["VIASOCKET_ORG_ID"],
    project_id=os.environ["VIASOCKET_PROJECT_ID"],
    secret=os.environ["VIASOCKET_EMBED_SECRET"],
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="viasocket_agent",
    instruction="Help the user with their Slack workspace.",
    tools=viasocket_tools(
        viasocket,
        user="me",  # the end user the apps were connected for
        apps=["slack"],
        actions={"slack": ["send-message"]},
    ),
)
```

## Available tools

The tools depend on the apps and actions you choose. Tool names follow
`<app>_<action>`.

Tool | Description
---- | -----------
`slack_send-message` | Send or schedule a message to a channel, user or thread
`slack_list-options` | List the values a field accepts, such as channels, from the user's account
`google-sheets_add-new-row-to-sheet` | Add a row to a sheet

An app left out of `actions` gives every published action as a tool. Name
actions by their path on the app's viaSocket page (`send-message`) or by their
`action_id`. If the user has not connected an app, or the app returns an error,
the tool answers the model with text instead of raising an exception.

## Additional resources

- [viaSocket Python package on PyPI](https://pypi.org/project/viasocket/)
- [viaSocket Python package README](https://github.com/Walkover-Web-Solution/viasocket-apps/tree/main/python#readme)
- [viaSocket on GitHub](https://github.com/Walkover-Web-Solution/viasocket-apps)
