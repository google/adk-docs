# MCP Toolbox for Databases

[MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) is an
open source MCP server for databases. It was designed with enterprise-grade and
production-quality in mind. It enables you to develop tools easier, faster, and
more securely by handling the complexities such as connection pooling,
authentication, and more.

Google’s Agent Development Kit (ADK) has built in support for Toolbox. For more
information on
[getting started](https://googleapis.github.io/genai-toolbox/getting-started/) or
[configuring](https://googleapis.github.io/genai-toolbox/getting-started/configure/)
Toolbox, see the
[documentation](https://googleapis.github.io/genai-toolbox/getting-started/introduction/).

![GenAI Toolbox](../../assets/mcp_db_toolbox.png)

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

Toolbox is an open source server that you deploy and manage yourself. For more
instructions on deploying and configuring, see the official Toolbox
documentation:

* [Installing the Server](https://googleapis.github.io/genai-toolbox/getting-started/introduction/#installing-the-server)
* [Configuring Toolbox](https://googleapis.github.io/genai-toolbox/getting-started/configure/)

## Install client SDK for ADK

ADK relies on the `toolbox-core` python package to use Toolbox. Install the
package before getting started:

```shell
pip install toolbox-core
```

## Loading Toolbox Tools

Once you’re Toolbox server is configured and up and running, you can load tools
from your server using ADK:

```python
from google.adk.agents import Agent
from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("https://127.0.0.1:5000")

# Load a specific set of tools
tools = toolbox.load_toolset('my-toolset-name'),
# Load single tool
tools = toolbox.load_tool('my-tool-name'),

root_agent = Agent(
    ...,
    tools=tools # Provide the list of tools to the Agent

)
```

## Advanced Toolbox Features

Toolbox has a variety of features to make developing Gen AI tools for databases.
For more information, read more about the following features:

* [Authenticated Parameters](https://googleapis.github.io/genai-toolbox/resources/tools/#authenticated-parameters): bind tool inputs to values from OIDC tokens automatically, making it easy to run sensitive queries without potentially leaking data
* [Authorized Invocations:](https://googleapis.github.io/genai-toolbox/resources/tools/#authorized-invocations)  restrict access to use a tool based on the users Auth token
* [OpenTelemetry](https://googleapis.github.io/genai-toolbox/how-to/export_telemetry/): get metrics and tracing from Toolbox with OpenTelemetry
