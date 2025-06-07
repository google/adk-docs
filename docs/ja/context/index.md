# コンテキスト

## コンテキストとは何か

Agent Development Kit (ADK)において、「コンテキスト」とは、特定のアクション中にエージェントとそのツールが利用できる重要な情報の束を指します。現在のタスクや会話のターンを効果的に処理するために必要な背景知識やリソースだと考えてください。

エージェントが優れたパフォーマンスを発揮するためには、多くの場合、最新のユーザーメッセージだけでは不十分です。コンテキストは以下のことを可能にするため、不可欠です：

1.  **状態の維持：** 会話の複数のステップにわたって詳細を記憶すること（例：ユーザー設定、以前の計算結果、ショッピングカート内のアイテム）。これは主に**セッション状態**を通じて管理されます。
2.  **データの受け渡し：** あるステップ（LLM呼び出しやツール実行など）で発見または生成された情報を、後続のステップと共有すること。ここでもセッション状態が鍵となります。
3.  **サービスへのアクセス：** 以下のようなフレームワークの機能と対話すること：
    *   **アーティファクトストレージ：** セッションに関連付けられたファイルやデータブロブ（PDF、画像、設定ファイルなど）を保存または読み込むこと。
    *   **メモリ：** 過去の対話やユーザーに関連する外部の知識ソースから関連情報を検索すること。
    *   **認証：** ツールが外部APIに安全にアクセスするために必要な認証情報を要求および取得すること。
4.  **IDと追跡：** 現在どのエージェントが実行中か（`agent.name`）を把握し、現在のリクエスト-レスポンスサイクル（`invocation_id`）をロギングやデバッグのために一意に識別すること。
5.  **ツール固有のアクション：** 認証の要求やメモリの検索など、現在の対話の詳細へのアクセスを必要とする、ツール内での特化した操作を可能にすること。

単一の完全なユーザーリクエストから最終応答までのサイクル（**呼び出し (invocation)**）のすべての情報を保持する中心的な要素が`InvocationContext`です。しかし、通常、このオブジェクトを直接作成したり管理したりすることはありません。ADKフレームワークは、呼び出しが開始されるとき（例：`runner.run_async`経由）にそれを作成し、関連するコンテキスト情報を暗黙的にエージェントのコード、コールバック、ツールに渡します。

=== "Python"

    ```python
    # 概念的な疑似コード：フレームワークがどのようにコンテキストを提供するか（内部ロジック）
    
    # runner = Runner(agent=my_root_agent, session_service=..., artifact_service=...)
    # user_message = types.Content(...)
    # session = session_service.get_session(...) # または新規作成
    
    # --- runner.run_async(...) の内部 ---
    # 1. フレームワークがこの特定の実行のためのメインコンテキストを作成
    # invocation_context = InvocationContext(
    #     invocation_id="this-run-no-tame-id",
    #     session=session,
    #     user_content=user_message,
    #     agent=my_root_agent, # 開始エージェント
    #     session_service=session_service,
    #     artifact_service=artifact_service,
    #     memory_service=memory_service,
    #     # ... 他の必要なフィールド ...
    # )
    #
    # 2. フレームワークがエージェントの実行メソッドを呼び出し、コンテキストを暗黙的に渡す
    #    (エージェントのメソッドシグネチャがそれを受け取る、例：runAsyncImpl(InvocationContext invocationContext))
    # await my_root_agent.run_async(invocation_context)
    #   --- 内部ロジックの終わり ---
    #
    # 開発者としては、メソッドの引数で提供されるコンテキストオブジェクトを扱います。
    ```

=== "Java"

    ```java
    /* 概念的な疑似コード：フレームワークがどのようにコンテキストを提供するか（内部ロジック） */
    InMemoryRunner runner = new InMemoryRunner(agent);
    Session session = runner
        .sessionService()
        .createSession(runner.appName(), USER_ID, initialState, SESSION_ID )
        .blockingGet();

    try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
      while (true) {
        System.out.print("\nあなた > ");
        String userInput = scanner.nextLine();
        if ("quit".equalsIgnoreCase(userInput)) {
          break;
        }
        Content userMsg = Content.fromParts(Part.fromText(userInput));
        Flowable<Event> events = runner.runAsync(session.userId(), session.id(), userMsg);
        System.out.print("\nエージェント > ");
        events.blockingForEach(event -> System.out.print(event.stringifyContent()));
      }
    }
    ```

## さまざまな種類のコンテキスト

`InvocationContext`が包括的な内部コンテナとして機能する一方で、ADKは特定の状況に合わせて調整された特殊なコンテキストオブジェクトを提供します。これにより、内部コンテキストの完全な複雑さをどこでも扱う必要なく、手元のタスクに適したツールと権限を持つことが保証されます。以下は、遭遇するであろうさまざまな「フレーバー」です：

