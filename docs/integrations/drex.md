---
catalog_title: Drex
catalog_description: Answer yes or no questions about text from an ADK tool
catalog_icon: /integrations/assets/drex.svg
---

# Decision questions with Drex

[Drex](https://console.nace.ai/docs) answers yes or no questions about text.
Call it from an ADK tool with [nace-sdk](https://pypi.org/project/nace-sdk/) 0.4.0.
A yes answer is a probability, not a boolean.

## Prerequisites

- Python 3.11 or later
- A [Nace API key](https://console.nace.ai/dashboard/api-keys)
- A [Gemini API key](https://aistudio.google.com/app/apikey), if you run the agent locally

## Install dependencies

```bash
pip install google-adk 'nace-sdk==0.4.0'
```

## Set environment variables

`NaceClient()` reads `NACE_API_KEY`.
Do not pass the key in code.

```env title="my_agent/.env"
GOOGLE_API_KEY="YOUR_API_KEY"
NACE_API_KEY="YOUR_API_KEY"
```

## Example: Ask Drex from a tool

```python
# my_agent/agent.py

from google.adk.agents import Agent
from nace_sdk import NaceClient, Noul


def refund_requested(message: str) -> dict:
    """Returns the probability that the message asks for a refund."""
    with NaceClient() as client:
        result = client.system_one(
            state=message,
            questions={
                "wants_refund": Noul(
                    instructions="Is the customer asking for a refund?",
                ),
            },
            model="drex-v2.0",
        )
    answer = result.nouls["wants_refund"]
    return {"wants_refund": answer.noul}


root_agent = Agent(
    model="gemini-flash-latest",
    name="root_agent",
    description="Checks whether a customer message asks for a refund.",
    instruction=(
        "You help with billing questions. Use the refund_requested tool "
        "before you decide whether the customer wants a refund."
    ),
    tools=[refund_requested],
)
```

Set `model` to `"drex-v2.0"` on the call.
If you omit `model`, the client uses `NACE_DEFAULT_DECISION_MODEL`.
When that variable is unset, the client uses `drex-latest`.

Pass a string for `instructions`.
Do not pass `None`.

Images require `model="drex-max"`.
If you send images to `drex-v2.0`, the API returns HTTP 422.

If the tool is async, import `AsyncNaceClient` from `nace_sdk`.
Await `client.system_one` with the same arguments.

`answer.noul` is the probability of a yes answer.
Values near 0.5 mean the model is unsure.

Run the agent with:

```bash
adk run my_agent
```

## Resources

- [nace-sdk on PyPI](https://pypi.org/project/nace-sdk/):
  Python client used above. Install 0.4.0.
- [Drex Python client](https://console.nace.ai/docs/developer-tools/python):
  Reference for `NaceClient` and `system_one`.
