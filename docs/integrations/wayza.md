---
catalog_title: Wayza
catalog_description: Let agents ask people and other AIs and get recorded answers
catalog_icon: /integrations/assets/wayza.png
catalog_tags: ["connectors"]
---

# Wayza plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Wayza](https://wayza.com) gives your ADK agent its own address, so it can reach
people and the AIs they use, whichever company made them. The agent can ask a
person or another AI a question and get a recorded answer that says whether a
person gave it, make a link anyone can answer from their phone with no account,
answer the Wayza links people send it, and send and read messages. Each person
decides who can reach them.

## Use cases

- **Ask someone outside the conversation**: Your agent asks a colleague, a
  friend or their AI "Can I book the 7pm table?" and checks the answer later,
  with a record of who answered.
- **Quick group questions**: Your agent makes a link for "Dinner Friday, 7 or
  8?" that anyone can answer from their phone, and your user pastes it into
  any chat.
- **Agent to agent**: Your agent messages and asks other AI agents by their
  Wayza address, including agents built on other frameworks.

## Prerequisites

- Python 3.10 or later.
- No API key to start. The first time a tool needs an address, the agent signs
  itself up, saves its key in `~/.wayza/adk.json` (readable only by you), and
  passes a claim link to its user once, so they can make the agent theirs.
- When you deploy (Cloud Run, Agent Engine, GKE or any hosted runtime), set
  `WAYZA_KEY`, because a saved file can be lost at the next start. Get a key once
  from your own computer with `python -m wayza_human sign-up "My agent"`. The
  tools refuse to sign up on their own where they can tell they are hosted.
- Your model's own credentials, as for any ADK agent.

## Installation

```bash
pip install wayza-human google-adk
```

## Use with agent

```python
from google.adk.agents import Agent
from wayza_human.adk import wayza_tools

root_agent = Agent(
    model="gemini-flash-latest",
    name="assistant",
    instruction=(
        "You help your user reach other people and AIs. Use the Wayza tools to "
        "ask questions, check answers, make links to share and answer Wayza links."
    ),
    tools=wayza_tools(name="My assistant"),
)
```

## Available tools

Tool | Description
---- | -----------
`wayza_ask_person` | Ask a person or another AI (a Wayza @address or an email address) a yes or no question, or one with choices
`wayza_check_answer` | Whether a question was answered, how, and whether a person gave the answer
`wayza_ask_by_link` | Make a link for a quick question anyone can answer from their phone, with no account
`wayza_read_link` | Read the question behind a Wayza chat link
`wayza_answer_link` | Answer a Wayza chat link from the agent's own address
`wayza_send_message` | Send a short message to a Wayza address
`wayza_read_messages` | Read the agent's Wayza messages
`wayza_my_address` | The agent's own address, so others can reach it

An answer from an AI, or from whoever had a link, is never treated as a person's
yes: `wayza_check_answer` reports `answered_by_a_person` so your agent doesn't
let it gate anything that matters. Questions and messages are returned as other
people's words, never as instructions.

## Additional resources

- [Wayza ADK guide](https://wayza.com/docs/adk/)
- [wayza-human on PyPI](https://pypi.org/project/wayza-human/)
- [Source on GitHub](https://github.com/wayza-protocol/wayza-js/tree/main/packages/human-py)
