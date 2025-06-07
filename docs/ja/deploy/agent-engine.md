# Vertex AI Agent Engineへのデプロイ

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="Vertex AI Agent Engineは現在Pythonのみをサポートしています。" }

[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)は、開発者が本番環境でAIエージェントをデプロイ、管理、スケーリングできるようにする、フルマネージドのGoogle Cloudサービスです。Agent Engineが本番環境でのエージェントのスケーリングに必要なインフラストラクチャを処理するため、開発者はインテリジェントでインパクトのあるアプリケーションの作成に集中できます。

```python
from vertexai import agent_engines

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
    ]
)
```

## Vertex AI SDKのインストール

Agent Engineは、Vertex AI SDK for Pythonの一部です。詳細については、[Agent Engineクイックスタートドキュメント](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/quickstart)をご覧ください。

### Vertex AI SDKのインストール

```shell
pip install google-cloud-aiplatform[adk,agent_engines]
```

!!!info
    Agent Engineがサポートしているのは、Pythonバージョン >=3.9 かつ <=3.12 のみです。

### 初期化

```py
import vertexai

PROJECT_ID = "your-project-id"  # あなたのプロジェクトID
LOCATION = "us-central1"  # リージョン
STAGING_BUCKET = "gs://your-google-cloud-storage-bucket"  # あなたのGoogle Cloud Storageバケット

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)
```

`LOCATION`については、[Agent Engineでサポートされているリージョン](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview#supported-regions)のリストを確認してください。

### エージェントの作成

以下のサンプルエージェントを使用できます。このエージェントには2つのツール（天気の取得、指定された都市の時刻の取得）があります。

```python
--8<-- "examples/python/snippets/get-started/multi_tool_agent/agent.py"
```

### Agent Engine向けにエージェントを準備する

`reasoning_engines.AdkApp()`を使用してエージェントをラップし、Agent Engineにデプロイできるようにします。

```py
from vertexai.preview import reasoning_engines

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)
```

### エージェントをローカルで試す

Agent Engineにデプロイする前に、ローカルで試すことができます。

#### セッションの作成（ローカル）

```py
session = app.create_session(user_id="u_123")
session
```

`create_session`の期待される出力（ローカル）:

```console
Session(id='c6a33dae-26ef-410c-9135-b434a528291f', app_name='default-app-name', user_id='u_123', state={}, events=[], last_update_time=1743440392.8689594)
```

#### セッションの一覧表示（ローカル）

```py
app.list_sessions(user_id="u_123")
```

`list_sessions`の期待される出力（ローカル）:

```console
ListSessionsResponse(session_ids=['c6a33dae-26ef-410c-9135-b434a528291f'])
```

#### 特定のセッションの取得（ローカル）

```py
session = app.get_session(user_id="u_123", session_id=session.id)
session
```

`get_session`の期待される出力（ローカル）:

```console
Session(id='c6a33dae-26ef-410c-9135-b434a528291f', app_name='default-app-name', user_id='u_123', state={}, events=[], last_update_time=1743681991.95696)
```

#### エージェントへのクエリ送信（ローカル）

```py
for event in app.stream_query(
    user_id="u_123",
    session_id=session.id,
    message="whats the weather in new york",
):
print(event)
```

`stream_query`の期待される出力（ローカル）:

```console
{'parts': [{'function_call': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```

### エージェントをAgent Engineにデプロイする

```python
from vertexai import agent_engines

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]"   
    ]
)
```

このステップは完了までに数分かかることがあります。デプロイされた各エージェントには一意の識別子があります。次のコマンドを実行して、デプロイされたエージェントの`resource_name`識別子を取得できます。

```python
remote_app.resource_name
```

応答は次のような文字列になります。

```
f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"
```

追加の詳細については、Agent Engineドキュメントの[エージェントのデプロイ](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy)および[デプロイ済みエージェントの管理](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)をご覧ください。

### Agent Engine上のエージェントを試す

#### セッションの作成（リモート）

```py
remote_session = remote_app.create_session(user_id="u_456")
remote_session
```

`create_session`の期待される出力（リモート）:

```console
{'events': [],
'user_id': 'u_456',
'state': {},
'id': '7543472750996750336',
'app_name': '7917477678498709504',
'last_update_time': 1743683353.030133}
```

`id`はセッションID、`app_name`はAgent EngineにデプロイされたエージェントのリソースIDです。

#### セッションの一覧表示（リモート）

```py
remote_app.list_sessions(user_id="u_456")
```

#### 特定のセッションの取得（リモート）

```py
remote_app.get_session(user_id="u_456", session_id=remote_session["id"])
```

!!!note
    ローカルでエージェントを使用する場合、セッションIDは`session.id`に保存されますが、Agent Engine上でリモートでエージェントを使用する場合、セッションIDは`remote_session["id"]`に保存されます。

#### エージェントへのクエリ送信（リモート）

```py
for event in remote_app.stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message="whats the weather in new york",
):
    print(event)
```

`stream_query`の期待される出力（リモート）:

```console
{'parts': [{'function_call': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```



## クリーンアップ

作業が完了したら、クラウドリソースをクリーンアップすることをお勧めします。
デプロイされたAgent Engineインスタンスを削除することで、Google Cloudアカウントでの予期せぬ
課金を避けることができます。

```python
remote_app.delete(force=True)
```

`force=True`は、セッションなど、デプロイされたエージェントから生成された子リソースも削除します。