1.  **`InvocationContext`**
    *   **使用場所：** エージェントのコア実装メソッド（`_run_async_impl`、`_run_live_impl`）内で直接`ctx`引数として受け取られます。
    *   **目的：** 現在の呼び出しの*全体*の状態へのアクセスを提供します。これは最も包括的なコンテキストオブジェクトです。
    *   **主要な内容：** `session`（`state`と`events`を含む）への直接アクセス、現在の`agent`インスタンス、`invocation_id`、初期の`user_content`、設定されたサービス（`artifact_service`、`memory_service`、`session_service`）への参照、およびライブ/ストリーミングモードに関連するフィールド。
    *   **ユースケース：** 主に、エージェントのコアロジックがセッション全体やサービスへの直接アクセスを必要とする場合に使用されますが、多くの場合、状態やアーティファクトの操作は、独自のコンテキストを使用するコールバック/ツールに委任されます。また、呼び出し自体を制御するためにも使用されます（例：`ctx.end_invocation = True`を設定）。

    === "Python"
    
        ```python
        # 疑似コード：InvocationContextを受け取るエージェントの実装
        from google.adk.agents import BaseAgent
        from google.adk.agents.invocation_context import InvocationContext
        from google.adk.events import Event
        from typing import AsyncGenerator
    
        class MyAgent(BaseAgent):
            async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
                # 直接アクセスの例
                agent_name = ctx.agent.name
                session_id = ctx.session.id
                print(f"エージェント {agent_name} がセッション {session_id} の呼び出し {ctx.invocation_id} で実行中")
                # ... ctxを使用したエージェントロジック ...
                yield # ... イベント ...
        ```
    
    === "Java"
    
        ```java
        // 疑似コード：InvocationContextを受け取るエージェントの実装
        import com.google.adk.agents.BaseAgent;
        import com.google.adk.agents.InvocationContext;
        
        // ... LlmAgentのビルド ...
    
        protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
            // 直接アクセスの例
            String agentName = invocationContext.agent().name();
            String sessionId = invocationContext.session().id();
            String invocationId = invocationContext.invocationId();
            System.out.println("エージェント " + agentName + " がセッション " + sessionId + " の呼び出し " + invocationId + " で実行中");
            // ... invocationContextを使用したエージェントロジック ...
            return Flowable.empty(); // ... イベントを返す ...
        }
        ```

2.  **`ReadonlyContext`**
    *   **使用場所：** 基本情報への読み取りアクセスのみが必要で、変更が許可されていないシナリオ（例：`InstructionProvider`関数）で提供されます。また、他のコンテキストの基底クラスでもあります。
    *   **目的：** 基本的なコンテキスト詳細の安全な読み取り専用ビューを提供します。
    *   **主要な内容：** `invocation_id`、`agent_name`、および現在の`state`の読み取り専用*ビュー*。

    === "Python"
    
        ```python
        # 疑似コード：ReadonlyContextを受け取るInstructionプロバイダ
        from google.adk.agents import ReadonlyContext
    
        def my_instruction_provider(context: ReadonlyContext) -> str:
            # 読み取り専用アクセスの例
            user_tier = context.state().get("user_tier", "standard") # stateを読み取れる
            # context.state['new_key'] = 'value' # これは通常エラーを引き起こすか、効果がない
            return f"{user_tier}ユーザーのリクエストを処理してください。"
        ```
    
    === "Java"
    
        ```java
        // 疑似コード：ReadonlyContextを受け取るInstructionプロバイダ
        import com.google.adk.agents.ReadonlyContext;
    
        public String myInstructionProvider(ReadonlyContext context){
            // 読み取り専用アクセスの例
            String userTier = (String) context.state().getOrDefault("user_tier", "standard");
            // context.state().put("new_key", "value"); //これは通常エラーを引き起こす
            return "Process the request for a " + userTier + " user.";
        }
        ```
    
3.  **`CallbackContext`**
    *   **使用場所：** エージェントのライフサイクルコールバック（`before_agent_callback`、`after_agent_callback`）およびモデルのインタラクションコールバック（`before_model_callback`、`after_model_callback`）に`callback_context`として渡されます。
    *   **目的：** *特にコールバック内*で、状態の検査と変更、アーティファクトとの対話、および呼び出し詳細へのアクセスを容易にします。
    *   **主要な機能（`ReadonlyContext`に追加）：**
        *   **変更可能な`state`プロパティ：** セッション状態の読み取り*および書き込み*を許可します。ここで行われた変更（`callback_context.state['key'] = value`）は追跡され、コールバック後にフレームワークによって生成されるイベントに関連付けられます。
        *   **アーティファクトメソッド：** 設定された`artifact_service`と対話するための`load_artifact(filename)`および`save_artifact(filename, part)`メソッド。
        *   `user_content`への直接アクセス。

    === "Python"
    
        ```python
        # 疑似コード：CallbackContextを受け取るコールバック
        from google.adk.agents.callback_context import CallbackContext
        from google.adk.models import LlmRequest
        from google.genai import types
        from typing import Optional
    
        def my_before_model_cb(callback_context: CallbackContext, request: LlmRequest) -> Optional[types.Content]:
            # 状態の読み書きの例
            call_count = callback_context.state.get("model_calls", 0)
            callback_context.state["model_calls"] = call_count + 1 # 状態を変更
    
            # オプションでアーティファクトを読み込む
            # config_part = callback_context.load_artifact("model_config.json")
            print(f"呼び出し {callback_context.invocation_id} のモデル呼び出し #{call_count + 1} を準備中")
            return None # モデル呼び出しを続行させる
        ```
    
    === "Java"
    
        ```java
        // 疑似コード：CallbackContextを受け取るコールバック
        import com.google.adk.agents.CallbackContext;
        import com.google.adk.models.LlmRequest;
        import com.google.genai.types.Content;
        import java.util.Optional;
    
        public Maybe<LlmResponse> myBeforeModelCb(CallbackContext callbackContext, LlmRequest request){
            // 状態の読み書きの例
            int callCount = (int) callbackContext.state().getOrDefault("model_calls", 0);
            callbackContext.state().put("model_calls", callCount + 1); // 状態を変更
    
            // オプションでアーティファクトを読み込む
            // Maybe<Part> configPart = callbackContext.loadArtifact("model_config.json");
            System.out.println("Preparing model call " + (callCount + 1));
            return Maybe.empty(); // モデル呼び出しを続行させる
        }
        ```

