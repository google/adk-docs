# Google Cloud ツール

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="この機能は現在Pythonでのみサポートされています。Javaのサポートは計画中/近日公開予定です。" }

Google Cloudツールを使用すると、エージェントをGoogle Cloudの製品やサービスに簡単に接続できます。わずか数行のコードでこれらのツールを使用して、エージェントを以下に接続できます。

*   開発者がApigeeでホストする**任意のカスタムAPI**。
*   Salesforce、Workday、SAPなどのエンタープライズシステムへの**100以上**の**事前構築済みコネクタ**。
*   Application Integrationを使用して構築された**自動化ワークフロー**。
*   データベース向けMCP Toolboxを使用して、Spanner、AlloyDB、Postgresなどの**データベース**。

![Google Cloud ツール](../assets/google_cloud_tools.svg)

## Apigee API Hub ツール

**ApiHubToolset**を使用すると、Apigee API Hubからドキュメント化された任意のAPIを、わずか数行のコードでツールに変換できます。このセクションでは、APIへの安全な接続のための認証設定を含む、ステップバイステップの手順を説明します。

**前提条件**

1.  [ADKをインストールする](../get-started/installation.md)
2.  [Google Cloud CLI](https://cloud.google.com/sdk/docs/install?db=bigtable-docs#installation_instructions)をインストールする。
3.  ドキュメント化された（つまりOpenAPI仕様を持つ）APIを含む
    [Apigee API Hub](https://cloud.google.com/apigee/docs/apihub/what-is-api-hub)
    インスタンス
4.  プロジェクト構造を設定し、必要なファイルを作成する

```console
project_root_folder
 |
 `-- my_agent
     |-- .env
     |-- __init__.py
     |-- agent.py
     `__ tool.py
```

### API Hubツールセットの作成

注：このチュートリアルにはエージェントの作成が含まれています。すでにエージェントをお持ちの場合は、これらの手順の一部のみを従う必要があります。

1.  アクセストークンを取得し、`APIHubToolset`がAPI Hub APIから仕様を取得できるようにします。
    ターミナルで次のコマンドを実行します。

    ```shell
    gcloud auth print-access-token
    # 'ya29....' のようなアクセストークンが出力されます
    ```

2.  使用するアカウントに必要な権限があることを確認します。
    事前定義されたロール`roles/apihub.viewer`を使用するか、以下の権限を割り当てることができます。

    1.  **apihub.specs.get (必須)**
    2.  apihub.apis.get (任意)
    3.  apihub.apis.list (任意)
    4.  apihub.versions.get (任意)
    5.  apihub.versions.list (任意)
    6.  apihub.specs.list (任意)

3.  `APIHubToolset`を使用してツールを作成します。以下を`tools.py`に追加します。

    APIが認証を必要とする場合は、ツールの認証を設定する必要があります。
    以下のコードサンプルは、APIキーを設定する方法を示しています。ADKはトークンベースの認証（APIキー、ベアラートークン）、サービスアカウント、およびOpenID Connectをサポートしています。近日中に、さまざまなOAuth2フローのサポートを追加する予定です。

    ```py
    from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
    from google.adk.tools.apihub_tool.apihub_toolset import APIHubToolset

    # APIの認証を提供します。APIが認証を必要としない場合は不要です。
    auth_scheme, auth_credential = token_to_scheme_credential(
        "apikey", "query", "apikey", apikey_credential_str
    )

    sample_toolset_with_auth = APIHubToolset(
        name="apihub-sample-tool",
        description="サンプルツール",
        access_token="...",  # ステップ1で生成したアクセストークンをコピー
        apihub_resource_name="...", # API Hubのリソース名
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
    )
    ```

    本番環境へのデプロイでは、アクセストークンの代わりにサービスアカウントを使用することをお勧めします。上記のコードスニペットでは、トークンの代わりに`service_account_json=service_account_cred_json_str`を使用し、サービスアカウントの認証情報を提供してください。

    `apihub_resource_name`については、APIに使用されているOpenAPI仕様の特定のIDがわかっている場合は、
    `` `projects/my-project-id/locations/us-west1/apis/my-api-id/versions/version-id/specs/spec-id` `` を使用します。
    ツールセットがAPIから利用可能な最初の仕様を自動的に取得するようにしたい場合は、
    `` `projects/my-project-id/locations/us-west1/apis/my-api-id` `` を使用します。

4.  エージェントファイル[Agent.py](http://Agent.py)を作成し、作成したツールをエージェントの定義に追加します。

    ```py
    from google.adk.agents.llm_agent import LlmAgent
    from .tools import sample_toolset

    root_agent = LlmAgent(
        model='gemini-2.0-flash',
        name='enterprise_assistant',
        instruction='ユーザーを助け、アクセスできるツールを活用してください',
        tools=sample_toolset.get_tools(),
    )
    ```

5.  `__init__.py`を設定してエージェントを公開します。

    ```py
    from . import agent
    ```

6.  Google ADK Web UIを起動し、エージェントを試します。

    ```shell
    # `adk web` は project_root_folder から実行してください
    adk web
    ```

   次に、[http://localhost:8000](http://localhost:8000)にアクセスして、Web UIからエージェントを試します。

---

## Application Integration ツール

**ApplicationIntegrationToolset**を使用すると、Integration Connectorの100以上の事前構築済みコネクタ（Salesforce, ServiceNow, JIRA, SAPなど）を使用して、エージェントをエンタープライズアプリケーションにシームレスかつ安全に、管理された方法で接続できます。オンプレミスとSaaSの両方のアプリケーションをサポートしています。さらに、Application IntegrationのワークフローをADKエージェントにツールとして提供することで、既存のApplication Integrationプロセス自動化をエージェントワークフローに変換できます。

**前提条件**

1.  [ADKをインストールする](../get-started/installation.md)
2.  エージェントで使用したい既存の
    [Application Integration](https://cloud.google.com/application-integration/docs/overview)
    ワークフローまたは
    [Integrations Connector](https://cloud.google.com/integration-connectors/docs/overview)
    接続
3.  デフォルトの認証情報でツールを使用するには、Google Cloud CLIをインストールしておく必要があります。
    [インストールガイド](https://cloud.google.com/sdk/docs/install#installation_instructions)を参照してください*。*

   *実行:*

   ```shell
   gcloud config set project <project-id>
   gcloud auth application-default login
   gcloud auth application-default set-quota-project <project-id>
   ```

5.  プロジェクト構造を設定し、必要なファイルを作成します。

    ```console
    project_root_folder
    |-- .env
    `-- my_agent
        |-- __init__.py
        |-- agent.py
        `__ tools.py
    ```

エージェントを実行するときは、`project_root_folder`で`adk web`を実行してください。

### Integration Connectorsの使用

[Integration Connectors](https://cloud.google.com/integration-connectors/docs/overview)を使用して、エージェントをエンタープライズアプリケーションに接続します。

**前提条件**

1.  Integration Connectorsからコネクタを使用するには、接続と同じリージョンで、「QUICK SETUP」ボタンをクリックしてApplication Integrationを[プロビジョニング](https://console.cloud.google.com/integrations)する必要があります。

   ![Google Cloud ツール](../assets/application-integration-overview.png)
   
2.  テンプレートライブラリから[Connection Tool](https://console.cloud.google.com/integrations/templates/connection-tool/locations/us-central1)テンプレートに移動し、「USE TEMPLATE」ボタンをクリックします。

    ![Google Cloud ツール](../assets/use-connection-tool-template.png)
   
3.  Integration Nameに**ExecuteConnection**と入力し（この統合名のみを使用することが必須です）、接続リージョンと同じリージョンを選択します。「CREATE」をクリックします。

4.  Application Integrationエディタの「PUBLISH」ボタンを使用して統合を公開します。

    ![Google Cloud ツール](../assets/publish-integration.png)  

**手順:**

1.  `tools.py`ファイル内に`ApplicationIntegrationToolset`を使用してツールを作成します。

    ```py
    from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset

    connector_tool = ApplicationIntegrationToolset(
        project="test-project", # TODO: 接続のGCPプロジェクトに置き換えてください
        location="us-central1", #TODO: 接続のロケーションに置き換えてください
        connection="test-connection", #TODO: 接続名に置き換えてください
        entity_operations={"Entity_One": ["LIST","CREATE"], "Entity_Two": []},#空のリストはエンティティ上のすべての操作がサポートされていることを意味します。
        actions=["action1"], #TODO: アクションに置き換えてください
        service_account_credentials='{...}', # 任意。サービスアカウントキーの文字列化されたJSON
        tool_name_prefix="tool_prefix2",
        tool_instructions="..."
    )
    ```

    注：
    -   [サービスアカウントキー](https://cloud.google.com/iam/docs/keys-create-delete#creating)を生成し、サービスアカウントに適切なApplication IntegrationとIntegration ConnectorのIAMロールを付与することで、デフォルトの認証情報の代わりに使用するサービスアカウントを提供できます。
    -   接続でサポートされているエンティティとアクションのリストを見つけるには、コネクタAPIを使用します:
        [listActions](https://cloud.google.com/integration-connectors/docs/reference/rest/v1/projects.locations.connections.connectionSchemaMetadata/listActions) または 
        [listEntityTypes](https://cloud.google.com/integration-connectors/docs/reference/rest/v1/projects.locations.connections.connectionSchemaMetadata/listEntityTypes)

    `ApplicationIntegrationToolset`は、Integration Connectors向けの動的なOAuth2認証のために`auth_scheme`と`auth_credential`の提供もサポートするようになりました。これを使用するには、`tools.py`ファイル内に次のようなツールを作成します。

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
                      "Google Cloud Platformサービス全体のデータを表示および管理します"
                  ),
                  "https://www.googleapis.com/auth/calendar.readonly": "カレンダーを表示します"
              },
          }
      },
    }

    oauth_scheme = dict_to_auth_scheme(oauth2_data_google_cloud)
    
    auth_credential = AuthCredential(
      auth_type=AuthCredentialTypes.OAUTH2,
      oauth2=OAuth2Auth(
          client_id="...", #TODO: client_idに置き換えてください
          client_secret="...", #TODO: client_secretに置き換えてください
      ),
    )

    connector_tool = ApplicationIntegrationToolset(
        project="test-project", # TODO: 接続のGCPプロジェクトに置き換えてください
        location="us-central1", #TODO: 接続のロケーションに置き換えてください
        connection="test-connection", #TODO: 接続名に置き換えてください
        entity_operations={"Entity_One": ["LIST","CREATE"], "Entity_Two": []},#空のリストはエンティティ上のすべての操作がサポートされていることを意味します。
        actions=["GET_calendars/%7BcalendarId%7D/events"], #TODO: アクションに置き換えてください。これはイベントを一覧表示するためのものです。
        service_account_credentials='{...}', # 任意。サービスアカウントキーの文字列化されたJSON
        tool_name_prefix="tool_prefix2",
        tool_instructions="...",
        auth_scheme=oauth_scheme,
        auth_credential=auth_credential
    )
    ```


2.  ツールをエージェントに追加します。`agent.py`ファイルを更新します。

    ```py
    from google.adk.agents.llm_agent import LlmAgent
    from .tools import connector_tool

    root_agent = LlmAgent(
        model='gemini-2.0-flash',
        name='connector_agent',
        instruction="ユーザーを助け、アクセスできるツールを活用してください",
        tools=[connector_tool],
    )
    ```

3.  `__init__.py`を設定してエージェントを公開します。

    ```py
    from . import agent
    ```

4.  Google ADK Web UIを起動し、エージェントを試します。

    ```shell
    # `adk web` は project_root_folder から実行してください
    adk web
    ```

   次に、[http://localhost:8000](http://localhost:8000)にアクセスし、
   my\_agentエージェント（エージェントフォルダ名と同じ）を選択します。

### App Integrationワークフローの使用

既存の
[Application Integration](https://cloud.google.com/application-integration/docs/overview)
ワークフローをエージェントのツールとして使用するか、新しいものを作成します。

**手順:**

1.  `tools.py`ファイル内に`ApplicationIntegrationToolset`を使用してツールを作成します。

    ```py
    integration_tool = ApplicationIntegrationToolset(
        project="test-project", # TODO: 接続のGCPプロジェクトに置き換えてください
        location="us-central1", #TODO: 接続のロケーションに置き換えてください
        integration="test-integration", #TODO: 統合名に置き換えてください
        triggers=["api_trigger/test_trigger"],#TODO: トリガーIDに置き換えてください。空のリストは統合内のすべてのAPIトリガーが考慮されることを意味します。
        service_account_credentials='{...}', #任意。サービスアカウントキーの文字列化されたJSON
        tool_name_prefix="tool_prefix1",
        tool_instructions="..."
    )
    ```

    注：[サービスアカウントキー](https://cloud.google.com/iam/docs/keys-create-delete#creating)を生成し、サービスアカウントに適切なApplication IntegrationとIntegration ConnectorのIAMロールを付与することで、デフォルトの認証情報の代わりに使用するサービスアカウントを提供できます。

2.  ツールをエージェントに追加します。`agent.py`ファイルを更新します。

    ```py
    from google.adk.agents.llm_agent import LlmAgent
    from .tools import integration_tool, connector_tool

    root_agent = LlmAgent(
        model='gemini-2.0-flash',
        name='integration_agent',
        instruction="ユーザーを助け、アクセスできるツールを活用してください",
        tools=[integration_tool],
    )
    ```

3.  `__init__.py`を設定してエージェントを公開します。

    ```py
    from . import agent
    ```

4.  Google ADK Web UIを起動し、エージェントを試します。

    ```shell
    # `adk web` は project_root_folder から実行してください
    adk web
    ```

    次に、[http://localhost:8000](http://localhost:8000)にアクセスし、
    my\_agentエージェント（エージェントフォルダ名と同じ）を選択します。

---

## データベース向けToolboxツール

[MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox)は、
データベース向けのオープンソースMCPサーバーです。エンタープライズグレードと
本番品質を念頭に置いて設計されています。接続プーリング、
認証などの複雑さを処理することで、ツールの開発をより簡単に、より速く、
より安全に行うことができます。

GoogleのAgent Development Kit (ADK)は、Toolboxを組み込みでサポートしています。
Toolboxの[利用開始](https://googleapis.github.io/genai-toolbox/getting-started)や
[設定](https://googleapis.github.io/genai-toolbox/getting-started/configure/)
に関する詳細については、
[ドキュメント](https://googleapis.github.io/genai-toolbox/getting-started/introduction/)を参照してください。

![GenAI Toolbox](../assets/mcp_db_toolbox.png)

### 設定とデプロイ

Toolboxは、自分でデプロイして管理するオープンソースサーバーです。
デプロイと設定に関する詳細な手順については、公式のToolboxドキュメントを参照してください。

*   [サーバーのインストール](https://googleapis.github.io/genai-toolbox/getting-started/introduction/#installing-the-server)
*   [Toolboxの設定](https://googleapis.github.io/genai-toolbox/getting-started/configure/)

### クライアントSDKのインストール

ADKは、Toolboxを使用するために`toolbox-core` Pythonパッケージに依存しています。
始める前にパッケージをインストールしてください。

```shell
pip install toolbox-core
```

### Toolboxツールの読み込み

Toolboxサーバーが設定され、稼働したら、
ADKを使用してサーバーからツールを読み込むことができます。

```python
from google.adk.agents import Agent
from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("https://127.0.0.1:5000")

# 特定のツールセットを読み込む
tools = toolbox.load_toolset('my-toolset-name'),
# 単一のツールを読み込む
tools = toolbox.load_tool('my-tool-name'),

root_agent = Agent(
    ...,
    tools=tools # Agentにツールのリストを提供する

)
```

### 高度なToolbox機能

Toolboxには、データベース向けのGen AIツール開発を容易にするさまざまな機能があります。
詳細については、以下の機能についてお読みください。

*   [認証済みパラメータ](https://googleapis.github.io/genai-toolbox/resources/tools/#authenticated-parameters): ツールの入力をOIDCトークンの値に自動的にバインドし、データ漏洩の可能性なしに機密性の高いクエリを簡単に実行できます。
*   [認可された呼び出し](https://googleapis.github.io/genai-toolbox/resources/tools/#authorized-invocations): ユーザーのAuthトークンに基づいてツールの使用を制限します。
*   [OpenTelemetry](https://googleapis.github.io/genai-toolbox/how-to/export_telemetry/): OpenTelemetryを使用してToolboxからメトリクスとトレースを取得します。