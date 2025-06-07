# ADKにおけるマルチエージェントシステム

エージェントアプリケーションが複雑になるにつれて、単一のモノリシックなエージェントとして構造化することは、開発、保守、そして論理的思考が困難になる可能性があります。Agent Development Kit (ADK) は、複数の異なる`BaseAgent`インスタンスを組み合わせて**マルチエージェントシステム (MAS)** を構築することで、洗練されたアプリケーションの構築をサポートします。

ADKにおけるマルチエージェントシステムとは、多くの場合階層を形成するさまざまなエージェントが、より大きな目標を達成するために協力または協調するアプリケーションです。このようにアプリケーションを構造化することで、モジュール性、専門性、再利用性、保守性の向上、そして専用のワークフローエージェントを使用した構造化された制御フローの定義能力など、大きな利点が得られます。

これらのシステムを構築するために、`BaseAgent`から派生したさまざまなタイプのエージェントを組み合わせることができます。

*   **LLMエージェント:** 大規模言語モデルを搭載したエージェント。(参照: [LLMエージェント](llm-agents.md))
*   **ワークフローエージェント:** サブエージェントの実行フローを管理するために設計された特殊なエージェント (`SequentialAgent`, `ParallelAgent`, `LoopAgent`)。(参照: [ワークフローエージェント](workflow-agents/index.md))
*   **カスタムエージェント:** `BaseAgent`から継承した、LLM以外の特殊なロジックを持つ独自のエージェント。(参照: [カスタムエージェント](custom-agents.md))

以下のセクションでは、これらのマルチエージェントシステムを効果的に構築・管理できるようにするための、エージェント階層、ワークフローエージェント、インタラクションメカニズムといったADKのコアプリミティブについて詳しく説明します。

## 1. エージェント構成のためのADKプリミティブ

ADKは、マルチエージェントシステム内の構造化とインタラクションの管理を可能にする、コアとなる構成要素（プリミティブ）を提供します。

!!! Note
    プリミティブの具体的なパラメータ名やメソッド名は、SDKの言語によって若干異なる場合があります（例: Pythonでは`sub_agents`、Javaでは`subAgents`）。詳細については、各言語固有のAPIドキュメントを参照してください。

### 1.1. エージェント階層 (親エージェント、サブエージェント)

マルチエージェントシステムを構造化するための基盤は、`BaseAgent`で定義される親子関係です。

