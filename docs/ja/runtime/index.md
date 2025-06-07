# ランタイム

## ランタイムとは？

ADKランタイムは、ユーザーとの対話中にエージェントアプリケーションを動かす基盤となるエンジンです。あなたが定義したエージェント、ツール、コールバックを受け取り、ユーザーの入力に応じてそれらの実行を調整し、情報の流れ、状態の変更、LLMやストレージのような外部サービスとの対話を管理するシステムです。

ランタイムは、あなたのエージェントアプリケーションの**「エンジン」**だと考えてください。あなたが部品（エージェント、ツール）を定義し、ランタイムがユーザーのリクエストを満たすためにそれらがどのように接続され、一緒に実行されるかを処理します。

## 中核的なアイデア：イベントループ

ADKランタイムの中心は、**イベントループ**で動作します。このループは、`Runner`コンポーネントと、あなたが定義した「実行ロジック」（エージェント、それらが呼び出すLLM、コールバック、ツールを含む）との間の双方向の通信を促進します。

![intro_components.png](../assets/event-loop.png)

簡単に言うと：

1.  `Runner`はユーザーのクエリを受け取り、メインの`Agent`に処理を開始するよう依頼します。
2.  `Agent`（および関連ロジック）は、報告すべき何か（応答、ツールの使用リクエスト、状態変更など）があるまで実行され、その後`Event`を**yield（生成）**または**emit（送出）**します。
3.  `Runner`はこの`Event`を受け取り、関連するアクション（`Services`を介した状態変更の保存など）を処理し、イベントを前方（例：ユーザーインターフェース）に転送します。
4.  `Runner`がイベントを処理した*後*にのみ、`Agent`のロジックは一時停止したところから**再開**し、今度はRunnerによってコミットされた変更の影響を見ることができます。
5.  このサイクルは、エージェントが現在のユーザーのクエリに対して生成すべきイベントがなくなるまで繰り返されます。

このイベント駆動のループが、ADKがあなたのエージェントコードを実行する基本的なパターンです。

## 心臓部：イベントループの内部動作

イベントループは、`Runner`とあなたのカスタムコード（エージェント、ツール、コールバック、これらをまとめて「実行ロジック」または設計ドキュメントでは「ロジックコンポーネント」と呼びます）との間の相互作用を定義する中心的な運用パターンです。これにより、責任の分担が明確になります：

!!! Note
    具体的なメソッド名やパラメータ名は、SDKの言語によって若干異なる場合があります（例：Javaでは`agent_to_run.runAsync(...)`、Pythonでは`agent_to_run.run_async(...)`）。詳細は各言語のAPIドキュメントを参照してください。

### Runnerの役割（オーケストレーター）

`Runner`は、単一のユーザー呼び出しに対する中心的な調整役として機能します。ループ内でのその責任は次のとおりです：

1.  **開始：** エンドユーザーのクエリ（`new_message`）を受け取り、通常は`SessionService`を介してセッション履歴に追加します。
2.  **キックオフ：** メインエージェントの実行メソッド（例：`agent_to_run.run_async(...)`）を呼び出して、イベント生成プロセスを開始します。
3.  **受信と処理：** エージェントロジックが`Event`を`yield`または`emit`するのを待ちます。イベントを受信すると、Runnerはそれを**速やかに処理**します。これには以下が含まれます：
    *   設定された`Services`（`SessionService`、`ArtifactService`、`MemoryService`）を使用して、`event.actions`で示された変更（`state_delta`、`artifact_delta`など）をコミットします。
    *   その他の内部的な管理業務を実行します。
4.  **上流へのyield：** 処理されたイベントを前方（例：呼び出し元のアプリケーションやUIのレンダリングのため）に転送します。
5.  **反復：** エージェントロジックに対し、yieldされたイベントの処理が完了したことを通知し、ロジックが再開して*次*のイベントを生成できるようにします。

*概念的なRunnerのループ：*

