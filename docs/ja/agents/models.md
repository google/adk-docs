# ADKでさまざまなモデルを使用する

!!! Note
    Java ADKは現在、GeminiおよびAnthropicモデルをサポートしています。より多くのモデルのサポートが近日中に追加される予定です。

Agent Development Kit (ADK)は柔軟性を重視して設計されており、さまざまな大規模言語モデル（LLM）をエージェントに統合することができます。Google Geminiモデルの設定については[基盤モデルのセットアップ](../get-started/installation.md)ガイドで説明していますが、このページでは、Geminiを効果的に活用し、外部でホストされているモデルやローカルで実行されているモデルを含む他の人気のあるモデルを統合する方法について詳しく説明します。

ADKは主に2つのメカニズムでモデルを統合します：

1.  **直接文字列/レジストリ：** Google Cloudと密接に統合されたモデル（Google AI StudioやVertex AI経由でアクセスされるGeminiモデルなど）や、Vertex AIエンドポイントでホストされているモデル向けです。通常、モデル名またはエンドポイントのリソース文字列を`LlmAgent`に直接提供します。ADKの内部レジストリがこの文字列を適切なバックエンドクライアントに解決し、多くの場合`google-genai`ライブラリを利用します。
2.  **ラッパークラス：** Googleエコシステム外のモデルや、特定のクライアント設定が必要なモデル（LiteLLM経由でアクセスされるモデルなど）との幅広い互換性のために使用します。特定のラッパークラス（例：`LiteLlm`）をインスタンス化し、このオブジェクトを`LlmAgent`の`model`パラメータとして渡します。

以下のセクションでは、ニーズに応じてこれらの方法を使用するためのガイドを提供します。

## Google Geminiモデルの使用

これは、ADK内でGoogleの主力モデルを使用する最も直接的な方法です。

**統合方法：** モデルの識別子文字列を`LlmAgent`（またはそのエイリアスである`Agent`）の`model`パラメータに直接渡します。

**バックエンドオプションとセットアップ：**

ADKがGeminiのために内部で使用する`google-genai`ライブラリは、Google AI StudioまたはVertex AIのいずれかを通じて接続できます。