4.  **`ToolContext`**
    *   **使用場所：** `FunctionTool`を支える関数、およびツールの実行コールバック（`before_tool_callback`、`after_tool_callback`）に`tool_context`として渡されます。
    *   **目的：** `CallbackContext`が提供するすべてのものに加えて、認証の処理、メモリの検索、アーティファクトのリスト表示など、ツールの実行に不可欠な特殊なメソッドを提供します。
    *   **主要な機能（`CallbackContext`に追加）：**
        *   **認証メソッド：** 認証フローをトリガーする`request_credential(auth_config)`、およびユーザー/システムから提供された認証情報を取得する`get_auth_response(auth_config)`。
        *   **アーティファクトのリスト表示：** セッションで利用可能なアーティファクトを発見する`list_artifacts()`。
        *   **メモリ検索：** 設定された`memory_service`にクエリを投げる`search_memory(query)`。
        *   **`function_call_id`プロパティ：** このツールの実行をトリガーしたLLMからの特定の関数呼び出しを識別し、認証リクエストやレスポンスを正しくリンクするために重要です。
        *   **`actions`プロパティ：** このステップの`EventActions`オブジェクトへの直接アクセスを許可し、ツールが状態の変更、認証リクエストなどを通知できるようにします。

    === "Python"
    
        ```python
        # 疑似コード：ToolContextを受け取るツール関数
        from google.adk.tools import ToolContext
        from typing import Dict, Any
    
        # この関数がFunctionToolでラップされていると仮定
        def search_external_api(query: str, tool_context: ToolContext) -> Dict[str, Any]:
            api_key = tool_context.state.get("api_key")
            if not api_key:
                # 必要な認証設定を定義
                # auth_config = AuthConfig(...)
                # tool_context.request_credential(auth_config) # 認証情報をリクエスト
                # 'actions'プロパティを使用して認証リクエストが行われたことを通知
                # tool_context.actions.requested_auth_configs[tool_context.function_call_id] = auth_config
                return {"status": "認証が必要です"}
    
            # APIキーを使用...
            print(f"ツールがクエリ '{query}' でAPIキーを使用して実行中。呼び出し: {tool_context.invocation_id}")
    
            # オプションでメモリを検索したりアーティファクトをリスト表示したりする
            # relevant_docs = tool_context.search_memory(f"{query}に関連する情報")
            # available_files = tool_context.list_artifacts()
    
            return {"result": f"{query} のデータを取得しました。"}
        ```
    
    === "Java"
    
        ```java
        // 疑似コード：ToolContextを受け取るツール関数
        import com.google.adk.tools.ToolContext;
        import java.util.HashMap;
        import java.util.Map;
    
        // この関数がFunctionToolでラップされていると仮定
        public Map<String, Object> searchExternalApi(String query, ToolContext toolContext){
            String apiKey = (String) toolContext.state().get("api_key");
            if(apiKey == null || apiKey.isEmpty()){
                // 必要な認証設定を定義
                // authConfig = new AuthConfig(...);
                // toolContext.requestCredential(authConfig); // 認証情報をリクエスト
                // 'actions'プロパティを使用して認証リクエストが行われたことを通知
                ...
                return Map.of("status", "認証が必要です");
            }
    
            // APIキーを使用...
            System.out.println("ツールがクエリ " + query + " でAPIキーを使用して実行中。");
    
            // オプションでアーティファクトをリスト表示
            // Single<List<String>> availableFiles = toolContext.listArtifacts();
    
            return Map.of("result", "Data for " + query + " fetched");
        }
        ```

これらの異なるコンテキストオブジェクトと、それらをいつ使用するかを理解することが、ADKアプリケーションの状態を効果的に管理し、サービスにアクセスし、フローを制御するための鍵となります。次のセクションでは、これらのコンテキストを使用して実行できる一般的なタスクについて詳しく説明します。

## コンテキストを使用した一般的なタスク

異なるコンテキストオブジェクトを理解したところで、エージェントやツールを構築する際に、それらを一般的なタスクにどのように使用するかに焦点を当てましょう。