=== "Python"

    ```py
    # Runnerのメインループのロジックの簡略化されたビュー
    def run(new_query, ...) -> Generator[Event, None, None]:
        # 1. new_queryをセッションのイベント履歴に追加（SessionService経由）
        session_service.append_event(session, Event(author='user', content=new_query))
    
        # 2. エージェントを呼び出してイベントループを開始
        agent_event_generator = agent_to_run.run_async(context)
    
        async for event in agent_event_generator:
            # 3. 生成されたイベントを処理し、変更をコミット
            session_service.append_event(session, event) # state/artifactの差分などをコミット
            # memory_service.update_memory(...) # 該当する場合
            # artifact_serviceはエージェント実行中にcontext経由で既に呼び出されている可能性がある
    
            # 4. 上流の処理（例：UIレンダリング）のためにイベントをyieldする
            yield event
            # Runnerはyield後にエージェントジェネレータが続行できることを暗黙的に示す
    ```

=== "Java"

    ```java
    // JavaにおけるRunnerのメインループのロジックの簡略化された概念的ビュー
    public Flowable<Event> runConceptual(
        Session session,                  
        InvocationContext invocationContext, 
        Content newQuery                
        ) {
    
        // 1. new_queryをセッションのイベント履歴に追加（SessionService経由）
        // ...
        sessionService.appendEvent(session, userEvent).blockingGet();
    
        // 2. エージェントを呼び出してイベントストリームを開始
        Flowable<Event> agentEventStream = agentToRun.runAsync(invocationContext);
    
        // 3. 生成された各イベントを処理し、変更をコミットし、「yield」または「emit」する
        return agentEventStream.map(event -> {
            // これはセッションオブジェクトを変更する（イベントを追加し、stateDeltaを適用する）。
            // appendEventの戻り値（Single<Event>）は、概念的には処理後のイベントそのものである。
            sessionService.appendEvent(session, event).blockingGet(); // 簡略化されたブロッキング呼び出し
    
            // memory_service.update_memory(...) # 該当する場合 - 概念的
            // artifact_serviceはエージェント実行中にcontext経由で既に呼び出されている可能性がある
    
            // 4. 上流の処理のためにイベントを「yield」する
            //    RxJavaでは、mapでイベントを返すことは、事実上、次のオペレータやサブスクライバにそれをyieldすることになる。
            return event;
        });
    }
    ```

### 実行ロジックの役割（エージェント、ツール、コールバック）

エージェント、ツール、コールバック内のあなたのコードは、実際の計算と意思決定を担当します。ループとの相互作用には以下が含まれます：

1.  **実行：** 現在の`InvocationContext`に基づいてロジックを実行します。これには、実行が再開された時点でのセッション状態が含まれます。
2.  **Yield：** ロジックが通信する必要がある場合（メッセージの送信、ツールの呼び出し、状態変更の報告）、関連するコンテンツとアクションを含む`Event`を構築し、このイベントを`Runner`に`yield`します。
3.  **一時停止：** 重要なことに、エージェントロジックの実行は`yield`文（またはRxJavaでは`return`）の直後で**一時停止**します。`Runner`がステップ3（処理とコミット）を完了するのを待ちます。
4.  **再開：** `Runner`がyieldされたイベントを処理した*後*にのみ、エージェントロジックは`yield`の直後の文から実行を再開します。
5.  **更新された状態の確認：** 再開すると、エージェントロジックは、*以前にyieldされた*イベントから`Runner`によってコミットされた変更を反映したセッション状態（`ctx.session.state`）に確実にアクセスできます。

*概念的な実行ロジック：*

=== "Python"

    ```py
    # Agent.run_async、コールバック、またはツール内のロジックの簡略化されたビュー
    
    # ... 以前のコードが現在の状態に基づいて実行される ...
    
    # 1. 変更や出力が必要であると判断し、イベントを構築する
    # 例：状態の更新
    update_data = {'field_1': 'value_2'}
    event_with_state_change = Event(
        author=self.name,
        actions=EventActions(state_delta=update_data),
        content=types.Content(parts=[types.Part(text="状態が更新されました。")])
        # ... 他のイベントフィールド ...
    )
    
    # 2. 処理とコミットのためにイベントをRunnerにyieldする
    yield event_with_state_change
    # <<<<<<<<<<<< ここで実行が一時停止 >>>>>>>>>>>>
    
    # <<<<<<<<<<<< RUNNERがイベントを処理・コミット >>>>>>>>>>>>
    
    # 3. Runnerが上記のイベントの処理を終えた後にのみ実行を再開する。
    # これで、Runnerによってコミットされた状態が確実に反映される。
    # 後続のコードは、yieldされたイベントからの変更が発生したと安全に仮定できる。
    val = ctx.session.state['field_1']
    # ここで `val` は "value_2" であることが保証される（Runnerが正常にコミットしたと仮定）
    print(f"実行再開。field_1の値は現在：{val}")
    
    # ... 後続のコードが続く ...
    # 後で別のイベントをyieldするかもしれない...
    ```

