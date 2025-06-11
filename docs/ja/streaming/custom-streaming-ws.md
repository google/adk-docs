# カスタムオーディオストリーミングアプリ (WebSocket) {#custom-streaming-websocket}

この記事では、ADKストリーミングと[FastAPI](https://fastapi.tiangolo.com/)で構築されたカスタム非同期ウェブアプリのサーバーとクライアントのコードを概説し、WebSocketによるリアルタイムで双方向の音声・テキスト通信を可能にする方法を説明します。

**注:** このガイドは、JavaScriptおよびPythonの`asyncio`プログラミングの経験があることを前提としています。

## 音声/ビデオストリーミングでサポートされているモデル {#supported-models}

ADKで音声/ビデオストリーミングを使用するには、Live APIをサポートするGeminiモデルを使用する必要があります。Gemini Live APIをサポートする**モデルID**は、以下のドキュメントで確認できます。

-   [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
-   [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

サンプルの[SSE](custom-streaming.md)版も利用可能です。

## 1. ADKのインストール {#1.-setup-installation}

仮想環境の作成と有効化（推奨）:

```bash
# 作成
python -m venv .venv
# 有効化 (新しいターミナルごと)
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

サンプルコードをダウンロードします:

```bash
git clone --no-checkout https://github.com/google/adk-docs.git
cd adk-docs
git sparse-checkout init --cone
git sparse-checkout set examples/python/snippets/streaming/adk-streaming-ws
git checkout main
cd examples/python/snippets/streaming/adk-streaming-ws/app
```

このサンプルコードには、以下のファイルとフォルダが含まれています。

```console
adk-streaming-ws/
└── app/ # ウェブアプリフォルダ
    ├── .env # Gemini APIキー / Google CloudプロジェクトID
    ├── main.py # FastAPIウェブアプリ
    ├── static/ # 静的コンテンツフォルダ
    |   ├── js # JavaScriptファイルフォルダ (app.jsを含む)
    |   └── index.html # ウェブクライアントページ
    └── google_search_agent/ # エージェントフォルダ
        ├── __init__.py # Pythonパッケージ
        └── agent.py # エージェントの定義
```

## 2. プラットフォームの設定 {#2.-set-up-the-platform}

サンプルアプリを実行するために、Google AI StudioまたはGoogle Cloud Vertex AIのいずれかのプラットフォームを選択します。

=== "Gemini - Google AI Studio"
    1.  [Google AI Studio](https://aistudio.google.com/apikey)でAPIキーを取得します。
    2.  (`app/`内にある) **`.env`** ファイルを開き、以下のコードをコピー＆ペーストします。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3.  `PASTE_YOUR_ACTUAL_API_KEY_HERE`の部分を、実際の`APIキー`に置き換えてください。

=== "Gemini - Google Cloud Vertex AI"
    1.  既存の[Google Cloud](https://cloud.google.com/?e=48754805&hl=en)アカウントとプロジェクトが必要です。
        *   [Google Cloudプロジェクトのセットアップ](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
        *   [gcloud CLIのセットアップ](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
        *   ターミナルから `gcloud auth login` を実行してGoogle Cloudに認証します。
        *   [Vertex AI APIの有効化](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)
    2.  (`app/`内にある) **`.env`** ファイルを開きます。以下のコードをコピー＆ペーストし、プロジェクトIDとロケーションを更新してください。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=PASTE_YOUR_ACTUAL_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=us-central1
        ```


### agent.py

`google_search_agent`フォルダ内のエージェント定義コード`agent.py`には、エージェントのロジックが記述されています。

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

**注:** テキストと音声/ビデオの両方の入力を有効にするには、モデルがgenerateContent（テキスト用）とbidiGenerateContentメソッドをサポートしている必要があります。これらの機能については、[モデル一覧のドキュメント](https://ai.google.dev/api/models#method:-models.list)を参照して確認してください。このクイックスタートでは、デモンストレーション目的で`gemini-2.0-flash-exp`モデルを利用します。

[Google検索によるグラウンディング](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search)機能がいかに簡単に統合できるかにお気づきでしょうか。`Agent`クラスと`google_search`ツールがLLMとの複雑なやり取りや検索APIによるグラウンディングを処理してくれるため、あなたはエージェントの*目的*と*振る舞い*に集中できます。

![intro_components.png](../assets/quickstart-streaming-tool.png)

## 3. ストリーミングアプリとの対話 {#3.-interact-with-your-streaming-app}

1.  **正しいディレクトリへの移動:**

    エージェントを効果的に実行するために、**appフォルダ (`adk-streaming-ws/app`)** にいることを確認してください。

2.  **FastAPIの起動:** 次のコマンドを実行してCLIインターフェースを起動します。

```console
uvicorn main:app --reload
```

3.  **テキストモードでのアプリへのアクセス:** アプリが起動すると、ターミナルにローカルURL（例: [http://localhost:8000](http://localhost:8000)）が表示されます。このリンクをクリックしてブラウザでUIを開きます。

次のようなUIが表示されるはずです。

![ADKストリーミングアプリ](../assets/adk-streaming-text.png)

「What time is it now?」と質問してみてください。エージェントはGoogle検索を使用してあなたのクエリに応答します。UIがエージェントの応答をストリーミングテキストとして表示することに気づくでしょう。エージェントがまだ応答中であっても、いつでもメッセージを送信できます。これはADKストリーミングの双方向通信能力を示しています。

4.  **オーディオモードでのアプリへのアクセス:** `Start Audio`ボタンをクリックします。アプリはオーディオモードでサーバーに再接続し、UIには初回に以下のダイアログが表示されます。

![ADKストリーミングアプリ](../assets/adk-streaming-audio-dialog.png)

`Allow while visiting the site`をクリックすると、ブラウザの上部にマイクアイコンが表示されます。

![ADKストリーミングアプリ](../assets/adk-streaming-mic.png)

これで、音声でエージェントと話すことができます。「What time is it now?」のような質問を音声で尋ねると、エージェントも音声で応答するのを聞くことができます。ADKのストリーミングは[多言語](https://ai.google.dev/gemini-api/docs/live#supported-languages)をサポートしているため、サポートされている言語での質問にも応答できます。

5.  **コンソールログの確認**

Chromeブラウザを使用している場合は、右クリックして`Inspect`を選択し、DevToolsを開きます。`Console`タブで、`[CLIENT TO AGENT]`や`[AGENT TO CLIENT]`のような送受信される音声データを確認できます。これらはブラウザとサーバー間でストリーミングされる音声データを表しています。

同時に、アプリサーバーのコンソールには次のようなものが表示されるはずです。

```
INFO:     ('127.0.0.1', 50068) - "WebSocket /ws/70070018?is_audio=true" [accepted]
Client #70070018 connected, audio mode: true
INFO:     connection open
INFO:     127.0.0.1:50061 - "GET /static/js/pcm-player-processor.js HTTP/1.1" 200 OK
INFO:     127.0.0.1:50060 - "GET /static/js/pcm-recorder-processor.js HTTP/1.1" 200 OK
[AGENT TO CLIENT]: audio/pcm: 9600 bytes.
INFO:     127.0.0.1:50082 - "GET /favicon.ico HTTP/1.1" 404 Not Found
[AGENT TO CLIENT]: audio/pcm: 11520 bytes.
[AGENT TO CLIENT]: audio/pcm: 11520 bytes.
```

これらのコンソールログは、独自のストリーミングアプリケーションを開発する場合に重要です。多くの場合、ブラウザとサーバー間の通信障害がストリーミングアプリケーションのバグの主な原因となります。

6.  **トラブルシューティングのヒント**

-   **`ws://`が機能しない場合:** Chrome DevToolsで`ws://`接続に関するエラーが表示された場合は、`app/static/js/app.js`の28行目で`ws://`を`wss://`に置き換えてみてください。これは、クラウド環境でサンプルを実行し、ブラウザからプロキシ接続を使用している場合に発生することがあります。
-   **`gemini-2.0-flash-exp`モデルが機能しない場合:** アプリサーバーのコンソールで`gemini-2.0-flash-exp`モデルの可用性に関するエラーが表示された場合は、`app/google_search_agent/agent.py`の6行目で`gemini-2.0-flash-live-001`に置き換えてみてください。

## 4. サーバーコードの概要 {#4.-server-side-code-overview}

このサーバーアプリは、WebSocketを介してADKエージェントとのリアルタイムなストリーミング対話を可能にします。クライアントはテキスト/音声をADKエージェントに送信し、ストリーミングされたテキスト/音声の応答を受信します。

主な機能:
1.  ADKエージェントセッションの初期化/管理。
2.  クライアントのWebSocket接続の処理。
3.  クライアントメッセージのADKエージェントへのリレー。
4.  ADKエージェントの応答（テキスト/音声）のクライアントへのストリーミング。

### ADKストリーミングのセットアップ

```py
import os
import json
import asyncio
import base64

from pathlib import Path
from dotenv import load_dotenv

from google.genai.types import (
    Part,
    Content,
    Blob,
)

from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.in_memory_session_service import InMemorySessionService

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from google_search_agent.agent import root_agent
```

*   **インポート:** 標準的なPythonライブラリ、環境変数用の`dotenv`、Google ADK、FastAPIを含みます。
*   **`load_dotenv()`:** 環境変数をロードします。
*   **`APP_NAME`**: ADK用のアプリケーション識別子です。
*   **`session_service = InMemorySessionService()`**: インメモリのADKセッションサービスを初期化します。これは単一インスタンスまたは開発用途に適しています。本番環境では永続的なストアを使用する場合があります。

### `start_agent_session(session_id, is_audio=False)`

```py
async def start_agent_session(user_id, is_audio=False):
    """エージェントセッションを開始します"""

    # Runnerを作成
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=root_agent,
    )

    # セッションを作成
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,  # 実際のユーザーIDに置き換えます
    )

    # 応答モダリティを設定
    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(response_modalities=[modality])

    # このセッション用にLiveRequestQueueを作成
    live_request_queue = LiveRequestQueue()

    # エージェントセッションを開始
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue
```

この関数は、ADKエージェントのライブセッションを初期化します。

| パラメータ    | 型    | 説明                                             |
|--------------|---------|---------------------------------------------------------|
| `user_id` | `str`   | 一意のクライアント識別子。                       |
| `is_audio`   | `bool`  | 音声応答の場合は`True`、テキストの場合は`False`（デフォルト）。 |

**主なステップ:**
1.  **Runnerの作成:** `root_agent`用のADKランナーをインスタンス化します。
2.  **セッションの作成:** ADKセッションを確立します。
3.  **応答モダリティの設定:** エージェントの応答を「AUDIO」または「TEXT」に設定します。
4.  **LiveRequestQueueの作成:** クライアントからエージェントへの入力用のキューを作成します。
5.  **エージェントセッションの開始:** `runner.run_live(...)`がエージェントを開始し、以下を返します。
    *   `live_events`: エージェントイベント（テキスト、音声、完了）用の非同期イテラブル。
    *   `live_request_queue`: エージェントにデータを送信するためのキュー。

**戻り値:** `(live_events, live_request_queue)`.

### `agent_to_client_messaging(websocket, live_events)`

```py

async def agent_to_client_messaging(websocket, live_events):
    """エージェントからクライアントへの通信"""
    while True:
        async for event in live_events:

            # ターンが完了または中断された場合は、それを送信
            if event.turn_complete or event.interrupted:
                message = {
                    "turn_complete": event.turn_complete,
                    "interrupted": event.interrupted,
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: {message}")
                continue

            # Contentとその最初のPartを読み取る
            part: Part = (
                event.content and event.content.parts and event.content.parts[0]
            )
            if not part:
                continue

            # 音声の場合は、Base64エンコードされた音声データを送信
            is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/pcm")
            if is_audio:
                audio_data = part.inline_data and part.inline_data.data
                if audio_data:
                    message = {
                        "mime_type": "audio/pcm",
                        "data": base64.b64encode(audio_data).decode("ascii")
                    }
                    await websocket.send_text(json.dumps(message))
                    print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                    continue

            # テキストで部分的なテキストの場合は、それを送信
            if part.text and event.partial:
                message = {
                    "mime_type": "text/plain",
                    "data": part.text
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: text/plain: {message}")
```

この非同期関数は、ADKエージェントのイベントをWebSocketクライアントにストリーミングします。

**ロジック:**
1.  エージェントからの`live_events`を反復処理します。
2.  **ターンの完了/中断:** ステータスフラグをクライアントに送信します。
3.  **コンテンツ処理:**
    *   イベントコンテンツから最初の`Part`を抽出します。
    *   **音声データ:** 音声（PCM）の場合、Base64エンコードしてJSONとして送信します: `{ "mime_type": "audio/pcm", "data": "<base64_audio>" }`。
    *   **テキストデータ:** 部分的なテキストの場合、JSONとして送信します: `{ "mime_type": "text/plain", "data": "<partial_text>" }`。
4.  メッセージをログに記録します。

### `client_to_agent_messaging(websocket, live_request_queue)`

```py

async def client_to_agent_messaging(websocket, live_request_queue):
    """クライアントからエージェントへの通信"""
    while True:
        # JSONメッセージをデコード
        message_json = await websocket.receive_text()
        message = json.loads(message_json)
        mime_type = message["mime_type"]
        data = message["data"]

        # メッセージをエージェントに送信
        if mime_type == "text/plain":
            # テキストメッセージを送信
            content = Content(role="user", parts=[Part.from_text(text=data)])
            live_request_queue.send_content(content=content)
            print(f"[CLIENT TO AGENT]: {data}")
        elif mime_type == "audio/pcm":
            # 音声データを送信
            decoded_data = base64.b64decode(data)
            live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
        else:
            raise ValueError(f"サポートされていないMIMEタイプ: {mime_type}")
```

この非同期関数は、WebSocketクライアントからのメッセージをADKエージェントにリレーします。

**ロジック:**
1.  WebSocketからJSONメッセージを受信して解析します。期待される形式は `{ "mime_type": "text/plain" | "audio/pcm", "data": "<data>" }` です。
2.  **テキスト入力:** "text/plain"の場合、`live_request_queue.send_content()`を介してエージェントに`Content`を送信します。
3.  **音声入力:** "audio/pcm"の場合、Base64データをデコードし、`Blob`でラップして`live_request_queue.send_realtime()`を介して送信します。
4.  サポートされていないMIMEタイプに対して`ValueError`を発生させます。
5.  メッセージをログに記録します。

### FastAPIウェブアプリケーション

```py

app = FastAPI()

STATIC_DIR = Path("static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """index.htmlを提供します"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, is_audio: str):
    """クライアントWebSocketエンドポイント"""

    # クライアント接続を待機
    await websocket.accept()
    print(f"クライアント #{user_id} が接続しました, オーディオモード: {is_audio}")

    # エージェントセッションを開始
    user_id_str = str(user_id)
    live_events, live_request_queue = await start_agent_session(user_id_str, is_audio == "true")

    # タスクを開始
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )

    # WebSocketが切断されるかエラーが発生するまで待機
    tasks = [agent_to_client_task, client_to_agent_task]
    await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    # LiveRequestQueueを閉じる
    live_request_queue.close()

    # 切断
    print(f"クライアント #{user_id} が切断しました")

```

*   **`app = FastAPI()`**: アプリケーションを初期化します。
*   **静的ファイル:** `static`ディレクトリのファイルを`/static`で提供します。
*   **`@app.get("/")` (ルートエンドポイント):** `index.html`を提供します。
*   **`@app.websocket("/ws/{user_id}")` (WebSocketエンドポイント):**
    *   **パスパラメータ:** `user_id` (int) と `is_audio` (str: "true"/"false")。
    *   **接続処理:**
        1.  WebSocket接続を受け入れます。
        2.  `user_id`と`is_audio`を使用して`start_agent_session()`を呼び出します。
        3.  **同時メッセージングタスク:** `asyncio.gather`を使用して`agent_to_client_messaging`と`client_to_agent_messaging`を同時に作成して実行します。これらのタスクは双方向のメッセージフローを処理します。
        4.  クライアントの接続と切断をログに記録します。

### 仕組み (全体のフロー)

1.  クライアントは`ws://<server>/ws/<user_id>?is_audio=<true_or_false>`に接続します。
2.  サーバーの`websocket_endpoint`が接続を受け入れ、ADKセッションを開始します (`start_agent_session`)。
3.  2つの`asyncio`タスクが通信を管理します。
    *   `client_to_agent_messaging`: クライアントのWebSocketメッセージ -> ADKの`live_request_queue`。
    *   `agent_to_client_messaging`: ADKの`live_events` -> クライアントのWebSocket。
4.  切断またはエラーが発生するまで、双方向のストリーミングが続行されます。

## 5. クライアントコードの概要 {#5.-client-side-code-overview}

JavaScriptの`app.js`（`app/static/js`内）は、ADKストリーミングWebSocketバックエンドとのクライアント側の対話を管理します。テキスト/音声の送信と、ストリーミングされた応答の受信/表示を処理します。

主な機能:
1.  WebSocket接続の管理。
2.  テキスト入力の処理。
3.  マイク音声のキャプチャ（Web Audio API, AudioWorklets）。
4.  テキスト/音声のバックエンドへの送信。
5.  テキスト/音声のエージェント応答の受信とレンダリング。
6.  UIの管理。

### 前提条件

*   **HTML構造:** 特定の要素IDが必要です（例: `messageForm`, `message`, `messages`, `sendButton`, `startAudioButton`）。
*   **バックエンドサーバー:** Python FastAPIサーバーが実行中である必要があります。
*   **Audio Workletファイル:** 音声処理のための`audio-player.js`と`audio-recorder.js`。

### WebSocketの処理

```JavaScript

// WebSocket接続でサーバーに接続
const sessionId = Math.random().toString().substring(10);
const ws_url =
  "ws://" + window.location.host + "/ws/" + sessionId;
let websocket = null;
let is_audio = false;

// DOM要素を取得
const messageForm = document.getElementById("messageForm");
const messageInput = document.getElementById("message");
const messagesDiv = document.getElementById("messages");
let currentMessageId = null;

// WebSocketハンドラ
function connectWebsocket() {
  // WebSocketに接続
  websocket = new WebSocket(ws_url + "?is_audio=" + is_audio);

  // 接続が開いたときの処理
  websocket.onopen = function () {
    // 接続が開いたメッセージ
    console.log("WebSocket connection opened.");
    document.getElementById("messages").textContent = "Connection opened";

    // 送信ボタンを有効にする
    document.getElementById("sendButton").disabled = false;
    addSubmitHandler();
  };

  // メッセージ受信時の処理
  websocket.onmessage = function (event) {
    // 受信メッセージを解析
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

    // 音声の場合は再生
    if (message_from_server.mime_type == "audio/pcm" && audioPlayerNode) {
      audioPlayerNode.port.postMessage(base64ToArray(message_from_server.data));
    }

    // テキストの場合は表示
    if (message_from_server.mime_type == "text/plain") {
      // 新しいターンのために新しいメッセージを追加
      if (currentMessageId == null) {
        currentMessageId = Math.random().toString(36).substring(7);
        const message = document.createElement("p");
        message.id = currentMessageId;
        // messagesDivにメッセージ要素を追加
        messagesDiv.appendChild(message);
      }

      // 既存のメッセージ要素にメッセージテキストを追加
      const message = document.getElementById(currentMessageId);
      message.textContent += message_from_server.data;

      // messagesDivの最下部にスクロール
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
  };

  // 接続が閉じたときの処理
  websocket.onclose = function () {
    console.log("WebSocket connection closed.");
    document.getElementById("sendButton").disabled = true;
    document.getElementById("messages").textContent = "Connection closed";
    setTimeout(function () {
      console.log("Reconnecting...");
      connectWebsocket();
    }, 5000);
  };

  websocket.onerror = function (e) {
    console.log("WebSocket error: ", e);
  };
}
connectWebsocket();

// フォームに送信ハンドラを追加
function addSubmitHandler() {
  messageForm.onsubmit = function (e) {
    e.preventDefault();
    const message = messageInput.value;
    if (message) {
      const p = document.createElement("p");
      p.textContent = "> " + message;
      messagesDiv.appendChild(p);
      messageInput.value = "";
      sendMessage({
        mime_type: "text/plain",
        data: message,
      });
      console.log("[CLIENT TO AGENT] " + message);
    }
    return false;
  };
}

// サーバーにメッセージをJSON文字列として送信
function sendMessage(message) {
  if (websocket && websocket.readyState == WebSocket.OPEN) {
    const messageJson = JSON.stringify(message);
    websocket.send(messageJson);
  }
}

// Base64データを配列にデコード
function base64ToArray(base64) {
  const binaryString = window.atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}
```

*   **接続設定:** `sessionId`を生成し、`ws_url`を構築します。`is_audio`フラグ（初期値は`false`）は、アクティブな場合にURLに`?is_audio=true`を追加します。`connectWebsocket()`が接続を初期化します。
*   **`websocket.onopen`**: 送信ボタンを有効にし、UIを更新し、`addSubmitHandler()`を呼び出します。
*   **`websocket.onmessage`**: サーバーからの受信JSONを解析します。
    *   **ターンの完了:** エージェントのターンが完了した場合、`currentMessageId`をリセットします。
    *   **音声データ (`audio/pcm`):** Base64音声をデコード（`base64ToArray()`）し、再生のために`audioPlayerNode`に送信します。
    *   **テキストデータ (`text/plain`):** 新しいターンの場合（`currentMessageId`がnull）、新しい`<p>`を作成します。受信したテキストを現在のメッセージ段落に追加して、ストリーミング効果を出します。`messagesDiv`をスクロールします。
*   **`websocket.onclose`**: 送信ボタンを無効にし、UIを更新し、5秒後に自動再接続を試みます。
*   **`websocket.onerror`**: エラーをログに記録します。
*   **初期接続:** スクリプト読み込み時に`connectWebsocket()`が呼び出されます。

#### DOM操作とメッセージ送信

*   **要素取得:** 必要なDOM要素を取得します。
*   **`addSubmitHandler()`**: `messageForm`のsubmitイベントにアタッチされます。デフォルトの送信を防ぎ、`messageInput`からテキストを取得し、ユーザーメッセージを表示し、入力をクリアし、`{ mime_type: "text/plain", data: messageText }`で`sendMessage()`を呼び出します。
*   **`sendMessage(messagePayload)`**: WebSocketが開いている場合、JSON文字列化された`messagePayload`を送信します。

### 音声の処理

```JavaScript

let audioPlayerNode;
let audioPlayerContext;
let audioRecorderNode;
let audioRecorderContext;
let micStream;

// オーディオワークレットをインポート
import { startAudioPlayerWorklet } from "./audio-player.js";
import { startAudioRecorderWorklet } from "./audio-recorder.js";

// オーディオを開始
function startAudio() {
  // オーディオ出力を開始
  startAudioPlayerWorklet().then(([node, ctx]) => {
    audioPlayerNode = node;
    audioPlayerContext = ctx;
  });
  // オーディオ入力を開始
  startAudioRecorderWorklet(audioRecorderHandler).then(
    ([node, ctx, stream]) => {
      audioRecorderNode = node;
      audioRecorderContext = ctx;
      micStream = stream;
    }
  );
}

// ユーザーがボタンをクリックしたときにのみオーディオを開始
// (Web Audio APIのジェスチャー要件のため)
const startAudioButton = document.getElementById("startAudioButton");
startAudioButton.addEventListener("click", () => {
  startAudioButton.disabled = true;
  startAudio();
  is_audio = true;
  connectWebsocket(); // オーディオモードで再接続
});

// オーディオレコーダーハンドラ
function audioRecorderHandler(pcmData) {
  // pcmデータをbase64として送信
  sendMessage({
    mime_type: "audio/pcm",
    data: arrayBufferToBase64(pcmData),
  });
  console.log("[CLIENT TO AGENT] sent %s bytes", pcmData.byteLength);
}

// 配列バッファをBase64にエンコード
function arrayBufferToBase64(buffer) {
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}
```

*   **オーディオワークレット:** `audio-player.js`（再生用）と`audio-recorder.js`（キャプチャ用）を介して`AudioWorkletNode`を使用します。
*   **状態変数:** AudioContextとWorkletNode（例: `audioPlayerNode`）を保存します。
*   **`startAudio()`**: プレーヤーとレコーダーのワークレットを初期化します。レコーダーに`audioRecorderHandler`をコールバックとして渡します。
*   **「Start Audio」ボタン (`startAudioButton`):**
    *   Web Audio APIにはユーザーのジェスチャーが必要です。
    *   クリック時: ボタンを無効にし、`startAudio()`を呼び出し、`is_audio = true`を設定し、オーディオモードでWebSocketを再接続するために`connectWebsocket()`を呼び出します（URLに`?is_audio=true`が含まれます）。
*   **`audioRecorderHandler(pcmData)`**: レコーダーワークレットからのPCM音声チャンクを持つコールバックです。`pcmData`をBase64にエンコードし（`arrayBufferToBase64()`）、`mime_type: "audio/pcm"`でサーバーに`sendMessage()`を介して送信します。
*   **ヘルパー関数:** `base64ToArray()`（サーバー音声 -> クライアントプレーヤー）と`arrayBufferToBase64()`（クライアントマイク音声 -> サーバー）。

### 仕組み (クライアント側のフロー)

1.  **ページ読み込み:** テキストモードでWebSocketを確立します。
2.  **テキスト対話:** ユーザーがテキストを入力/送信し、サーバーに送信されます。サーバーのテキスト応答が表示され、ストリーミングされます。
3.  **オーディオモードへの切り替え:** 「Start Audio」ボタンをクリックすると、オーディオワークレットが初期化され、`is_audio=true`が設定され、オーディオモードでWebSocketが再接続されます。
4.  **オーディオ対話:** レコーダーがマイク音声（Base64 PCM）をサーバーに送信します。サーバーの音声/テキスト応答は、再生/表示のために`websocket.onmessage`によって処理されます。
5.  **接続管理:** WebSocketが閉じた場合に自動再接続します。


## まとめ

この記事では、ADKストリーミングとFastAPIで構築されたカスタム非同期ウェブアプリのサーバーとクライアントのコードを概説し、リアルタイムで双方向の音声・テキスト通信を可能にする方法を説明しました。

Python FastAPIサーバーコードは、テキストまたは音声応答用に設定されたADKエージェントセッションを初期化します。クライアント接続を処理するためにWebSocketエンドポイントを使用します。非同期タスクが双方向のメッセージングを管理します。クライアントのテキストまたはBase64エンコードされたPCM音声をADKエージェントに転送し、エージェントからのテキストまたはBase64エンコードされたPCM音声応答をクライアントにストリーミングします。

クライアント側のJavaScriptコードは、テキストモードとオーディオモードを切り替えるために再確立できるWebSocket接続を管理します。ユーザー入力（テキストまたはWeb Audio APIとAudioWorkletsを介してキャプチャされたマイク音声）をサーバーに送信します。サーバーからの受信メッセージは処理されます。テキストは表示（ストリーミング）され、Base64エンコードされたPCM音声はデコードされてAudioWorkletを使用して再生されます。

### 本番環境への次のステップ

本番アプリでADKストリーミングを使用する際には、次の点を考慮するとよいでしょう。

*   **複数インスタンスのデプロイ:** 単一ではなく、FastAPIアプリケーションの複数のインスタンスを実行します。
*   **ロードバランシングの実装:** アプリケーションインスタンスの前にロードバランサーを配置し、受信WebSocket接続を分散させます。
    *   **WebSocket用の設定:** ロードバランサーが長寿命のWebSocket接続をサポートしていることを確認し、「スティッキーセッション」（セッションアフィニティ）を検討してクライアントを同じバックエンドインスタンスにルーティングするか、ステートレスインスタンス用に設計します（次のポイントを参照）。
*   **セッション状態の外部化:** ADKの`InMemorySessionService`を、分散型の永続的なセッションストアに置き換えます。これにより、どのサーバーインスタンスでも任意のユーザーのセッションを処理できるようになり、アプリケーションサーバーレベルでの真のステートレス性が実現し、耐障害性が向上します。
*   **ヘルスチェックの実装:** WebSocketサーバーインスタンスに堅牢なヘルスチェックを設定し、ロードバランサーが不健全なインスタンスを自動的にローテーションから除外できるようにします。
*   **オーケストレーションの活用:** Kubernetesのようなオーケストレーションプラットフォームを使用して、WebSocketサーバーインスタンスの自動デプロイ、スケーリング、自己修復、および管理を検討します。