### 情報へのアクセス

コンテキスト内に保存されている情報を読み取る必要が頻繁にあります。

*   **セッション状態の読み取り：** 以前のステップで保存されたデータや、ユーザー/アプリレベルの設定にアクセスします。`state`プロパティに対して辞書のようなアクセスを使用します。

    === "Python"
    
        ```python
        # 疑似コード：ツール関数内
        from google.adk.tools import ToolContext
    
        def my_tool(tool_context: ToolContext, **kwargs):
            user_pref = tool_context.state.get("user_display_preference", "default_mode")
            api_endpoint = tool_context.state.get("app:api_endpoint") # アプリレベルの状態を読み取る
    
            if user_pref == "dark_mode":
                # ... ダークモードのロジックを適用 ...
                pass
            print(f"APIエンドポイントを使用中: {api_endpoint}")
            # ... ツールの残りのロジック ...
    
        # 疑似コード：コールバック関数内
        from google.adk.agents.callback_context import CallbackContext
    
        def my_callback(callback_context: CallbackContext, **kwargs):
            last_tool_result = callback_context.state.get("temp:last_api_result") # 一時的な状態を読み取る
            if last_tool_result:
                print(f"最後のツールからの一時的な結果を発見: {last_tool_result}")
            # ... コールバックのロジック ...
        ```
    
    === "Java"
    
        ```java
        // 疑似コード：ツール関数内
        import com.google.adk.tools.ToolContext;
    
        public void myTool(ToolContext toolContext){
           String userPref = (String) toolContext.state().getOrDefault("user_display_preference", "default_mode");
           String apiEndpoint = (String) toolContext.state().get("app:api_endpoint"); // アプリレベルの状態を読み取る
           if("dark_mode".equals(userPref)){
                // ... ダークモードのロジックを適用 ...
            }
           System.out.println("APIエンドポイントを使用中: " + apiEndpoint);
           // ... ツールの残りのロジック ...
        }
    
        // 疑似コード：コールバック関数内
        import com.google.adk.agents.CallbackContext;
    
        public void myCallback(CallbackContext callbackContext){
            String lastToolResult = (String) callbackContext.state().get("temp:last_api_result"); // 一時的な状態を読み取る
            if(lastToolResult != null && !lastToolResult.isEmpty()){
                System.out.println("最後のツールからの一時的な結果を発見: " + lastToolResult);
            }
            // ... コールバックのロジック ...
        }
        ```

*   **現在の識別子の取得：** ロギングや、現在の操作に基づいたカスタムロジックに役立ちます。

    === "Python"
    
        ```python
        # 疑似コード：任意のコンテキスト内（ToolContextで示す）
        from google.adk.tools import ToolContext
    
        def log_tool_usage(tool_context: ToolContext, **kwargs):
            agent_name = tool_context.agent_name
            inv_id = tool_context.invocation_id
            func_call_id = getattr(tool_context, 'function_call_id', 'N/A') # ToolContextに特有
    
            print(f"ログ: 呼び出し={inv_id}, エージェント={agent_name}, FunctionCallID={func_call_id} - ツール実行済み。")
        ```
    
    === "Java"
    
        ```java
        // 疑似コード：任意のコンテキスト内（ToolContextで示す）
         import com.google.adk.tools.ToolContext;
    
         public void logToolUsage(ToolContext toolContext){
            String agentName = toolContext.agentName();
            String invId = toolContext.invocationId();
            String functionCallId = toolContext.functionCallId().orElse("N/A"); // ToolContextに特有
            System.out.println("ログ: 呼び出し=" + invId + ", エージェント=" + agentName);
        }
        ```

*   **最初のユーザー入力へのアクセス：** 現在の呼び出しを開始したメッセージを参照します。

    === "Python"
    
        ```python
        # 疑似コード：コールバック内
        from google.adk.agents.callback_context import CallbackContext
    
        def check_initial_intent(callback_context: CallbackContext, **kwargs):
            initial_text = "N/A"
            if callback_context.user_content and callback_context.user_content.parts:
                initial_text = callback_context.user_content.parts.text or "非テキスト入力"
    
            print(f"この呼び出しはユーザー入力: '{initial_text}' で開始されました")
    
        # 疑似コード：エージェントの_run_async_impl内
        # async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        #     if ctx.user_content and ctx.user_content.parts:
        #         initial_text = ctx.user_content.parts.text
        #         print(f"エージェントロジックが最初のクエリを記憶: {initial_text}")
        #     ...
        ```
    
    === "Java"
    
        ```java
        // 疑似コード：コールバック内
        import com.google.adk.agents.CallbackContext;
    
        public void checkInitialIntent(CallbackContext callbackContext){
            String initialText = "N/A";
            if(callbackContext.userContent().isPresent() && callbackContext.userContent().get().parts().isPresent()){
                initialText = callbackContext.userContent().get().parts().get().get(0).text().orElse("非テキスト入力");
                System.out.println("この呼び出しはユーザー入力: " + initialText + " で開始されました");
            }
        }
        ```
    
### セッション状態の管理