=== "Java"

    ```java
    // Agent.runAsync、コールバック、またはツール内のロジックの簡略化されたビュー
    // ... 以前のコードが現在の状態に基づいて実行される ...
    
    // 1. 変更や出力が必要であると判断し、イベントを構築する
    // 例：状態の更新
    ConcurrentMap<String, Object> updateData = new ConcurrentHashMap<>();
    updateData.put("field_1", "value_2");
    
    EventActions actions = EventActions.builder().stateDelta(updateData).build();
    Content eventContent = Content.builder().parts(Part.fromText("状態が更新されました。")).build();
    
    Event eventWithStateChange = Event.builder()
        .author(self.name())
        .actions(actions)
        .content(Optional.of(eventContent))
        // ... 他のイベントフィールド ...
        .build();
    
    // 2. イベントを「yield」する。RxJavaでは、これはストリームにそれを送出することを意味する。
    //    Runner（または上流のコンシューマ）がこのFlowableを購読する。
    //    Runnerがこのイベントを受け取ると、それを処理する（例：sessionService.appendEventを呼び出す）。
    //    Java ADKの 'appendEvent' は 'ctx'（InvocationContext）内の 'Session' オブジェクトを変更する。
    
    // <<<<<<<<<<<< 概念的な一時停止ポイント >>>>>>>>>>>>
    // RxJavaでは、'eventWithStateChange'の送出が発生し、その後ストリームは
    // Runnerがこのイベントを処理した*後*のロジックを表す 'flatMap' や 'concatMap' オペレータで
    // 続くかもしれない。
    
    // 「Runnerが処理を終えた後にのみ実行を再開する」をモデル化するには：
    // Runnerの`appendEvent`は通常、それ自体が非同期操作である（Single<Event>を返す）。
    // エージェントのフローは、コミットされた状態に依存する後続のロジックが、
    // その`appendEvent`が完了した*後*に実行されるように構成する必要がある。
    
    // これはRunnerが通常それを調整する方法である：
    // Runner:
    //   agent.runAsync(ctx)
    //     .concatMapEager(eventFromAgent ->
    //         sessionService.appendEvent(ctx.session(), eventFromAgent) // これがctx.session().state()を更新する
    //             .toFlowable() // 処理後にイベントを送出する
    //     )
    //     .subscribe(processedEvent -> { /* UIがprocessedEventをレンダリング */ });
    
    // したがって、エージェント自身のロジック内で、それがyieldしたイベントが処理され、
    // その状態変更がctx.session().state()に反映された*後*に何かをする必要がある場合、
    // その後続のロジックは通常、そのリアクティブチェーンの別のステップにある。
    
    // この概念的な例では、イベントを送出し、その後「再開」をFlowableチェーンの後続の操作としてシミュレートする。
    
    return Flowable.just(eventWithStateChange) // ステップ2：イベントをyieldする
        .concatMap(yieldedEvent -> {
            // <<<<<<<<<<<< RUNNERが概念的にイベントを処理・コミット >>>>>>>>>>>>
            // この時点で、実際のrunnerでは、ctx.session().appendEvent(yieldedEvent)が
            // Runnerによって呼び出され、ctx.session().state()が更新されているだろう。
            // 我々はこれをモデル化しようとするエージェントの概念的なロジックの*内部*にいるので、
            // Runnerのアクションが暗黙的に我々の'ctx.session()'を更新したと仮定する。
    
            // 3. 実行を再開する。
            // これで、Runnerによってコミットされた状態（sessionService.appendEvent経由で）が
            // ctx.session().state()に確実に反映される。
            Object val = ctx.session().state().get("field_1");
            // ここで `val` は "value_2" であることが保証される。なぜなら、Runnerによって呼び出された
            // `sessionService.appendEvent`が`ctx`オブジェクト内のセッション状態を更新したからである。
    
            System.out.println("実行再開。field_1の値は現在：" + val);
    
            // ... 後続のコードが続く ...
            // この後続のコードが別のイベントをyieldする必要がある場合、ここでそれを行う。
    ```

`Runner`とあなたの実行ロジックとの間のこの協力的なyield/pause/resumeサイクルは、`Event`オブジェクトを介して行われ、ADKランタイムの中核を形成します。

