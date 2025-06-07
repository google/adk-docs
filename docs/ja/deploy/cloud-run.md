# Cloud Runへのデプロイ

[Cloud Run](https://cloud.google.com/run)は、Googleのスケーラブルなインフラストラクチャ上で直接コードを実行できる、フルマネージドのプラットフォームです。

エージェントをデプロイするには、`adk deploy cloud_run`コマンド（*Pythonに推奨*）を使用するか、Cloud Runを介して`gcloud run deploy`コマンドを使用する方法があります。

## エージェントのサンプル

各コマンドでは、[LLMエージェント](../agents/llm-agents.md)ページで定義されている`Capital Agent`のサンプルを参照します。これはディレクトリ（例：`capital_agent`）内にあると仮定します。

先に進む前に、エージェントのコードが以下のように設定されていることを確認してください：

=== "Python"

    1.  エージェントのコードは、エージェントディレクトリ内の`agent.py`というファイルにあります。
    2.  エージェント変数の名前は`root_agent`です。
    3.  `__init__.py`がエージェントディレクトリ内にあり、`from . import agent`を含んでいます。

=== "Java"

    1.  エージェントのコードは、エージェントディレクトリ内の`CapitalAgent.java`というファイルにあります。
    2.  エージェント変数はグローバルで、`public static BaseAgent ROOT_AGENT`の形式に従います。
    3.  エージェントの定義は静的クラスメソッド内に存在します。

    詳細については、以下のセクションを参照してください。Githubリポジトリには[サンプルアプリ](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run)もあります。

## 環境変数

[セットアップとインストール](../get-started/installation.md)ガイドで説明されているように、環境変数を設定します。

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1 # またはお好みのロケーション
export GOOGLE_GENAI_USE_VERTEXAI=True```

*（`your-project-id`を実際のGCPプロジェクトIDに置き換えてください）*

## デプロイコマンド

=== "Python - adk CLI"

    ### adk CLI

    `adk deploy cloud_run`コマンドは、エージェントのコードをGoogle Cloud Runにデプロイします。

    Google Cloudで認証済みであることを確認してください（`gcloud auth login`および`gcloud config set project <your-project-id>`）。

    #### 環境変数の設定

    オプションですが推奨：環境変数を設定すると、デプロイコマンドがすっきりします。

    ```bash
    # Google CloudプロジェクトIDを設定
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

    # 希望するGoogle Cloudのロケーションを設定
    export GOOGLE_CLOUD_LOCATION="us-central1" # 例：ロケーション

    # エージェントコードディレクトリへのパスを設定
    export AGENT_PATH="./capital_agent" # capital_agentが現在のディレクトリにあると仮定

    # Cloud Runサービスの名前を設定（オプション）
    export SERVICE_NAME="capital-agent-service"

    # アプリケーション名を設定（オプション）
    export APP_NAME="capital-agent-app"
    ```

    #### コマンドの使用法

    ##### 最小限のコマンド

    ```bash
    adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    $AGENT_PATH
    ```

    ##### オプションフラグ付きの完全なコマンド

    ```bash
    adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --service_name=$SERVICE_NAME \
    --app_name=$APP_NAME \
    --with_ui \
    $AGENT_PATH
    ```

    ##### 引数

    *   `AGENT_PATH`: (必須) エージェントのソースコードを含むディレクトリへのパスを指定する位置引数（例：例では`$AGENT_PATH`、または`capital_agent/`）。このディレクトリには、少なくとも`__init__.py`とメインのエージェントファイル（例：`agent.py`）が含まれている必要があります。

    ##### オプション

    *   `--project TEXT`: (必須) あなたのGoogle CloudプロジェクトID（例：`$GOOGLE_CLOUD_PROJECT`）。
    *   `--region TEXT`: (必須) デプロイするGoogle Cloudのロケーション（例：`$GOOGLE_CLOUD_LOCATION`、`us-central1`）。
    *   `--service_name TEXT`: (オプション) Cloud Runサービスの名前（例：`$SERVICE_NAME`）。デフォルトは`adk-default-service-name`。
    *   `--app_name TEXT`: (オプション) ADK APIサーバーのアプリケーション名（例：`$APP_NAME`）。デフォルトは`AGENT_PATH`で指定されたディレクトリの名前（例：`AGENT_PATH`が`./capital_agent`なら`capital_agent`）。
    *   `--agent_engine_id TEXT`: (オプション) Vertex AI Agent Engineを介してマネージドセッションサービスを使用している場合、そのリソースIDをここで提供します。
    *   `--port INTEGER`: (オプション) コンテナ内でADK APIサーバーがリッスンするポート番号。デフォルトは8000。
    *   `--with_ui`: (オプション) これを含めると、エージェントAPIサーバーと共にADK開発UIもデプロイされます。デフォルトでは、APIサーバーのみがデプロイされます。
    *   `--temp_folder TEXT`: (オプション) デプロイプロセス中に生成される中間ファイルを保存するディレクトリを指定します。デフォルトは、システムの一次ディレクトリ内のタイムスタンプ付きフォルダです。*（注：このオプションは、問題をトラブルシューティングする場合を除き、通常は不要です）*。
    *   `--help`: ヘルプメッセージを表示して終了します。

    ##### 認証アクセス
    デプロイプロセス中に、「`[your-service-name]`への未認証の呼び出しを許可しますか？(y/N)?」と尋ねられることがあります。

    *   認証なしでエージェントのAPIエンドポイントへのパブリックアクセスを許可する場合は`y`を入力します。
    *   認証を要求する場合（例：「エージェントのテスト」セクションで示すIDトークンの使用）は`N`を入力するか、デフォルトでEnterキーを押します。

    正常に実行されると、コマンドはエージェントをCloud Runにデプロイし、デプロイされたサービスのURLを提供します。

=== "Python - gcloud CLI"

    ### gcloud CLI

    または、標準の`gcloud run deploy`コマンドと`Dockerfile`を使用してデプロイすることもできます。この方法は`adk`コマンドと比較して手動でのセットアップが多く必要ですが、特にカスタムの[FastAPI](https://fastapi.tiangolo.com/)アプリケーションにエージェントを埋め込みたい場合に柔軟性を提供します。

    Google Cloudで認証済みであることを確認してください（`gcloud auth login`および`gcloud config set project <your-project-id>`）。

    #### プロジェクト構造

    プロジェクトファイルを以下のように整理します：

    ```txt
    your-project-directory/
    ├── capital_agent/
    │   ├── __init__.py
    │   └── agent.py       # エージェントのコード（「エージェントのサンプル」タブを参照）
    ├── main.py            # FastAPIアプリケーションのエントリポイント
    ├── requirements.txt   # Pythonの依存関係
    └── Dockerfile         # コンテナのビルド手順
    ```

    `your-project-directory/`のルートに以下のファイル（`main.py`、`requirements.txt`、`Dockerfile`）を作成します。

    #### コードファイル

    1.  このファイルは、ADKの`get_fast_api_app()`を使用してFastAPIアプリケーションをセットアップします：

        ```python title="main.py"
        import os

        import uvicorn
        from google.adk.cli.fast_api import get_fast_api_app

        # main.pyが配置されているディレクトリを取得
        AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
        # セッションDBのURL例（例：SQLite）
        SESSION_DB_URL = "sqlite:///./sessions.db"
        # CORSの許可オリジン例
        ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
        # Webインターフェースを提供する場合はweb=True、それ以外はFalseに設定
        SERVE_WEB_INTERFACE = True

        # FastAPIアプリインスタンスを取得する関数を呼び出す
        # エージェントディレクトリ名（'capital_agent'）がエージェントフォルダと一致することを確認
        app = get_fast_api_app(
            agents_dir=AGENT_DIR,
            session_db_url=SESSION_DB_URL,
            allow_origins=ALLOWED_ORIGINS,
            web=SERVE_WEB_INTERFACE,
        )

        # 必要に応じて、以下にFastAPIのルートや設定を追加できます
        # 例：
        # @app.get("/hello")
        # async def read_root():
        #     return {"Hello": "World"}

        if __name__ == "__main__":
            # Cloud Runから提供されるPORT環境変数を使用し、デフォルトは8080
            uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
        ```

        *注：`agent_dir`を`main.py`があるディレクトリに指定し、Cloud Runとの互換性のために`os.environ.get("PORT", 8080)`を使用します。*

    2.  必要なPythonパッケージをリストアップします：

        ```txt title="requirements.txt"
        google_adk
        # エージェントが必要とするその他の依存関係を追加
        ```

    3.  コンテナイメージを定義します：

        ```dockerfile title="Dockerfile"
        FROM python:3.13-slim
        WORKDIR /app

        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        RUN adduser --disabled-password --gecos "" myuser && \
            chown -R myuser:myuser /app

        COPY . .

        USER myuser

        ENV PATH="/home/myuser/.local/bin:$PATH"

        CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
        ```

    #### 複数のエージェントの定義

    `your-project-directory/`のルートに個別のフォルダを作成することで、同じCloud Runインスタンス内に複数のエージェントを定義し、デプロイできます。各フォルダは1つのエージェントを表し、その設定で`root_agent`を定義する必要があります。

    構造例：

    ```txt
    your-project-directory/
    ├── capital_agent/
    │   ├── __init__.py
    │   └── agent.py       # `root_agent`の定義を含む
    ├── population_agent/
    │   ├── __init__.py
    │   └── agent.py       # `root_agent`の定義を含む
    └── ...
    ```

    #### `gcloud`を使用したデプロイ

    ターミナルで`your-project-directory`に移動します。

    ```bash
    gcloud run deploy capital-agent-service \
    --source . \
    --region $GOOGLE_CLOUD_LOCATION \
    --project $GOOGLE_CLOUD_PROJECT \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
    # エージェントが必要とするその他の環境変数を追加
    ```

    *   `capital-agent-service`: Cloud Runサービスに付けたい名前。
    *   `--source .`: gcloudに現在のディレクトリのDockerfileからコンテナイメージをビルドするように指示します。
    *   `--region`: デプロイリージョンを指定します。
    *   `--project`: GCPプロジェクトを指定します。
    *   `--allow-unauthenticated`: サービスへのパブリックアクセスを許可します。プライベートサービスの場合はこのフラグを削除します。
    *   `--set-env-vars`: 実行中のコンテナに必要な環境変数を渡します。ADKとエージェントが必要とするすべての変数（Application Default Credentialsを使用しない場合のAPIキーなど）が含まれていることを確認してください。

    `gcloud`はDockerイメージをビルドし、Google Artifact Registryにプッシュし、Cloud Runにデプロイします。完了すると、デプロイされたサービスのURLが出力されます。

    デプロイオプションの完全なリストについては、[`gcloud run deploy`リファレンスドキュメント](https://cloud.google.com/sdk/gcloud/reference/run/deploy)を参照してください。

=== "Java - gcloud CLI"

    ### gcloud CLI

    標準の`gcloud run deploy`コマンドと`Dockerfile`を使用してJavaエージェントをデプロイできます。これは現在、JavaエージェントをGoogle Cloud Runにデプロイする推奨方法です。

    Google Cloudで[認証](https://cloud.google.com/docs/authentication/gcloud)済みであることを確認してください。
    具体的には、ターミナルから`gcloud auth login`と`gcloud config set project <your-project-id>`コマンドを実行します。

    #### プロジェクト構造

    プロジェクトファイルを以下のように整理します：

    ```txt
    your-project-directory/
    ├── src/
    │   └── main/
    │       └── java/
    │             └── agents/
    │                 ├── capitalagent/
    │                     └── CapitalAgent.java    # エージェントのコード
    ├── pom.xml                                    # Java ADKとADK-devの依存関係
    └── Dockerfile                                 # コンテナのビルド手順
    ```

    プロジェクトディレクトリのルートに`pom.xml`と`Dockerfile`を作成します。エージェントのコードファイル（`CapitalAgent.java`）は、上記のようにディレクトリ内に配置します。

    #### コードファイル

    1.  これはエージェントの定義です。これは[LLMエージェント](../agents/llm-agents.md)にあるコードと同じですが、2つの注意点があります：
       
           * エージェントは**グローバルなpublic static変数**として初期化されます。
    
           * エージェントの定義は、静的メソッド内か、宣言時にインラインで公開できます。

        ```java title="CapitalAgent.java"
        --8<-- "examples/java/cloud-run/src/main/java/demo/agents/capitalagent/CapitalAgent.java:full_code"
        ```

    2.  `pom.xml`ファイルに以下の依存関係とプラグインを追加します。

        ```xml title="pom.xml"
        <dependencies>
          <dependency>
             <groupId>com.google.adk</groupId>
             <artifactId>google-adk</artifactId>
             <version>0.1.0</version>
          </dependency>
          <dependency>
             <groupId>com.google.adk</groupId>
             <artifactId>google-adk-dev</artifactId>
             <version>0.1.0</version>
          </dependency>
        </dependencies>
        
        <plugin>
          <groupId>org.codehaus.mojo</groupId>
          <artifactId>exec-maven-plugin</artifactId>
          <version>3.2.0</version>
          <configuration>
            <mainClass>com.google.adk.web.AdkWebServer</mainClass>
            <classpathScope>compile</classpathScope>
          </configuration>
        </plugin>
        ```

    3.  コンテナイメージを定義します：

        ```dockerfile title="Dockerfile"
        --8<-- "examples/java/cloud-run/Dockerfile"
        ```

    #### `gcloud`を使用したデプロイ

    ターミナルで`your-project-directory`に移動します。

    ```bash
    gcloud run deploy capital-agent-service \
    --source . \
    --region $GOOGLE_CLOUD_LOCATION \
    --project $GOOGLE_CLOUD_PROJECT \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
    # エージェントが必要とするその他の環境変数を追加
    ```

    *   `capital-agent-service`: Cloud Runサービスに付けたい名前。
    *   `--source .`: gcloudに現在のディレクトリのDockerfileからコンテナイメージをビルドするように指示します。
    *   `--region`: デプロイリージョンを指定します。
    *   `--project`: GCPプロジェクトを指定します。
    *   `--allow-unauthenticated`: サービスへのパブリックアクセスを許可します。プライベートサービスの場合はこのフラグを削除します。
    *   `--set-env-vars`: 実行中のコンテナに必要な環境変数を渡します。ADKとエージェントが必要とするすべての変数（Application Default Credentialsを使用しない場合のAPIキーなど）が含まれていることを確認してください。

    `gcloud`はDockerイメージをビルドし、Google Artifact Registryにプッシュし、Cloud Runにデプロイします。完了すると、デプロイされたサービスのURLが出力されます。

    デプロイオプションの完全なリストについては、[`gcloud run deploy`リファレンスドキュメント](https://cloud.google.com/sdk/gcloud/reference/run/deploy)を参照してください。

## エージェントのテスト

エージェントがCloud Runにデプロイされたら、デプロイされたUI（有効な場合）を介して、または`curl`のようなツールを使用して直接APIエンドポイントと対話できます。デプロイ後に提供されるサービスURLが必要です。

=== "UIテスト"

    ### UIテスト

    UIを有効にしてエージェントをデプロイした場合：

    *   **adk CLI:** デプロイ時に`--with_ui`フラグを含めました。
    *   **gcloud CLI:** `main.py`で`SERVE_WEB_INTERFACE = True`と設定しました。

    Webブラウザでデプロイ後に提供されるCloud RunサービスのURLに移動するだけで、エージェントをテストできます。

    ```bash
    # URL形式の例
    # https://your-service-name-abc123xyz.a.run.app
    ```

    ADK開発UIを使用すると、エージェントと対話し、セッションを管理し、実行の詳細をブラウザで直接表示できます。

    エージェントが意図したとおりに動作していることを確認するには、次のことができます：

    1.  ドロップダウンメニューからエージェントを選択します。
    2.  メッセージを入力し、エージェントから期待される応答を受け取ることを確認します。

    予期しない動作が発生した場合は、[Cloud Run](https://console.cloud.google.com/run)のコンソールログを確認してください。

=== "APIテスト (curl)"

    ### APIテスト (curl)

    `curl`のようなツールを使用して、エージェントのAPIエンドポイントと対話できます。これは、プログラムによる対話や、UIなしでデプロイした場合に便利です。

    デプロイ後に提供されるサービスURLと、サービスが未認証アクセスを許可するように設定されていない場合は認証用のIDトークンが必要です。

    #### アプリケーションURLの設定

    例のURLを、デプロイされたCloud Runサービスの実際のURLに置き換えます。

    ```bash
    export APP_URL="YOUR_CLOUD_RUN_SERVICE_URL"
    # 例： export APP_URL="https://adk-default-service-name-abc123xyz.a.run.app"
    ```

    #### IDトークンの取得（必要な場合）

    サービスが認証を必要とする場合（つまり、`gcloud`で`--allow-unauthenticated`を使用しなかったか、`adk`のプロンプトで'N'と答えた場合）、IDトークンを取得します。

    ```bash
    export TOKEN=$(gcloud auth print-identity-token)
    ```

    *サービスが未認証アクセスを許可している場合は、以下の`curl`コマンドから`-H "Authorization: Bearer $TOKEN"`ヘッダーを省略できます。*

    #### 利用可能なアプリのリスト表示

    デプロイされたアプリケーション名を確認します。

    ```bash
    curl -X GET -H "Authorization: Bearer $TOKEN" $APP_URL/list-apps
    ```

    *（必要に応じて、この出力に基づいて以下のコマンドの`app_name`を調整してください。デフォルトは多くの場合、エージェントディレクトリ名、例：`capital_agent`です）*。

    #### セッションの作成または更新

    特定のユーザーとセッションの状態を初期化または更新します。`capital_agent`を実際のアプリ名に置き換えてください。`user_123`と`session_abc`の値は例であり、希望のユーザーIDとセッションIDに置き換えることができます。

    ```bash
    curl -X POST -H "Authorization: Bearer $TOKEN" \
        $APP_URL/apps/capital_agent/users/user_123/sessions/session_abc \
        -H "Content-Type: application/json" \
        -d '{"state": {"preferred_language": "English", "visit_count": 5}}'
    ```

    #### エージェントの実行

    エージェントにプロンプトを送信します。`capital_agent`をアプリ名に置き換え、ユーザー/セッションIDとプロンプトを必要に応じて調整します。

    ```bash
    curl -X POST -H "Authorization: Bearer $TOKEN" \
        $APP_URL/run_sse \
        -H "Content-Type: application/json" \
        -d '{
        "app_name": "capital_agent",
        "user_id": "user_123",
        "session_id": "session_abc",
        "new_message": {
            "role": "user",
            "parts": [{
            "text": "カナダの首都は何ですか？"
            }]
        },
        "streaming": false
        }'
    ```

    *   サーバー送信イベント（SSE）を受信したい場合は、`"streaming": true`に設定します。
    *   応答には、最終的な回答を含むエージェントの実行イベントが含まれます。