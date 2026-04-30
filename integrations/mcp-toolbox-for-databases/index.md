# MCP Toolbox for Databases tool for ADK

Supported in ADKPythonTypescriptGo

[MCP Toolbox for Databases](https://github.com/googleapis/mcp-toolbox) is an open source MCP server for databases. It was designed with enterprise-grade and production-quality in mind. It enables you to develop tools easier, faster, and more securely by handling the complexities such as connection pooling, authentication, and more.

Google’s Agent Development Kit (ADK) has built in support for MCP Toolbox. For more information on [getting started](https://mcp-toolbox.dev/documentation/introduction/) or [configuring](https://mcp-toolbox.dev/documentation/configuration/) MCP Toolbox, see the [documentation](https://mcp-toolbox.dev/documentation/introduction/).

## Supported Data Sources

MCP Toolbox provides out-of-the-box toolsets for the following databases and data platforms:

### Google Cloud

- [BigQuery](https://mcp-toolbox.dev/integrations/bigquery/source/) (including tools for SQL execution, schema discovery, and AI-powered time series forecasting)
- [AlloyDB](https://mcp-toolbox.dev/integrations/alloydb/source/) (PostgreSQL-compatible, with tools for both standard queries and natural language queries)
- [AlloyDB Admin](https://mcp-toolbox.dev/integrations/alloydb/source/)
- [Spanner](https://mcp-toolbox.dev/integrations/spanner/source/) (supporting both GoogleSQL and PostgreSQL dialects)
- Cloud SQL (with dedicated support for [Cloud SQL for PostgreSQL](https://mcp-toolbox.dev/integrations/cloud-sql-pg/source/), [Cloud SQL for MySQL](https://mcp-toolbox.dev/integrations/cloud-sql-mysql/source/), and [Cloud SQL for SQL Server](https://mcp-toolbox.dev/integrations/cloud-sql-mssql/source/))
- [Cloud SQL Admin](https://mcp-toolbox.dev/integrations/cloud-sql-admin/source/)
- [Firestore](https://mcp-toolbox.dev/integrations/firestore/source/)
- [Bigtable](https://mcp-toolbox.dev/integrations/bigtable/source/)
- [Dataplex](https://mcp-toolbox.dev/integrations/dataplex/source/) (for data discovery and metadata search)
- [Cloud Monitoring](https://mcp-toolbox.dev/integrations/cloudmonitoring/source/)
- [Cloud Healthcare](https://mcp-toolbox.dev/integrations/cloudhealthcare/source/)
- [Cloud Logging Admin](https://mcp-toolbox.dev/integrations/cloudloggingadmin/source/)
- [Dataproc](https://mcp-toolbox.dev/integrations/dataproc/source/)
- [Serverless Spark](https://mcp-toolbox.dev/integrations/serverless-spark/source/)
- [Cloud GDA](https://mcp-toolbox.dev/integrations/cloudgda/source/)

### Relational & SQL Databases

- [PostgreSQL](https://mcp-toolbox.dev/integrations/postgres/source/) (generic)
- [MySQL](https://mcp-toolbox.dev/integrations/mysql/source/) (generic)
- [Microsoft SQL Server](https://mcp-toolbox.dev/integrations/mssql/source/) (generic)
- [ClickHouse](https://mcp-toolbox.dev/integrations/clickhouse/source/)
- [TiDB](https://mcp-toolbox.dev/integrations/tidb/source/)
- [OceanBase](https://mcp-toolbox.dev/integrations/oceanbase/source/)
- [Firebird](https://mcp-toolbox.dev/integrations/firebird/source/)
- [SQLite](https://mcp-toolbox.dev/integrations/sqlite/source/)
- [YugabyteDB](https://mcp-toolbox.dev/integrations/yuagbytedb/source/)
- [CockroachDB](https://mcp-toolbox.dev/integrations/cockroachdb/source/)
- [Oracle](https://mcp-toolbox.dev/integrations/oracle/source/)
- [SingleStore](https://mcp-toolbox.dev/integrations/singlestore/source/)

### NoSQL & Key-Value Stores

- [MongoDB](https://mcp-toolbox.dev/integrations/mongodb/source/)
- [Couchbase](https://mcp-toolbox.dev/integrations/couchbase/source/)
- [Redis](https://mcp-toolbox.dev/integrations/redis/source/)
- [Valkey](https://mcp-toolbox.dev/integrations/valkey/source/)
- [Cassandra](https://mcp-toolbox.dev/integrations/cassandra/source/)
- [Elasticsearch](https://mcp-toolbox.dev/integrations/elasticsearch/source/)

### Graph Databases

- [Neo4j](https://mcp-toolbox.dev/integrations/neo4j/source/) (with tools for Cypher queries and schema inspection)
- [Dgraph](https://mcp-toolbox.dev/integrations/dgraph/source/)

### Data Platforms & Federation

- [Looker](https://mcp-toolbox.dev/integrations/looker/source/) (for running Looks, queries, and building dashboards via the Looker API)
- [Trino](https://mcp-toolbox.dev/integrations/trino/source/) (for running federated queries across multiple sources)
- [Snowflake](https://mcp-toolbox.dev/integrations/snowflake/source/)
- [MindsDB](https://mcp-toolbox.dev/integrations/mindsdb/source/)

### Other

- [HTTP](https://mcp-toolbox.dev/integrations/http/source/)

## Configure and deploy

MCP Toolbox is an open source server that you deploy and manage yourself. For more instructions on deploying and configuring, see the official Toolbox documentation:

- [Installing the Server](https://mcp-toolbox.dev/documentation/introduction/)
- [Configuring MCP Toolbox](https://mcp-toolbox.dev/documentation/configuration/)

## Install Client SDK for ADK

ADK relies on the `toolbox-adk` python package to use MCP Toolbox. Install the package before getting started:

```shell
pip install google-adk[toolbox]
```

### Loading MCP Toolbox Tools

Once your MCP Toolbox server is configured, up and running, you can load tools from your server using ADK:

```python
from google.adk import Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset

toolset = ToolboxToolset(
    server_url="http://127.0.0.1:5000"
)

root_agent = Agent(
    ...,
    tools=[toolset] # Provide the toolset to the Agent
)
```

### Authentication

The `ToolboxToolset` supports various authentication strategies including Workload Identity (ADC), User Identity (OAuth2), and API Keys. For full documentation, see the [MCP Toolbox ADK Authentication Guide](https://github.com/googleapis/mcp-toolbox-sdk-python/tree/main/packages/toolbox-adk#authentication).

**Example: Workload Identity (ADC)**

Recommended for Cloud Run, GKE, or local development with `gcloud auth login`.

```python
from google.adk.tools.toolbox_toolset import ToolboxToolset
from toolbox_adk import CredentialStrategy

# target_audience: The URL of your MCP Toolbox server
creds = CredentialStrategy.workload_identity(target_audience="<TOOLBOX_URL>")

toolset = ToolboxToolset(
    server_url="<TOOLBOX_URL>",
    credentials=creds
)
```

### Advanced Configuration

You can configure parameter binding and additional headers. See the [MCP Toolbox ADK documentation](https://github.com/googleapis/mcp-toolbox-sdk-python/tree/main/packages/toolbox-adk) for details. For example, you can bind values to tool parameters.

Note

These values are hidden from the model.

```python
toolset = ToolboxToolset(
    server_url="...",
    bound_params={
        "region": "us-central1",
        "api_key": lambda: get_api_key() # Can be a callable
    }
)
```

ADK relies on the `@toolbox-sdk/adk` TS package to use MCP Toolbox. Install the package before getting started:

```shell
npm install @toolbox-sdk/adk
```

### Loading MCP Toolbox Tools

Once your MCP Toolbox server is configured and up and running, you can load tools from your server using ADK:

```typescript
import {InMemoryRunner, LlmAgent} from '@google/adk';
import {Content} from '@google/genai';
import {ToolboxClient} from '@toolbox-sdk/adk'

const toolboxClient = new ToolboxClient("http://127.0.0.1:5000");
const loadedTools = await toolboxClient.loadToolset();

export const rootAgent = new LlmAgent({
  name: 'weather_time_agent',
  model: 'gemini-flash-latest',
  description:
    'Agent to answer questions about the time and weather in a city.',
  instruction:
    'You are a helpful agent who can answer user questions about the time and weather in a city.',
  tools: loadedTools,
});

async function main() {
  const userId = 'test_user';
  const appName = rootAgent.name;
  const runner = new InMemoryRunner({agent: rootAgent, appName});
  const session = await runner.sessionService.createSession({
    appName,
    userId,
  });

  const prompt = 'What is the weather in New York? And the time?';
  const content: Content = {
    role: 'user',
    parts: [{text: prompt}],
  };
  console.log(content);
  for await (const e of runner.runAsync({
    userId,
    sessionId: session.id,
    newMessage: content,
  })) {
    if (e.content?.parts?.[0]?.text) {
      console.log(`${e.author}: ${JSON.stringify(e.content, null, 2)}`);
    }
  }
}

main().catch(console.error);
```

ADK relies on the `mcp-toolbox-sdk-go` go module to use MCP Toolbox. Install the module before getting started:

```shell
go get github.com/googleapis/mcp-toolbox-sdk-go
```

### Loading MCP Toolbox Tools

Once your MCP Toolbox server is configured and up and running, you can load tools from your server using ADK:

```go
package main

import (
    "context"
    "fmt"

    "github.com/googleapis/mcp-toolbox-sdk-go/tbadk"
    "google.golang.org/adk/agent/llmagent"
)

func main() {

  toolboxClient, err := tbadk.NewToolboxClient("https://127.0.0.1:5000")
    if err != nil {
        log.Fatalf("Failed to create MCP Toolbox client: %v", err)
    }

  // Load a specific set of tools
  toolboxtools, err := toolboxClient.LoadToolset("my-toolset-name", ctx)
  if err != nil {
    return fmt.Sprintln("Could not load MCP Toolbox Toolset", err)
  }

  toolsList := make([]tool.Tool, len(toolboxtools))
    for i := range toolboxtools {
      toolsList[i] = &toolboxtools[i]
    }

  llmagent, err := llmagent.New(llmagent.Config{
    ...,
    Tools:       toolsList,
  })

  // Load a single tool
  tool, err := client.LoadTool("my-tool-name", ctx)
  if err != nil {
    return fmt.Sprintln("Could not load MCP Toolbox Tool", err)
  }

  llmagent, err := llmagent.New(llmagent.Config{
    ...,
    Tools:       []tool.Tool{&toolboxtool},
  })
}
```

## Advanced MCP Toolbox Features

MCP Toolbox has a variety of features to make developing Gen AI tools for databases. For more information, read more about the following features:

- [Authenticated Parameters](https://mcp-toolbox.dev/documentation/connect-to/toolbox-sdks/python-sdk/core/#parameter-binding): bind tool inputs to values from OIDC tokens automatically, making it easy to run sensitive queries without potentially leaking data
- [Authorized Invocations:](https://mcp-toolbox.dev/documentation/connect-to/toolbox-sdks/python-sdk/core/#client-to-server-authentication) restrict access to use a tool based on the users Auth token
- [OpenTelemetry](https://mcp-toolbox.dev/documentation/connect-to/toolbox-sdks/python-sdk/core/#opentelemetry): get metrics and tracing from Toolbox with OpenTelemetry