## ランタイムの主要コンポーネント

ADKランタイム内では、いくつかのコンポーネントが連携してエージェントの呼び出しを実行します。それらの役割を理解することで、イベントループがどのように機能するかが明確になります：

1.  ### `Runner`

    *   **役割：** 単一のユーザークエリに対する主要なエントリーポイントおよびオーケストレーター（`run_async`）。
    *   **機能：** 全体的なイベントループを管理し、実行ロジックからyieldされたイベントを受け取り、イベントのアクション（状態/アーティファクトの変更）を処理・コミットするためにサービスと連携し、処理済みのイベントを上流（例：UI）に転送します。yieldされたイベントに基づいて、会話をターンごとに駆動します。（`google.adk.runners.runner`で定義）。

2.  ### 実行ロジックコンポーネント

    *   **役割：** あなたのカスタムコードとエージェントのコア機能を含む部分。
    *   **コンポーネント：**
        *   `Agent`（`BaseAgent`, `LlmAgent`など）：情報を処理し、アクションを決定する主要なロジックユニット。イベントをyieldする`_run_async_impl`メソッドを実装します。
        *   `Tools`（`BaseTool`, `FunctionTool`, `AgentTool`など）：エージェント（多くの場合`LlmAgent`）が外部の世界と対話したり、特定のタスクを実行したりするために使用する外部関数または機能。実行して結果を返し、それらはイベントにラップされます。
        *   `Callbacks`（関数）：エージェントにアタッチされたユーザー定義関数（例：`before_agent_callback`, `after_model_callback`）で、実行フローの特定のポイントにフックし、振る舞いや状態を修正する可能性があり、その影響はイベントにキャプチャされます。
    *   **機能：** 実際の思考、計算、または外部との対話を行います。結果やニーズを**`Event`オブジェクトをyield**することで伝え、Runnerがそれらを処理するまで一時停止します。

3.  ### `Event`

    *   **役割：** `Runner`と実行ロジックとの間でやり取りされるメッセージ。
    *   **機能：** 原子的な発生（ユーザー入力、エージェントテキスト、ツール呼び出し/結果、状態変更リクエスト、制御シグナル）を表します。発生のコンテンツと意図された副作用（`state_delta`のような`actions`）の両方を運びます。

4.  ### `Services`

    *   **役割：** 永続的または共有リソースを管理するバックエンドコンポーネント。主にイベント処理中に`Runner`によって使用されます。
    *   **コンポーネント：**
        *   `SessionService`（`BaseSessionService`, `InMemorySessionService`など）：`Session`オブジェクトを管理し、それらの保存/読み込み、セッション状態への`state_delta`の適用、`event history`へのイベントの追加を含みます。
        *   `ArtifactService`（`BaseArtifactService`, `InMemoryArtifactService`, `GcsArtifactService`など）：バイナリのアーティファクトデータの保存と取得を管理します。`save_artifact`は実行ロジック中にコンテキストを介して呼び出されますが、イベント内の`artifact_delta`がRunner/SessionServiceのアクションを確認します。
        *   `MemoryService`（`BaseMemoryService`など）：（オプション）ユーザーのセッションをまたいだ長期的な意味的メモリを管理します。
    *   **機能：** 永続化層を提供します。`Runner`は、`event.actions`によって示された変更が、実行ロジックが再開される*前*に確実に保存されるように、それらと対話します。

5.  ### `Session`

    *   **役割：** ユーザーとアプリケーション間の*特定の1つの会話*の状態と履歴を保持するデータコンテナ。
    *   **機能：** 現在の`state`辞書、過去のすべての`events`のリスト（`event history`）、および関連するアーティファクトへの参照を保存します。これは、`SessionService`によって管理される対話の主要な記録です。

6.  ### `Invocation`

    *   **役割：** `Runner`がそれを受け取った瞬間から、エージェントロジックがそのクエリに対するイベントのyieldを終えるまで、*単一の*ユーザークエリに応答して発生するすべてのことを表す概念的な用語。
    *   **機能：** 1つの呼び出しには、複数のエージェント実行（エージェント転送または`AgentTool`を使用する場合）、複数のLLM呼び出し、ツール実行、およびコールバック実行が含まれる場合があり、すべてが`InvocationContext`内の単一の`invocation_id`によって結び付けられます。

