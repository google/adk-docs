# Google Cloud Tools

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="This feature is currently available for Python. Java support is planned/ coming soon."}

Google Cloud tools make it easier to connect your agents to Google Cloud’s
products and services. With just a few lines of code you can use these tools to
connect your agents with:

* **Any custom APIs** that developers host in Apigee.
* **100s** of **prebuilt connectors** to enterprise systems such as Salesforce,
  Workday, and SAP.
* **Automation workflows** built using application integration.
* **Databases** such as Spanner, AlloyDB, Postgres and more using the MCP Toolbox for
  databases.

![Google Cloud Tools](../assets/google_cloud_tools.svg)

## Apigee API Hub Tools

**ApiHubToolset** lets you turn any documented API from Apigee API hub into a
tool with a few lines of code. This section shows you the step by step
instructions including setting up authentication for a secure connection to your
APIs.

**Prerequisites**

1. [Install ADK](../get-started/installation.md)
2. Install the
   [Google Cloud CLI](https://cloud.google.com/sdk/docs/install?db=bigtable-docs#installation_instructions).
3. [Apigee API hub](https://cloud.google.com/apigee/docs/apihub/what-is-api-hub)
    instance with documented (i.e. OpenAPI spec) APIs
4. Set up your project structure and create required files

```console
project_root_folder
 |
 `-- my_agent
     |-- .env
     |-- __init__.py
     |-- agent.py
     `__ tool.py
```

### Create an API Hub Toolset

Note: This tutorial includes an agent creation. If you already have an agent,
you only need to follow a subset of these steps.

1. Get your access token, so that APIHubToolset can fetch spec from API Hub API.
   In your terminal run the following command

    ```shell
    gcloud auth print-access-token
    # Prints your access token like 'ya29....'
    ```

2. Ensure that the account used has the required permissions. You can use the
   pre-defined role `roles/apihub.viewer` or assign the following permissions:

    1. **apihub.specs.get (required)**
    2. apihub.apis.get (optional)
    3. apihub.apis.list (optional)
    4. apihub.versions.get (optional)
    5. apihub.versions.list (optional)
    6. apihub.specs.list (optional)

3. Create a tool with `APIHubToolset`. Add the below to `tools.py`

    If your API requires authentication, you must configure authentication for
    the tool. The following code sample demonstrates how to configure an API
    key. ADK supports token based auth (API Key, Bearer token), service account,
    and OpenID Connect. We will soon add support for various OAuth2 flows.

    ```py
    from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
    from google.adk.tools.apihub_tool.apihub_toolset import APIHubToolset

    # Provide authentication for your APIs. Not required if your APIs don't required authentication.
    auth_scheme, auth_credential = token_to_scheme_credential(
        "apikey", "query", "apikey", apikey_credential_str
    )

    sample_toolset = APIHubToolset(
        name="apihub-sample-tool",
        description="Sample Tool",
        access_token="...",  # Copy your access token generated in step 1
        apihub_resource_name="...", # API Hub resource name
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
    )
    ```

    For production deployment we recommend using a service account instead of an
    access token. In the code snippet above, use
    `service_account_json=service_account_cred_json_str` and provide your
    security account credentials instead of the token.

    For apihub\_resource\_name, if you know the specific ID of the OpenAPI Spec
    being used for your API, use
    `` `projects/my-project-id/locations/us-west1/apis/my-api-id/versions/version-id/specs/spec-id` ``.
    If you would like the Toolset to automatically pull the first available spec
    from the API, use
    `` `projects/my-project-id/locations/us-west1/apis/my-api-id` ``

4. Create your agent file Agent.py and add the created tools to your agent
   definition:

    ```py
    from google.adk.agents.llm_agent import LlmAgent
    from .tools import sample_toolset

    root_agent = LlmAgent(
        model='gemini-2.0-flash',
        name='enterprise_assistant',
        instruction='Help user, leverage the tools you have access to',
        tools=sample_toolset.get_tools(),
    )
    ```

5. Configure your `__init__.py` to expose your agent

    ```py
    from . import agent
    ```

6. Start the Google ADK Web UI and try your agent:

    ```shell
    # make sure to run `adk web` from your project_root_folder
    adk web
    ```

   Then go to [http://localhost:8000](http://localhost:8000) to try your agent from the Web UI.

---

## Application Integration Tools

With **ApplicationIntegrationToolset**, you can seamlessly give your agents
secure and governed access to enterprise applications using Integration
Connectors' 100+ pre-built connectors for systems like Salesforce, ServiceNow,
JIRA, SAP, and more.

It supports both on-premise and SaaS applications. In addition, you can turn
your existing Application Integration process automations into agentic workflows
by providing application integration workflows as tools to your ADK agents.

Federated search within Application Integration lets you use ADK agents to query
multiple enterprise applications and data sources simultaneously.

[:fontawesome-brands-youtube:{.youtube-red-icon} See how ADK Federated Search in Application Integration works in this video walkthrough](https://www.youtube.com/watch?v=JdlWOQe5RgU){: target="_blank" rel="noopener noreferrer"}

<iframe width="560" height="315" src="https://www.youtube.com/embed/JdlWOQe5RgU?si=bFY_-jJ6Oliy5UMG" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### Prerequisites

#### 1. Install ADK

Install Agent Development Kit following the steps in the
[installation guide](../get-started/installation.md).

#### 2. Install CLI

Install the
[Google Cloud CLI](https://cloud.google.com/sdk/docs/install#installation_instructions).
To use the tool with default credentials, run the following commands:

```shell
gcloud config set project <project-id>
gcloud auth application-default login
gcloud auth application-default set-quota-project <project-id>
```

Replace `<project-id>` with the unique ID of your Google Cloud project.

#### 3. Provision Application Integration workflow and publish Connection Tool

Use an existing
[Application Integration](https://cloud.google.com/application-integration/docs/overview)
workflow or
[Integrations Connector](https://cloud.google.com/integration-connectors/docs/overview)
connection you want to use with your agent. You can also create a new
[Application Integration workflow](https://cloud.google.com/application-integration/docs/setup-application-integration)
or a
[connection](https://cloud.google.com/integration-connectors/docs/connectors/neo4j/configure#configure-the-connector).

Import and publish the
[Connection Tool](https://console.cloud.google.com/integrations/templates/connection-tool/locations/global)
from the template library.

**Note**: To use a connector from Integration Connectors, you need to provision
the Application Integration in the same region as your connection.

#### 4. Create project structure

=== "Python"

    Set up your project structure and create the required files:

      ```console
      project_root_folder
      ├── .env
      └── my_agent
          ├── __init__.py
          ├── agent.py
          └── tools.py
      ```

    When running the agent, make sure to run `adk web` from the `project_root_folder`.

=== "Java"

    Set up your project structure and create the required files:

      ```console
        project_root_folder
        └── my_agent
            ├── agent.java
            └── pom.xml
      ```

     When running the agent, make sure to run the commands from the `project_root_folder`.

#### 5. Set roles and permissions

To get the permissions that you need to set up
**ApplicationIntegrationToolset**, you must have the following IAM roles on the
project (common to both Integration Connectors and Application Integration
Workflows):

    - roles/integrations.integrationEditor
    - roles/connectors.invoker
    - roles/secretmanager.secretAccessor

**Note:** When using Agent Engine (AE) for deployment, don't use
`roles/integrations.integrationInvoker`, as it can result in 403 errors. Use
`roles/integrations.integrationEditor` instead.

### Use Integration Connectors

Connect your agent to enterprise applications using
[Integration Connectors](https://cloud.google.com/integration-connectors/docs/overview).

#### Before you begin

**Note:** The *ExecuteConnection* integration is typically created automatically when you provision Application Integration in a given region. If the *ExecuteConnection* doesn't exist in the [list of integrations](https://console.cloud.google.com/integrations/list), you must follow these steps to create it:

1. To use a connector from Integration Connectors, click **QUICK SETUP** and [provision](https://console.cloud.google.com/integrations)
   Application Integration in the same region as your connection.

   ![Google Cloud Tools](../assets/application-integration-overview.png)



2. Go to the [Connection Tool](https://console.cloud.google.com/integrations/templates/connection-tool/locations/us-central1)
   template in the template library and click **USE TEMPLATE**.


    ![Google Cloud Tools](../assets/use-connection-tool-template.png)

3. Enter the Integration Name as *ExecuteConnection* (it is mandatory to use this exact integration name only).
   Then, select the region to match your connection region and click **CREATE**.

4. Click **PUBLISH** to publish the integration in the <i>Application Integration</i> editor.


    ![Google Cloud Tools](../assets/publish-integration.png)


#### Create an Application Integration Toolset

To create an Application Integration Toolset for Integration Connectors, follow these steps:

1.  Create a tool with `ApplicationIntegrationToolset` in the `tools.py` file:

    ```py
    from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset

    connector_tool = ApplicationIntegrationToolset(
        project="test-project", # TODO: replace with GCP project of the connection
        location="us-central1", #TODO: replace with location of the connection
        connection="test-connection", #TODO: replace with connection name
        entity_operations={"Entity_One": ["LIST","CREATE"], "Entity_Two": []},#empty list for actions means all operations on the entity are supported.
        actions=["action1"], #TODO: replace with actions
        service_account_json='{...}', # optional. Stringified json for service account key
        tool_name_prefix="tool_prefix2",
        tool_instructions="..."
    )
    ```

    **Note:**

    * You can provide a service account to be used instead of default credentials by generating a [Service Account Key](https://cloud.google.com/iam/docs/keys-create-delete#creating), and providing the right [Application Integration and Integration Connector IAM roles](#prerequisites) to the service account.
    * To find the list of supported entities and actions for a connection, use the Connectors APIs: [listActions](https://cloud.google.com/integration-connectors/docs/reference/rest/v1/projects.locations.connections.connectionSchemaMetadata/listActions) or [listEntityTypes](https://cloud.google.com/integration-connectors/docs/reference/rest/v1/projects.locations.connections.connectionSchemaMetadata/listEntityTypes).


    `ApplicationIntegrationToolset` supports `auth_scheme` and `auth_credential` for **dynamic OAuth2 authentication** for Integration Connectors. To use it, create a tool similar to this in the `tools.py` file:

    ```py
    from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset
    from google.adk.tools.openapi_tool.auth.auth_helpers import dict_to_auth_scheme
    from google.adk.auth import AuthCredential
    from google.adk.auth import AuthCredentialTypes
    from google.adk.auth import OAuth2Auth

    oauth2_data_google_cloud = {
      "type": "oauth2",
      "flows": {
          "authorizationCode": {
              "authorizationUrl": "https://accounts.google.com/o/oauth2/auth",
              "tokenUrl": "https://oauth2.googleapis.com/token",
              "scopes": {
                  "https://www.googleapis.com/auth/cloud-platform": (
                      "View and manage your data across Google Cloud Platform"
                      " services"
                  ),
                  "https://www.googleapis.com/auth/calendar.readonly": "View your calendars"
              },
          }
      },
    }

    oauth_scheme = dict_to_auth_scheme(oauth2_data_google_cloud)

    auth_credential = AuthCredential(
      auth_type=AuthCredentialTypes.OAUTH2,
      oauth2=OAuth2Auth(
          client_id="...", #TODO: replace with client_id
          client_secret="...", #TODO: replace with client_secret
      ),
    )

    connector_tool = ApplicationIntegrationToolset(
        project="test-project", # TODO: replace with GCP project of the connection
        location="us-central1", #TODO: replace with location of the connection
        connection="test-connection", #TODO: replace with connection name
        entity_operations={"Entity_One": ["LIST","CREATE"], "Entity_Two": []},#empty list for actions means all operations on the entity are supported.
        actions=["GET_calendars/%7BcalendarId%7D/events"], #TODO: replace with actions. this one is for list events
        service_account_json='{...}', # optional. Stringified json for service account key
        tool_name_prefix="tool_prefix2",
        tool_instructions="...",
        auth_scheme=oauth_scheme,
        auth_credential=auth_credential
    )
    ```


2. Update the `agent.py` file and add tool to your agent:

    ```py
    from google.adk.agents.llm_agent import LlmAgent
    from .tools import connector_tool

    root_agent = LlmAgent(
        model='gemini-2.0-flash',
        name='connector_agent',
        instruction="Help user, leverage the tools you have access to",
        tools=[connector_tool],
    )
    ```

3. Configure  `__init__.py` to expose your agent:

    ```py
    from . import agent
    ```

4. Start the Google ADK Web UI and use your agent:

    ```shell
    # make sure to run `adk web` from your project_root_folder
    adk web
    ```

After completing the above steps, go to [http://localhost:8000](http://localhost:8000), and choose
   `my\_agent` agent (which is the same as the agent folder name).


### Use Application Integration Workflows

Use an existing
[Application Integration](https://cloud.google.com/application-integration/docs/overview)
workflow as a tool for your agent or create a new one.


#### 1. Create a tool

=== "Python"

    To create a tool with `ApplicationIntegrationToolset` in the `tools.py` file, use the following code:

      ```py
          integration_tool = ApplicationIntegrationToolset(
              project="test-project", # TODO: replace with GCP project of the connection
              location="us-central1", #TODO: replace with location of the connection
              integration="test-integration", #TODO: replace with integration name
              triggers=["api_trigger/test_trigger"],#TODO: replace with trigger id(s). Empty list would mean all api triggers in the integration to be considered.
              service_account_json='{...}', #optional. Stringified json for service account key
              tool_name_prefix="tool_prefix1",
              tool_instructions="..."
          )
      ```

      **Note:** You can provide a service account to be used instead of using default credentials. To do this, generate a [Service Account Key](https://cloud.google.com/iam/docs/keys-create-delete#creating) and provide the correct
         [Application Integration and Integration Connector IAM roles](#prerequisites) to the service account. For more details about the IAM roles, refer to the [Prerequisites](#prerequisites) section.

=== "Java"

    To create a tool with `ApplicationIntegrationToolset` in the `tools.java` file, use the following code:

      ```java
          import com.google.adk.tools.applicationintegrationtoolset.ApplicationIntegrationToolset;
          import com.google.common.collect.ImmutableList;
          import com.google.common.collect.ImmutableMap;

          public class Tools {
              private static ApplicationIntegrationToolset integrationTool;
              private static ApplicationIntegrationToolset connectionsTool;

              static {
                  integrationTool = new ApplicationIntegrationToolset(
                          "test-project",
                          "us-central1",
                          "test-integration",
                          ImmutableList.of("api_trigger/test-api"),
                          null,
                          null,
                          null,
                          "{...}",
                          "tool_prefix1",
                          "...");

                  connectionsTool = new ApplicationIntegrationToolset(
                          "test-project",
                          "us-central1",
                          null,
                          null,
                          "test-connection",
                          ImmutableMap.of("Issue", ImmutableList.of("GET")),
                          ImmutableList.of("ExecuteCustomQuery"),
                          "{...}",
                          "tool_prefix",
                          "...");
              }
          }
      ```

      **Note:** You can provide a service account to be used instead of using default credentials. To do this, generate a [Service Account Key](https://cloud.google.com/iam/docs/keys-create-delete#creating) and provide the correct [Application Integration and Integration Connector IAM roles](#prerequisites) to the service account. For more details about the IAM roles, refer to the [Prerequisites](#prerequisites) section.

#### 2. Add the tool to your agent

=== "Python"

    To update the `agent.py` file and add the tool to your agent, use the following code:

      ```py
          from google.adk.agents.llm_agent import LlmAgent
          from .tools import integration_tool, connector_tool

          root_agent = LlmAgent(
              model='gemini-2.0-flash',
              name='integration_agent',
              instruction="Help user, leverage the tools you have access to",
              tools=[integration_tool],
          )
      ```

=== "Java"

    To update the `agent.java` file and add the tool to your agent, use the following code:

      ```java
          import com.google.adk.agent.LlmAgent;
          import com.google.adk.tools.BaseTool;
          import com.google.common.collect.ImmutableList;

            public class MyAgent {
                public static void main(String[] args) {
                    // Assuming Tools class is defined as in the previous step
                    ImmutableList<BaseTool> tools = ImmutableList.<BaseTool>builder()
                            .add(Tools.integrationTool)
                            .add(Tools.connectionsTool)
                            .build();

                    // Finally, create your agent with the tools generated automatically.
                    LlmAgent rootAgent = LlmAgent.builder()
                            .name("science-teacher")
                            .description("Science teacher agent")
                            .model("gemini-2.0-flash")
                            .instruction(
                                    "Help user, leverage the tools you have access to."
                            )
                            .tools(tools)
                            .build();

                    // You can now use rootAgent to interact with the LLM
                    // For example, you can start a conversation with the agent.
                }
            }
        ```

**Note:** To find the list of supported entities and actions for a
        connection, use these Connector APIs: `listActions`, `listEntityTypes`.

#### 3. Expose your agent

=== "Python"

    To configure `__init__.py` to expose your agent, use the following code:

      ```py
          from . import agent
      ```

#### 4. Use your agent

=== "Python"

    To start the Google ADK Web UI and use your agent, use the following commands:

      ```shell
          # make sure to run `adk web` from your project_root_folder
          adk web
      ```
    After completing the above steps, go to [http://localhost:8000](http://localhost:8000), and choose the `my_agent` agent (which is the same as the agent folder name).

=== "Java"

    To start the Google ADK Web UI and use your agent, use the following commands:

      ```bash
          mvn install

          mvn exec:java \
              -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
              -Dexec.args="--adk.agents.source-dir=src/main/java" \
              -Dexec.classpathScope="compile"
      ```

    After completing the above steps, go to [http://localhost:8000](http://localhost:8000), and choose the `my_agent` agent (which is the same as the agent folder name).

---

## Toolbox Tools for Databases

[MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) is an
open source MCP server for databases. It was designed with enterprise-grade and
production-quality in mind. It enables you to develop tools easier, faster, and
more securely by handling the complexities such as connection pooling,
authentication, and more.

Google’s Agent Development Kit (ADK) has built in support for Toolbox. For more
information on
[getting started](https://googleapis.github.io/genai-toolbox/getting-started) or
[configuring](https://googleapis.github.io/genai-toolbox/getting-started/configure/)
Toolbox, see the
[documentation](https://googleapis.github.io/genai-toolbox/getting-started/introduction/).

![GenAI Toolbox](../assets/mcp_db_toolbox.png)

### Supported Data Sources

MCP Toolbox provides out-of-the-box toolsets for the following databases and data platforms:

#### Google Cloud

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

#### Relational & SQL Databases

*   [PostgreSQL](https://googleapis.github.io/genai-toolbox/resources/sources/postgres/) (generic)
*   [MySQL](https://googleapis.github.io/genai-toolbox/resources/sources/mysql/) (generic)
*   [Microsoft SQL Server](https://googleapis.github.io/genai-toolbox/resources/sources/mssql/) (generic)
*   [ClickHouse](https://googleapis.github.io/genai-toolbox/resources/sources/clickhouse/)
*   [TiDB](https://googleapis.github.io/genai-toolbox/resources/sources/tidb/)
*   [OceanBase](https://googleapis.github.io/genai-toolbox/resources/sources/oceanbase/)
*   [Firebird](https://googleapis.github.io/genai-toolbox/resources/sources/firebird/)
*   [SQLite](https://googleapis.github.io/genai-toolbox/resources/sources/sqlite/)
*   [YugabyteDB](https://googleapis.github.io/genai-toolbox/resources/sources/yugabytedb/)

#### NoSQL & Key-Value Stores

*   [MongoDB](https://googleapis.github.io/genai-toolbox/resources/sources/mongodb/)
*   [Couchbase](https://googleapis.github.io/genai-toolbox/resources/sources/couchbase/)
*   [Redis](https://googleapis.github.io/genai-toolbox/resources/sources/redis/)
*   [Valkey](https://googleapis.github.io/genai-toolbox/resources/sources/valkey/)
*   [Cassandra](https://googleapis.github.io/genai-toolbox/resources/sources/cassandra/)

#### Graph Databases

*   [Neo4j](https://googleapis.github.io/genai-toolbox/resources/sources/neo4j/) (with tools for Cypher queries and schema inspection)
*   [Dgraph](https://googleapis.github.io/genai-toolbox/resources/sources/dgraph/)

#### Data Platforms & Federation

*   [Looker](https://googleapis.github.io/genai-toolbox/resources/sources/looker/) (for running Looks, queries, and building dashboards via the Looker API)
*   [Trino](https://googleapis.github.io/genai-toolbox/resources/sources/trino/) (for running federated queries across multiple sources)

#### Other

*   [HTTP](https://googleapis.github.io/genai-toolbox/resources/sources/http/)

### Configure and deploy

Toolbox is an open source server that you deploy and manage yourself. For more
instructions on deploying and configuring, see the official Toolbox
documentation:

* [Installing the Server](https://googleapis.github.io/genai-toolbox/getting-started/introduction/#installing-the-server)
* [Configuring Toolbox](https://googleapis.github.io/genai-toolbox/getting-started/configure/)

### Install client SDK

ADK relies on the `toolbox-core` python package to use Toolbox. Install the
package before getting started:

```shell
pip install toolbox-core
```

### Loading Toolbox Tools

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

### Advanced Toolbox Features

Toolbox has a variety of features to make developing Gen AI tools for databases.
For more information, read more about the following features:

* [Authenticated Parameters](https://googleapis.github.io/genai-toolbox/resources/tools/#authenticated-parameters): bind tool inputs to values from OIDC tokens automatically, making it easy to run sensitive queries without potentially leaking data
* [Authorized Invocations:](https://googleapis.github.io/genai-toolbox/resources/tools/#authorized-invocations)  restrict access to use a tool based on the users Auth token
* [OpenTelemetry](https://googleapis.github.io/genai-toolbox/how-to/export_telemetry/): get metrics and tracing from Toolbox with OpenTelemetry