*   **階層の確立:** 親エージェントを初期化する際に、`sub_agents`引数にエージェントインスタンスのリストを渡すことで、ツリー構造を作成します。ADKは初期化時に各子エージェントに`parent_agent`属性を自動的に設定します。
*   **単一親のルール:** エージェントインスタンスは、サブエージェントとして一度しか追加できません。2番目の親を割り当てようとすると`ValueError`が発生します。
*   **重要性:** この階層は、[ワークフローエージェント](#12-workflow-agents-as-orchestrators)のスコープを定義し、LLM駆動のデリゲーションの潜在的なターゲットに影響を与えます。`agent.parent_agent`を使用して階層をナビゲートしたり、`agent.find_agent(name)`を使用して子孫を見つけたりすることができます。

=== "Python"

    ```python
    # 概念例: 階層の定義
    from google.adk.agents import LlmAgent, BaseAgent
    
    # 個々のエージェントを定義
    greeter = LlmAgent(name="Greeter", model="gemini-2.0-flash")
    task_doer = BaseAgent(name="TaskExecutor") # カスタムの非LLMエージェント
    
    # 親エージェントを作成し、sub_agents経由で子を割り当て
    coordinator = LlmAgent(
        name="Coordinator",
        model="gemini-2.0-flash",
        description="挨拶とタスクを調整します。",
        sub_agents=[ # ここでサブエージェントを割り当て
            greeter,
            task_doer
        ]
    )
    
    # フレームワークが自動的に設定:
    # assert greeter.parent_agent == coordinator
    # assert task_doer.parent_agent == coordinator
    ```

=== "Java"

    ```java
    // 概念例: 階層の定義
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.agents.LlmAgent;
    
    // 個々のエージェントを定義
    LlmAgent greeter = LlmAgent.builder().name("Greeter").model("gemini-2.0-flash").build();
    SequentialAgent taskDoer = SequentialAgent.builder().name("TaskExecutor").subAgents(...).build(); // SequentialAgent
    
    // 親エージェントを作成し、サブエージェントを割り当て
    LlmAgent coordinator = LlmAgent.builder()
        .name("Coordinator")
        .model("gemini-2.0-flash")
        .description("挨拶とタスクを調整します")
        .subAgents(greeter, taskDoer) // ここでサブエージェントを割り当て
        .build();
    
    // フレームワークが自動的に設定:
    // assert greeter.parentAgent().equals(coordinator);
    // assert taskDoer.parentAgent().equals(coordinator);
    ```

### 1.2. オーケストレーターとしてのワークフローエージェント

ADKには、自身はタスクを実行せず、`sub_agents`の実行フローをオーケストレートする、`BaseAgent`から派生した特殊なエージェントが含まれています。

*   **[`SequentialAgent`](workflow-agents/sequential-agents.md):** `sub_agents`をリストされている順に一つずつ実行します。
    *   **コンテキスト:** *同じ*[`InvocationContext`](../runtime/index.md)を順次渡すため、エージェントは共有状態を介して簡単に結果を渡すことができます。

=== "Python"

    ```python
    # 概念例: シーケンシャルパイプライン
    from google.adk.agents import SequentialAgent, LlmAgent

    step1 = LlmAgent(name="Step1_Fetch", output_key="data") # 出力をstate['data']に保存
    step2 = LlmAgent(name="Step2_Process", instruction="stateキー'data'のデータを処理します。")

    pipeline = SequentialAgent(name="MyPipeline", sub_agents=[step1, step2])
    # パイプラインが実行されると、Step2はStep1によって設定されたstate['data']にアクセスできます。
    ```

=== "Java"

    ```java
    // 概念例: シーケンシャルパイプライン
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.agents.LlmAgent;

    LlmAgent step1 = LlmAgent.builder().name("Step1_Fetch").outputKey("data").build(); // 出力をstate.get("data")に保存
    LlmAgent step2 = LlmAgent.builder().name("Step2_Process").instruction("stateキー'data'のデータを処理します。").build();

    SequentialAgent pipeline = SequentialAgent.builder().name("MyPipeline").subAgents(step1, step2).build();
    // パイプラインが実行されると、Step2はStep1によって設定されたstate.get("data")にアクセスできます。
    ```

*   **[`ParallelAgent`](workflow-agents/parallel-agents.md):** `sub_agents`を並列に実行します。サブエージェントからのイベントはインターリーブされる可能性があります。
    *   **コンテキスト:** 各子エージェントの`InvocationContext.branch`を変更し（例: `ParentBranch.ChildName`）、一部のメモリ実装で履歴を分離するのに役立つ別々のコンテキストパスを提供します。
    *   **状態:** ブランチが異なっても、すべての並列の子は*同じ共有*の`session.state`にアクセスするため、初期状態の読み取りと結果の書き込みが可能です（競合状態を避けるために別々のキーを使用してください）。

=== "Python"

    ```python
    # 概念例: 並列実行
    from google.adk.agents import ParallelAgent, LlmAgent

    fetch_weather = LlmAgent(name="WeatherFetcher", output_key="weather")
    fetch_news = LlmAgent(name="NewsFetcher", output_key="news")

    gatherer = ParallelAgent(name="InfoGatherer", sub_agents=[fetch_weather, fetch_news])
    # gathererが実行されると、WeatherFetcherとNewsFetcherは同時に実行されます。
    # 後続のエージェントはstate['weather']とstate['news']を読み取ることができます。
    ```
  
=== "Java"

    ```java
    // 概念例: 並列実行
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.ParallelAgent;
   
    LlmAgent fetchWeather = LlmAgent.builder()
        .name("WeatherFetcher")
        .outputKey("weather")
        .build();
    
    LlmAgent fetchNews = LlmAgent.builder()
        .name("NewsFetcher")
        .instruction("news")
        .build();
    
    ParallelAgent gatherer = ParallelAgent.builder()
        .name("InfoGatherer")
        .subAgents(fetchWeather, fetchNews)
        .build();
    
    // gathererが実行されると、WeatherFetcherとNewsFetcherは同時に実行されます。
    // 後続のエージェントはstate['weather']とstate['news']を読み取ることができます。
    ```

  * **[`LoopAgent`](workflow-agents/loop-agents.md):** `sub_agents`をループ内で順次実行します。
      * **終了条件:** オプションの`max_iterations`に達した場合、またはいずれかのサブエージェントがEvent Actionsに`escalate=True`を持つ[`Event`](../events/index.md)を返した場合にループが停止します。
      * **コンテキストと状態:** 各イテレーションで*同じ*`InvocationContext`を渡すため、状態の変更（カウンターやフラグなど）がループ間で持続します。

=== "Python"

      ```python
      # 概念例: 条件付きループ
      from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
      from google.adk.events import Event, EventActions
      from google.adk.agents.invocation_context import InvocationContext
      from typing import AsyncGenerator

      class CheckCondition(BaseAgent): # 状態をチェックするカスタムエージェント
          async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
              status = ctx.session.state.get("status", "pending")
              is_done = (status == "completed")
              yield Event(author=self.name, actions=EventActions(escalate=is_done)) # 完了ならエスカレーション

      process_step = LlmAgent(name="ProcessingStep") # state['status']を更新する可能性のあるエージェント

      poller = LoopAgent(
          name="StatusPoller",
          max_iterations=10,
          sub_agents=[process_step, CheckCondition(name="Checker")]
      )
      # pollerが実行されると、Checkerがエスカレーションする（state['status'] == 'completed'）か
      # 10回のイテレーションが経過するまで、process_stepとCheckerを繰り返し実行します。
      ```
    
=== "Java"

    ```java
    // 概念例: 条件付きループ
    // 状態をチェックし、エスカレーションする可能性のあるカスタムエージェント
    public static class CheckConditionAgent extends BaseAgent {
      public CheckConditionAgent(String name, String description) {
        super(name, description, List.of(), null, null);
      }
  
      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext ctx) {
        String status = (String) ctx.session().state().getOrDefault("status", "pending");
        boolean isDone = "completed".equalsIgnoreCase(status);

        // 条件が満たされた場合にエスカレーション（ループを抜ける）を知らせるイベントを発行します。
        // 未完了の場合、escalateフラグはfalseまたは存在せず、ループは継続します。
        Event checkEvent = Event.builder()
                .author(name())
                .id(Event.generateEventId()) // イベントに一意のIDを付与することが重要
                .actions(EventActions.builder().escalate(isDone).build()) // 完了ならエスカレーション
                .build();
        return Flowable.just(checkEvent);
      }
    }
  
    // state.put("status")を更新する可能性のあるエージェント
    LlmAgent processingStepAgent = LlmAgent.builder().name("ProcessingStep").build();
    // 条件をチェックするためのカスタムエージェントインスタンス
    CheckConditionAgent conditionCheckerAgent = new CheckConditionAgent(
        "ConditionChecker",
        "ステータスが'completed'かどうかをチェックします。"
    );
    LoopAgent poller = LoopAgent.builder().name("StatusPoller").maxIterations(10).subAgents(processingStepAgent, conditionCheckerAgent).build();
    // pollerが実行されると、Checkerがエスカレーションする（state.get("status") == "completed"）か
    // 10回のイテレーションが経過するまで、processingStepAgentとconditionCheckerAgentを繰り返し実行します。
    ```

### 1.3. インタラクションとコミュニケーションのメカニズム

システム内のエージェントは、しばしばデータの交換や互いのアクションのトリガーを必要とします。ADKはこれを以下の方法で促進します。

#### a) 共有セッション状態 (`session.state`)

同じ呼び出し内で動作し、したがって`InvocationContext`を介して同じ[`Session`](../sessions/session.md)オブジェクトを共有するエージェントが、受動的に通信するための最も基本的な方法です。

*   **メカニズム:** あるエージェント（またはそのツール/コールバック）が値を書き込み（`context.state['data_key'] = processed_data`）、後続のエージェントがそれを読み取ります（`data = context.state.get('data_key')`）。状態の変更は[`CallbackContext`](../callbacks/index.md)を介して追跡されます。
*   **利便性:** [`LlmAgent`](llm-agents.md)の`output_key`プロパティは、エージェントの最終的な応答テキスト（または構造化出力）を指定された状態キーに自動的に保存します。
*   **性質:** 非同期的で受動的な通信。`SequentialAgent`によってオーケストレートされるパイプラインや、`LoopAgent`のイテレーション間でデータを渡すのに理想的です。
*   **参照:** [状態管理](../sessions/state.md)

=== "Python"

    ```python
    # 概念例: output_keyの使用と状態の読み取り
    from google.adk.agents import LlmAgent, SequentialAgent
    
    agent_A = LlmAgent(name="AgentA", instruction="フランスの首都を調べてください。", output_key="capital_city")
    agent_B = LlmAgent(name="AgentB", instruction="stateキー'capital_city'に保存されている都市について教えてください。")
    
    pipeline = SequentialAgent(name="CityInfo", sub_agents=[agent_A, agent_B])
    # AgentAが実行され、"Paris"をstate['capital_city']に保存します。
    # AgentBが実行され、その命令プロセッサがstate['capital_city']を読み取って"Paris"を取得します。
    ```

=== "Java"

    ```java
    // 概念例: outputKeyの使用と状態の読み取り
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;
    
    LlmAgent agentA = LlmAgent.builder()
        .name("AgentA")
        .instruction("フランスの首都を調べてください。")
        .outputKey("capital_city")
        .build();
    
    LlmAgent agentB = LlmAgent.builder()
        .name("AgentB")
        .instruction("stateキー'capital_city'に保存されている都市について教えてください。")
        .outputKey("capital_city")
        .build();
    
    SequentialAgent pipeline = SequentialAgent.builder().name("CityInfo").subAgents(agentA, agentB).build();
    // AgentAが実行され、"Paris"をstate('capital_city')に保存します。
    // AgentBが実行され、その命令プロセッサがstate.get("capital_city")を読み取って"Paris"を取得します。
    ```

#### b) LLM駆動のデリゲーション (エージェント移譲)

[`LlmAgent`](llm-agents.md)の理解力を活用して、階層内の他の適切なエージェントにタスクを動的にルーティングします。

*   **メカニズム:** エージェントのLLMが特定の関数呼び出しを生成します: `transfer_to_agent(agent_name='target_agent_name')`。
*   **処理:** サブエージェントが存在する場合や移譲が禁止されていない場合にデフォルトで使用される`AutoFlow`が、この呼び出しをインターセプトします。`root_agent.find_agent()`を使用してターゲットエージェントを特定し、`InvocationContext`を更新して実行フォーカスを切り替えます。
*   **要件:** 呼び出し元の`LlmAgent`は、いつ移譲するかについての明確な`instructions`を必要とし、潜在的なターゲットエージェントは、LLMが情報に基づいた決定を下すための明確な`description`を必要とします。移譲のスコープ（親、サブエージェント、兄弟）は`LlmAgent`で設定できます。
*   **性質:** LLMの解釈に基づく、動的で柔軟なルーティング。

=== "Python"

    ```python
    # 概念的な設定: LLM移譲
    from google.adk.agents import LlmAgent
    
    booking_agent = LlmAgent(name="Booker", description="フライトとホテルの予約を処理します。")
    info_agent = LlmAgent(name="Info", description="一般的な情報を提供し、質問に答えます。")
    
    coordinator = LlmAgent(
        name="Coordinator",
        model="gemini-2.0-flash",
        instruction="アシスタントです。予約タスクはBookerに、情報要求はInfoに委任してください。",
        description="メインコーディネーター。",
        # AutoFlowは通常、ここで暗黙的に使用されます
        sub_agents=[booking_agent, info_agent]
    )
    # coordinatorが「フライトを予約して」というリクエストを受け取った場合、そのLLMは以下を生成するべきです:
    # FunctionCall(name='transfer_to_agent', args={'agent_name': 'Booker'})
    # ADKフレームワークはその後、実行をbooking_agentにルーティングします。
    ```

=== "Java"

    ```java
    // 概念的な設定: LLM移譲
    import com.google.adk.agents.LlmAgent;
    
    LlmAgent bookingAgent = LlmAgent.builder()
        .name("Booker")
        .description("フライトとホテルの予約を処理します。")
        .build();
    
    LlmAgent infoAgent = LlmAgent.builder()
        .name("Info")
        .description("一般的な情報を提供し、質問に答えます。")
        .build();
    
    // コーディネーターエージェントを定義
    LlmAgent coordinator = LlmAgent.builder()
        .name("Coordinator")
        .model("gemini-2.0-flash") // または希望のモデル
        .instruction("アシスタントです。予約タスクはBookerに、情報要求はInfoに委任してください。")
        .description("メインコーディネーター。")
        // subAgentsが存在し、移譲が禁止されていないため、AutoFlowがデフォルトで（暗黙的に）使用されます。
        .subAgents(bookingAgent, infoAgent)
        .build();

    // coordinatorが「フライトを予約して」というリクエストを受け取った場合、そのLLMは以下を生成するべきです:
    // FunctionCall.builder.name("transferToAgent").args(ImmutableMap.of("agent_name", "Booker")).build()
    // ADKフレームワークはその後、実行をbookingAgentにルーティングします。
    ```

#### c) 明示的な呼び出し (`AgentTool`)

[`LlmAgent`](llm-agents.md)が別の`BaseAgent`インスタンスを呼び出し可能な関数または[ツール](../tools/index.md)として扱うことを可能にします。

*   **メカニズム:** ターゲットエージェントインスタンスを`AgentTool`でラップし、親`LlmAgent`の`tools`リストに含めます。`AgentTool`は、LLMに対応する関数宣言を生成します。
*   **処理:** 親LLMが`AgentTool`をターゲットとする関数呼び出しを生成すると、フレームワークは`AgentTool.run_async`を実行します。このメソッドはターゲットエージェントを実行し、その最終応答をキャプチャし、状態/アーティファクトの変更を親のコンテキストに転送し、その応答をツールの結果として返します。
*   **性質:** （親のフロー内で）同期的で、明示的で、他のツールと同様に制御された呼び出し。
*   **(注:** `AgentTool`は明示的にインポートして使用する必要があります)。

=== "Python"

    ```python
    # 概念的な設定: ツールとしてのエージェント
    from google.adk.agents import LlmAgent, BaseAgent
    from google.adk.tools import agent_tool
    from pydantic import BaseModel
    
    # ターゲットエージェントを定義（LlmAgentまたはカスタムBaseAgent）
    class ImageGeneratorAgent(BaseAgent): # カスタムエージェントの例
        name: str = "ImageGen"
        description: str = "プロンプトに基づいて画像を生成します。"
        # ... 内部ロジック ...
        async def _run_async_impl(self, ctx): # 単純化された実行ロジック
            prompt = ctx.session.state.get("image_prompt", "default prompt")
            # ... 画像バイトを生成 ...
            image_bytes = b"..."
            yield Event(author=self.name, content=types.Content(parts=[types.Part.from_bytes(image_bytes, "image/png")]))
    
    image_agent = ImageGeneratorAgent()
    image_tool = agent_tool.AgentTool(agent=image_agent) # エージェントをラップ
    
    # 親エージェントがAgentToolを使用
    artist_agent = LlmAgent(
        name="Artist",
        model="gemini-2.0-flash",
        instruction="プロンプトを作成し、ImageGenツールを使用して画像を生成してください。",
        tools=[image_tool] # AgentToolを含める
    )
    # ArtistのLLMはプロンプトを生成し、その後以下を呼び出します:
    # FunctionCall(name='ImageGen', args={'image_prompt': '帽子をかぶった猫'})
    # フレームワークはimage_tool.run_async(...)を呼び出し、ImageGeneratorAgentを実行します。
    # 結果の画像Partは、ツールの結果としてArtistエージェントに返されます。
    ```

=== "Java"

    ```java
    // 概念的な設定: ツールとしてのエージェント
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;

    // カスタムエージェントの例（LlmAgentまたはカスタムBaseAgent）
    public class ImageGeneratorAgent extends BaseAgent  {
    
      public ImageGeneratorAgent(String name, String description) {
        super(name, description, List.of(), null, null);
      }
    
      // ... 内部ロジック ...
      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) { // 単純化された実行ロジック
        invocationContext.session().state().get("image_prompt");
        // 画像バイトを生成
        // ...
    
        Event responseEvent = Event.builder()
            .author(this.name())
            .content(Content.fromParts(Part.fromText("\b...")))
            .build();
    
        return Flowable.just(responseEvent);
      }
    
      @Override
      protected Flowable<Event> runLiveImpl(InvocationContext invocationContext) {
        return null;
      }
    }

    // AgentToolを使用してエージェントをラップ
    ImageGeneratorAgent imageAgent = new ImageGeneratorAgent("image_agent", "画像を生成します");
    AgentTool imageTool = AgentTool.create(imageAgent);
    
    // 親エージェントがAgentToolを使用
    LlmAgent artistAgent = LlmAgent.builder()
            .name("Artist")
            .model("gemini-2.0-flash")
            .instruction(
                    "あなたはアーティストです。画像のための詳細なプロンプトを作成し、" +
                            "'ImageGen'ツールを使って画像を生成してください。" +
                            " 'ImageGen'ツールは、画像プロンプトを含む'request'という名前の単一の文字列引数を期待します。" +
                            "ツールは'result'フィールドに、'image_base64'、'mime_type'、'status'を含むJSON文字列を返します。"
            )
            .description("生成ツールを使って画像を作成できるエージェント。")
            .tools(imageTool) // AgentToolを含める
            .build();
    
    // ArtistのLLMはプロンプトを生成し、その後以下を呼び出します:
    // FunctionCall(name='ImageGen', args={'imagePrompt': '帽子をかぶった猫'})
    // フレームワークはimageTool.runAsync(...)を呼び出し、ImageGeneratorAgentを実行します。
    // 結果の画像Partは、ツールの結果としてArtistエージェントに返されます。
    ```

これらのプリミティブは、密結合されたシーケンシャルなワークフローから、動的なLLM駆動のデリゲーションネットワークまで、さまざまなマルチエージェントのインタラクションを設計する柔軟性を提供します。

## 2. ADKプリミティブを使用した一般的なマルチエージェントパターン

ADKの構成プリミティブを組み合わせることで、マルチエージェント連携のためのさまざまな確立されたパターンを実装できます。

### コーディネーター/ディスパッチャーパターン

*   **構造:** 中央の[`LlmAgent`](llm-agents.md)（コーディネーター）が、複数の専門的な`sub_agents`を管理します。
*   **目標:** 受信したリクエストを適切な専門エージェントにルーティングします。
*   **使用されるADKプリミティブ:**
    *   **階層:** コーディネーターの`sub_agents`に専門エージェントがリストされます。
    *   **インタラクション:** 主に**LLM駆動のデリゲーション**（サブエージェントの明確な`description`とコーディネーターの適切な`instruction`が必要）または**明示的な呼び出し (`AgentTool`)**（コーディネーターが`tools`に`AgentTool`でラップした専門エージェントを含める）を使用します。

=== "Python"

    ```python
    # 概念コード: LLM移譲を使用するコーディネーター
    from google.adk.agents import LlmAgent
    
    billing_agent = LlmAgent(name="Billing", description="請求に関する問い合わせを処理します。")
    support_agent = LlmAgent(name="Support", description="技術的なサポートリクエストを処理します。")
    
    coordinator = LlmAgent(
        name="HelpDeskCoordinator",
        model="gemini-2.0-flash",
        instruction="ユーザーリクエストをルーティングしてください: 支払い問題にはBillingエージェント、技術的な問題にはSupportエージェントを使用してください。",
        description="メインのヘルプデスクルーター。",
        # allow_transfer=TrueはAutoFlowでsub_agentsがあれば暗黙的に設定されることが多い
        sub_agents=[billing_agent, support_agent]
    )
    # ユーザーが「支払いが失敗しました」と尋ねる -> コーディネーターのLLMはtransfer_to_agent(agent_name='Billing')を呼び出すべき
    # ユーザーが「ログインできません」と尋ねる -> コーディネーターのLLMはtransfer_to_agent(agent_name='Support')を呼び出すべき
    ```

=== "Java"

    ```java
    // 概念コード: LLM移譲を使用するコーディネーター
    import com.google.adk.agents.LlmAgent;

    LlmAgent billingAgent = LlmAgent.builder()
        .name("Billing")
        .description("請求に関する問い合わせや支払い問題を処理します。")
        .build();

    LlmAgent supportAgent = LlmAgent.builder()
        .name("Support")
        .description("技術的なサポートリクエストやログイン問題を処理します。")
        .build();

    LlmAgent coordinator = LlmAgent.builder()
        .name("HelpDeskCoordinator")
        .model("gemini-2.0-flash")
        .instruction("ユーザーリクエストをルーティングしてください: 支払い問題にはBillingエージェント、技術的な問題にはSupportエージェントを使用してください。")
        .description("メインのヘルプデスクルーター。")
        .subAgents(billingAgent, supportAgent)
        // エージェント移譲は、disallowTransferToParentやdisallowTransferToPeersで指定されない限り、
        // Autoflowのサブエージェントでは暗黙的に有効です
        .build();

    // ユーザーが「支払いが失敗しました」と尋ねる -> コーディネーターのLLMは
    // transferToAgent(agentName='Billing')を呼び出すべき
    // ユーザーが「ログインできません」と尋ねる -> コーディネーターのLLMは
    // transferToAgent(agentName='Support')を呼び出すべき
    ```

### シーケンシャルパイプラインパターン

*   **構造:** [`SequentialAgent`](workflow-agents/sequential-agents.md)が、固定された順序で実行される`sub_agents`を含みます。
*   **目標:** あるステップの出力が次のステップの入力となる多段階プロセスを実装します。
*   **使用されるADKプリミティブ:**
    *   **ワークフロー:** `SequentialAgent`が順序を定義します。
    *   **コミュニケーション:** 主に**共有セッション状態**を使用します。前のエージェントが結果を書き込み（多くは`output_key`を介して）、後のエージェントがその結果を`context.state`から読み取ります。

=== "Python"

    ```python
    # 概念コード: シーケンシャルデータパイプライン
    from google.adk.agents import SequentialAgent, LlmAgent
    
    validator = LlmAgent(name="ValidateInput", instruction="入力を検証します。", output_key="validation_status")
    processor = LlmAgent(name="ProcessData", instruction="stateキー'validation_status'が'valid'の場合にデータを処理します。", output_key="result")
    reporter = LlmAgent(name="ReportResult", instruction="stateキー'result'から結果を報告します。")
    
    data_pipeline = SequentialAgent(
        name="DataPipeline",
        sub_agents=[validator, processor, reporter]
    )
    # validatorが実行 -> state['validation_status']に保存
    # processorが実行 -> state['validation_status']を読み取り、state['result']に保存
    # reporterが実行 -> state['result']を読み取り
    ```

=== "Java"

    ```java
    // 概念コード: シーケンシャルデータパイプライン
    import com.google.adk.agents.SequentialAgent;
    
    LlmAgent validator = LlmAgent.builder()
        .name("ValidateInput")
        .instruction("入力を検証します")
        .outputKey("validation_status") // メインのテキスト出力をsession.state["validation_status"]に保存
        .build();
    
    LlmAgent processor = LlmAgent.builder()
        .name("ProcessData")
        .instruction("stateキー'validation_status'が'valid'の場合にデータを処理します")
        .outputKey("result") // メインのテキスト出力をsession.state["result"]に保存
        .build();
    
    LlmAgent reporter = LlmAgent.builder()
        .name("ReportResult")
        .instruction("stateキー'result'から結果を報告します")
        .build();
    
    SequentialAgent dataPipeline = SequentialAgent.builder()
        .name("DataPipeline")
        .subAgents(validator, processor, reporter)
        .build();
    
    // validatorが実行 -> state['validation_status']に保存
    // processorが実行 -> state['validation_status']を読み取り、state['result']に保存
    // reporterが実行 -> state['result']を読み取り
    ```

### 並列ファンアウト/ギャザーパターン

*   **構造:** [`ParallelAgent`](workflow-agents/parallel-agents.md)が複数の`sub_agents`を同時に実行し、その後、結果を集約する後続のエージェント（`SequentialAgent`内）が続くことがよくあります。
*   **目標:** 独立したタスクを同時に実行して遅延を減らし、その出力を結合します。
*   **使用されるADKプリミティブ:**
    *   **ワークフロー:** `ParallelAgent`が並行実行（ファンアウト）を担当します。後続の集約ステップ（ギャザー）を処理するために、しばしば`SequentialAgent`内にネストされます。
    *   **コミュニケーション:** サブエージェントは、**共有セッション状態**の別々のキーに結果を書き込みます。後続の「ギャザー」エージェントは、複数の状態キーを読み取ります。

=== "Python"

    ```python
    # 概念コード: 並列情報収集
    from google.adk.agents import SequentialAgent, ParallelAgent, LlmAgent
    
    fetch_api1 = LlmAgent(name="API1Fetcher", instruction="API 1からデータを取得します。", output_key="api1_data")
    fetch_api2 = LlmAgent(name="API2Fetcher", instruction="API 2からデータを取得します。", output_key="api2_data")
    
    gather_concurrently = ParallelAgent(
        name="ConcurrentFetch",
        sub_agents=[fetch_api1, fetch_api2]
    )
    
    synthesizer = LlmAgent(
        name="Synthesizer",
        instruction="stateキー'api1_data'と'api2_data'の結果を結合します。"
    )
    
    overall_workflow = SequentialAgent(
        name="FetchAndSynthesize",
        sub_agents=[gather_concurrently, synthesizer] # 並列取得を実行し、次に統合
    )
    # fetch_api1とfetch_api2が同時に実行され、stateに保存します。
    # synthesizerが後で実行され、state['api1_data']とstate['api2_data']を読み取ります。
    ```
=== "Java"

    ```java
    // 概念コード: 並列情報収集
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.ParallelAgent;
    import com.google.adk.agents.SequentialAgent;

    LlmAgent fetchApi1 = LlmAgent.builder()
        .name("API1Fetcher")
        .instruction("API 1からデータを取得します。")
        .outputKey("api1_data")
        .build();

    LlmAgent fetchApi2 = LlmAgent.builder()
        .name("API2Fetcher")
        .instruction("API 2からデータを取得します。")
        .outputKey("api2_data")
        .build();

    ParallelAgent gatherConcurrently = ParallelAgent.builder()
        .name("ConcurrentFetcher")
        .subAgents(fetchApi2, fetchApi1)
        .build();

    LlmAgent synthesizer = LlmAgent.builder()
        .name("Synthesizer")
        .instruction("stateキー'api1_data'と'api2_data'の結果を結合します。")
        .build();

    SequentialAgent overallWorfklow = SequentialAgent.builder()
        .name("FetchAndSynthesize") // 並列取得を実行し、次に統合
        .subAgents(gatherConcurrently, synthesizer)
        .build();

    // fetch_api1とfetch_api2が同時に実行され、stateに保存します。
    // synthesizerが後で実行され、state['api1_data']とstate['api2_data']を読み取ります。
    ```


### 階層的タスク分解

*   **構造:** 上位のエージェントが複雑な目標を分解し、下位のエージェントにサブタスクを委任する、多層のツリー構造のエージェント。
*   **目標:** 複雑な問題を、より単純で実行可能なステップに再帰的に分解することで解決します。
*   **使用されるADKプリミティブ:**
    *   **階層:** 多層の`parent_agent`/`sub_agents`構造。
    *   **インタラクション:** 親エージェントがサブエージェントにタスクを割り当てるために、主に**LLM駆動のデリゲーション**または**明示的な呼び出し (`AgentTool`)** を使用します。結果は階層を上って返されます（ツールの応答または状態を介して）。

=== "Python"

    ```python
    # 概念コード: 階層的リサーチタスク
    from google.adk.agents import LlmAgent
    from google.adk.tools import agent_tool
    
    # 低レベルのツールのようなエージェント
    web_searcher = LlmAgent(name="WebSearch", description="事実をウェブ検索します。")
    summarizer = LlmAgent(name="Summarizer", description="テキストを要約します。")
    
    # ツールを組み合わせる中間レベルのエージェント
    research_assistant = LlmAgent(
        name="ResearchAssistant",
        model="gemini-2.0-flash",
        description="トピックに関する情報を見つけて要約します。",
        tools=[agent_tool.AgentTool(agent=web_searcher), agent_tool.AgentTool(agent=summarizer)]
    )
    
    # リサーチを委任する高レベルのエージェント
    report_writer = LlmAgent(
        name="ReportWriter",
        model="gemini-2.0-flash",
        instruction="トピックXに関するレポートを作成してください。ResearchAssistantを使用して情報を収集してください。",
        tools=[agent_tool.AgentTool(agent=research_assistant)]
        # あるいは、research_assistantがsub_agentならLLM移譲を使用することも可能
    )
    # ユーザーはReportWriterと対話します。
    # ReportWriterはResearchAssistantツールを呼び出します。
    # ResearchAssistantはWebSearchツールとSummarizerツールを呼び出します。
    # 結果は上方にフローバックします。
    ```

=== "Java"

    ```java
    // 概念コード: 階層的リサーチタスク
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;
    
    // 低レベルのツールのようなエージェント
    LlmAgent webSearcher = LlmAgent.builder()
        .name("WebSearch")
        .description("事実をウェブ検索します。")
        .build();
    
    LlmAgent summarizer = LlmAgent.builder()
        .name("Summarizer")
        .description("テキストを要約します。")
        .build();
    
    // ツールを組み合わせる中間レベルのエージェント
    LlmAgent researchAssistant = LlmAgent.builder()
        .name("ResearchAssistant")
        .model("gemini-2.0-flash")
        .description("トピックに関する情報を見つけて要約します。")
        .tools(AgentTool.create(webSearcher), AgentTool.create(summarizer))
        .build();
    
    // リサーチを委任する高レベルのエージェント
    LlmAgent reportWriter = LlmAgent.builder()
        .name("ReportWriter")
        .model("gemini-2.0-flash")
        .instruction("トピックXに関するレポートを作成してください。ResearchAssistantを使用して情報を収集してください。")
        .tools(AgentTool.create(researchAssistant))
        // あるいは、research_assistantがsubAgentならLLM移譲を使用することも可能
        .build();
    
    // ユーザーはReportWriterと対話します。
    // ReportWriterはResearchAssistantツールを呼び出します。
    // ResearchAssistantはWebSearchツールとSummarizerツールを呼び出します。
    // 結果は上方にフローバックします。
    ```

### レビュー/批評パターン (生成者-批評者)

*   **構造:** 通常、[`SequentialAgent`](workflow-agents/sequential-agents.md)内に2つのエージェント、生成者と批評者/レビューアーが関与します。
*   **目標:** 専用のエージェントにレビューさせることで、生成された出力の品質や妥当性を向上させます。
*   **使用されるADKプリミティブ:**
    *   **ワークフロー:** `SequentialAgent`が、レビューの前に生成が行われることを保証します。
    *   **コミュニケーション:** **共有セッション状態**（生成者は`output_key`を使用して出力を保存し、レビューアーはその状態キーを読み取る）。レビューアーは、後続のステップのためにフィードバックを別の状態キーに保存する場合があります。

=== "Python"

    ```python
    # 概念コード: 生成者-批評者
    from google.adk.agents import SequentialAgent, LlmAgent
    
    generator = LlmAgent(
        name="DraftWriter",
        instruction="主題Xについての短い段落を書いてください。",
        output_key="draft_text"
    )
    
    reviewer = LlmAgent(
        name="FactChecker",
        instruction="stateキー'draft_text'のテキストの事実の正確性をレビューしてください。'valid'または'invalid'を理由とともにアウトプットしてください。",
        output_key="review_status"
    )
    
    # オプション: review_statusに基づくさらなるステップ
    
    review_pipeline = SequentialAgent(
        name="WriteAndReview",
        sub_agents=[generator, reviewer]
    )
    # generatorが実行 -> state['draft_text']に下書きを保存
    # reviewerが実行 -> state['draft_text']を読み取り、state['review_status']にステータスを保存
    ```

=== "Java"

    ```java
    // 概念コード: 生成者-批評者
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;
    
    LlmAgent generator = LlmAgent.builder()
        .name("DraftWriter")
        .instruction("主題Xについての短い段落を書いてください。")
        .outputKey("draft_text")
        .build();
    
    LlmAgent reviewer = LlmAgent.builder()
        .name("FactChecker")
        .instruction("stateキー'draft_text'のテキストの事実の正確性をレビューしてください。'valid'または'invalid'を理由とともにアウトプットしてください。")
        .outputKey("review_status")
        .build();
    
    // オプション: review_statusに基づくさらなるステップ
    
    SequentialAgent reviewPipeline = SequentialAgent.builder()
        .name("WriteAndReview")
        .subAgents(generator, reviewer)
        .build();
    
    // generatorが実行 -> state['draft_text']に下書きを保存
    // reviewerが実行 -> state['draft_text']を読み取り、state['review_status']にステータスを保存
    ```

### 反復的改善パターン

*   **構造:** [`LoopAgent`](workflow-agents/loop-agents.md)を使用し、複数のイテレーションにわたってタスクに取り組む1つ以上のエージェントを含みます。
*   **目標:** 品質基準が満たされるか、最大イテレーション数に達するまで、セッション状態に保存された結果（例: コード、テキスト、計画）を段階的に改善します。
*   **使用されるADKプリミティブ:**
    *   **ワークフロー:** `LoopAgent`が反復を管理します。
    *   **コミュニケーション:** **共有セッション状態**が不可欠で、エージェントが前のイテレーションの出力を読み取り、改善版を保存します。
    *   **終了条件:** ループは通常、`max_iterations`に基づいて終了するか、または結果が満足のいくものである場合に専用のチェックエージェントが`Event Actions`で`escalate=True`を設定することによって終了します。

=== "Python"

    ```python
    # 概念コード: 反復的コード改善
    from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
    from google.adk.events import Event, EventActions
    from google.adk.agents.invocation_context import InvocationContext
    from typing import AsyncGenerator
    
    # state['current_code']とstate['requirements']に基づいてコードを生成/改善するエージェント
    code_refiner = LlmAgent(
        name="CodeRefiner",
        instruction="state['current_code']（存在する場合）とstate['requirements']を読み取ります。要件を満たすPythonコードを生成/改善し、state['current_code']に保存します。",
        output_key="current_code" # stateの以前のコードを上書き
    )
    
    # コードが品質基準を満たしているかチェックするエージェント
    quality_checker = LlmAgent(
        name="QualityChecker",
        instruction="state['current_code']のコードをstate['requirements']に対して評価します。'pass'または'fail'を出力してください。",
        output_key="quality_status"
    )
    
    # ステータスをチェックし、'pass'ならエスカレーションするカスタムエージェント
    class CheckStatusAndEscalate(BaseAgent):
        async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
            status = ctx.session.state.get("quality_status", "fail")
            should_stop = (status == "pass")
            yield Event(author=self.name, actions=EventActions(escalate=should_stop))
    
    refinement_loop = LoopAgent(
        name="CodeRefinementLoop",
        max_iterations=5,
        sub_agents=[code_refiner, quality_checker, CheckStatusAndEscalate(name="StopChecker")]
    )
    # ループ実行: Refiner -> Checker -> StopChecker
    # state['current_code']は各イテレーションで更新されます。
    # QualityCheckerが'pass'を出力する（StopCheckerがエスカレーションする）か、5イテレーション後にループは停止します。
    ```

=== "Java"

    ```java
    // 概念コード: 反復的コード改善
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.LoopAgent;
    import com.google.adk.events.Event;
    import com.google.adk.events.EventActions;
    import com.google.adk.agents.InvocationContext;
    import io.reactivex.rxjava3.core.Flowable;
    import java.util.List;
    
    // state['current_code']とstate['requirements']に基づいてコードを生成/改善するエージェント
    LlmAgent codeRefiner = LlmAgent.builder()
        .name("CodeRefiner")
        .instruction("state['current_code']（存在する場合）とstate['requirements']を読み取ります。要件を満たすJavaコードを生成/改善し、state['current_code']に保存します。")
        .outputKey("current_code") // stateの以前のコードを上書き
        .build();
    
    // コードが品質基準を満たしているかチェックするエージェント
    LlmAgent qualityChecker = LlmAgent.builder()
        .name("QualityChecker")
        .instruction("state['current_code']のコードをstate['requirements']に対して評価します。'pass'または'fail'を出力してください。")
        .outputKey("quality_status")
        .build();
    
    BaseAgent checkStatusAndEscalate = new BaseAgent(
        "StopChecker","quality_statusをチェックし、'pass'ならエスカレーションします。", List.of(), null, null) {
    
      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
        String status = (String) invocationContext.session().state().getOrDefault("quality_status", "fail");
        boolean shouldStop = "pass".equals(status);
    
        EventActions actions = EventActions.builder().escalate(shouldStop).build();
        Event event = Event.builder()
            .author(this.name())
            .actions(actions)
            .build();
        return Flowable.just(event);
      }
    };
    
    LoopAgent refinementLoop = LoopAgent.builder()
        .name("CodeRefinementLoop")
        .maxIterations(5)
        .subAgents(codeRefiner, qualityChecker, checkStatusAndEscalate)
        .build();
    
    // ループ実行: Refiner -> Checker -> StopChecker
    // state['current_code']は各イテレーションで更新されます。
    // QualityCheckerが'pass'を出力する（StopCheckerがエスカレーションする）か、5イテレーション後にループは停止します。
    ```

### ヒューマンインザループパターン

*   **構造:** エージェントのワークフロー内に人間の介入点を統合します。
*   **目標:** 人間の監督、承認、修正、またはAIが実行できないタスクを可能にします。
*   **使用されるADKプリミティブ (概念):**
    *   **インタラクション:** 実行を一時停止し、外部システム（例: UI、チケットシステム）にリクエストを送信して人間の入力を待つカスタム**ツール**を使用して実装できます。ツールはその後、人間の応答をエージェントに返します。
    *   **ワークフロー:** **LLM駆動のデリゲーション** (`transfer_to_agent`) を使用して、外部ワークフローをトリガーする概念的な「ヒューマンエージェント」をターゲットにするか、`LlmAgent`内でカスタムツールを使用することができます。
    *   **状態/コールバック:** 状態は人間向けのタスク詳細を保持でき、コールバックはインタラクションフローを管理できます。
    *   **注:** ADKには組み込みの「ヒューマンエージェント」タイプはないため、これにはカスタム統合が必要です。

=== "Python"

    ```python
    # 概念コード: 人間の承認にツールを使用
    from google.adk.agents import LlmAgent, SequentialAgent
    from google.adk.tools import FunctionTool
    
    # --- external_approval_toolが存在すると仮定 ---
    # このツールは次のようになります:
    # 1. 詳細（例: request_id, amount, reason）を受け取る。
    # 2. これらの詳細を人間のレビューシステムに送信する（例: API経由）。
    # 3. 人間の応答（承認/拒否）をポーリングまたは待機する。
    # 4. 人間の決定を返す。
    # async def external_approval_tool(amount: float, reason: str) -> str: ...
    approval_tool = FunctionTool(func=external_approval_tool)
    
    # リクエストを準備するエージェント
    prepare_request = LlmAgent(
        name="PrepareApproval",
        instruction="ユーザー入力に基づいて承認リクエストの詳細を準備します。金額と理由をstateに保存します。",
        # ... state['approval_amount']とstate['approval_reason']を設定する可能性が高い ...
    )
    
    # 人間の承認ツールを呼び出すエージェント
    request_approval = LlmAgent(
        name="RequestHumanApproval",
        instruction="state['approval_amount']の金額とstate['approval_reason']の理由でexternal_approval_toolを使用します。",
        tools=[approval_tool],
        output_key="human_decision"
    )
    
    # 人間の決定に基づいて処理を進めるエージェント
    process_decision = LlmAgent(
        name="ProcessDecision",
        instruction="stateキー'human_decision'をチェックします。'approved'なら処理を進め、'rejected'ならユーザーに通知します。"
    )
    
    approval_workflow = SequentialAgent(
        name="HumanApprovalWorkflow",
        sub_agents=[prepare_request, request_approval, process_decision]
    )
    ```

=== "Java"

    ```java
    // 概念コード: 人間の承認にツールを使用
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.tools.FunctionTool;
    
    // --- external_approval_toolが存在すると仮定 ---
    // このツールは次のようになります:
    // 1. 詳細（例: request_id, amount, reason）を受け取る。
    // 2. これらの詳細を人間のレビューシステムに送信する（例: API経由）。
    // 3. 人間の応答（承認/拒否）をポーリングまたは待機する。
    // 4. 人間の決定を返す。
    // public boolean externalApprovalTool(float amount, String reason) { ... }
    FunctionTool approvalTool = FunctionTool.create(externalApprovalTool);
    
    // リクエストを準備するエージェント
    LlmAgent prepareRequest = LlmAgent.builder()
        .name("PrepareApproval")
        .instruction("ユーザー入力に基づいて承認リクエストの詳細を準備します。金額と理由をstateに保存します。")
        // ... state['approval_amount']とstate['approval_reason']を設定する可能性が高い ...
        .build();
    
    // 人間の承認ツールを呼び出すエージェント
    LlmAgent requestApproval = LlmAgent.builder()
        .name("RequestHumanApproval")
        .instruction("state['approval_amount']の金額とstate['approval_reason']の理由でexternal_approval_toolを使用します。")
        .tools(approvalTool)
        .outputKey("human_decision")
        .build();
    
    // 人間の決定に基づいて処理を進めるエージェント
    LlmAgent processDecision = LlmAgent.builder()
        .name("ProcessDecision")
        .instruction("stateキー'human_decision'をチェックします。'approved'なら処理を進め、'rejected'ならユーザーに通知します。")
        .build();
    
    SequentialAgent approvalWorkflow = SequentialAgent.builder()
        .name("HumanApprovalWorkflow")
        .subAgents(prepareRequest, requestApproval, processDecision)
        .build();
    ```

これらのパターンは、マルチエージェントシステムを構造化するための出発点となります。特定のアプリケーションに最も効果的なアーキテクチャを作成するために、必要に応じてこれらを組み合わせることができます。