これらのプレイヤーは、イベントループを通じて継続的に相互作用し、ユーザーのリクエストを処理します。

## 仕組み：簡略化された呼び出し

ツールを呼び出すLLMエージェントが関与する、典型的なユーザークエリの簡略化されたフローを追跡してみましょう：

![intro_components.png](../assets/invocation-flow.png)

### ステップバイステップの内訳

1.  **ユーザー入力：** ユーザーがクエリを送信します（例：「フランスの首都は？」）。
2.  **Runnerの開始：** `Runner.run_async`が開始されます。`SessionService`と対話し、関連する`Session`をロードし、ユーザーのクエリを最初の`Event`としてセッション履歴に追加します。`InvocationContext`（`ctx`）が準備されます。
3.  **エージェントの実行：** `Runner`は、指定されたルートエージェント（例：`LlmAgent`）で`agent.run_async(ctx)`を呼び出します。
4.  **LLM呼び出し（例）：** `Agent_Llm`は、おそらくツールを呼び出すことによって、情報が必要であると判断します。`LLM`へのリクエストを準備します。LLMが`MyTool`を呼び出すことを決定したと仮定しましょう。
5.  **FunctionCallイベントのYield：** `Agent_Llm`はLLMから`FunctionCall`応答を受け取り、それを`Event(author='Agent_Llm', content=Content(parts=[Part(function_call=...)]))`にラップし、このイベントを`yield`または`emit`します。
6.  **エージェントの一時停止：** `Agent_Llm`の実行は`yield`の直後に一時停止します。
7.  **Runnerの処理：** `Runner`はFunctionCallイベントを受け取ります。それを`SessionService`に渡して履歴に記録します。`Runner`はイベントを上流の`User`（またはアプリケーション）にyieldします。
8.  **エージェントの再開：** `Runner`はイベントが処理されたことを通知し、`Agent_Llm`は実行を再開します。
9.  **ツールの実行：** `Agent_Llm`の内部フローは、要求された`MyTool`の実行に進みます。`tool.run_async(...)`を呼び出します。
10. **ツールの結果返却：** `MyTool`が実行され、その結果を返します（例：`{'result': 'Paris'}`）。
11. **FunctionResponseイベントのYield：** エージェント（`Agent_Llm`）は、ツールの結果を`FunctionResponse`パートを含む`Event`にラップします（例：`Event(author='Agent_Llm', content=Content(role='user', parts=[Part(function_response=...)]))`）。このイベントには、ツールが状態を変更した場合（`state_delta`）やアーティファクトを保存した場合（`artifact_delta`）に`actions`も含まれる場合があります。エージェントはこのイベントを`yield`します。
12. **エージェントの一時停止：** `Agent_Llm`は再び一時停止します。
13. **Runnerの処理：** `Runner`はFunctionResponseイベントを受け取ります。それを`SessionService`に渡し、`state_delta`/`artifact_delta`を適用し、イベントを履歴に追加します。`Runner`はイベントを上流にyieldします。
14. **エージェントの再開：** `Agent_Llm`は、ツールの結果と状態の変更がコミットされたことを知って再開します。
15. **最終的なLLM呼び出し（例）：** `Agent_Llm`は、自然言語の応答を生成するためにツールの結果を`LLM`に送り返します。
16. **最終テキストイベントのYield：** `Agent_Llm`は`LLM`から最終的なテキストを受け取り、それを`Event(author='Agent_Llm', content=Content(parts=[Part(text=...)]))`にラップし、それを`yield`します。
17. **エージェントの一時停止：** `Agent_Llm`は一時停止します。
18. **Runnerの処理：** `Runner`は最終的なテキストイベントを受け取り、履歴のために`SessionService`に渡し、上流の`User`にyieldします。これはおそらく`is_final_response()`としてマークされます。
19. **エージェントの再開と終了：** `Agent_Llm`は再開します。この呼び出しのタスクを完了したため、その`run_async`ジェネレータは終了します。
20. **Runnerの完了：** `Runner`はエージェントのジェネレータが尽きたのを見て、この呼び出しのループを終了します。

このyield/pause/process/resumeサイクルにより、状態の変更が一貫して適用され、実行ロジックがイベントをyieldした後に常に最新のコミットされた状態で動作することが保証されます。

## 重要なランタイムの振る舞い

ADKランタイムが状態、ストリーミング、非同期操作をどのように処理するかについてのいくつかの重要な側面を理解することは、予測可能で効率的なエージェントを構築するために不可欠です。

