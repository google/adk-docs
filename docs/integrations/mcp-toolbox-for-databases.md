---
catalog_title: MCP Toolbox for Databases
catalog_description: Connect over 30 different data sources to your agents
catalog_icon: /adk-docs/integrations/assets/mcp-toolbox-for-databases.png
catalog_tags: ["mcp","data","google"]
---

# MCP Toolbox for Databases tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">Typescript</span><span class="lst-go">Go</span>
</div>

[MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) is an
open source MCP server for databases. It was designed with enterprise-grade and
production-quality in mind. It enables you to develop tools easier, faster, and
more securely by handling the complexities such as connection pooling,
authentication, and more.

Google’s Agent Development Kit (ADK) has built in support for MCP Toolbox. For more
information on
[getting started](https://googleapis.github.io/genai-toolbox/getting-started/) or
[configuring](https://googleapis.github.io/genai-toolbox/getting-started/configure/)
MCP Toolbox, see the
[documentation](https://googleapis.github.io/genai-toolbox/getting-started/introduction/).

![MCP Toolbox for Databases](/adk-docs/integrations/assets/mcp-db-toolbox.png)

## Supported Data Sources

MCP Toolbox provides out-of-the-box toolsets for the following databases and data platforms:

### Google Cloud

*   [BigQuery](https://googleapis.github.io/genai-toolbox/resources/sources/bigquery/) (including tools for SQL execution, schema discovery, and AI-powered time series forecasting)
*   [AlloyDB](https://googleapis.github.io/genai-toolbox/resources/sources/alloydb-pg/) (PostgreSQL-compatible, with tools for both standard queries and natural language queries)
*   [AlloyDB Admin](https://googleapis.github.io/genai-toolbox/resources/sources/alloydb-admin/)
*   [Spanner](https://googleapis.github.io/genai-toolbox/resources/sources/spanner/) (supporting both GoogleSQL and PostgreSQL dialects)
*   Cloud SQL (with dedicated support for [Cloud SQL for PostgreSQL](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-pg/), [Cloud SQL for MySQL](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-mysql/), and [Cloud SQL for SQL Server](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-mssql/))
*   [Cloud SQL Admin](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-admin/)
*   [Firestore](https://googleapis.github.io/genai-toolbox/resources/sources/firestore/)
*   [Bigtable](https://googleapis.github.io/genai-toolbox/resources/sources/bigtable/)
*   [Dataplex](https://googleapis.github.io/genai-toolbox/resources/sources/dataplex/) (for data discovery and metadata search)
*   [Cloud Monitoring](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-monitoring/)

### Relational & SQL Databases

*   [PostgreSQL](https://googleapis.github.io/genai-toolbox/resources/sources/postgres/) (generic)
*   [MySQL](https://googleapis.github.io/genai-toolbox/resources/sources/mysql/) (generic)
*   [Microsoft SQL Server](https://googleapis.github.io/genai-toolbox/resources/sources/mssql/) (generic)
*   [ClickHouse](https://googleapis.github.io/genai-toolbox/resources/sources/clickhouse/)
*   [TiDB](https://googleapis.github.io/genai-toolbox/resources/sources/tidb/)
*   [OceanBase](https://googleapis.github.io/genai-toolbox/resources/sources/oceanbase/)
*   [Firebird](https://googleapis.github.io/genai-toolbox/resources/sources/firebird/)
*   [SQLite](https://googleapis.github.io/genai-toolbox/resources/sources/sqlite/)
*   [YugabyteDB](https://googleapis.github.io/genai-toolbox/resources/sources/yugabytedb/)

### NoSQL & Key-Value Stores

*   [MongoDB](https://googleapis.github.io/genai-toolbox/resources/sources/mongodb/)
*   [Couchbase](https://googleapis.github.io/genai-toolbox/resources/sources/couchbase/)
*   [Redis](https://googleapis.github.io/genai-toolbox/resources/sources/redis/)
*   [Valkey](https://googleapis.github.io/genai-toolbox/resources/sources/valkey/)
*   [Cassandra](https://googleapis.github.io/genai-toolbox/resources/sources/cassandra/)

### Graph Databases

*   [Neo4j](https://googleapis.github.io/genai-toolbox/resources/sources/neo4j/) (with tools for Cypher queries and schema inspection)
*   [Dgraph](https://googleapis.github.io/genai-toolbox/resources/sources/dgraph/)

### Data Platforms & Federation

*   [Looker](https://googleapis.github.io/genai-toolbox/resources/sources/looker/) (for running Looks, queries, and building dashboards via the Looker API)
*   [Trino](https://googleapis.github.io/genai-toolbox/resources/sources/trino/) (for running federated queries across multiple sources)

### Other

*   [HTTP](https://googleapis.github.io/genai-toolbox/resources/sources/http/)

## Configure and deploy

MCP Toolbox is an open source server that you deploy and manage yourself. For more
instructions on deploying and configuring, see the official Toolbox
documentation:

* [Installing the Server](https://googleapis.github.io/genai-toolbox/getting-started/introduction/#installing-the-server)
* [Configuring MCP Toolbox](https://googleapis.github.io/genai-toolbox/getting-started/configure/)

## Install Client SDK for ADK

=== "Python"

    ADK relies on the `toolbox-adk` python package to use MCP Toolbox. Install the
    package before getting started:

    ```shell
    pip install google-adk[toolbox]
    ```

    ### Loading MCP Toolbox Tools

    Once your MCP Toolbox server is configured, up and running, you can load tools
    from your server using ADK:

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

    !!! Note
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

=== "Typescript"

    ADK relies on the `@toolbox-sdk/adk` TS package to use MCP Toolbox. Install the
    package before getting started:

    ```shell
    npm install @toolbox-sdk/adk
    ```

    ### Loading MCP Toolbox Tools

    Once your MCP Toolbox server is configured and up and running, you can load tools
    from your server using ADK:

    ```typescript
    import {InMemoryRunner, LlmAgent} from '@google/adk';
    import {Content} from '@google/genai';
    import {ToolboxClient} from '@toolbox-sdk/adk'

    const toolboxClient = new ToolboxClient("http://127.0.0.1:5000");
    const loadedTools = await toolboxClient.loadToolset();

    export const rootAgent = new LlmAgent({
      name: 'weather_time_agent',
      model: 'gemini-2.5-flash',
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

=== "Go"

    ADK relies on the `mcp-toolbox-sdk-go` go module to use MCP Toolbox. Install the
    module before getting started:

    ```shell
    go get github.com/googleapis/mcp-toolbox-sdk-go
    ```

    ### Loading MCP Toolbox Tools

    Once your MCP Toolbox server is configured and up and running, you can load tools
    from your server using ADK:

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

MCP Toolbox has a variety of features to make developing Gen AI tools for databases.
For more information, read more about the following features:

* [Authenticated Parameters](https://googleapis.github.io/genai-toolbox/resources/tools/#authenticated-parameters): bind tool inputs to values from OIDC tokens automatically, making it easy to run sensitive queries without potentially leaking data
* [Authorized Invocations:](https://googleapis.github.io/genai-toolbox/resources/tools/#authorized-invocations)  restrict access to use a tool based on the users Auth token
* [OpenTelemetry](https://googleapis.github.io/genai-toolbox/how-to/export_telemetry/): get metrics and tracing from Toolbox with OpenTelemetry