!!!note "音声/ビデオストリーミングのモデルサポート"

    ADKで音声/ビデオストリーミングを使用するには、Live APIをサポートするGeminiモデルを使用する必要があります。Gemini Live APIをサポートする**モデルID**は、ドキュメントで確認できます：

    - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
    - [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

### Google AI Studio

*   **ユースケース：** Google AI Studioは、Geminiを始める最も簡単な方法です。[APIキー](https://aistudio.google.com/app/apikey)さえあれば利用できます。迅速なプロトタイピングと開発に最適です。
*   **セットアップ：** 通常、APIキーが必要です：
    *   環境変数として設定するか、
    *   以下の例のように、`Client`を介してモデルの初期化時に渡します。

```shell
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

*   **モデル：** 利用可能なすべてのモデルは[Google AI for Developersサイト](https://ai.google.dev/gemini-api/docs/models)で確認できます。

### Vertex AI

*   **ユースケース：** Google Cloudインフラストラクチャを活用する本番アプリケーションに推奨されます。Vertex AI上のGeminiは、エンタープライズグレードの機能、セキュリティ、およびコンプライアンス制御をサポートします。
*   **セットアップ：**
    *   Application Default Credentials (ADC)を使用して認証します：

        ```shell
        gcloud auth application-default login
        ```

    *   これらの変数を環境変数として設定するか、モデルの初期化時に直接提供します。
            
         Google Cloudプロジェクトとロケーションを設定します：
    
         ```shell
         export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
         export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # 例：us-central1
         ```     
    
         ライブラリに明示的にVertex AIを使用するように指示します：
    
         ```shell
         export GOOGLE_GENAI_USE_VERTEXAI=TRUE
         ```

*   **モデル：** 利用可能なモデルIDは[Vertex AIドキュメント](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)で確認できます。

**例：**

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    
    # --- 安定版のGemini Flashモデルを使用した例 ---
    agent_gemini_flash = LlmAgent(
        # 最新の安定版Flashモデル識別子を使用
        model="gemini-2.0-flash",
        name="gemini_flash_agent",
        instruction="あなたは高速で親切なGeminiアシスタントです。",
        # ... その他のエージェントパラメータ
    )
    
    # --- 強力なGemini Proモデルを使用した例 ---
    # 注：常に公式のGeminiドキュメントで最新のモデル名を確認してください。
    # 必要に応じて特定のプレビューバージョンも含まれます。プレビューモデルは
    # 利用可能性やクォータ制限が異なる場合があります。
    agent_gemini_pro = LlmAgent(
        # 最新の一般提供されているProモデル識別子を使用
        model="gemini-2.5-pro-preview-03-25",
        name="gemini_pro_agent",
        instruction="あなたは強力で知識豊富なGeminiアシスタントです。",
        # ... その他のエージェントパラメータ
    )
    ```

=== "Java"

    ```java
    // --- 例1：環境変数を使用して安定版のGemini Flashモデルを使用 ---
    LlmAgent agentGeminiFlash =
        LlmAgent.builder()
            // 最新の安定版Flashモデル識別子を使用
            .model("gemini-2.0-flash") // このモデルを使用するために環境変数を設定
            .name("gemini_flash_agent")
            .instruction("あなたは高速で親切なGeminiアシスタントです。")
            // ... その他のエージェントパラメータ
            .build();

    // --- 例2：モデルにAPIキーを指定して強力なGemini Proモデルを使用 ---
    LlmAgent agentGeminiPro =
        LlmAgent.builder()
            // 最新の一般提供されているProモデル識別子を使用
            .model(new Gemini("gemini-2.5-pro-preview-03-25",
                Client.builder()
                    .vertexAI(false)
                    .apiKey("API_KEY") // APIキー（またはプロジェクト/ロケーション）を設定
                    .build()))
            // または、APIキーを直接渡すこともできます
            // .model(new Gemini("gemini-2.5-pro-preview-03-25", "API_KEY"))
            .name("gemini_pro_agent")
            .instruction("あなたは強力で知識豊富なGeminiアシスタントです。")
            // ... その他のエージェントパラメータ
            .build();

    // 注：常に公式のGeminiドキュメントで最新のモデル名を確認してください。
    // 必要に応じて特定のプレビューバージョンも含まれます。プレビューモデルは
    // 利用可能性やクォータ制限が異なる場合があります。
    ```

## Anthropicモデルの使用

![java_only](https://img.shields.io/badge/サポート対象-Java-orange){ title="この機能は現在Javaで利用可能です。直接のAnthropic API（Vertex以外）のPythonサポートはLiteLLM経由です。" }

AnthropicのClaudeモデルを、APIキーを使用して直接、またはVertex AIバックエンドから、ADKの`Claude`ラッパークラスを使用してJava ADKアプリケーションに統合できます。

Vertex AIバックエンドについては、[Vertex AI上のサードパーティモデル](#third-party-models-on-vertex-ai-eg-anthropic-claude)セクションを参照してください。

**前提条件：**

1.  **依存関係：**
    *   **Anthropic SDKクラス（推移的）：** Java ADKの`com.google.adk.models.Claude`ラッパーは、Anthropicの公式Java SDKのクラスに依存しています。これらは通常、**推移的依存関係**として含まれます。

2.  **Anthropic APIキー：**
    *   AnthropicからAPIキーを取得します。このキーはシークレットマネージャーを使用して安全に管理してください。

**統合：**

`com.google.adk.models.Claude`をインスタンス化し、目的のClaudeモデル名とAPIキーで設定された`AnthropicOkHttpClient`を提供します。その後、この`Claude`インスタンスを`LlmAgent`に渡します。

**例：**

```java
import com.anthropic.client.AnthropicClient;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Claude;
import com.anthropic.client.okhttp.AnthropicOkHttpClient; // AnthropicのSDKから

public class DirectAnthropicAgent {
  
  private static final String CLAUDE_MODEL_ID = "claude-3-7-sonnet-latest"; // またはお好みのClaudeモデル

  public static LlmAgent createAgent() {

    // 機密キーは安全な設定から読み込むことをお勧めします
    AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
        .apiKey("ANTHROPIC_API_KEY")
        .build();

    Claude claudeModel = new Claude(
        CLAUDE_MODEL_ID,
        anthropicClient
    );

    return LlmAgent.builder()
        .name("claude_direct_agent")
        .model(claudeModel)
        .instruction("あなたはAnthropic Claudeを搭載した親切なAIアシスタントです。")
        // ... その他のLlmAgent設定
        .build();
  }

  public static void main(String[] args) {
    try {
      LlmAgent agent = createAgent();
      System.out.println("直接のAnthropicエージェントが正常に作成されました: " + agent.name());
    } catch (IllegalStateException e) {
      System.err.println("エージェントの作成中にエラーが発生しました: " + e.getMessage());
    }
  }
}
```

## LiteLLMを介したクラウドおよびプロプライエタリモデルの使用

![python_only](https://img.shields.io/badge/サポート対象-Python-blue)

OpenAI、Anthropic（Vertex AI以外）、Cohereなど、さまざまなプロバイダーからの広範なLLMにアクセスするために、ADKはLiteLLMライブラリを介した統合を提供します。

**統合方法：** `LiteLlm`ラッパークラスをインスタンス化し、それを`LlmAgent`の`model`パラメータに渡します。

**LiteLLMの概要：** [LiteLLM](https://docs.litellm.ai/)は翻訳レイヤーとして機能し、100以上のLLMに対して標準化されたOpenAI互換のインターフェースを提供します。

**セットアップ：**

1.  **LiteLLMのインストール：**
    ```shell
    pip install litellm
    ```
2.  **プロバイダーAPIキーの設定：** 使用する特定のプロバイダーのAPIキーを環境変数として設定します。

    *   *OpenAIの例：*

        ```shell
        export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
        ```

    *   *Anthropic（Vertex AI以外）の例：*

        ```shell
        export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
        ```

    *   *他のプロバイダーの正しい環境変数名については、[LiteLLMプロバイダーのドキュメント](https://docs.litellm.ai/docs/providers)を参照してください。*

        **例：**

        ```python
        from google.adk.agents import LlmAgent
        from google.adk.models.lite_llm import LiteLlm

        # --- OpenAIのGPT-4oを使用したエージェントの例 ---
        # (OPENAI_API_KEYが必要)
        agent_openai = LlmAgent(
            model=LiteLlm(model="openai/gpt-4o"), # LiteLLMのモデル文字列形式
            name="openai_agent",
            instruction="あなたはGPT-4oを搭載した親切なアシスタントです。",
            # ... その他のエージェントパラメータ
        )

        # --- AnthropicのClaude Haiku（Vertex以外）を使用したエージェントの例 ---
        # (ANTHROPIC_API_KEYが必要)
        agent_claude_direct = LlmAgent(
            model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
            name="claude_direct_agent",
            instruction="あなたはClaude Haikuを搭載したアシスタントです。",
            # ... その他のエージェントパラメータ
        )
        ```

!!!info "Windowsユーザーへの注意"

    ### WindowsでのLiteLLM UnicodeDecodeErrorの回避
    WindowsでLiteLLMを使用してADKエージェントを実行すると、以下のエラーに遭遇することがあります：
    ```
    UnicodeDecodeError: 'charmap' codec can't decode byte...
    ```
    この問題は、`litellm`（LiteLlmが使用）がキャッシュされたファイル（例：モデルの価格情報）をUTF-8ではなく、デフォルトのWindowsエンコーディング（`cp1252`）で読み込もうとするために発生します。
    Windowsユーザーは、`PYTHONUTF8`環境変数を`1`に設定することでこの問題を回避できます。これにより、PythonがグローバルにUTF-8を使用するようになります。
    **例（PowerShell）：**
    ```powershell
    # 現在のセッションで設定
    $env:PYTHONUTF8 = "1"
    # ユーザーに対して永続的に設定
    [System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', [System.EnvironmentVariableTarget]::User)
    この設定を適用すると、PythonがUTF-8を使用してキャッシュファイルを読み込むようになり、デコードエラーを回避できます。
    ```

## LiteLLMを介したオープンおよびローカルモデルの使用

![python_only](https://img.shields.io/badge/サポート対象-Python-blue)

最大限の制御、コスト削減、プライバシー、またはオフラインでのユースケースのために、オープンソースモデルをローカルで実行したり、自己ホストしたりして、LiteLLMを使用して統合することができます。

**統合方法：** ローカルモデルサーバーを指すように設定された`LiteLlm`ラッパークラスをインスタンス化します。

### Ollamaの統合

[Ollama](https://ollama.com/)を使用すると、オープンソースモデルをローカルで簡単に実行できます。

#### モデルの選択

エージェントがツールに依存している場合は、[Ollamaウェブサイト](https://ollama.com/search?c=tools)からツールサポートのあるモデルを選択してください。

信頼性の高い結果を得るためには、ツールサポートのある適度なサイズのモデルを使用することをお勧めします。

モデルのツールサポートは、以下のコマンドで確認できます：

```bash
ollama show mistral-small3.1
  Model
    architecture        mistral3
    parameters          24.0B
    context length      131072
    embedding length    5120
    quantization        Q4_K_M

  Capabilities
    completion
    vision
    tools
```

機能の下に`tools`がリストされているはずです。

モデルが使用しているテンプレートを確認し、必要に応じて調整することもできます。

```bash
ollama show --modelfile llama3.2 > model_file_to_modify
```

例えば、上記のモデルのデフォルトテンプレートは、モデルが常に関数を呼び出すことを暗黙のうちに示唆しています。これにより、関数呼び出しの無限ループが発生する可能性があります。

```
以下の関数が与えられた場合、与えられたプロンプトに最もよく答える関数呼び出しのJSONを、適切な引数とともに応答してください。

{"name": 関数名, "parameters": 引数名とその値の辞書} の形式で応答してください。変数は使用しないでください。
```

無限のツール呼び出しループを防ぐために、このようなプロンプトをより説明的なものに置き換えることができます。

例：

```
ユーザーのプロンプトと以下にリストされている利用可能な関数を確認してください。
まず、これらの関数のいずれかを呼び出すことが最も適切な応答方法であるかどうかを判断します。プロンプトが特定のアクションを要求したり、外部データの検索を必要としたり、関数によって処理される計算を含んでいたりする場合、関数呼び出しが必要になる可能性が高いです。プロンプトが一般的な質問であるか、直接回答できる場合は、関数呼び出しは必要ない可能性が高いです。

関数呼び出しが必要であると判断した場合：{"name": "関数名", "parameters": {"引数名": "値"}} の形式のJSONオブジェクトのみで応答してください。パラメータ値が変数ではなく、具体的な値であることを確認してください。

関数呼び出しが不要であると判断した場合：プレーンテキストで直接ユーザーのプロンプトに応答し、要求された回答または情報を提供してください。JSONは出力しないでください。
```

その後、以下のコマンドで新しいモデルを作成できます：

```bash
ollama create llama3.2-modified -f model_file_to_modify
```

#### ollama_chatプロバイダーの使用

当社のLiteLLMラッパーを使用して、Ollamaモデルでエージェントを作成できます。

```py
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral-small3.1"),
    name="dice_agent",
    description=(
        "8面のサイコロを振ったり、素数かどうかをチェックしたりできるハローワールドエージェント。"
    ),
    instruction="""
      あなたはサイコロを振り、サイコロの目の結果についての質問に答えます。
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

**`ollama`ではなく、プロバイダーとして`ollama_chat`を設定することが重要です。`ollama`を使用すると、無限のツール呼び出しループや以前のコンテキストの無視など、予期しない振る舞いが発生します。**

`api_base`は生成のためにLiteLLM内で提供できますが、LiteLLMライブラリはv1.65.5現在、完了後に代わりに環境変数に依存して他のAPIを呼び出しています。そのため、現時点では、Ollamaサーバーを指すように環境変数`OLLAMA_API_BASE`を設定することをお勧めします。

```bash
export OLLAMA_API_BASE="http://localhost:11434"
adk web
```

#### openaiプロバイダーの使用

あるいは、プロバイダー名として`openai`を使用することもできます。ただし、これには`OLLAMA_API_BASE`の代わりに`OPENAI_API_BASE=http://localhost:11434/v1`と`OPENAI_API_KEY=anything`の環境変数を設定する必要があります。**api_baseの末尾に`/v1`が付いていることに注意してください。**

```py
root_agent = Agent(
    model=LiteLlm(model="openai/mistral-small3.1"),
    name="dice_agent",
    description=(
        "8面のサイコロを振ったり、素数かどうかをチェックしたりできるハローワールドエージェント。"
    ),
    instruction="""
      あなたはサイコロを振り、サイコロの目の結果についての質問に答えます。
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

```bash
export OPENAI_API_BASE=http://localhost:11434/v1
export OPENAI_API_KEY=anything
adk web
```

#### デバッグ

インポートの直後にエージェントコードに以下を追加することで、Ollamaサーバーに送信されたリクエストを確認できます。

```py
import litellm
litellm._turn_on_debug()
```

以下のような行を探してください：

```bash
Request Sent from LiteLLM:
curl -X POST \
http://localhost:11434/api/chat \
-d '{'model': 'mistral-small3.1', 'messages': [{'role': 'system', 'content': ...
```

### 自己ホスト型エンドポイント（例：vLLM）

![python_only](https://img.shields.io/badge/サポート対象-Python-blue)

[vLLM](https://github.com/vllm-project/vllm)のようなツールを使用すると、モデルを効率的にホストし、多くの場合OpenAI互換のAPIエンドポイントを公開できます。

**セットアップ：**

1.  **モデルのデプロイ：** vLLM（または同様のツール）を使用して選択したモデルをデプロイします。APIベースURL（例：`https://your-vllm-endpoint.run.app/v1`）をメモします。
    *   *ADKツールに関する重要事項：* デプロイする際、サービングツールがOpenAI互換のツール/関数呼び出しをサポートし、有効にしていることを確認してください。vLLMの場合、これには`--enable-auto-tool-choice`のようなフラグや、モデルによっては特定の`--tool-call-parser`が必要になる場合があります。vLLMのツール使用に関するドキュメントを参照してください。
2.  **認証：** エンドポイントが認証をどのように処理するか（例：APIキー、ベアラートークン）を決定します。

    **統合例：**

    ```python
    import subprocess
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm

    # --- vLLMエンドポイントでホストされているモデルを使用したエージェントの例 ---

    # vLLMデプロイメントによって提供されるエンドポイントURL
    api_base_url = "https://your-vllm-endpoint.run.app/v1"

    # *あなたの*vLLMエンドポイント設定で認識されるモデル名
    model_name_at_endpoint = "hosted_vllm/google/gemma-3-4b-it" # vllm_test.pyからの例

    # 認証（例：Cloud Runデプロイメントにgcloud IDトークンを使用）
    # エンドポイントのセキュリティに基づいてこれを適応させる
    try:
        gcloud_token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token", "-q"]
        ).decode().strip()
        auth_headers = {"Authorization": f"Bearer {gcloud_token}"}
    except Exception as e:
        print(f"警告：gcloudトークンを取得できませんでした - {e}。エンドポイントが安全でないか、異なる認証が必要な可能性があります。")
        auth_headers = None # またはエラーを適切に処理

    agent_vllm = LlmAgent(
        model=LiteLlm(
            model=model_name_at_endpoint,
            api_base=api_base_url,
            # 必要に応じて認証ヘッダーを渡す
            extra_headers=auth_headers
            # あるいは、エンドポイントがAPIキーを使用する場合：
            # api_key="YOUR_ENDPOINT_API_KEY"
        ),
        name="vllm_agent",
        instruction="あなたは自己ホスト型のvLLMエンドポイントで実行されている親切なアシスタントです。",
        # ... その他のエージェントパラメータ
    )
    ```

## Vertex AI上のホスト型およびチューニング済みモデルの使用

エンタープライズグレードのスケーラビリティ、信頼性、およびGoogle CloudのMLOpsエコシステムとの統合のために、Vertex AIエンドポイントにデプロイされたモデルを使用できます。これには、Model Gardenのモデルや、独自にファインチューニングしたモデルが含まれます。

**統合方法：** Vertex AIエンドポイントの完全なリソース文字列（`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`）を`LlmAgent`の`model`パラメータに直接渡します。

**Vertex AIのセットアップ（統合）：**

環境がVertex AI用に設定されていることを確認してください：

1.  **認証：** Application Default Credentials (ADC)を使用します：

    ```shell
    gcloud auth application-default login
    ```

2.  **環境変数：** プロジェクトとロケーションを設定します：

    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # 例：us-central1
    ```

3.  **Vertexバックエンドの有効化：** 重要なこととして、`google-genai`ライブラリがVertex AIをターゲットにしていることを確認してください：

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### Model Gardenのデプロイメント

![python_only](https://img.shields.io/badge/サポート対象-Python-blue){ title="この機能は現在Pythonで利用可能です。Javaのサポートは計画中/近日公開予定です。" }

[Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)からさまざまなオープンおよびプロプライエタリモデルをエンドポイントにデプロイできます。

**例：**

```python
from google.adk.agents import LlmAgent
from google.genai import types # configオブジェクト用

# --- Model GardenからデプロイされたLlama 3モデルを使用したエージェントの例 ---

# 実際のVertex AIエンドポイントリソース名に置き換えてください
llama3_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID"

agent_llama3_vertex = LlmAgent(
    model=llama3_endpoint,
    name="llama3_vertex_agent",
    instruction="あなたはVertex AIでホストされているLlama 3ベースの親切なアシスタントです。",
    generate_content_config=types.GenerateContentConfig(max_output_tokens=2048),
    # ... その他のエージェントパラメータ
)
```

### ファインチューニング済みモデルのエンドポイント

![python_only](https://img.shields.io/badge/サポート対象-Python-blue){ title="この機能は現在Pythonで利用可能です。Javaのサポートは計画中/近日公開予定です。" }

ファインチューニングしたモデル（Geminiベースか、Vertex AIがサポートする他のアーキテクチャかにかかわらず）をデプロイすると、直接使用できるエンドポイントが作成されます。

**例：**

```python
from google.adk.agents import LlmAgent

# --- ファインチューニングされたGeminiモデルのエンドポイントを使用したエージェントの例 ---

# ファインチューニングされたモデルのエンドポイントリソース名に置き換えてください
finetuned_gemini_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID"

agent_finetuned_gemini = LlmAgent(
    model=finetuned_gemini_endpoint,
    name="finetuned_gemini_agent",
    instruction="あなたは特定のデータでトレーニングされた専門のアシスタントです。",
    # ... その他のエージェントパラメータ
)
```

### Vertex AI上のサードパーティモデル（例：Anthropic Claude）

Anthropicのような一部のプロバイダーは、Vertex AIを介して直接モデルを利用可能にしています。

=== "Python"

    **統合方法：** 直接のモデル文字列（例：`"claude-3-sonnet@20240229"`）を使用しますが、ADK内での*手動登録*が必要です。
    
    **なぜ登録が必要か？** ADKのレジストリは、`gemini-*`文字列と標準のVertex AIエンドポイント文字列（`projects/.../endpoints/...`）を自動的に認識し、`google-genai`ライブラリを介してルーティングします。Vertex AIを介して直接使用される他のモデルタイプ（Claudeなど）については、どの特定のラッパークラス（この場合は`Claude`）がそのモデル識別子文字列をVertex AIバックエンドで処理する方法を知っているかを、ADKレジストリに明示的に伝える必要があります。
    
    **セットアップ：**
    
    1.  **Vertex AI環境：** 統合されたVertex AIのセットアップ（ADC、環境変数、`GOOGLE_GENAI_USE_VERTEXAI=TRUE`）が完了していることを確認します。
    
    2.  **プロバイダーライブラリのインストール：** Vertex AI用に設定された必要なクライアントライブラリをインストールします。
    
        ```shell
        pip install "anthropic[vertex]"
        ```
    
    3.  **モデルクラスの登録：** Claudeモデル文字列を使用してエージェントを作成する*前*に、アプリケーションの開始近くにこのコードを追加します：
    
        ```python
        # LlmAgentでVertex AI経由でClaudeモデル文字列を直接使用するために必要
        from google.adk.models.anthropic_llm import Claude
        from google.adk.models.registry import LLMRegistry
    
        LLMRegistry.register(Claude)
        ```
    
       **例：**

       ```python
       from google.adk.agents import LlmAgent
       from google.adk.models.anthropic_llm import Claude # 登録に必要
       from google.adk.models.registry import LLMRegistry # 登録に必要
       from google.genai import types
        
       # --- Claudeクラスの登録（起動時に一度行う）---
       LLMRegistry.register(Claude)
        
       # --- Vertex AI上のClaude 3 Sonnetを使用したエージェントの例 ---
        
       # Vertex AI上のClaude 3 Sonnetの標準モデル名
       claude_model_vertexai = "claude-3-sonnet@20240229"
        
       agent_claude_vertexai = LlmAgent(
           model=claude_model_vertexai, # 登録後に直接文字列を渡す
           name="claude_vertexai_agent",
           instruction="あなたはVertex AI上のClaude 3 Sonnetを搭載したアシスタントです。",
           generate_content_config=types.GenerateContentConfig(max_output_tokens=4096),
           # ... その他のエージェントパラメータ
       )
       ```

=== "Java"

    **統合方法：** プロバイダー固有のモデルクラス（例：`com.google.adk.models.Claude`）を直接インスタンス化し、Vertex AIバックエンドで設定します。
    
    **なぜ直接インスタンス化するのか？** Java ADKの`LlmRegistry`は、デフォルトで主にGeminiモデルを処理します。Vertex AI上のClaudeのようなサードパーティモデルについては、ADKのラッパークラス（例：`Claude`）のインスタンスを直接`LlmAgent`に提供します。このラッパークラスは、Vertex AI用に設定された特定のクライアントライブラリを介してモデルと対話する責任があります。
    
    **セットアップ：**
    
    1.  **Vertex AI環境：**
        *   Google Cloudプロジェクトとリージョンが正しく設定されていることを確認します。
        *   **Application Default Credentials (ADC)：** 環境でADCが正しく設定されていることを確認します。これは通常、`gcloud auth application-default login`を実行して行います。Javaクライアントライブラリはこれらの認証情報を使用してVertex AIで認証します。詳細なセットアップについては、[ADCに関するGoogle Cloud Javaのドキュメント](https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault__)に従ってください。
    
    2.  **プロバイダーライブラリの依存関係：**
        *   **サードパーティクライアントライブラリ（多くは推移的）：** ADKコアライブラリには、Vertex AI上の一般的なサードパーティモデル（Anthropicが必要とするクラスなど）に必要なクライアントライブラリが**推移的依存関係**として含まれていることがよくあります。これは、`pom.xml`や`build.gradle`にAnthropic Vertex SDK用の別の依存関係を明示的に追加する必要がないかもしれないことを意味します。

    3.  **モデルのインスタンス化と設定：**
        `LlmAgent`を作成する際に、`Claude`クラス（または他のプロバイダーの同等クラス）をインスタンス化し、その`VertexBackend`を設定します。
    
    **例：**

    ```java
    import com.anthropic.client.AnthropicClient;
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.anthropic.vertex.backends.VertexBackend;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Claude; // ADKのClaude用ラッパー
    import com.google.auth.oauth2.GoogleCredentials;
    import java.io.IOException;

    // ... その他のインポート

    public class ClaudeVertexAiAgent {

        public static LlmAgent createAgent() throws IOException {
            // Vertex AI上のClaude 3 Sonnetのモデル名（または他のバージョン）
            String claudeModelVertexAi = "claude-3-7-sonnet"; // または他のClaudeモデル

            // VertexBackendでAnthropicOkHttpClientを設定
            AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
                .backend(
                    VertexBackend.builder()
                        .region("us-east5") // Vertex AIリージョンを指定
                        .project("your-gcp-project-id") // GCPプロジェクトIDを指定
                        .googleCredentials(GoogleCredentials.getApplicationDefault())
                        .build())
                .build();

            // ADK ClaudeラッパーでLlmAgentをインスタンス化
            LlmAgent agentClaudeVertexAi = LlmAgent.builder()
                .model(new Claude(claudeModelVertexAi, anthropicClient)) // Claudeインスタンスを渡す
                .name("claude_vertexai_agent")
                .instruction("あなたはVertex AI上のClaude 3 Sonnetを搭載したアシスタントです。")
                // .generateContentConfig(...) // オプション：必要に応じて生成設定を追加
                // ... その他のエージェントパラメータ
                .build();
            
            return agentClaudeVertexAi;
        }

        public static void main(String[] args) {
            try {
                LlmAgent agent = createAgent();
                System.out.println("エージェントが正常に作成されました: " + agent.name());
                // ここでは通常、エージェントと対話するためにRunnerとSessionをセットアップします
            } catch (IOException e) {
                System.err.println("エージェントの作成に失敗しました: " + e.getMessage());
                e.printStackTrace();
            }
        }
    }
    ```