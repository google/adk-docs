---
catalog_title: Discovery Engine
catalog_description: Check whether supplied facts support an agent's answer
catalog_icon: /integrations/assets/adk.png
catalog_tags: ["google", "evaluation"]
---

# Discovery Engine CheckGrounding for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.15.0</span>
</div>

Use the experimental `CheckGroundingClient` to check a generated answer against
evidence you supply. It does not retrieve the evidence for you. For example,
after generating an answer with retrieval, pass the retrieved passages as facts
to check how well they support the answer.

## Setup

Install ADK with the Google Cloud extra:

```bash
pip install "google-adk[gcp]>=2.15.0"
```

Enable the Discovery Engine API in your Google Cloud project and configure
[Application Default Credentials](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc)
for a principal with the `discoveryengine.groundingConfigs.check` permission.
Set `GOOGLE_CLOUD_PROJECT` to your project ID, or pass `project_id` to the client.

## Check an answer

```python
import asyncio

from google.adk.integrations.discovery_engine import (
    CheckGroundingClient,
    FactChunk,
    GroundingStatus,
)


async def main():
    client = CheckGroundingClient()
    try:
        result = await client.check_grounding_async(
            answer_candidate="The museum closes at 6 p.m.",
            facts=[FactChunk(text="Museum hours: 10 a.m. to 6 p.m.")],
        )
        if result.status == GroundingStatus.OK:
            if result.support_score is not None:
                print("Support score:", result.support_score)
            print("Grounding metadata:", result.metadata)
        else:
            print("Grounding check did not complete:", result.status.value)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

The async transport is bound to its event loop, so close the client in the
same loop as the check. On the `CheckGroundingClient` constructor,
`location` and `grounding_config` default to `global` and
`default_grounding_config`. Set `citation_threshold` between 0 and 1 to control
the minimum confidence for citing a fact (default: 0.6). This threshold does not
determine whether the answer should be accepted.

## Interpret the result

Read the `GroundingResult.status` first. `OK` means the API ran, not that the
answer was supported. `support_score` is the optional answer-level score, and
`metadata` holds citation information. Do not treat a missing score as zero.
An empty fact list returns `SKIPPED_NO_FACTS`; a blank answer with facts returns
`SKIPPED_EMPTY`. For `REJECTED_TOO_LONG` and `API_ERROR`, see `error` for details.
See the [CheckGrounding API reference](https://docs.cloud.google.com/gemini/enterprise/docs/reference/rest/v1/projects.locations.groundingConfigs/check)
for request limits.
