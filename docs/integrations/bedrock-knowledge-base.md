---
catalog_title: Amazon Bedrock Knowledge Base
catalog_description: RAG retrieval from Amazon Bedrock Managed Knowledge Bases for ADK agents
catalog_icon: /integrations/assets/bedrock-knowledge-base.png
catalog_tags: ["tools", "rag", "aws"]
---

# Amazon Bedrock Knowledge Base

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

Connect your ADK agents to [Amazon Bedrock Managed Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) for retrieval-augmented generation (RAG). Agents can search enterprise documents and get grounded answers without hallucinating.

## Why Bedrock Knowledge Bases for ADK?

Amazon Bedrock Managed Knowledge Bases provide fully managed RAG infrastructure — no vector store to provision, no embeddings to configure, automatic scaling. Combined with ADK agents, your agent can:

- **Search enterprise documents** (PDFs, web pages, databases) in natural language
- **Use agentic retrieval** for multi-hop reasoning across documents
- **Get grounded answers** with source citations
- **Scale automatically** without managing infrastructure

## Use cases

- **Enterprise Q&A agents**: Answer questions from internal documentation, policies, and knowledge bases
- **Customer support agents**: Retrieve relevant help articles and product information
- **Research assistants**: Search across large document collections with multi-hop reasoning
- **Compliance agents**: Look up regulatory documents and provide cited answers

## Prerequisites

- AWS account with Amazon Bedrock access
- A Bedrock Managed Knowledge Base created (via [AWS Console](https://console.aws.amazon.com/bedrock/home#/knowledge-bases) or Terraform)
- AWS credentials configured (environment variables, IAM role, or AWS profile)
- Python 3.10+

## Installation

```bash
pip install google-adk-community boto3>=1.43.2
```

## Use with agent

```python
from google.adk.agents import Agent
from google.adk_community.tools.bedrock_kb import bedrock_kb_retrieve

# Create an agent with Bedrock KB retrieval
agent = Agent(
    model="gemini-2.0-flash",
    tools=[bedrock_kb_retrieve],
    instruction="You are a helpful assistant. Use bedrock_kb_retrieve to search the knowledge base when answering questions about company policies or documentation.",
)
```

The agent will automatically call `bedrock_kb_retrieve` when it needs information from the knowledge base.

### Configuration via environment variables

```bash
export KNOWLEDGE_BASE_ID="YOUR_KB_ID"
export AWS_REGION="us-west-2"
export USE_AGENTIC_RETRIEVAL="true"  # Multi-hop reasoning (default)
```

### Configuration via function arguments

```python
# Pass knowledge_base_id directly (overrides env var)
result = bedrock_kb_retrieve(
    query="What is our refund policy?",
    knowledge_base_id="YOUR_KB_ID",
    max_results=5,
)
```

## Available tools

Tool | Description
---- | -----------
`bedrock_kb_retrieve` | Searches a Bedrock Managed Knowledge Base and returns relevant passages with sources and scores. Supports agentic retrieval (multi-hop reasoning) with automatic fallback to standard search.

### Tool parameters

Parameter | Type | Description
--------- | ---- | -----------
`query` | `str` | The natural language question or search query (required)
`knowledge_base_id` | `str` | Bedrock KB ID. Defaults to `KNOWLEDGE_BASE_ID` env var
`max_results` | `int` | Maximum results to return. Defaults to 5

## Retrieval modes

### Agentic retrieval (default)

Uses `AgenticRetrieveStream` — the model reasons over multiple retrieval passes, decomposes complex queries, and applies managed reranking for better results.

```bash
export USE_AGENTIC_RETRIEVAL="true"
```

### Standard retrieval

Uses `Retrieve` with `managedSearchConfiguration` — single-pass semantic search.

```bash
export USE_AGENTIC_RETRIEVAL="false"
```

## IAM permissions

Your AWS credentials need:

```json
{
    "Effect": "Allow",
    "Action": [
        "bedrock:Retrieve",
        "bedrock:AgenticRetrieveStream"
    ],
    "Resource": "arn:aws:bedrock:REGION:ACCOUNT:knowledge-base/KB_ID"
}
```

## Resources

- [Amazon Bedrock Knowledge Bases documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [Create a managed knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-create.html)
- [AgenticRetrieveStream API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_AgenticRetrieveStream.html)
- [GitHub: adk-python-community](https://github.com/google/adk-python-community)