状態は、メモリとデータフローにとって重要です。`CallbackContext`または`ToolContext`を使用して状態を変更すると、変更はフレームワークによって自動的に追跡され、永続化されます。

*   **仕組み：** `callback_context.state['my_key'] = my_value`または`tool_context.state['my_key'] = my_value`に書き込むと、この変更が現在のステップのイベントに関連付けられた`EventActions.state_delta`に追加されます。その後、`SessionService`がイベントを永続化する際にこれらの差分を適用します。
*   **ツール間でのデータ受け渡し：**

    === "Python"
    
        ```python
        # 疑似コード：ツール1 - ユーザーIDを取得
        from google.adk.tools import ToolContext
        import uuid
    
        def get_user_profile(tool_context: ToolContext) -> dict:
            user_id = str(uuid.uuid4()) # ID取得をシミュレート
            # 次のツールのためにIDを状態に保存
            tool_context.state["temp:current_user_id"] = user_id
            return {"profile_status": "IDが生成されました"}
    
        # 疑似コード：ツール2 - 状態からユーザーIDを使用
        def get_user_orders(tool_context: ToolContext) -> dict:
            user_id = tool_context.state.get("temp:current_user_id")
            if not user_id:
                return {"error": "状態にユーザーIDが見つかりません"}
    
            print(f"ユーザーID: {user_id} の注文を取得中")
            # ... user_idを使用して注文を取得するロジック ...
            return {"orders": ["order123", "order456"]}
        ```
    
    === "Java"
    
        ```java
        // 疑似コード：ツール1 - ユーザーIDを取得
        import com.google.adk.tools.ToolContext;
        import java.util.UUID;
        import java.util.Map;
    
        public Map<String, String> getUserProfile(ToolContext toolContext){
            String userId = UUID.randomUUID().toString();
            // 次のツールのためにIDを状態に保存
            toolContext.state().put("temp:current_user_id", userId);
            return Map.of("profile_status", "IDが生成されました");
        }
    
        // 疑似コード：ツール2 - 状態からユーザーIDを使用
        public  Map<String, Object> getUserOrders(ToolContext toolContext){
            String userId = (String) toolContext.state().get("temp:current_user_id");
            if(userId == null || userId.isEmpty()){
                return Map.of("error", "状態にユーザーIDが見つかりません");
            }
            System.out.println("ユーザーID: " + userId + " の注文を取得中");
             // ... user_idを使用して注文を取得するロジック ...
            return Map.of("orders", List.of("order123", "order456"));
        }
        ```

*   **ユーザー設定の更新：**

    === "Python"
    
        ```python
        # 疑似コード：ツールまたはコールバックが設定を識別
        from google.adk.tools import ToolContext # または CallbackContext
    
        def set_user_preference(tool_context: ToolContext, preference: str, value: str) -> dict:
            # ユーザーレベルの状態には 'user:' プレフィックスを使用（永続的なSessionServiceを使用する場合）
            state_key = f"user:{preference}"
            tool_context.state[state_key] = value
            print(f"ユーザー設定 '{preference}' を '{value}' に設定しました")
            return {"status": "設定が更新されました"}
        ```
    
    === "Java"
    
        ```java
        // 疑似コード：ツールまたはコールバックが設定を識別
        import com.google.adk.tools.ToolContext; // または CallbackContext
        import java.util.Map;
    
        public Map<String, String> setUserPreference(ToolContext toolContext, String preference, String value){
            // ユーザーレベルの状態には 'user:' プレフィックスを使用（永続的なSessionServiceを使用する場合）
            String stateKey = "user:" + preference;
            toolContext.state().put(stateKey, value);
            System.out.println("ユーザー設定 '" + preference + "' を '" + value + "' に設定しました");
            return Map.of("status", "設定が更新されました");
        }
        ```

*   **状態プレフィックス：** 基本的な状態はセッション固有ですが、`app:`や`user:`のようなプレフィックスは、永続的な`SessionService`の実装（`DatabaseSessionService`や`VertexAiSessionService`など）と共に使用して、より広いスコープ（アプリ全体またはセッションをまたいだユーザー全体）を示すことができます。`temp:`は、現在の呼び出し内でのみ関連するデータを示すことができます。

### アーティファクトの操作

セッションに関連付けられたファイルや大きなデータブロブを扱うには、アーティファクトを使用します。一般的なユースケース：アップロードされたドキュメントの処理。

