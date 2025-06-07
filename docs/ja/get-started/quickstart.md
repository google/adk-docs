# クイックスタート

このクイックスタートでは、Agent Development Kit (ADK) のインストール、複数のツールを持つ基本的なエージェントのセットアップ、そしてターミナルまたは対話型のブラウザベース開発UIでローカルに実行する方法を説明します。

<!-- <img src="../../assets/quickstart.png" alt="Quickstart setup"> -->

このクイックスタートは、Python 3.9以上またはJava 17以上とターミナルアクセスが可能なローカルIDE（VS Code、PyCharm、IntelliJ IDEAなど）を前提としています。この方法は、アプリケーションを完全にあなたのマシン上で実行し、内部開発に推奨されます。

## 1. 環境のセットアップとADKのインストール {#venv-install}

=== "Python"

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
    pip install google-adk
    ```

=== "Java"

    ADKをインストールし、環境をセットアップするには、次の手順に進んでください。

## 2. エージェントプロジェクトの作成 {#create-agent-project}

### プロジェクト構造

=== "Python"

    以下のプロジェクト構造を作成する必要があります：

    ```console
    parent_folder/
        multi_tool_agent/
            __init__.py
            agent.py
            .env
    ```

    `multi_tool_agent`フォルダを作成します：

    ```bash
    mkdir multi_tool_agent/
    ```

    !!! info "Windowsユーザーへの注意"

        次のいくつかのステップでWindows上でADKを使用する場合、`mkdir`や`echo`のようなコマンドは通常、nullバイトや不正なエンコーディングのファイルを生成するため、ファイルエクスプローラーまたはIDEを使用してPythonファイルを作成することをお勧めします。

    ### `__init__.py`

    次に、フォルダ内に`__init__.py`ファイルを作成します：

    ```shell
    echo "from . import agent" > multi_tool_agent/__init__.py
    ```

    これで`__init__.py`は以下のようになります：

    ```python title="multi_tool_agent/__init__.py"
    --8<-- "examples/python/snippets/get-started/multi_tool_agent/__init__.py"
    ```

    ### `agent.py`

    同じフォルダに`agent.py`ファイルを作成します：

    ```shell
    touch multi_tool_agent/agent.py
    ```

    `agent.py`に以下のコードをコピー＆ペーストします：

    ```python title="multi_tool_agent/agent.py"
    --8<-- "examples/python/snippets/get-started/multi_tool_agent/agent.py"
    ```

    ### `.env`

    同じフォルダに`.env`ファイルを作成します：

    ```shell
    touch multi_tool_agent/.env
    ```

    このファイルに関する詳細は、次のセクション[モデルのセットアップ](#set-up-the-model)で説明します。

=== "Java"

    Javaプロジェクトは通常、以下のプロジェクト構造を持ちます：

    ```console
    project_folder/
    ├── pom.xml (または build.gradle)
    ├── src/
    ├── └── main/
    │       └── java/
    │           └── agents/
    │               └── multitool/
    └── test/
    ```

    ### `MultiToolAgent.java`の作成

    `src/main/java/agents/multitool/`ディレクトリ内の`agents.multitool`パッケージに`MultiToolAgent.java`ソースファイルを作成します。

    `MultiToolAgent.java`に以下のコードをコピー＆ペーストします：

    ```java title="agents/multitool/MultiToolAgent.java"
    --8<-- "examples/java/cloud-run/src/main/java/agents/multitool/MultiToolAgent.java:full_code"
    ```

![intro_components.png](../assets/quickstart-flow-tool.png)

## 3. モデルのセットアップ {#set-up-the-model}

エージェントがユーザーのリクエストを理解し、応答を生成する能力は、大規模言語モデル（LLM）によって支えられています。エージェントは、この外部のLLMサービスに対して安全な呼び出しを行う必要があり、そのためには認証情報が必要です。有効な認証がなければ、LLMサービスはエージェントのリクエストを拒否し、エージェントは機能できなくなります。

=== "Gemini - Google AI Studio"
    1.  [Google AI Studio](https://aistudio.google.com/apikey)からAPIキーを取得します。
    2.  Pythonを使用する場合、（`multi_tool_agent/`内にある）**`.env`**ファイルを開き、以下のコードをコピー＆ペーストします。

        ```env title="multi_tool_agent/.env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=ここに実際のAPIキーを貼り付けてください
        ```

        Javaを使用する場合、環境変数を定義します：

        ```console title="terminal"
        export GOOGLE_GENAI_USE_VERTEXAI=FALSE
        export GOOGLE_API_KEY=ここに実際のAPIキーを貼り付けてください
        ```

    3.  `ここに実際のAPIキーを貼り付けてください`を実際の`APIキー`に置き換えます。

=== "Gemini - Google Cloud Vertex AI"
    1.  既存の[Google Cloud](https://cloud.google.com/?e=48754805&hl=en)アカウントとプロジェクトが必要です。
        *   [Google Cloudプロジェクトのセットアップ](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
        *   [gcloud CLIのセットアップ](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
        *   ターミナルから`gcloud auth login`を実行してGoogle Cloudに認証します。
        *   [Vertex AI APIを有効にする](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)。
    2.  Pythonを使用する場合、（`multi_tool_agent/`内にある）**`.env`**ファイルを開きます。以下のコードをコピー＆ペーストし、プロジェクトIDとロケーションを更新します。

        ```env title="multi_tool_agent/.env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=LOCATION
        ```

        Javaを使用する場合、環境変数を定義します：

        ```console title="terminal"
        export GOOGLE_GENAI_USE_VERTEXAI=TRUE
        export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
        export GOOGLE_CLOUD_LOCATION=LOCATION
        ```

## 4. エージェントの実行 {#run-your-agent}

=== "Python"

    ターミナルを使用して、エージェントプロジェクトの親ディレクトリに移動します（例：`cd ..`を使用）：

    ```console
    parent_folder/      <-- このディレクトリに移動
        multi_tool_agent/
            __init__.py
            agent.py
            .env
    ```

    エージェントと対話するには複数の方法があります：

    === "開発UI (adk web)"
        以下のコマンドを実行して**開発UI**を起動します。

        ```shell
        adk web
        ```
        
        !!!info "Windowsユーザーへの注意"

            `_make_subprocess_transport NotImplementedError`が発生した場合、代わりに`adk web --no-reload`の使用を検討してください。


        **ステップ1：** 提供されたURL（通常は`http://localhost:8000`または`http://127.0.0.1:8000`）をブラウザで直接開きます。

        **ステップ2：** UIの左上隅にあるドロップダウンで、エージェントを選択できます。「multi_tool_agent」を選択します。

        !!!note "トラブルシューティング"

            ドロップダウンメニューに「multi_tool_agent」が表示されない場合は、`adk web`をエージェントフォルダの**親フォルダ**（つまり、multi_tool_agentの親フォルダ）で実行していることを確認してください。

        **ステップ3：** これで、テキストボックスを使用してエージェントとチャットできます：

        ![adk-web-dev-ui-chat.png](../assets/adk-web-dev-ui-chat.png)


        **ステップ4：** 左側の`Events`タブを使用すると、アクションをクリックすることで、個々の関数呼び出し、応答、モデルの応答を検査できます：

        ![adk-web-dev-ui-function-call.png](../assets/adk-web-dev-ui-function-call.png)

        `Events`タブで、`Trace`ボタンをクリックすると、各関数呼び出しのレイテンシを示す各イベントのトレースログを確認できます：

        ![adk-web-dev-ui-trace.png](../assets/adk-web-dev-ui-trace.png)

        **ステップ5：** マイクを有効にしてエージェントと話すこともできます：

        !!!note "音声/ビデオストリーミングのモデルサポート"

            ADKで音声/ビデオストリーミングを使用するには、Live APIをサポートするGeminiモデルを使用する必要があります。Gemini Live APIをサポートする**モデルID**は、ドキュメントで確認できます：

            - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
            - [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

            その後、以前に作成した`agent.py`ファイルの`root_agent`内の`model`文字列を置き換えることができます（[セクションへジャンプ](#agentpy)）。コードは次のようになります：

            ```py
            root_agent = Agent(
                name="weather_time_agent",
                model="モデルIDに置き換えてください", #例: gemini-2.0-flash-live-001
                ...
            ```

        ![adk-web-dev-ui-audio.png](../assets/adk-web-dev-ui-audio.png)

    === "ターミナル (adk run)"

        以下のコマンドを実行して、天気エージェントとチャットします。

        ```
        adk run multi_tool_agent
        ```

        ![adk-run.png](../assets/adk-run.png)

        終了するには、Cmd/Ctrl+Cを使用します。

    === "APIサーバー (adk api_server)"

        `adk api_server`を使用すると、単一のコマンドでローカルのFastAPIサーバーを作成でき、エージェントをデプロイする前にローカルのcURLリクエストをテストできます。

        ![adk-api-server.png](../assets/adk-api-server.png)

        `adk api_server`を使用してテストする方法については、[テストに関するドキュメント](testing.md)を参照してください。

=== "Java"

    ターミナルを使用して、エージェントプロジェクトの親ディレクトリに移動します（例：`cd ..`を使用）：

    ```console
    project_folder/                <-- このディレクトリに移動
    ├── pom.xml (または build.gradle)
    ├── src/
    ├── └── main/
    │       └── java/
    │           └── agents/
    │               └── multitool/
    │                   └── MultiToolAgent.java
    └── test/
    ```

    === "開発UI"

        ターミナルから以下のコマンドを実行して開発UIを起動します。

        **開発UIサーバーのメインクラス名を変更しないでください。**

        ```console title="terminal"
        mvn exec:java \
            -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
            -Dexec.args="--adk.agents.source-dir=src/main/java" \
            -Dexec.classpathScope="compile"
        ```

        **ステップ1：** 提供されたURL（通常は`http://localhost:8080`または`http://127.0.0.1:8080`）をブラウザで直接開きます。

        **ステップ2：** UIの左上隅にあるドロップダウンで、エージェントを選択できます。「multi_tool_agent」を選択します。

        !!!note "トラブルシューティング"

            ドロップダウンメニューに「multi_tool_agent」が表示されない場合は、Javaソースコードがある場所（通常は`src/main/java`）で`mvn`コマンドを実行していることを確認してください。

        **ステップ3：** これで、テキストボックスを使用してエージェントとチャットできます：

        ![adk-web-dev-ui-chat.png](../assets/adk-web-dev-ui-chat.png)

        **ステップ4：** アクションをクリックすることで、個々の関数呼び出し、応答、モデルの応答を検査することもできます：

        ![adk-web-dev-ui-function-call.png](../assets/adk-web-dev-ui-function-call.png)

    === "Maven"

        Mavenを使用する場合、以下のコマンドでJavaクラスの`main()`メソッドを実行します：

        ```console title="terminal"
        mvn compile exec:java -Dexec.mainClass="agents.multitool.MultiToolAgent"
        ```

    === "Gradle"

        Gradleを使用する場合、`build.gradle`または`build.gradle.kts`ビルドファイルには、`plugins`セクションに以下のJavaプラグインが必要です：

        ```groovy
        plugins {
            id("java")
            // 他のプラグイン
        }
        ```

        次に、ビルドファイルのトップレベルで、エージェントの`main()`メソッドを実行するための新しいタスクを作成します：

        ```groovy
        task runAgent(type: JavaExec) {
            classpath = sourceSets.main.runtimeClasspath
            mainClass = "agents.multitool.MultiToolAgent"
        }
        ```

        最後に、コマンドラインで以下のコマンドを実行します：

        ```console
        gradle runAgent
        ```

### 📝 試してみるプロンプトの例

*   What is the weather in New York?
*   What is the time in New York?
*   What is the weather in Paris?
*   What is the time in Paris?

## 🎉 おめでとうございます！

ADKを使用して初めてのエージェントを作成し、対話することに成功しました！

---

## 🛣️ 次のステップ

*   **チュートリアルに進む**: エージェントにメモリ、セッション、状態を追加する方法を学びます：
    [チュートリアル](../tutorials/index.md)。
*   **高度な設定を掘り下げる:** プロジェクト構造、設定、およびその他のインターフェースに関する詳細については、[セットアップ](installation.md)セクションを参照してください。
*   **コアコンセプトを理解する:** [エージェントの概念](../agents/index.md)について学びます。