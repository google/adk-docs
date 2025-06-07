# エージェントのテスト

エージェントをデプロイする前に、意図したとおりに動作するかどうかをテストする必要があります。開発環境でエージェントをテストする最も簡単な方法は、以下のコマンドでADK Web UIを使用することです。

=== "Python"

    ```py
    adk api_server
    ```

=== "Java"

    ポート番号を更新してください。

    ```java
    mvn compile exec:java \
         -Dexec.args="--adk.agents.source-dir=src/main/java/agents --server.port=8080"
    ```
    Javaでは、開発UIとAPIサーバーの両方がバンドルされています。

このコマンドはローカルのWebサーバーを起動し、そこでcURLコマンドを実行したり、APIリクエストを送信してエージェントをテストしたりできます。

## ローカルテスト

ローカルテストでは、ローカルのWebサーバーを起動し、セッションを作成し、エージェントにクエリを送信します。まず、正しい作業ディレクトリにいることを確認してください：

```console
parent_folder/
└── my_sample_agent/
    └── agent.py (または Agent.java)
```

**ローカルサーバーの起動**

次に、上記のコマンドを使用してローカルサーバーを起動します。

出力は次のようになります：

=== "Python"

    ```shell
    INFO:     Started server process
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
    ```

=== "Java"

    ```shell
    2025-05-13T23:32:08.972-06:00  INFO 37864 --- [ebServer.main()] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 8080 (http) with context path '/'
    2025-05-13T23:32:08.980-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : Started AdkWebServer in 1.15 seconds (process running for 2.877)
    2025-05-13T23:32:08.981-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : AdkWebServer application started successfully.
    ```

これでサーバーがローカルで実行されています。後続のすべてのコマンドで正しい**_ポート番号_**を使用してください。

**新しいセッションの作成**

APIサーバーが実行中のまま、新しいターミナルウィンドウまたはタブを開き、以下のコマンドを使用してエージェントとの新しいセッションを作成します：

```shell
curl -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"state": {"key1": "value1", "key2": 42}}'
```

何が起きているか分解してみましょう：

*   `http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123`: これは、エージェントフォルダの名前である`my_sample_agent`エージェントに対して、ユーザーID（`u_123`）とセッションID（`s_123`）で新しいセッションを作成します。`my_sample_agent`をあなたのエージェントフォルダの名前に置き換えることができます。`u_123`を特定のユーザーIDに、`s_123`を特定のセッションIDに置き換えることができます。
*   `{"state": {"key1": "value1", "key2": 42}}`: これはオプションです。これを使用して、セッション作成時にエージェントの既存の状態（dict）をカスタマイズできます。

これが正常に作成された場合、セッション情報が返されます。出力は次のようになります：

```shell
{"id":"s_123","appName":"my_sample_agent","userId":"u_123","state":{"state":{"key1":"value1","key2":42}},"events":[],"lastUpdateTime":1743711430.022186}
```

!!! info

    まったく同じユーザーIDとセッションIDで複数のセッションを作成することはできません。試みると、`{"detail":"Session already exists: s_123"}`のような応答が表示される場合があります。これを修正するには、そのセッション（例：`s_123`）を削除するか、別のセッションIDを選択します。

**クエリの送信**

エージェントにPOST経由でクエリを送信するには、`/run`または`/run_sse`の2つのルートがあります。

*   `POST http://localhost:8000/run`: すべてのイベントをリストとして収集し、一度にリスト全体を返します。ほとんどのユーザーに適しています（どちらを使えばいいかわからない場合は、こちらを使用することをお勧めします）。
*   `POST http://localhost:8000/run_sse`: サーバー送信イベント（Server-Sent-Events）として、イベントオブジェクトのストリームを返します。イベントが利用可能になり次第通知を受けたい場合に適しています。`/run_sse`では、`streaming`を`true`に設定してトークンレベルのストリーミングを有効にすることもできます。

**`/run`の使用**

```shell
curl -X POST http://localhost:8000/run \
-H "Content-Type: application/json" \
-d '{
"appName": "my_sample_agent",
"userId": "u_123",
"sessionId": "s_123",
"newMessage": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
}
}'
```

`/run`を使用すると、イベントの完全な出力がリストとして同時に表示されます。これは次のようになります：

```shell
[{"content":{"parts":[{"functionCall":{"id":"af-e75e946d-c02a-4aad-931e-49e4ab859838","args":{"city":"new york"},"name":"get_weather"}}],"role":"model"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"longRunningToolIds":[],"id":"2Btee6zW","timestamp":1743712220.385936},{"content":{"parts":[{"functionResponse":{"id":"af-e75e946d-c02a-4aad-931e-49e4ab859838","name":"get_weather","response":{"status":"success","report":"The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}}}],"role":"user"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"PmWibL2m","timestamp":1743712221.895042},{"content":{"parts":[{"text":"OK. The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).\n"}],"role":"model"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"sYT42eVC","timestamp":1743712221.899018}]
```

**`/run_sse`の使用**

```shell
curl -X POST http://localhost:8000/run_sse \
-H "Content-Type: application/json" \
-d '{
"appName": "my_sample_agent",
"userId": "u_123",
"sessionId": "s_123",
"newMessage": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
},
"streaming": false
}'
```

`streaming`を`true`に設定してトークンレベルのストリーミングを有効にすると、応答が複数のチャンクで返され、出力は次のようになります：

```shell
data: {"content":{"parts":[{"functionCall":{"id":"af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d","args":{"city":"new york"},"name":"get_weather"}}],"role":"model"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"longRunningToolIds":[],"id":"ptcjaZBa","timestamp":1743712255.313043}

data: {"content":{"parts":[{"functionResponse":{"id":"af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d","name":"get_weather","response":{"status":"success","report":"The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}}}],"role":"user"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"5aocxjaq","timestamp":1743712257.387306}

data: {"content":{"parts":[{"text":"OK. The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).\n"}],"role":"model"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"rAnWGSiV","timestamp":1743712257.391317}
```

!!! info

    `/run_sse`を使用している場合、各イベントが利用可能になり次第表示されるはずです。

## 統合

ADKは、[コールバック](../callbacks/index.md)を使用してサードパーティの可観測性ツールと統合します。これらの統合は、エージェントの呼び出しと対話の詳細なトレースをキャプチャし、これは振る舞いの理解、問題のデバッグ、パフォーマンスの評価に不可欠です。

*   [Comet Opik](https://github.com/comet-ml/opik)は、[ADKをネイティブにサポート](https://www.comet.com/docs/opik/tracing/integrations/adk)するオープンソースのLLM可観測性および評価プラットフォームです。

## エージェントのデプロイ

エージェントのローカルでの動作を確認したら、エージェントのデプロイに進む準備が整いました！エージェントをデプロイするには、いくつかの方法があります：

*   [Agent Engine](../deploy/agent-engine.md)にデプロイする。これは、Google Cloud上のVertex AIのマネージドサービスにADKエージェントをデプロイする最も簡単な方法です。
*   [Cloud Run](../deploy/cloud-run.md)にデプロイし、Google Cloud上のサーバーレスアーキテクチャを使用してエージェントのスケーリングと管理を完全に制御します。