# カスタムオーディオストリーミングアプリ (SSE) {#custom-streaming}

この記事では、ADKストリーミングと[FastAPI](https://fastapi.tiangolo.com/)で構築されたカスタム非同期Webアプリのサーバーとクライアントのコードを概観し、サーバー送信イベント（SSE）によるリアルタイムの双方向音声およびテキスト通信を可能にします。主な機能は以下の通りです：

**サーバーサイド (Python/FastAPI)**:
- FastAPI + ADKの統合
- リアルタイムストリーミングのためのサーバー送信イベント
- 分離されたユーザーコンテキストによるセッション管理
- テキストと音声の両方の通信モードのサポート
- 根拠のある応答のためのGoogle検索ツールの統合

**クライアントサイド (JavaScript/Web Audio API)**:
- SSEとHTTP POSTによるリアルタイム双方向通信
- AudioWorkletプロセッサを使用したプロフェッショナルな音声処理
- テキストと音声モード間のシームレスな切り替え
- 自動再接続とエラーハンドリング
- 音声データ伝送のためのBase64エンコーディング

## 1. ADKのインストール {#1.-setup-installation}

仮想環境の作成と有効化（推奨）：

```bash
# 作成
python -m venv .venv
# 有効化（新しいターミナルごと）
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

ADKのインストール：

```bash
pip install google-adk==1.0.0
```

以下のコマンドで`SSL_CERT_FILE`変数を設定します。

```shell
export SSL_CERT_FILE=$(python -m certifi)
```

サンプルコードをダウンロードします：

```bash
git clone --no-checkout https://github.com/google/adk-docs.git
cd adk-docs
git sparse-checkout init --cone
git sparse-checkout set examples/python/snippets/streaming/adk-streaming
git checkout main
cd examples/python/snippets/streaming/adk-streaming/app
```

このサンプルコードには、以下のファイルとフォルダが含まれています：

```console
adk-streaming/
└── app/ # Webアプリフォルダ
    ├── .env # Gemini APIキー / Google CloudプロジェクトID
    ├── main.py # FastAPI Webアプリ
    ├── static/ # 静的コンテンツフォルダ
    |   ├── js # JavaScriptファイルフォルダ（app.jsを含む）
    |   └── index.html # Webクライアントページ
    └── google_search_agent/ # エージェントフォルダ
        ├── __init__.py # Pythonパッケージ
        └── agent.py # エージェント定義
```

## 2. プラットフォームのセットアップ {#2.-set-up-the-platform}

サンプルアプリを実行するには、Google AI StudioまたはGoogle Cloud Vertex AIのいずれかのプラットフォームを選択します：

=== "Gemini - Google AI Studio"
    1.  [Google AI Studio](https://aistudio.google.com/apikey)からAPIキーを取得します。
    2.  （`app/`内にある）**`.env`**ファイルを開き、以下のコードをコピー＆ペーストします。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=ここに実際のAPIキーを貼り付けてください
        ```

    3.  `ここに実際のAPIキーを貼り付けてください`を実際の`APIキー`に置き換えます。

=== "Gemini - Google Cloud Vertex AI"
    1.  既存の[Google Cloud](https://cloud.google.com/?e=48754805&hl=en)アカウントとプロジェクトが必要です。
        *   [Google Cloudプロジェクトのセットアップ](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
        *   [gcloud CLIのセットアップ](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
        *   ターミナルから`gcloud auth login`を実行してGoogle Cloudに認証します。
        *   [Vertex AI APIを有効にする](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)。
    2.  （`app/`内にある）**`.env`**ファイルを開きます。以下のコードをコピー＆ペーストし、プロジェクトIDとロケーションを更新します。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=ここに実際のプロジェクトIDを貼り付けてください
        GOOGLE_CLOUD_LOCATION=us-central1
        ```

## 3. ストリーミングアプリとの対話 {#3.-interact-with-your-streaming-app}

1.  **正しいディレクトリに移動する：**

    エージェントを効果的に実行するためには、**appフォルダ（`adk-streaming/app`）**にいることを確認してください。

2.  **FastAPIを開始する**：以下のコマンドを実行してCLIインターフェースを開始します。

```console
uvicorn main:app --reload
```

3.  **テキストモードでアプリにアクセスする：** アプリが起動すると、ターミナルにローカルURL（例：[http://localhost:8000](http://localhost:8000)）が表示されます。このリンクをクリックして、ブラウザでUIを開きます。

すると、このようなUIが表示されるはずです：

![ADK Streaming app](../assets/adk-streaming-text.png)

「今何時？」と質問してみてください。エージェントはGoogle検索を使用してあなたのクエリに応答します。UIがエージェントの応答をストリーミングテキストとして表示することに気づくでしょう。エージェントがまだ応答している間でも、いつでもメッセージを送信できます。これはADKストリーミングの双方向通信機能を示しています。

4.  **音声モードでアプリにアクセスする：** 次に「Start Audio」ボタンをクリックします。アプリは音声モードでサーバーに再接続し、UIには初回に以下のダイアログが表示されます：

![ADK Streaming app](../assets/adk-streaming-audio-dialog.png)

「サイト訪問中は許可」をクリックすると、ブラウザの上部にマイクアイコンが表示されます：

![ADK Streaming app](../assets/adk-streaming-mic.png)

これで、音声でエージェントと話すことができます。「今何時？」のような質問を声で尋ねると、エージェントも声で応答するのを聞くことができます。ADKのストリーミングは[多言語](https://ai.google.dev/gemini-api/docs/live#supported-languages)をサポートしているため、サポートされている言語での質問にも応答できます。

5.  **コンソールログの確認**

Chromeブラウザを使用している場合は、右クリックして「検証」を選択し、DevToolsを開きます。「コンソール」では、「[CLIENT TO AGENT]」や「[AGENT TO CLIENT]」のような送受信される音声データを確認でき、ブラウザとサーバー間でストリーミングされる音声データを表しています。

同時に、アプリサーバーのコンソールには、次のようなものが表示されるはずです：

```
Client #90766266 connected via SSE, audio mode: false
INFO:     127.0.0.1:52692 - "GET /events/90766266?is_audio=false HTTP/1.1" 200 OK
[CLIENT TO AGENT]: hi
INFO:     127.0.0.1:52696 - "POST /send/90766266 HTTP/1.1" 200 OK
[AGENT TO CLIENT]: text/plain: {'mime_type': 'text/plain', 'data': 'Hi'}
[AGENT TO CLIENT]: text/plain: {'mime_type': 'text/plain', 'data': ' there! How can I help you today?\n'}
[AGENT TO CLIENT]: {'turn_complete': True, 'interrupted': None}
```

これらのコンソールログは、独自のストリーミングアプリケーションを開発する場合に重要です。多くの場合、ブラウザとサーバー間の通信障害がストリーミングアプリケーションのバグの主な原因となります。

6.  **トラブルシューティングのヒント**

-   **`gemini-2.0-flash-exp`モデルが動作しない場合：** アプリサーバーのコンソールで`gemini-2.0-flash-exp`モデルの可用性に関するエラーが表示された場合は、`app/google_search_agent/agent.py`の6行目で`gemini-2.0-flash-live-001`に置き換えてみてください。

## 4. エージェントの定義

`google_search_agent`フォルダ内のエージェント定義コード`agent.py`に、エージェントのロジックが記述されています：

```py
from google.adk.agents import Agent
from google.adk.tools import google_search  # ツールをインポート

root_agent = Agent(
   name="google_search_agent",
   model="gemini-2.0-flash-exp", # このモデルが動作しない場合は、以下を試してください
   #model="gemini-2.0-flash-live-001",
   description="Google検索を使用して質問に答えるエージェント。",
   instruction="Google検索ツールを使用して質問に答えてください。",
   tools=[google_search],
)
```

[Google検索によるグラウンディング](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search)機能をいかに簡単に統合できたかに注目してください。`Agent`クラスと`google_search`ツールが、LLMとの複雑な対話や検索APIとのグラウンディングを処理してくれるため、あなたはエージェントの*目的*と*振る舞い*に集中できます。

![intro_components.png](../assets/quickstart-streaming-tool.png)


サーバーとクライアントのアーキテクチャは、適切なセッション分離とリソース管理により、WebクライアントとAIエージェント間のリアルタイムな双方向通信を可能にします。

## 5. サーバーサイドのコード概要 {#5.-server-side-code-overview}

FastAPIサーバーは、WebクライアントとAIエージェント間のリアルタイム通信を提供します。

### 双方向通信の概要 {#4.-bidi-comm-overview}

#### クライアントからエージェントへのフロー：
1.  **接続確立** - クライアントが`/events/{user_id}`へのSSE接続を開き、セッション作成をトリガーし、リクエストキューを`active_sessions`に保存します。
2.  **メッセージ送信** - クライアントが`mime_type`と`data`を含むJSONペイロードで`/send/{user_id}`にPOSTします。
3.  **キュー処理** - サーバーがセッションの`live_request_queue`を取得し、`send_content()`または`send_realtime()`を介してメッセージをエージェントに転送します。

#### エージェントからクライアントへのフロー：
1.  **イベント生成** - エージェントがリクエストを処理し、`live_events`非同期ジェネレータを通じてイベントを生成します。
2.  **ストリーム処理** - `agent_to_client_sse()`がイベントをフィルタリングし、SSE互換のJSONとしてフォーマットします。
3.  **リアルタイム配信** - イベントは、適切なSSEヘッダーを持つ永続的なHTTP接続を介してクライアントにストリーミングされます。

#### セッション管理：
- **ユーザーごとの分離** - 各ユーザーは`active_sessions`辞書に保存される一意のセッションを取得します。
- **ライフサイクル管理** - セッションは切断時に自動的にクリーンアップされ、適切なリソース破棄が行われます。
- **同時サポート** - 複数のユーザーが同時にアクティブなセッションを持つことができます。

#### エラーハンドリング：
- **セッション検証** - POSTリクエストは処理前にセッションの存在を検証します。
- **ストリームの回復力** - SSEストリームは例外を処理し、自動的にクリーンアップを実行します。
- **接続回復** - クライアントはSSE接続を再確立することで再接続できます。

### エージェントセッション管理

`start_agent_session()`関数は、分離されたAIエージェントセッションを作成します：

```py
# ...(Pythonコードは変更しないため省略)...
```

- **InMemoryRunnerのセットアップ** - "ADK Streaming example"というアプリ名とGoogle検索エージェントで、エージェントのライフサイクルをメモリ内で管理するランナーインスタンスを作成します。

- **セッションの作成** - `runner.session_service.create_session()`を使用して、ユーザーIDごとに一意のセッションを確立し、複数の同時ユーザーを可能にします。

- **応答モダリティの設定** - `is_audio`パラメータに基づいて`RunConfig`に"AUDIO"または"TEXT"のモダリティを設定し、出力形式を決定します。

- **LiveRequestQueue** - クライアントとエージェント間で受信リクエストをキューに入れ、リアルタイムのメッセージパッシングを可能にする双方向通信チャネルを作成します。

- **ライブイベントストリーム** - `runner.run_live()`は、部分的な応答、ターンの完了、中断など、エージェントからのリアルタイムイベントを生成する非同期ジェネレータを返します。

### サーバー送信イベント (SSE) ストリーミング

`agent_to_client_sse()`関数は、エージェントからクライアントへのリアルタイムストリーミングを処理します：

```py
# ...(Pythonコードは変更しないため省略)...
```

- **イベント処理ループ** - `live_events`非同期ジェネレータを反復処理し、エージェントから到着する各イベントを処理します。

- **ターン管理** - 会話のターンの完了または中断イベントを検出し、`turn_complete`と`interrupted`フラグを持つJSONメッセージを送信して会話の状態変化を通知します。

- **コンテンツパートの抽出** - イベントコンテンツから最初の`Part`を抽出し、これにはテキストまたは音声データが含まれます。

- **音声ストリーミング** - PCM音声データを次のように処理します：
  - `inline_data`内の`audio/pcm` MIMEタイプを検出します。
  - 生の音声バイトをJSON伝送用にBase64エンコードします。
  - `mime_type`と`data`フィールドと共に送信します。

- **テキストストリーミング** - 生成されるにつれて増分テキスト更新を送信することで、部分的なテキスト応答を処理し、リアルタイムのタイピング効果を可能にします。

- **SSEフォーマット** - すべてのデータは、ブラウザのEventSource APIとの互換性のために、SSE仕様に従って`data: {json}\n\n`としてフォーマットされます。

### HTTPエンドポイントとルーティング

#### ルートエンドポイント
**GET /** - FastAPIの`FileResponse`を使用して、メインのアプリケーションインターフェースとして`static/index.html`を提供します。

#### SSEイベントエンドポイント

```py
# ...(Pythonコードは変更しないため省略)...
```

**GET /events/{user_id}** - 永続的なSSE接続を確立します：

- **パラメータ** - `user_id`（int）とオプションの`is_audio`クエリパラメータ（デフォルトは"false"）を取ります。

- **セッションの初期化** - `start_agent_session()`を呼び出し、`live_request_queue`を`user_id`をキーとして`active_sessions`辞書に保存します。

- **StreamingResponse** - 以下を持つ`StreamingResponse`を返します：
  - `agent_to_client_sse()`をラップする`event_generator()`非同期関数
  - MIMEタイプ：`text/event-stream` 
  - クロスオリジンアクセスのためのCORSヘッダー
  - キャッシングを防ぐためのCache-controlヘッダー

- **クリーンアップロジック** - リクエストキューを閉じ、アクティブなセッションから削除することで接続終了を処理し、ストリームの中断に対するエラーハンドリングも行います。

#### メッセージ送信エンドポイント

```py
# ...(Pythonコードは変更しないため省略)...
```

**POST /send/{user_id}** - クライアントメッセージを受信します：

- **セッション検索** - `active_sessions`から`live_request_queue`を取得するか、セッションが存在しない場合はエラーを返します。

- **メッセージ処理** - `mime_type`と`data`フィールドを持つJSONを解析します：
  - **テキストメッセージ** - `Part.from_text()`で`Content`を作成し、`send_content()`を介して送信します。
  - **音声メッセージ** - PCMデータをBase64デコードし、`Blob`で`send_realtime()`を介して送信します。

- **エラーハンドリング** - サポートされていないMIMEタイプや存在しないセッションに対して適切なエラー応答を返します。

## 6. クライアントサイドのコード概要 {#6.-client-side-code-overview}

クライアントサイドは、リアルタイム通信と音声機能を備えたWebインターフェースで構成されています：

### HTMLインターフェース (`static/index.html`)

```html
# ...(HTMLコードは変更しないため省略)...
```

シンプルなWebインターフェース：
- **メッセージ表示** - 会話履歴用のスクロール可能なdiv
- **テキスト入力フォーム** - テキストメッセージ用の入力フィールドと送信ボタン
- **音声制御** - 音声モードとマイクアクセスを有効にするボタン

### メインアプリケーションロジック (`static/js/app.js`)

#### セッション管理 (`app.js`)

```js
# ...(JavaScriptコードは変更しないため省略)...
```

- **ランダムセッションID** - 各ブラウザインスタンスに一意のセッションIDを生成します。
- **URL構築** - セッションIDを持つSSEおよび送信エンドポイントを構築します。
- **音声モードフラグ** - 音声モードが有効かどうかを追跡します。

#### サーバー送信イベント接続 (`app.js`)
**connectSSE()** 関数はリアルタイムのサーバー通信を処理します：

```js
# ...(JavaScriptコードは変更しないため省略)...
```

- **EventSourceのセットアップ** - 音声モードパラメータを持つSSE接続を作成します。
- **接続ハンドラ**：
  - **onopen** - 接続時に送信ボタンとフォーム送信を有効にします。
  - **onmessage** - エージェントからの受信メッセージを処理します。
  - **onerror** - 5秒後の自動再接続で切断を処理します。

#### メッセージ処理 (`app.js`)
サーバーからのさまざまなメッセージタイプを処理します：

```js
# ...(JavaScriptコードは変更しないため省略)...
```

- **ターン管理** - `turn_complete`を検出してメッセージの状態をリセットします。
- **音声再生** - Base64 PCMデータをデコードし、音声ワークレットに送信します。
- **テキスト表示** - 新しいメッセージ要素を作成し、リアルタイムのタイピング効果のために部分的なテキスト更新を追加します。

#### メッセージ送信 (`app.js`)
**sendMessage()** 関数はサーバーにデータを送信します：

```js
# ...(JavaScriptコードは変更しないため省略)...
```

- **HTTP POST** - `/send/{session_id}`エンドポイントにJSONペイロードを送信します。
- **エラーハンドリング** - 失敗したリクエストとネットワークエラーをログに記録します。
- **メッセージフォーマット** - 標準化された`{mime_type, data}`構造。

### オーディオプレーヤー (`static/js/audio-player.js`)

**startAudioPlayerWorklet()** 関数：

- **AudioContextのセットアップ** - 再生用に24kHzのサンプルレートでコンテキストを作成します。
- **ワークレットの読み込み** - 音声処理のためにPCMプレーヤープロセッサを読み込みます。
- **オーディオパイプライン** - ワークレットノードをオーディオの宛先（スピーカー）に接続します。

### オーディオレコーダー (`static/js/audio-recorder.js`)

**startAudioRecorderWorklet()** 関数：

- **AudioContextのセットアップ** - 録音用に16kHzのサンプルレートでコンテキストを作成します。
- **マイクアクセス** - 音声入力のためのユーザーメディア許可を要求します。
- **音声処理** - マイクをレコーダーワークレットに接続します。
- **データ変換** - Float32サンプルを16ビットPCM形式に変換します。

### オーディオワークレットプロセッサ

#### PCMプレーヤープロセッサ (`static/js/pcm-player-processor.js`)
**PCMPlayerProcessor**クラスは音声再生を処理します：

- **リングバッファ** - 180秒の24kHz音声用の循環バッファ。
- **データ取り込み** - Int16をFloat32に変換し、バッファに保存します。
- **再生ループ** - バッファから連続的に読み取り、出力チャネルに出力します。
- **オーバーフロー処理** - バッファがいっぱいになると最も古いサンプルを上書きします。

#### PCMレコーダープロセッサ (`static/js/pcm-recorder-processor.js`)
**PCMProcessor**クラスはマイク入力をキャプチャします：

- **音声入力** - 受信オーディオフレームを処理します。
- **データ転送** - Float32サンプルをコピーし、メッセージポート経由でメインスレッドに投稿します。

#### モード切り替え：
- **音声の有効化** - 「Start Audio」ボタンでマイクを有効にし、音声フラグ付きでSSEを再接続します。
- **シームレスな移行** - 既存の接続を閉じ、新しい音声対応セッションを確立します。

クライアントアーキテクチャは、テキストと音声の両方のモダリティでシームレスなリアルタイム通信を可能にし、プロフェッショナルグレードの音声処理のために最新のWeb APIを使用します。

## まとめ

このアプリケーションは、以下の主要な機能を備えた完全なリアルタイムAIエージェントシステムを示しています：

**アーキテクチャのハイライト**：
- **リアルタイム**：部分的なテキスト更新と連続的な音声によるストリーミング応答
- **堅牢**：包括的なエラーハンドリングと自動回復メカニズム
- **モダン**：最新のWeb標準（AudioWorklet、SSE、ES6モジュール）を使用

このシステムは、リアルタイムの対話、Web検索機能、およびマルチメディア通信を必要とする洗練されたAIアプリケーションを構築するための基盤を提供します。

### 本番環境への次のステップ

このシステムを本番環境にデプロイするには、以下の改善を実装することを検討してください：

#### セキュリティ
- **認証**：ランダムなセッションIDを適切なユーザー認証に置き換えます。
- **APIキーのセキュリティ**：環境変数またはシークレット管理サービスを使用します。
- **HTTPS**：すべての通信にTLS暗号化を強制します。
- **レート制限**：乱用を防ぎ、APIコストを制御します。

#### スケーラビリティ
- **永続ストレージ**：インメモリセッションを永続的なセッションに置き換えます。
- **ロードバランシング**：共有セッション状態で複数のサーバーインスタンスをサポートします。
- **音声最適化**：帯域幅の使用を減らすために圧縮を実装します。

#### モニタリング
- **エラートラッキング**：システムの障害を監視し、アラートを発します。
- **APIコストモニタリング**：予算超過を防ぐためにGoogle検索とGeminiの使用状況を追跡します。
- **パフォーマンスメトリクス**：応答時間と音声の遅延を監視します。

#### インフラストラクチャ
- **コンテナ化**：Cloud RunまたはAgent Engineでの一貫したデプロイのためにDockerでパッケージ化します。
- **ヘルスチェック**：アップタイム追跡のためにエンドポイント監視を実装します。