### 状態の更新とコミットのタイミング

*   **ルール：** あなたのコード（エージェント、ツール、またはコールバック内）がセッション状態を変更した場合（例：`context.state['my_key'] = 'new_value'`）、この変更は最初は現在の`InvocationContext`内でローカルに記録されます。変更は、対応する`state_delta`を`actions`に持つ`Event`があなたのコードによって`yield`され、その後`Runner`によって処理された*後*にのみ、**永続化されることが保証されます**（`SessionService`によって保存されます）。

*   **意味合い：** `yield`から再開した*後*に実行されるコードは、*yieldされたイベント*で示された状態変更がコミットされたと確実に仮定できます。

=== "Python"

    ```py
    # エージェントロジック内（概念的）
    
    # 1. 状態を変更する
    ctx.session.state['status'] = 'processing'
    event1 = Event(..., actions=EventActions(state_delta={'status': 'processing'}))
    
    # 2. 差分を持つイベントをyieldする
    yield event1
    # --- 一時停止 --- Runnerがevent1を処理し、SessionServiceが 'status' = 'processing' をコミット ---
    
    # 3. 実行を再開する
    # これでコミットされた状態に依存しても安全
    current_status = ctx.session.state['status'] # 'processing'であることが保証される
    print(f"再開後の状態：{current_status}")
    ```

=== "Java"

    ```java
    // エージェントロジック内（概念的）
    // ... 以前のコードが現在の状態に基づいて実行される ...
    
    // 1. 状態変更を準備し、イベントを構築する
    ConcurrentHashMap<String, Object> stateChanges = new ConcurrentHashMap<>();
    stateChanges.put("status", "processing");
    
    EventActions actions = EventActions.builder().stateDelta(stateChanges).build();
    Content content = Content.builder().parts(Part.fromText("状態更新：処理中")).build();
    
    Event event1 = Event.builder()
        .actions(actions)
        // ...
        .build();
    
    // 2. 差分を持つイベントをyieldする
    return Flowable.just(event1)
        .map(
            emittedEvent -> {
                // --- 概念的な一時停止とRUNNERの処理 ---
                // 3. 実行を再開する（概念的に）
                // これでコミットされた状態に依存しても安全。
                String currentStatus = (String) ctx.session().state().get("status");
                System.out.println("再開後の状態（エージェントロジック内）：" + currentStatus); // 'processing'であることが保証される
    
                // イベント自体（event1）が渡される。
                // このエージェントステップ内の後続ロジックが*別の*イベントを生成した場合、
                // concatMapを使用してその新しいイベントを送出する。
                return emittedEvent;
            });
    
    // ... 後続のエージェントロジックには、更新された`ctx.session().state()`に基づいて
    // さらなるリアクティブオペレータや、より多くのイベントの送出が含まれるかもしれない。
    ```

### セッション状態の「ダーティーリード」

*   **定義：** コミットは`yield`の*後*に行われますが、*同じ呼び出し内で後から*、しかし状態変更イベントが実際にyieldされて処理される*前*に実行されるコードは、**多くの場合、ローカルの、未コミットの変更を見ることができます**。これは時々「ダーティーリード」と呼ばれます。
*   **例：**

=== "Python"

    ```py
    # before_agent_callback内のコード
    callback_context.state['field_1'] = 'value_1'
    # 状態はローカルで'value_1'に設定されるが、まだRunnerによってコミットされていない
    
    # ... エージェントが実行 ...
    
    # 後で*同じ呼び出し内で*呼び出されるツール内のコード
    # 読み取り可能（ダーティーリード）、しかし'value_1'はまだ永続的であることが保証されていない。
    val = tool_context.state['field_1'] # ここで'val'は'value_1'になる可能性が高い
    print(f"ツール内のダーティーリード値：{val}")
    
    # state_delta={'field_1': 'value_1'} を持つイベントが
    # このツールが実行された*後*にyieldされ、Runnerによって処理されると仮定する。
    ```