*   **ドキュメント要約のフロー例：**

    1.  **参照の取り込み（例：セットアップツールまたはコールバック内）：** ドキュメント全体のコンテンツではなく、その*パスまたはURI*をアーティファクトとして保存します。

        === "Python"
    
               ```python
               # 疑似コード：コールバックまたは初期ツール内
               from google.adk.agents import CallbackContext # または ToolContext
               from google.genai import types
                
               async def save_document_reference(context: CallbackContext, file_path: str) -> None:
                   # file_pathが "gs://my-bucket/docs/report.pdf" や "/local/path/to/report.pdf" のようなものであると仮定
                   try:
                       # パス/URIテキストを含むPartを作成
                       artifact_part = types.Part(text=file_path)
                       version = await context.save_artifact("document_to_summarize.txt", artifact_part)
                       print(f"ドキュメント参照 '{file_path}' をアーティファクトバージョン {version} として保存しました")
                       # 他のツールで必要な場合はファイル名を状態に保存
                       context.state["temp:doc_artifact_name"] = "document_to_summarize.txt"
                   except ValueError as e:
                       print(f"アーティファクトの保存エラー: {e}") # 例：アーティファクトサービスが設定されていない
                   except Exception as e:
                       print(f"アーティファクト参照の保存中に予期しないエラーが発生しました: {e}")
                
               # 使用例：
               # await save_document_reference(callback_context, "gs://my-bucket/docs/report.pdf")
               ```
    
        === "Java"
    
               ```java
               // 疑似コード：コールバックまたは初期ツール内
               import com.google.adk.agents.CallbackContext;
               import com.google.genai.types.Part;
                
               public void saveDocumentReference(CallbackContext context, String filePath){
                   // file_pathが "gs://my-bucket/docs/report.pdf" や "/local/path/to/report.pdf" のようなものであると仮定
                   try{
                       // パス/URIテキストを含むPartを作成
                       Part artifactPart = Part.fromText(filePath);
                       Optional<Integer> version = context.saveArtifact("document_to_summarize.txt", artifactPart);
                       version.ifPresent(v -> System.out.println("ドキュメント参照 " + filePath + " をアーティファクトバージョン " + v + " として保存しました"));
                       // 他のツールで必要な場合はファイル名を状態に保存
                       context.state().put("temp:doc_artifact_name", "document_to_summarize.txt");
                   } catch(Exception e){
                       System.out.println("アーティファクト参照の保存中に予期しないエラーが発生しました: " + e);
                   }
               }
                    
               // 使用例：
               // saveDocumentReference(context, "gs://my-bucket/docs/report.pdf");
               ```

    2.  **要約ツール：** アーティファクトをロードしてパス/URIを取得し、適切なライブラリを使用して実際のドキュメントコンテンツを読み、要約して結果を返します。

        === "Python"

            ```python
            # 疑似コード：要約ツールの関数内
            from google.adk.tools import ToolContext
            from google.genai import types
            # google.cloud.storageや組み込みのopenのようなライブラリが利用可能であると仮定
            # 'summarize_text'関数が存在すると仮定
            # from my_summarizer_lib import summarize_text

            async def summarize_document_tool(tool_context: ToolContext) -> dict:
                artifact_name = tool_context.state.get("temp:doc_artifact_name")
                if not artifact_name:
                    return {"error": "状態にドキュメントのアーティファクト名が見つかりません。"}

                try:
                    # 1. パス/URIを含むアーティファクトパートを読み込む
                    artifact_part = await tool_context.load_artifact(artifact_name)
                    if not artifact_part or not artifact_part.text:
                        return {"error": f"アーティファクトを読み込めないか、アーティファクトにテキストパスがありません: {artifact_name}"}

                    file_path = artifact_part.text
                    print(f"ドキュメント参照を読み込みました: {file_path}")

                    # 2. 実際のドキュメントコンテンツを読み込む（ADKコンテキスト外で）
                    document_content = ""
                    if file_path.startswith("gs://"):
                        # 例：GCSクライアントライブラリを使用してダウンロード/読み込み
                        # from google.cloud import storage
                        # client = storage.Client()
                        # blob = storage.Blob.from_string(file_path, client=client)
                        # document_content = blob.download_as_text() # または形式に応じてバイト
                        pass # 実際のGCS読み取りロジックに置き換える
                    elif file_path.startswith("/"):
                         # 例：ローカルファイルシステムを使用
                         with open(file_path, 'r', encoding='utf-8') as f:
                             document_content = f.read()
                    else:
                        return {"error": f"サポートされていないファイルパススキームです: {file_path}"}

                    # 3. コンテンツを要約する
                    if not document_content:
                         return {"error": "ドキュメントコンテンツの読み取りに失敗しました。"}

                    # summary = summarize_text(document_content) # 要約ロジックを呼び出す
                    summary = f"{file_path} のコンテンツの要約" # プレースホルダー

                    return {"summary": summary}

                except ValueError as e:
                     return {"error": f"アーティファクトサービスエラー: {e}"}
                except FileNotFoundError:
                     return {"error": f"ローカルファイルが見つかりません: {file_path}"}
                # except Exception as e: # GCSなどの特定のエラーをキャッチ
                #      return {"error": f"ドキュメント {file_path} の読み取りエラー: {e}"}
            ```

        === "Java"

            ```java
            // 疑似コード：要約ツールの関数内
            import com.google.adk.tools.ToolContext;
            import com.google.genai.types.Part;
            import java.util.Map;
            import java.io.FileNotFoundException;

            public Map<String, String> summarizeDocumentTool(ToolContext toolContext){
                String artifactName = (String) toolContext.state().get("temp:doc_artifact_name");
                if(artifactName == null || artifactName.isEmpty()){
                    return Map.of("error", "状態にドキュメントのアーティファクト名が見つかりません。");
                }
                try{
                    // 1. パス/URIを含むアーティファクトパートを読み込む
                    Maybe<Part> artifactPartMaybe = toolContext.loadArtifact(artifactName);
                    Part artifactPart = artifactPartMaybe.blockingGet(); // 簡単のためブロック
                    if(artifactPart == null || artifactPart.text().isEmpty()){
                        return Map.of("error", "アーティファクトを読み込めないか、アーティファクトにテキストパスがありません: " + artifactName);
                    }
                    String filePath = artifactPart.text().get();
                    System.out.println("ドキュメント参照を読み込みました: " + filePath);

                    // 2. 実際のドキュメントコンテンツを読み込む（ADKコンテキスト外で）
                    String documentContent = "";
                    if(filePath.startsWith("gs://")){
                        // 例：GCSクライアントライブラリを使用してdocumentContentにダウンロード/読み込み
                        // ... 実際のGCS読み取りロジックに置き換える ...
                    } else {
                        // ... 他のファイルシステムロジック ...
                        return Map.of("error", "サポートされていないファイルパススキームです: " + filePath); 
                    }

                    // 3. コンテンツを要約する
                    if(documentContent.isEmpty()){
                        return Map.of("error", "ドキュメントコンテンツの読み取りに失敗しました。"); 
                    }

                    // String summary = summarizeText(documentContent); // 要約ロジックを呼び出す
                    String summary = filePath + " のコンテンツの要約"; // プレースホルダー

                    return Map.of("summary", summary);
                } catch(Exception e){
                    return Map.of("error", "ドキュメント " + artifactName + " の読み取りエラー: " + e);
                }
            }
            ```
    
