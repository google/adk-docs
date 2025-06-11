# カスタムオーディオストリーミングアプリ (SSE) {#custom-streaming}

この記事では、ADKストリーミングと[FastAPI](https://fastapi.tiangolo.com/)で構築されたカスタム非同期Webアプリケーションのサーバーおよびクライアントコードの概要を説明します。このアプリは、サーバー送信イベント（Server-Sent Events, SSE）を用いて、リアルタイムの双方向オーディオおよびテキスト通信を可能にします。主な機能は以下の通りです。

**サーバーサイド (Python/FastAPI)**:
- FastAPIとADKの統合
- リアルタイムストリーミングのためのサーバー送信イベント (SSE)
- 分離されたユーザーコンテキストによるセッション管理
- テキストとオーディオ両方の通信モードをサポート
- 根拠のある回答のためのGoogle Searchツールの統合

**クライアントサイド (JavaScript/Web Audio API)**:
- SSEとHTTP POSTによるリアルタイム双方向通信
- AudioWorkletプロセッサを使用した高度なオーディオ処理
- テキストとオーディオ間のシームレスなモード切り替え
- 自動再接続とエラーハンドリング
- オーディオデータ転送のためのBase64エンコーディング

このサンプルの[WebSocket](custom-streaming-ws.md)版も利用可能です。

## 1. ADKのインストール {#1.-setup-installation}

仮想環境の作成と有効化 (推奨):

```bash
# 作成
python -m venv .venv
# 有効化 (新しいターミナルごとに実行)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

ADKのインストール:

```bash
pip install --upgrade google-adk==1.2.1
```

次のコマンドで`SSL_CERT_FILE`変数を設定します。

```shell
export SSL_CERT_FILE=$(python -m certifi)
```

サンプルコードのダウンロード:

```bash
git clone --no-checkout https://github.com/google/adk-docs.git
cd adk-docs
git sparse-checkout init --cone
git sparse-checkout set examples/python/snippets/streaming/adk-streaming
git checkout main
cd examples/python/snippets/streaming/adk-streaming/app
```

このサンプルコードには、以下のファイルとフォルダが含まれています:

```console
adk-streaming/
└── app/ # Webアプリのフォルダ
    ├── .env # Gemini APIキー / Google CloudプロジェクトID
    ├── main.py # FastAPI Webアプリ
    ├── static/ # 静的コンテンツのフォルダ
    |   ├── js # JavaScriptファイルのフォルダ (app.jsを含む)
    |   └── index.html # Webクライアントページ
    └── google_search_agent/ # エージェントのフォルダ
        ├── __init__.py # Pythonパッケージ
        └── agent.py # エージェントの定義
```

## 2. プラットフォームのセットアップ {#2.-set-up-the-platform}

サンプルアプリを実行するには、Google AI StudioまたはGoogle Cloud Vertex AIのいずれかのプラットフォームを選択します。

=== "Gemini - Google AI Studio"
    1. [Google AI Studio](https://aistudio.google.com/apikey)でAPIキーを取得します。
    2. (`app/`内にある) **`.env`** ファイルを開き、次のコードをコピー＆ペーストします。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3. `PASTE_YOUR_ACTUAL_API_KEY_HERE`を実際の`APIキー`に置き換えてください。

=== "Gemini - Google Cloud Vertex AI"
    1. 既存の[Google Cloud](https://cloud.google.com/?e=48754805&hl=en)アカウントとプロジェクトが必要です。
        * [Google Cloudプロジェクトのセットアップ](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
        * [gcloud CLIのセットアップ](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
        * ターミナルから`gcloud auth login`を実行してGoogle Cloudに認証します。
        * [Vertex AI APIの有効化](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)。
    2. (`app/`内にある) **`.env`** ファイルを開きます。次のコードをコピー＆ペーストし、プロジェクトIDとロケーションを更新してください。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=PASTE_YOUR_ACTUAL_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=us-central1
        ```

## 3. ストリーミングアプリとの対話 {#3.-interact-with-your-streaming-app}

1. **正しいディレクトリへの移動:**

   エージェントを効果的に実行するために、**appフォルダ (`adk-streaming/app`)** にいることを確認してください。

2. **FastAPIの起動**: 次のコマンドを実行してCLIインターフェースを起動します。

```console
uvicorn main:app --reload
```

3. **テキストモードでアプリにアクセス:** アプリが起動すると、ターミナルにローカルURL（例: [http://localhost:8000](http://localhost:8000)）が表示されます。このリンクをクリックして、ブラウザでUIを開きます。

次のようなUIが表示されます:

![ADK Streaming app](../assets/adk-streaming-text.png)

`What time is it now?` (今何時？) のように質問してみてください。エージェントはGoogle Searchを使ってあなたの質問に答えます。UIにはエージェントの応答がストリーミングテキストとして表示されるのがわかります。エージェントがまだ応答している最中でも、いつでもメッセージを送信できます。これはADKストリーミングの双方向通信機能を示しています。

4. **オーディオモードでアプリにアクセス:** `Start Audio`ボタンをクリックします。アプリはオーディオモードでサーバーに再接続し、初回はUIに次のようなダイアログが表示されます:

![ADK Streaming app](../assets/adk-streaming-audio-dialog.png)

`(このサイトにアクセスしている間) 許可`をクリックすると、ブラウザの上部にマイクのアイコンが表示されます:

![ADK Streaming app](../assets/adk-streaming-mic.png)

これで、エージェントと音声で会話できるようになります。`What time is it now?` のような質問を音声で行うと、エージェントも音声で応答するのが聞こえます。ADKのストリーミングは[複数の言語](https://ai.google.dev/gemini-api/docs/live#supported-languages)をサポートしているため、サポートされている言語で質問すれば、その言語で応答することもできます。

5. **コンソールログの確認**

Chromeブラウザを使用している場合、右クリックして`検証 (Inspect)`を選択し、デベロッパーツールを開きます。`コンソール (Console)`タブでは、`[CLIENT TO AGENT]`や`[AGENT TO CLIENT]`のような送受信オーディオデータを確認できます。これは、ブラウザとサーバー間でオーディオデータがストリーミングされていることを示します。

同時に、アプリサーバーのコンソールには、次のようなログが表示されるはずです:

```
Client #90766266 connected via SSE, audio mode: false
INFO:     127.0.0.1:52692 - "GET /events/90766266?is_audio=false HTTP/1.1" 200 OK
[CLIENT TO AGENT]: hi
INFO:     127.0.0.1:52696 - "POST /send/90766266 HTTP/1.1" 200 OK
[AGENT TO CLIENT]: text/plain: {'mime_type': 'text/plain', 'data': 'Hi'}
[AGENT TO CLIENT]: text/plain: {'mime_type': 'text/plain', 'data': ' there! How can I help you today?\n'}
[AGENT TO CLIENT]: {'turn_complete': True, 'interrupted': None}
```

これらのコンソールログは、独自のストリーミングアプリケーションを開発する際に重要です。多くの場合、ブラウザとサーバー間の通信障害が、ストリーミングアプリケーションのバグの主な原因となります。

6. **トラブルシューティングのヒント**

- **SSHプロキシ経由でブラウザがサーバーに接続できない場合:** 様々なクラウドサービスで使用されるSSHプロキシは、SSEでは動作しないことがあります。ローカルのラップトップを使用するなど、SSHプロキシなしで試すか、[WebSocket](custom-streaming-ws.md)版をお試しください。
- **`gemini-2.0-flash-exp`モデルが動作しない場合:** アプリサーバーのコンソールで`gemini-2.0-flash-exp`モデルの利用可能性に関するエラーが表示された場合は、`app/google_search_agent/agent.py`の6行目を`gemini-2.0-flash-live-001`に置き換えてみてください。

## 4. エージェントの定義

`google_search_agent`フォルダにあるエージェント定義コード`agent.py`に、エージェントのロジックを記述します:

```py
from google.adk.agents import Agent
from google.adk.tools import google_search  # ツールをインポート

root_agent = Agent(
   name="google_search_agent",
   model="gemini-2.0-flash-exp", # このモデルが動作しない場合は、以下を試してください
   #model="gemini-2.0-flash-live-001",
   description="Agent to answer questions using Google Search.",
   instruction="Answer the question using the Google Search tool.",
   tools=[google_search],
)
```

[Google Searchによるグラウンディング](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search)機能がいかに簡単に統合されたかをご覧ください。`Agent`クラスと`google_search`ツールが、LLMとの複雑なやり取りや検索APIによるグラウンディングを処理するため、開発者はエージェントの*目的*と*振る舞い*に集中できます。

![intro_components.png](../assets/quickstart-streaming-tool.png)

このサーバーとクライアントのアーキテクチャは、適切なセッション分離とリソース管理により、WebクライアントとAIエージェント間のリアルタイムな双方向通信を可能にします。

## 5. サーバーサイドのコード概要 {#5.-server-side-code-overview}

FastAPIサーバーは、WebクライアントとAIエージェント間のリアルタイム通信を提供します。

### 双方向通信の概要 {#4.-bidi-comm-overview}

#### クライアントからエージェントへのフロー:
1. **接続の確立** - クライアントが`/events/{user_id}`へのSSE接続を開くと、セッションが作成され、リクエストキューが`active_sessions`に保存されます。
2. **メッセージの送信** - クライアントは`mime_type`と`data`を含むJSONペイロードを`/send/{user_id}`にPOSTします。
3. **キューの処理** - サーバーはセッションの`live_request_queue`を取得し、`send_content()`または`send_realtime()`を介してエージェントにメッセージを転送します。

#### エージェントからクライアントへのフロー:
1. **イベントの生成** - エージェントはリクエストを処理し、`live_events`非同期ジェネレータを通じてイベントを生成します。
2. **ストリームの処理** - `agent_to_client_sse()`はイベントをフィルタリングし、SSE互換のJSON形式にフォーマットします。
3. **リアルタイム配信** - イベントは、適切なSSEヘッダを持つ永続的なHTTP接続を介してクライアントにストリーミングされます。

#### セッション管理:
- **ユーザーごとの分離** - 各ユーザーは`active_sessions`辞書に保存される一意のセッションを取得します。
- **ライフサイクル管理** - 接続が切断されると、セッションは自動的にクリーンアップされ、リソースも適切に破棄されます。
- **同時接続のサポート** - 複数のユーザーが同時にアクティブなセッションを持つことができます。

#### エラーハンドリング:
- **セッションの検証** - POSTリクエストは処理前にセッションの存在を検証します。
- **ストリームの耐障害性** - SSEストリームは例外を処理し、自動的にクリーンアップを実行します。
- **接続の復旧** - クライアントはSSE接続を再確立することで再接続できます。

### エージェントのセッション管理

`start_agent_session()`関数は、分離されたAIエージェントセッションを作成します:

```py
async def start_agent_session(user_id, is_audio=False):
    """エージェントセッションを開始します"""

    # Runnerを作成
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=root_agent,
    )

    # Sessionを作成
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,  # 実際のユーザーIDに置き換える
    )

    # 応答モダリティを設定
    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(response_modalities=[modality])

    # このセッション用のLiveRequestQueueを作成
    live_request_queue = LiveRequestQueue()

    # エージェントセッションを開始
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue
```

- **InMemoryRunnerのセットアップ** - アプリ名「ADK Streaming example」とGoogle Searchエージェントを使用して、エージェントのライフサイクルをメモリ内で管理するランナーインスタンスを作成します。

- **セッションの作成** - `runner.session_service.create_session()`を使用してユーザーIDごとに一意のセッションを確立し、複数の同時ユーザーを可能にします。

- **応答モダリティの設定** - `is_audio`パラメータに基づいて`RunConfig`に「AUDIO」または「TEXT」のモダリティを設定し、出力形式を決定します。

- **LiveRequestQueue** - 入力リクエストをキューに入れ、クライアントとエージェント間のリアルタイムメッセージングを可能にする双方向通信チャネルを作成します。

- **ライブイベントストリーム** - `runner.run_live()`は、部分的な応答、ターンの完了、割り込みなど、エージェントからのリアルタイムイベントを生成する非同期ジェネレータを返します。

### サーバー送信イベント (SSE) ストリーミング

`agent_to_client_sse()`関数は、エージェントからクライアントへのリアルタイムストリーミングを処理します:

```py
async def agent_to_client_sse(live_events):
    """SSEを介したエージェントからクライアントへの通信"""
    async for event in live_events:
        # ターンが完了または中断された場合は、それを送信
        if event.turn_complete or event.interrupted:
            message = {
                "turn_complete": event.turn_complete,
                "interrupted": event.interrupted,
            }
            yield f"data: {json.dumps(message)}\n\n"
            print(f"[AGENT TO CLIENT]: {message}")
            continue

        # Contentとその最初のPartを読み取る
        part: Part = (
            event.content and event.content.parts and event.content.parts[0]
        )
        if not part:
            continue

        # オーディオの場合は、Base64エンコードされたオーディオデータを送信
        is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/pcm")
        if is_audio:
            audio_data = part.inline_data and part.inline_data.data
            if audio_data:
                message = {
                    "mime_type": "audio/pcm",
                    "data": base64.b64encode(audio_data).decode("ascii")
                }
                yield f"data: {json.dumps(message)}\n\n"
                print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                continue

        # テキストで、かつ部分的なテキストの場合は、それを送信
        if part.text and event.partial:
            message = {
                "mime_type": "text/plain",
                "data": part.text
            }
            yield f"data: {json.dumps(message)}\n\n"
            print(f"[AGENT TO CLIENT]: text/plain: {message}")
```

- **イベント処理ループ** - `live_events`非同期ジェネレータを反復処理し、エージェントから到着する各イベントを処理します。

- **ターン管理** - 会話のターンの完了または中断イベントを検出し、`turn_complete`および`interrupted`フラグを持つJSONメッセージを送信して、会話の状態変化を通知します。

- **コンテンツパートの抽出** - テキストまたはオーディオデータを含むイベントコンテンツから最初の`Part`を抽出します。

- **オーディオストリーミング** - PCMオーディオデータを次のように処理します:
  - `inline_data`で`audio/pcm` MIMEタイプを検出します。
  - JSON送信用に生のオーディオバイトをBase64エンコードします。
  - `mime_type`と`data`フィールドを付けて送信します。

- **テキストストリーミング** - 生成されるたびに増分テキスト更新を送信することで、部分的なテキスト応答を処理し、リアルタイムのタイピング効果を可能にします。

- **SSEフォーマット** - すべてのデータは、ブラウザのEventSource APIとの互換性のために、SSE仕様に従って`data: {json}\n\n`としてフォーマットされます。

### HTTPエンドポイントとルーティング

#### ルートエンドポイント
**GET /** - FastAPIの`FileResponse`を使用して、メインアプリケーションインターフェースとして`static/index.html`を提供します。

#### SSEイベントエンドポイント

```py
@app.get("/events/{user_id}")
async def sse_endpoint(user_id: int, is_audio: str = "false"):
    """エージェントからクライアントへの通信のためのSSEエンドポイント"""

    # エージェントセッションを開始
    user_id_str = str(user_id)
    live_events, live_request_queue = await start_agent_session(user_id_str, is_audio == "true")

    # このユーザーのリクエストキューを保存
    active_sessions[user_id_str] = live_request_queue

    print(f"Client #{user_id} connected via SSE, audio mode: {is_audio}")

    def cleanup():
        live_request_queue.close()
        if user_id_str in active_sessions:
            del active_sessions[user_id_str]
        print(f"Client #{user_id} disconnected from SSE")

    async def event_generator():
        try:
            async for data in agent_to_client_sse(live_events):
                yield data
        except Exception as e:
            print(f"Error in SSE stream: {e}")
        finally:
            cleanup()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )
```

**GET /events/{user_id}** - 永続的なSSE接続を確立します:

- **パラメータ** - `user_id` (int) と、オプションの`is_audio`クエリパラメータ（デフォルトは "false"）を受け取ります。

- **セッションの初期化** - `start_agent_session()`を呼び出し、`user_id`をキーとして`live_request_queue`を`active_sessions`辞書に保存します。

- **StreamingResponse** - 以下を含む`StreamingResponse`を返します:
  - `agent_to_client_sse()`をラップする非同期関数`event_generator()`
  - MIMEタイプ: `text/event-stream` 
  - クロスオリジンアクセスのためのCORSヘッダ
  - キャッシングを防ぐためのCache-Controlヘッダ

- **クリーンアップロジック** - ストリームの中断に対するエラーハンドリングと共に、リクエストキューを閉じてアクティブセッションから削除することで、接続終了を処理します。

#### メッセージ送信エンドポイント

```py
@app.post("/send/{user_id}")
async def send_message_endpoint(user_id: int, request: Request):
    """クライアントからエージェントへの通信のためのHTTPエンドポイント"""

    user_id_str = str(user_id)

    # このユーザーのライブリクエストキューを取得
    live_request_queue = active_sessions.get(user_id_str)
    if not live_request_queue:
        return {"error": "Session not found"}

    # メッセージをパース
    message = await request.json()
    mime_type = message["mime_type"]
    data = message["data"]

    # エージェントにメッセージを送信
    if mime_type == "text/plain":
        content = Content(role="user", parts=[Part.from_text(text=data)])
        live_request_queue.send_content(content=content)
        print(f"[CLIENT TO AGENT]: {data}")
    elif mime_type == "audio/pcm":
        decoded_data = base64.b64decode(data)
        live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
        print(f"[CLIENT TO AGENT]: audio/pcm: {len(decoded_data)} bytes")
    else:
        return {"error": f"Mime type not supported: {mime_type}"}

    return {"status": "sent"}
```

**POST /send/{user_id}** - クライアントメッセージを受信します:

- **セッションの検索** - `active_sessions`から`live_request_queue`を取得するか、セッションが存在しない場合はエラーを返します。

- **メッセージ処理** - `mime_type`と`data`フィールドを持つJSONをパースします:
  - **テキストメッセージ** - `Part.from_text()`で`Content`を作成し、`send_content()`経由で送信します。
  - **オーディオメッセージ** - PCMデータをBase64デコードし、`Blob`と共に`send_realtime()`経由で送信します。

- **エラーハンドリング** - サポートされていないMIMEタイプや存在しないセッションに対して、適切なエラー応答を返します。

## 6. クライアントサイドのコード概要 {#6.-client-side-code-overview}

クライアントサイドは、リアルタイム通信とオーディオ機能を備えたWebインターフェースで構成されています:

### HTMLインターフェース (`static/index.html`)

```html
<!doctype html>
<html>
  <head>
    <title>ADK Streaming Test (Audio)</title>
    <script src="/static/js/app.js" type="module"></script>
  </head>

  <body>
    <h1>ADK Streaming Test</h1>
    <div
      id="messages"
      style="height: 300px; overflow-y: auto; border: 1px solid black"></div>
    <br />

    <form id="messageForm">
      <label for="message">Message:</label>
      <input type="text" id="message" name="message" />
      <button type="submit" id="sendButton" disabled>Send</button>
      <button type="button" id="startAudioButton">Start Audio</button>
    </form>
  </body>

</html>
```

シンプルなWebインターフェース:
- **メッセージ表示** - 会話履歴のためのスクロール可能なdiv
- **テキスト入力フォーム** - テキストメッセージ用の入力フィールドと送信ボタン
- **オーディオコントロール** - オーディオモードとマイクアクセスを有効にするボタン

### メインアプリケーションロジック (`static/js/app.js`)

#### セッション管理 (`app.js`)

```js
const sessionId = Math.random().toString().substring(10);
const sse_url =
  "http://" + window.location.host + "/events/" + sessionId;
const send_url =
  "http://" + window.location.host + "/send/" + sessionId;
let is_audio = false;
```

- **ランダムなセッションID** - 各ブラウザインスタンスに一意のセッションIDを生成します。
- **URLの構築** - セッションIDを使用してSSEと送信エンドポイントを構築します。
- **オーディオモードフラグ** - オーディオモードが有効かどうかを追跡します。

#### Server-Sent Events接続 (`app.js`)
**connectSSE()** 関数は、リアルタイムのサーバー通信を処理します:

```js
// SSEハンドラ
function connectSSE() {
  // SSEエンドポイントに接続
  eventSource = new EventSource(sse_url + "?is_audio=" + is_audio);

  // 接続開始をハンドル
  eventSource.onopen = function () {
    // 接続開始メッセージ
    console.log("SSE connection opened.");
    document.getElementById("messages").textContent = "Connection opened";

    // 送信ボタンを有効化
    document.getElementById("sendButton").disabled = false;
    addSubmitHandler();
  };

  // 受信メッセージをハンドル
  eventSource.onmessage = function (event) {
    ...
  };

  // 接続終了をハンドル
  eventSource.onerror = function (event) {
    console.log("SSE connection error or closed.");
    document.getElementById("sendButton").disabled = true;
    document.getElementById("messages").textContent = "Connection closed";
    eventSource.close();
    setTimeout(function () {
      console.log("Reconnecting...");
      connectSSE();
    }, 5000);
  };
}
```

- **EventSourceのセットアップ** - オーディオモードパラメータ付きでSSE接続を作成します。
- **接続ハンドラ**:
  - **onopen** - 接続時に送信ボタンとフォーム送信を有効にします。
  - **onmessage** - エージェントからの受信メッセージを処理します。
  - **onerror** - 5秒後の自動再接続で切断を処理します。

#### メッセージ処理 (`app.js`)
サーバーからのさまざまなメッセージタイプを処理します:

```js
  // 受信メッセージをハンドル
  eventSource.onmessage = function (event) {
    // 受信メッセージをパース
    const message_from_server = JSON.parse(event.data);
    console.log("[AGENT TO CLIENT] ", message_from_server);

    // ターンが完了したかチェック
    // ターンが完了したら、新しいメッセージを追加
    if (
      message_from_server.turn_complete &&
      message_from_server.turn_complete == true
    ) {
      currentMessageId = null;
      return;
    }

    // オーディオなら再生
    if (message_from_server.mime_type == "audio/pcm" && audioPlayerNode) {
      audioPlayerNode.port.postMessage(base64ToArray(message_from_server.data));
    }

    // テキストなら表示
    if (message_from_server.mime_type == "text/plain") {
      // 新しいターンのために新しいメッセージを追加
      if (currentMessageId == null) {
        currentMessageId = Math.random().toString(36).substring(7);
        const message = document.createElement("p");
        message.id = currentMessageId;
        // メッセージ要素をmessagesDivに追加
        messagesDiv.appendChild(message);
      }

      // 既存のメッセージ要素にメッセージテキストを追加
      const message = document.getElementById(currentMessageId);
      message.textContent += message_from_server.data;

      // messagesDivの最下部までスクロール
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
```

- **ターン管理** - `turn_complete`を検出してメッセージの状態をリセットします。
- **オーディオ再生** - Base64 PCMデータをデコードし、オーディオワークレットに送信します。
- **テキスト表示** - 新しいメッセージ要素を作成し、リアルタイムのタイピング効果のために部分的なテキスト更新を追加します。

#### メッセージ送信 (`app.js`)
**sendMessage()** 関数はサーバーにデータを送信します:

```js
async function sendMessage(message) {
  try {
    const response = await fetch(send_url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(message)
    });
    
    if (!response.ok) {
      console.error('Failed to send message:', response.statusText);
    }
  } catch (error) {
    console.error('Error sending message:', error);
  }
}
```

- **HTTP POST** - JSONペイロードを`/send/{session_id}`エンドポイントに送信します。
- **エラーハンドリング** - 失敗したリクエストやネットワークエラーをログに記録します。
- **メッセージフォーマット** - 標準化された`{mime_type, data}`構造。

### オーディオプレーヤー (`static/js/audio-player.js`)

**startAudioPlayerWorklet()** 関数:

- **AudioContextのセットアップ** - 再生用に24kHzのサンプルレートでコンテキストを作成します。
- **Workletの読み込み** - オーディオ処理のためにPCMプレーヤープロセッサを読み込みます。
- **オーディオパイプライン** - ワークレットノードをオーディオの出力先（スピーカー）に接続します。

### オーディオレコーダー (`static/js/audio-recorder.js`)

**startAudioRecorderWorklet()** 関数:

- **AudioContextのセットアップ** - 録音用に16kHzのサンプルレートでコンテキストを作成します。
- **マイクへのアクセス** - オーディオ入力のためにユーザーメディアの許可を要求します。
- **オーディオ処理** - マイクをレコーダーワークレットに接続します。
- **データ変換** - Float32サンプルを16ビットPCM形式に変換します。

### Audio Workletプロセッサ

#### PCMプレーヤープロセッサ (`static/js/pcm-player-processor.js`)
**PCMPlayerProcessor**クラスはオーディオ再生を処理します:

- **リングバッファ** - 24kHzのオーディオを180秒間保持する循環バッファ。
- **データ入力** - Int16をFloat32に変換してバッファに保存します。
- **再生ループ** - 継続的にバッファから読み取り、出力チャンネルに送ります。
- **オーバーフロー処理** - バッファがいっぱいになると、最も古いサンプルを上書きします。

#### PCMレコーダープロセッサ (`static/js/pcm-recorder-processor.js`)
**PCMProcessor**クラスはマイク入力をキャプチャします:

- **オーディオ入力** - 受信したオーディオフレームを処理します。
- **データ転送** - Float32サンプルをコピーし、メッセージポート経由でメインスレッドに投稿します。

#### モード切り替え:
- **オーディオの有効化** - 「Start Audio」ボタンでマイクを有効にし、オーディオフラグ付きでSSEを再接続します。
- **シームレスな移行** - 既存の接続を閉じ、新しいオーディオ対応セッションを確立します。

クライアントアーキテクチャは、最新のWeb APIを使用してプロフェッショナルグレードのオーディオ処理を行い、テキストとオーディオの両方のモダリティでシームレスなリアルタイム通信を可能にします。

## まとめ

このアプリケーションは、以下の主要な機能を備えた完全なリアルタイムAIエージェントシステムを示しています:

**アーキテクチャのハイライト**:
- **リアルタイム**: 部分的なテキスト更新と連続的なオーディオによるストリーミング応答
- **堅牢性**: 包括的なエラーハンドリングと自動復旧メカニズム
- **モダン**: 最新のWeb標準（AudioWorklet, SSE, ES6モジュール）を使用

このシステムは、リアルタイムの対話、Web検索機能、およびマルチメディア通信を必要とする高度なAIアプリケーションを構築するための基盤を提供します。

### 本番環境への次のステップ

このシステムを本番環境にデプロイするには、以下の改善を実装することを検討してください:

#### セキュリティ
- **認証**: ランダムなセッションIDを適切なユーザー認証に置き換えます。
- **APIキーのセキュリティ**: 環境変数またはシークレット管理サービスを使用します。
- **HTTPS**: すべての通信でTLS暗号化を強制します。
- **レート制限**: 不正使用を防ぎ、APIコストを制御します。

#### スケーラビリティ
- **永続ストレージ**: インメモリセッションを永続的なセッションストアに置き換えます。
- **ロードバランシング**: 共有セッション状態で複数のサーバーインスタンスをサポートします。
- **オーディオの最適化**: 帯域幅の使用量を減らすために圧縮を実装します。

#### モニタリング
- **エラー追跡**: システム障害を監視し、アラートを発します。
- **APIコスト監視**: 予算超過を防ぐためにGoogle SearchとGeminiの使用状況を追跡します。
- **パフォーマンスメトリクス**: 応答時間とオーディオ遅延を監視します。

#### インフラストラクチャ
- **コンテナ化**: Cloud RunまたはAgent Engineでの一貫したデプロイメントのためにDockerでパッケージ化します。
- **ヘルスチェック**: アップタイム追跡のためのエンドポイント監視を実装します。