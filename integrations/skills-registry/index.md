# Google Cloud Skill Registry

Supported in ADKPython v1.27.0Preview

The **Google Cloud Skill Registry** integration within the Agent Development Kit (ADK) allows developers to dynamically search, discover, and fetch remote Skills cataloged within a central repository.

Rather than statically injecting every available skill into your agent's context window at initialization, the Skill Registry enables **on-demand targeted retrieval**. As your catalog of specialized capabilities scales to hundreds or thousands of skills, agents can dynamically discover, download, and activate the exact instructions and tools they need based on user intent. For more information about the Skills Registry service, see the [Google Cloud Skills Registry](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/skill-registry) documentation.

Preview release

The Google Cloud Skills Registry feature is a Preview release. For more information, see the [launch stage descriptions](https://cloud.google.com/products#product-launch-stages).

## Use Cases

- **Context Window Optimization**: Save valuable tokens by only loading a skill's system instructions and tools when the user's prompt actually requires them.
- **Enterprise Reusability**: Build a central, managed repository of shared and private skills that multiple agents across different applications can consume.
- **Secure Isolation**: Automatically cache dynamically loaded skills within the agent's specific session state or isolated sandbox environments.

______________________________________________________________________

## Prerequisites

- A [Google Cloud project](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects).
- The **Skill Registry API** enabled in your Google Cloud project.
- Authentication configured for your environment. We recommend logging in using [Application Default Credentials](https://docs.cloud.google.com/docs/authentication/application-default-credentials) (`gcloud auth application-default login`).
- Environment variables `GOOGLE_CLOUD_PROJECT` set to your project ID and `GOOGLE_CLOUD_LOCATION` set to your deployment region (e.g., `us-central1`).

Internet Access Requirements

Since the GCP Skill Registry interacts with Vertex AI services using the Vertex AI Client SDK, agents running in sandboxed environments without outbound network access to Vertex AI endpoints will fail to reach the registry. Ensure proper network access is configured, or else the system falls back to local, filesystem-loaded skills.

For more information on connecting to Google Cloud from ADK agents, see [Connect to Google Cloud and Agent Platform](/get-started/google-cloud/).

## Installation

The Skill Registry client is included in the core ADK library. Install it via pip:

```bash
pip install google-adk
```

______________________________________________________________________

## Use with Agent

To configure an agent to dynamically discover and load skills on demand, instantiate a `GCPSkillRegistry` and pass it as the `registry` parameter in your `SkillToolset`.

```python
import os
from google.adk import Agent
from google.adk.integrations.gcp_skill_registry import GCPSkillRegistry
from google.adk.tools.skill_toolset import SkillToolset

# 1. Initialize the GCP Skill Registry
# Project ID and location can also be set via GOOGLE_CLOUD_PROJECT
# and GOOGLE_CLOUD_LOCATION environment variables.
registry = GCPSkillRegistry(
    project_id=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
)

# 2. Create the SkillToolset with the Registry
# You can optionally pre-load some local skills as well.
skill_toolset = SkillToolset(
    skills=[],
    registry=registry
)

# 3. Define your Agent with the SkillToolset
agent = Agent(
    model="gemini-flash-latest",
    name="registry_agent",
    description="An agent that can dynamically discover and execute skills.",
    instruction="You are a helpful assistant. Use search_skills and load_skill to leverage remote capabilities.",
    tools=[skill_toolset],
)
```

______________________________________________________________________

## How it Works

When you configure a `SkillToolset` with a remote registry, ADK automatically equips your agent with two built-in tools to manage the skill lifecycle:

```
sequenceDiagram
    autonumber
    actor User
    participant Agent as ADK Agent (LLM)
    participant Toolset as SkillToolset
    participant Registry as Vertex AI SDK

    User->>Agent: "How to optimize a BigQuery query?"
    Note over Agent: LLM realizes it does not have<br/>instructions for BigQuery locally.

    Agent->>Toolset: search_skills(query="BigQuery optimization")
    Toolset->>Registry: Search matching skills
    Registry-->>Toolset: Returns frontmatters (e.g., "bigquery")
    Toolset-->>Agent: Returns list of matches (filtered)

    Note over Agent: LLM identifies "bigquery" as<br/>the best candidate.

    Agent->>Toolset: load_skill(skill_name="bigquery")
    Toolset->>Registry: Fetch remote skill details
    Registry-->>Toolset: Returns skill payload
    Note over Toolset: Unpacks payload &<br/>caches skill in Session State
    Toolset-->>Agent: Success. Skill loaded.

    Note over Agent: LLM appends skill instructions to system prompt,<br/>making tools available.
    Agent-->>User: Fulfills request utilizing BigQuery skill instructions!
```

### Semantic Discovery (`search_skills`)

If the agent determines that its current system instructions are insufficient to answer a user query, it automatically invokes the `search_skills` tool.

- **Collision Prevention**: To prevent namespace conflicts, ADK automatically filters out registry skills that duplicate the name of any locally loaded skills.

### On-Demand Loading (`load_skill`)

Once the agent identifies a matching remote skill (e.g., `"bigquery"`), it invokes the `load_skill` tool.

- **SDK Fetch**: ADK calls the Vertex AI Client SDK to retrieve the remote skill.
- **Extraction & Parsing**: The remote payload is unpacked and parsed into an executable `Skill` object.
- **Agent Session Caching**: The skill instructions and resources are cached in the current agent session state so subsequent turns do not require additional remote API calls.
- **Prompt Enrichment**: The skill's instructions are appended to the system prompt, and any scripts or tools provided by the skill become instantly executable.

______________________________________________________________________

## Configuration & API Reference

### `GCPSkillRegistry` Configuration

The `GCPSkillRegistry` client constructor accepts the following options:

| Parameter    | Type  | Default | Description                                                                                       |
| ------------ | ----- | ------- | ------------------------------------------------------------------------------------------------- |
| `project_id` | `str` | `None`  | The Google Cloud project ID. If omitted, falls back to `GOOGLE_CLOUD_PROJECT` env variable.       |
| `location`   | `str` | `None`  | The Google Cloud region/location. If omitted, falls back to `GOOGLE_CLOUD_LOCATION` env variable. |

### Methods

- **`search_skills(query: str) -> List[Frontmatter]`**: Performs a semantic or keyword query against the registry catalog, returning a list of skill frontmatter metadata (names and descriptions).
- **`get_skill(name: str, version: Optional[str] = None) -> Skill`**: Fetches the remote skill payload using the Vertex AI Client SDK for a specific skill name (and optional revision/version), unpacks it, and returns a loaded `Skill` object.