*   **アーティファクトのリスト表示：** どのファイルが利用可能かを発見します。
    
    === "Python"
        
        ```python
        # 疑似コード：ツール関数内
        from google.adk.tools import ToolContext
        
        async def check_available_docs(tool_context: ToolContext) -> dict:
            try:
                artifact_keys = await tool_context.list_artifacts()
                print(f"利用可能なアーティファクト: {artifact_keys}")
                return {"available_docs": artifact_keys}
            except ValueError as e:
                return {"error": f"アーティファクトサービスエラー: {e}"}
        ```
        
    === "Java"
        
        ```java
        // 疑似コード：ツール関数内
        import com.google.adk.tools.ToolContext;
        import java.util.Map;
        import java.util.List;
        import io.reactivex.rxjava3.core.Single;
        
        public Map<String, Object> checkAvailableDocs(ToolContext toolContext){
            try{
                Single<List<String>> artifactKeysSingle = toolContext.listArtifacts();
                List<String> artifactKeys = artifactKeysSingle.blockingGet(); // 簡単のためブロック
                System.out.println("利用可能なアーティファクト" + artifactKeys);
                return Map.of("availableDocs", artifactKeys);
            } catch(Exception e){
                return Map.of("error", "アーティファクトサービスエラー: " + e);
            }
        }
        ```

### ツール認証の処理 