=== "Java"

    ```java
    // 状態を変更 - BeforeAgentCallback内のコード
    // AND この変更をcallbackContext.eventActions().stateDelta()にステージングする。
    callbackContext.state().put("field_1", "value_1");

    // --- エージェントが実行 ... ---

    // --- 後で*同じ呼び出し内で*呼び出されるツール内のコード ---
    // 読み取り可能（ダーティーリード）、しかし'value_1'はまだ永続的であることが保証されていない。
    Object val = toolContext.state().get("field_1"); // ここで'val'は'value_1'になる可能性が高い
    System.out.println("ツール内のダーティーリード値：" + val);
    // state_delta={'field_1': 'value_1'} を持つイベントが
    // このツールが実行された*後*にyieldされ、Runnerによって処理されると仮定する。
    ```

*   **意味合い：**
    *   **利点：** 1つの複雑なステップ内（例：次のLLMターン前の複数のコールバックやツール呼び出し）の異なるロジック部分が、完全なyield/commitサイクルを待たずに状態を使用して調整できます。
    *   **注意点：** 重要なロジックでダーティーリードに大きく依存するのは危険な場合があります。`state_delta`を持つイベントがyieldされ、`Runner`によって処理される*前*に呼び出しが失敗した場合、コミットされていない状態変更は失われます。重要な状態遷移については、それらが正常に処理されるイベントに関連付けられていることを確認してください。

### ストリーミング vs. 非ストリーミング出力（`partial=True`）

これは主に、特にストリーミング生成APIを使用している場合に、LLMからの応答がどのように処理されるかに関連します。

*   **ストリーミング：** LLMは応答をトークンごと、または小さなチャンクで生成します。
    *   フレームワーク（多くの場合`BaseLlmFlow`内）は、1つの概念的な応答に対して複数の`Event`オブジェクトをyieldします。これらのイベントのほとんどは`partial=True`を持ちます。
    *   `Runner`は、`partial=True`を持つイベントを受け取ると、通常はそれを即座に上流（UI表示用）に**転送**しますが、その`actions`（`state_delta`など）の処理は**スキップ**します。
    *   最終的に、フレームワークはその応答に対して、非部分的（`partial=False`または暗黙的に`turn_complete=True`経由）としてマークされた最終的なイベントをyieldします。
    *   `Runner`は、**この最終的なイベントのみを完全に処理**し、関連する`state_delta`や`artifact_delta`をコミットします。
*   **非ストリーミング：** LLMは応答全体を一度に生成します。フレームワークは非部分的としてマークされた単一のイベントをyieldし、`Runner`はそれを完全に処理します。
*   **なぜ重要か：** UIがテキストを生成されるにつれて段階的に表示できるようにしながら、状態の変更がLLMからの*完全な*応答に基づいて一度だけ原子的に適用されることを保証します。

## 非同期が基本（`run_async`）

*   **コア設計：** ADKランタイムは、根本的に非同期ライブラリ（Pythonの`asyncio`やJavaの`RxJava`など）に基づいて構築されており、同時操作（LLMの応答やツール実行の待機など）をブロッキングなしで効率的に処理します。
*   **主要なエントリーポイント：** `Runner.run_async`は、エージェントの呼び出しを実行するための主要なメソッドです。すべての主要な実行可能コンポーネント（エージェント、特定のフロー）は、内部的に`asynchronous`メソッドを使用します。
*   **同期的な利便性（`run`）：** 同期的な`Runner.run`メソッドは、主に利便性のため（例：単純なスクリプトやテスト環境で）に存在します。しかし、内部的には、`Runner.run`は通常、`Runner.run_async`を呼び出し、非同期イベントループの実行を管理します。
*   **開発者体験：** 最高のパフォーマンスを得るために、アプリケーション（ADKを使用するWebサーバーなど）を非同期で設計することをお勧めします。Pythonでは、これは`asyncio`を使用することを意味し、Javaでは`RxJava`のリアクティブプログラミングモデルを活用します。
*   **同期コールバック/ツール：** ADKフレームワークは、ツールとコールバックの両方で同期的および非同期的な関数をサポートします。
    *   **ブロッキングI/O：** 長時間実行される同期I/O操作に対して、フレームワークは停止を防ごうとします。Python ADKは`asyncio.to_thread`を使用する場合があり、Java ADKはブロッキング呼び出しに対して適切なRxJavaスケジューラまたはラッパーに依存することがよくあります。
    *   **CPUバウンドな作業：** 純粋にCPU集約的な同期タスクは、両方の環境でその実行スレッドをブロックします。

これらの振る舞いを理解することで、より堅牢なADKアプリケーションを作成し、状態の一貫性、ストリーミング更新、および非同期実行に関連する問題をデバッグするのに役立ちます。