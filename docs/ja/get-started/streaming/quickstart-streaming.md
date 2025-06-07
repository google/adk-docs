# クイックスタート (ストリーミング / Python) {#adk-streaming-quickstart}

このクイックスタートでは、簡単なエージェントを作成し、ADKストリーミングを使用して、低遅延かつ双方向の音声・ビデオ通信を実現する方法を学びます。ADKのインストール、基本的な「Google Search」エージェントの設定、`adk web`ツールを使ったエージェントの実行を試した後、ADKストリーミングと[FastAPI](https://fastapi.tiangolo.com/)を使用して簡単な非同期ウェブアプリを自作する方法を説明します。

**注:** このガイドは、Windows、Mac、Linux環境でのターミナル使用経験があることを前提としています。

## 音声/ビデオストリーミングでサポートされているモデル {#supported-models}

ADKで音声/ビデオストリーミングを使用するには、Live APIをサポートするGeminiモデルを使用する必要があります。Gemini Live APIをサポートする**モデルID**は、以下のドキュメントで確認できます。

-   [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
-   [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## 1. 環境設定とADKのインストール {#1.-setup-installation}

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
pip install google-adk
```

## 2. プロジェクト構造 {#2.-project-structure}

以下のフォルダ構造で空のファイルを作成します。

```console
adk-streaming/  # プロジェクトフォルダ
└── app/ # ウェブアプリフォルダ
    ├── .env # Gemini APIキー
    └── google_search_agent/ # エージェントフォルダ
        ├── __init__.py # Pythonパッケージ
        └── agent.py # エージェントの定義
```

### agent.py

以下のコードブロックを [`agent.py`](http://agent.py) にコピー＆ペーストしてください。

`model`については、前述の[モデルのセクション](#supported-models)で説明したように、モデルIDを再確認してください。

```py
from google.adk.agents import Agent
from google.adk.tools import google_search  # ツールをインポート

root_agent = Agent(
   # エージェントの一意な名前
   name="basic_search_agent",
   # エージェントが使用する大規模言語モデル (LLM)
   model="gemini-2.0-flash-exp",
   # model="gemini-2.0-flash-live-001",  # 2025年2月時点の新しいストリーミングモデルバージョン
   # エージェントの目的の簡単な説明
   description="Google Searchを使って質問に答えるエージェント",
   # エージェントの振る舞いを設定するための指示
   instruction="あなたは熟練の研究者です。常に事実に忠実に行動してください。",
   # Google検索によるグラウンディングを行うためにgoogle_searchツールを追加
   tools=[google_search]
)
```

**注:** テキストと音声/ビデオの両方の入力を有効にするには、モデルがgenerateContent（テキスト用）とbidiGenerateContentメソッドをサポートしている必要があります。これらの機能については、[モデル一覧のドキュメント](https://ai.google.dev/api/models#method:-models.list)を参照して確認してください。このクイックスタートでは、デモンストレーション目的で`gemini-2.0-flash-exp`モデルを利用します。

`agent.py`には、すべてのエージェントのロジックが保存され、`root_agent`を定義する必要があります。

[Google検索によるグラウンディング](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search)機能がいかに簡単に統合できるかにお気づきでしょうか。`Agent`クラスと`google_search`ツールがLLMとの複雑なやり取りや検索APIによるグラウンディングを処理してくれるため、あなたはエージェントの*目的*と*振る舞い*に集中できます。

![intro_components.png](../../assets/quickstart-streaming-tool.png)

以下のコードブロックを `__init__.py` ファイルにコピー＆ペーストしてください。

```py title="__init__.py"
from . import agent
```

## 3. プラットフォームの設定 {#3.-set-up-the-platform}

エージェントを実行するために、Google AI StudioまたはGoogle Cloud Vertex AIのいずれかのプラットフォームを選択します。

=== "Gemini - Google AI Studio"
    1. [Google AI Studio](https://aistudio.google.com/apikey)でAPIキーを取得します。
    2. (`app/`内にある) **`.env`** ファイルを開き、以下のコードをコピー＆ペーストします。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=ここに実際のAPIキーを貼り付け
        ```

    3. `ここに実際のAPIキーを貼り付け` の部分を、実際の`APIキー`に置き換えてください。

=== "Gemini - Google Cloud Vertex AI"
    1. 既存の[Google Cloud](https://cloud.google.com/?e=48754805&hl=en)アカウントとプロジェクトが必要です。
        * [Google Cloudプロジェクトのセットアップ](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
        * [gcloud CLIのセットアップ](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
        * ターミナルから `gcloud auth login` を実行してGoogle Cloudに認証します。
        * [Vertex AI APIの有効化](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)
    2. (`app/`内にある) **`.env`** ファイルを開きます。以下のコードをコピー＆ペーストし、プロジェクトIDとロケーションを更新してください。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=ここに実際のプロジェクトIDを貼り付け
        GOOGLE_CLOUD_LOCATION=us-central1
        ```

## 4. `adk web`でエージェントを試す {#4.-try-it-adk-web}

これでエージェントを試す準備ができました。次のコマンドを実行して**開発用UI**を起動します。まず、カレントディレクトリが`app`になっていることを確認してください。

```shell
cd app
```

また、後の音声・ビデオテストで必要になるため、以下のコマンドで`SSL_CERT_FILE`変数を設定します。

```shell
export SSL_CERT_FILE=$(python -m certifi)
```

次に、開発用UIを実行します。

```shell
adk web
```

!!!info "Windowsユーザーへの注記"

    `_make_subprocess_transport NotImplementedError` が発生した場合は、代わりに `adk web --no-reload` の使用を検討してください。

提供されたURL（通常は `http://localhost:8000` または `http://127.0.0.1:8000`）を**直接ブラウザで開きます**。この接続は完全にローカルマシン上で完結します。`google_search_agent`を選択してください。

### テキストで試す

UIに以下のプロンプトを入力して試してみてください。

*   ニューヨークの天気は？
*   ニューヨークの時間は？
*   パリの天気は？
*   パリの時間は？

エージェントは`google_search`ツールを使用して最新の情報を取得し、これらの質問に答えます。

### 音声とビデオで試す

音声で試すには、ウェブブラウザをリロードし、マイクボタンをクリックして音声入力を有効にし、同じ質問を音声で尋ねます。リアルタイムで答えが音声で返ってきます。

ビデオで試すには、ウェブブラウザをリロードし、カメラボタンをクリックしてビデオ入力を有効にし、「何が見える？」のような質問をします。エージェントはビデオ入力で見えるものを答えます。

### ツールを停止する

コンソールで`Ctrl-C`を押して`adk web`を停止します。

### ADKストリーミングに関する注記

Callback、LongRunningTool、ExampleTool、およびシェルエージェント（例：SequentialAgent）の機能は、ADKストリーミングの将来のバージョンでサポートされる予定です。

おめでとうございます！ これでADKを使用して最初のストリーミングエージェントの作成と対話が正常に完了しました！

## 次のステップ: カスタムストリーミングアプリの構築

[カスタム音声ストリーミングアプリ](../../streaming/custom-streaming.md)のチュートリアルでは、ADKストリーミングと[FastAPI](https://fastapi.tiangolo.com/)で構築されたカスタム非同期ウェブアプリのサーバーとクライアントのコードを概説し、リアルタイムで双方向の音声・テキスト通信を可能にする方法を説明します。