![python_only](https://img.shields.io/badge/現在サポートされているのは-Python-blue){ title="この機能は現在Pythonで利用可能です。Javaのサポートは計画中/近日公開予定です。" }

ツールが必要とするAPIキーやその他の認証情報を安全に管理します。

```python
# 疑似コード：認証が必要なツール
from google.adk.tools import ToolContext
from google.adk.auth import AuthConfig # 適切なAuthConfigが定義されていると仮定

# 必要な認証設定を定義（例：OAuth, APIキー）
MY_API_AUTH_CONFIG = AuthConfig(...)
AUTH_STATE_KEY = "user:my_api_credential" # 取得した認証情報を保存するキー

async def call_secure_api(tool_context: ToolContext, request_data: str) -> dict:
    # 1. 状態に認証情報が既に存在するかチェック
    credential = tool_context.state.get(AUTH_STATE_KEY)

    if not credential:
        # 2. なければリクエストする
        print("認証情報が見つかりません、リクエストしています...")
        try:
            await tool_context.request_credential(MY_API_AUTH_CONFIG)
            # フレームワークがイベントのyieldを処理します。このターンのツール実行はここで停止します。
            return {"status": "認証が必要です。認証情報を提供してください。"}
        except ValueError as e:
            return {"error": f"認証エラー: {e}"} # 例：function_call_idが見つからない
        except Exception as e:
            return {"error": f"認証情報のリクエストに失敗しました: {e}"}

    # 3. 認証情報が存在する場合（リクエスト後の前のターンからかもしれない）
    #    または外部の認証フローが完了した後の後続の呼び出しの場合
    try:
        # オプションで、必要に応じて再検証/再取得、または直接使用
        # 外部フローが完了したばかりの場合、ここで認証情報を取得するかもしれない
        auth_credential_obj = await tool_context.get_auth_response(MY_API_AUTH_CONFIG)
        api_key = auth_credential_obj.api_key # または access_token など

        # セッション内の将来の呼び出しのために状態に保存し直す
        tool_context.state[AUTH_STATE_KEY] = auth_credential_obj.model_dump() # 取得した認証情報を永続化

        print(f"取得した認証情報を使用してAPIをデータ: {request_data} で呼び出しています")
        # ... api_keyを使用して実際のAPI呼び出しを行う ...
        api_result = f"{request_data} のAPI結果"

        return {"result": api_result}
    except Exception as e:
        # 認証情報の取得/使用中のエラーを処理
        print(f"認証情報の使用中にエラーが発生しました: {e}")
        # 認証情報が無効な場合は状態キーをクリアする？
        # tool_context.state[AUTH_STATE_KEY] = None
        return {"error": "認証情報の使用に失敗しました"}
```
*覚えておいてください：`request_credential`はツールを一時停止させ、認証の必要性を通知します。ユーザー/システムが認証情報を提供し、後続の呼び出しで`get_auth_response`（または再度状態をチェック）することで、ツールは続行できます。* `tool_context.function_call_id`は、リクエストとレスポンスをリンクするためにフレームワークによって暗黙的に使用されます。

### メモリの活用 

![python_only](https://img.shields.io/badge/現在サポートされているのは-Python-blue){ title="この機能は現在Pythonで利用可能です。Javaのサポートは計画中/近日公開予定です。" }

過去や外部ソースから関連情報にアクセスします。

```python
# 疑似コード：メモリ検索を使用するツール
from google.adk.tools import ToolContext

async def find_related_info(tool_context: ToolContext, topic: str) -> dict:
    try:
        search_results = await tool_context.search_memory(f"{topic}に関する情報")
        if search_results.results:
            print(f"'{topic}' に関するメモリ検索結果が {len(search_results.results)} 件見つかりました")
            # search_results.results (SearchMemoryResponseEntry) を処理
            top_result_text = search_results.results.text
            return {"memory_snippet": top_result_text}
        else:
            return {"message": "関連するメモリが見つかりませんでした。"}
    except ValueError as e:
        return {"error": f"メモリサービスエラー: {e}"} # 例：サービスが設定されていない
    except Exception as e:
        return {"error": f"メモリ検索中に予期しないエラーが発生しました: {e}"}
```

### 高度な使い方：直接的な`InvocationContext`の使用 

![python_only](https://img.shields.io/badge/現在サポートされているのは-Python-blue){ title="この機能は現在Pythonで利用可能です。Javaのサポートは計画中/近日公開予定です。" }

ほとんどのインタラクションは`CallbackContext`または`ToolContext`を介して行われますが、時にはエージェントのコアロジック（`_run_async_impl`/`_run_live_impl`）が直接アクセスを必要とすることがあります。

```python
# 疑似コード：エージェントの_run_async_impl内
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator

class MyControllingAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 例：特定のサービスが利用可能かチェック
        if not ctx.memory_service:
            print("この呼び出しではメモリサービスは利用できません。")
            # 潜在的にエージェントの振る舞いを変更

        # 例：何らかの条件に基づいて早期終了
        if ctx.session.state.get("critical_error_flag"):
            print("重大なエラーが検出されたため、呼び出しを終了します。")
            ctx.end_invocation = True # フレームワークに処理停止を通知
            yield Event(author=self.name, invocation_id=ctx.invocation_id, content="重大なエラーのため停止します。")
            return # このエージェントの実行を停止

        # ... 通常のエージェント処理 ...
        yield # ... イベント ...
```

`ctx.end_invocation = True`を設定することは、エージェントまたはそのコールバック/ツール内から（それぞれのコンテキストオブジェクトも基礎となる`InvocationContext`のフラグを変更するアクセス権を持っているため）、リクエスト-レスポンスサイクル全体を正常に停止する方法です。

## 主要なポイントとベストプラクティス

*   **適切なコンテキストを使用する：** 常に提供される最も具体的なコンテキストオブジェクトを使用します（ツール/ツールコールバックでは`ToolContext`、エージェント/モデルコールバックでは`CallbackContext`、該当する場合は`ReadonlyContext`）。完全な`InvocationContext`（`ctx`）は、`_run_async_impl` / `_run_live_impl`内で必要な場合にのみ直接使用します。
*   **データフローには状態を使用する：** `context.state`は、*呼び出し内*でデータを共有し、設定を記憶し、会話のメモリを管理する主要な方法です。永続ストレージを使用する場合は、プレフィックス（`app:`、`user:`、`temp:`）を慎重に使用します。
*   **ファイルにはアーティファクトを使用する：** ファイル参照（パスやURIなど）やより大きなデータブロブを管理するには、`context.save_artifact`および`context.load_artifact`を使用します。参照を保存し、コンテンツはオンデマンドで読み込みます。
*   **追跡される変更：** コンテキストメソッドを介して行われた状態やアーティファクトへの変更は、現在のステップの`EventActions`に自動的にリンクされ、`SessionService`によって処理されます。
*   **シンプルに始める：** まずは`state`と基本的なアーティファクトの使用に焦点を当てます。ニーズがより複雑になるにつれて、認証、メモリ、および高度な`InvocationContext`のフィールド（ライブストリーミング用のものなど）を探求します。

これらのコンテキストオブジェクトを理解し、効果的に使用することで、ADKでより洗練された、状態を持つ、能力の高いエージェントを構築できます。