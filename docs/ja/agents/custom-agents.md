!!! warning "高度な概念"

    `_run_async_impl`（または他の言語での同等のメソッド）を直接実装してカスタムエージェントを構築すると、強力な制御が可能になりますが、事前定義された`LlmAgent`や標準の`WorkflowAgent`タイプを使用するよりも複雑です。カスタムオーケストレーションロジックに取り組む前に、まずこれらの基本的なエージェントタイプを理解することをお勧めします。

# カスタムエージェント

カスタムエージェントは、ADKにおいて究極の柔軟性を提供します。`BaseAgent`から直接継承し、独自の制御フローを実装することで、**任意のオーケストレーションロジック**を定義できます。これにより、`SequentialAgent`、`LoopAgent`、`ParallelAgent`といった事前定義されたパターンの枠を超え、非常に特殊で複雑なエージェントワークフローを構築することが可能になります。

## はじめに: 事前定義されたワークフローを超えて

### カスタムエージェントとは？

カスタムエージェントとは、本質的に`google.adk.agents.BaseAgent`を継承し、そのコア実行ロジックを`_run_async_impl`非同期メソッド内に実装することで作成するクラスのことです。このメソッドが他のエージェント（サブエージェント）をどのように呼び出し、状態を管理し、イベントを処理するかを完全に制御できます。

!!! Note
    エージェントのコア非同期ロジックを実装するための具体的なメソッド名は、SDKの言語によって若干異なる場合があります（例: Javaでは`runAsyncImpl`、Pythonでは`_run_async_impl`）。詳細については、各言語固有のAPIドキュメントを参照してください。

### なぜ使用するのか？

標準の[ワークフローエージェント](workflow-agents/index.md)（`SequentialAgent`、`LoopAgent`、`ParallelAgent`）は一般的なオーケストレーションパターンをカバーしていますが、要件に以下のようなものが含まれる場合はカスタムエージェントが必要になります。

*   **条件付きロジック:** 実行時の条件や前のステップの結果に基づいて、異なるサブエージェントを実行したり、異なるパスをたどったりする。
*   **複雑な状態管理:** 単純な逐次的な受け渡しを超えて、ワークフロー全体で状態を維持・更新するための複雑なロジックを実装する。
*   **外部連携:** 外部API、データベース、またはカスタムライブラリの呼び出しを、オーケストレーションのフロー制御内に直接組み込む。
*   **動的なエージェント選択:** 状況や入力の動的な評価に基づいて、次に実行するサブエージェントを選択する。
*   **独自のワークフローパターン:** 標準的な逐次、並列、またはループ構造に当てはまらないオーケストレーションロジックを実装する。


![intro_components.png](../assets/custom-agent-flow.png)


## カスタムロジックの実装:

カスタムエージェントの核となるのは、そのユニークな非同期の振る舞いを定義するメソッドです。このメソッドにより、サブエージェントをオーケストレートし、実行フローを管理することができます。

=== "Python"

      カスタムエージェントの心臓部は`_run_async_impl`メソッドです。ここでそのユニークな振る舞いを定義します。
      
      * **シグネチャ:** `async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:`
      * **非同期ジェネレータ:** `async def`関数であり、`AsyncGenerator`を返す必要があります。これにより、サブエージェントや自身のロジックによって生成されたイベントをランナーに`yield`（送出）できます。
      * **`ctx` (InvocationContext):** 実行時の重要な情報へのアクセスを提供します。最も重要なのは`ctx.session.state`で、これはカスタムエージェントによってオーケストレートされるステップ間でデータを共有する主要な方法です。

=== "Java"

    カスタムエージェントの心臓部は、`BaseAgent`からオーバーライドする`runAsyncImpl`メソッドです。

    *   **シグネチャ:** `protected Flowable<Event> runAsyncImpl(InvocationContext ctx)`
    *   **リアクティブストリーム (`Flowable`):** `io.reactivex.rxjava3.core.Flowable<Event>`を返す必要があります。この`Flowable`は、カスタムエージェントのロジックによって生成されるイベントのストリームを表し、多くの場合、サブエージェントからの複数の`Flowable`を組み合わせたり変換したりして作成されます。
    *   **`ctx` (InvocationContext):** 実行時の重要な情報へのアクセスを提供します。最も重要なのは`ctx.session().state()`で、これは`java.util.concurrent.ConcurrentMap<String, Object>`です。これはカスタムエージェントによってオーケストレートされるステップ間でデータを共有する主要な方法です。

**コア非同期メソッド内の主な機能:**

=== "Python"

    1. **サブエージェントの呼び出し:** サブエージェント（通常は`self.my_llm_agent`のようにインスタンス属性として保存される）を、その`run_async`メソッドを使って呼び出し、そのイベントを`yield`します。

          ```python
          async for event in self.some_sub_agent.run_async(ctx):
              # 必要に応じてイベントを検査またはログ記録
              yield event # イベントを上位に渡す
          ```

    2. **状態管理:** セッション状態ディクショナリ（`ctx.session.state`）の読み書きを行い、サブエージェントの呼び出し間でデータを渡したり、意思決定を行ったりします。
          ```python
          # 前のエージェントによって設定されたデータを読み取る
          previous_result = ctx.session.state.get("some_key")
      
          # 状態に基づいて意思決定を行う
          if previous_result == "some_value":
              # ... 特定のサブエージェントを呼び出す ...
          else:
              # ... 別のサブエージェントを呼び出す ...
      
          # 後のステップのために結果を保存する（多くはサブエージェントのoutput_keyを介して行われる）
          # ctx.session.state["my_custom_result"] = "calculated_value"
          ```

    3. **制御フローの実装:** 標準的なPythonの構文（`if`/`elif`/`else`、`for`/`while`ループ、`try`/`except`）を使用して、サブエージェントを含む、洗練された条件付きまたは反復的なワークフローを作成します。

=== "Java"

    1. **サブエージェントの呼び出し:** サブエージェント（通常はインスタンス属性やオブジェクトとして保存される）を、その非同期実行メソッドを使って呼び出し、イベントストリームを返します。

           通常、`concatWith`、`flatMapPublisher`、`concatArray`のようなRxJavaオペレータを使用して、サブエージェントからの`Flowable`を連鎖させます。

           ```java
           // 例: 1つのサブエージェントを実行する
           // return someSubAgent.runAsync(ctx);
      
           // 例: サブエージェントを順次実行する
           Flowable<Event> firstAgentEvents = someSubAgent1.runAsync(ctx)
               .doOnNext(event -> System.out.println("エージェント1からのイベント: " + event.id()));
      
           Flowable<Event> secondAgentEvents = Flowable.defer(() ->
               someSubAgent2.runAsync(ctx)
                   .doOnNext(event -> System.out.println("エージェント2からのイベント: " + event.id()))
           );
      
           return firstAgentEvents.concatWith(secondAgentEvents);
           ```
           `Flowable.defer()`は、後続のステージの実行が前のステージの完了や状態に依存する場合によく使用されます。

    2. **状態管理:** セッション状態の読み書きを行い、サブエージェントの呼び出し間でデータを渡したり、意思決定を行ったりします。セッション状態は`ctx.session().state()`を介して取得される`java.util.concurrent.ConcurrentMap<String, Object>`です。
        
        ```java
        // 前のエージェントによって設定されたデータを読み取る
        Object previousResult = ctx.session().state().get("some_key");

        // 状態に基づいて意思決定を行う
        if ("some_value".equals(previousResult)) {
            // ... 特定のサブエージェントのFlowableを含めるロジック ...
        } else {
            // ... 別のサブエージェントのFlowableを含めるロジック ...
        }

        // 後のステップのために結果を保存する（多くはサブエージェントのoutput_keyを介して行われる）
        // ctx.session().state().put("my_custom_result", "calculated_value");
        ```

    3. **制御フローの実装:** 標準的な言語構文（`if`/`else`、ループ、`try`/`catch`）をリアクティブオペレータ（RxJava）と組み合わせて、洗練されたワークフローを作成します。

          *   **条件付き:** 条件に基づいてどの`Flowable`を購読するかを選択するための`Flowable.defer()`、またはストリーム内のイベントをフィルタリングする場合は`filter()`。
          *   **反復的:** `repeat()`、`retry()`のようなオペレータ、または条件に基づいて自身の部分を再帰的に呼び出すように`Flowable`チェーンを構成する（多くは`flatMapPublisher`や`concatMap`で管理される）。

## サブエージェントと状態の管理

通常、カスタムエージェントは他のエージェント（`LlmAgent`、`LoopAgent`など）をオーケストレートします。

*   **初期化:** 通常、これらのサブエージェントのインスタンスをカスタムエージェントのコンストラクタに渡し、インスタンスフィールド/属性として保存します（例: `this.story_generator = story_generator_instance` または `self.story_generator = story_generator_instance`）。これにより、カスタムエージェントのコア非同期実行ロジック（`_run_async_impl`メソッドなど）内からそれらにアクセスできるようになります。
*   **サブエージェントリスト:** `super()`コンストラクタを使用して`BaseAgent`を初期化する際、`sub agents`リストを渡す必要があります。このリストは、このカスタムエージェントの直接の階層の一部であるエージェントをADKフレームワークに伝えます。これは、たとえコア実行ロジック（`_run_async_impl`）が`self.xxx_agent`を介してエージェントを直接呼び出す場合でも、ライフサイクル管理、イントロスペクション、および将来のルーティング機能などのフレームワーク機能にとって重要です。カスタムロジックがトップレベルで直接呼び出すエージェントを含めてください。
*   **状態:** 前述の通り、`ctx.session.state`は、サブエージェント（特に`output_key`を使用する`LlmAgent`）が結果をオーケストレータに返し、オーケストレータが必要な入力を渡すための標準的な方法です。

## デザインパターン例: `StoryFlowAgent`

条件付きロジックを持つ多段階のコンテンツ生成ワークフローというパターン例を使って、カスタムエージェントの強力さを説明しましょう。

**目標:** 物語を生成し、批評と修正を通じて繰り返し洗練させ、最終チェックを行い、そして重要な点として、*最終的なトーンチェックに失敗した場合は物語を再生成する*システムを作成します。

**なぜカスタムか？** ここでカスタムエージェントを必要とする核心的な要件は、**トーンチェックに基づく条件付きの再生成**です。標準のワークフローエージェントには、サブエージェントのタスクの結果に基づいて条件分岐する組み込み機能がありません。オーケストレータ内にカスタムロジック（`if tone == "negative": ...`）が必要です。

---

### パート1: カスタムエージェントの単純化された初期化

=== "Python"

    `BaseAgent`を継承する`StoryFlowAgent`を定義します。`__init__`では、必要なサブエージェント（渡されたもの）をインスタンス属性として保存し、このカスタムエージェントが直接オーケストレートするトップレベルのエージェントを`BaseAgent`フレームワークに伝えます。
    
    ```python
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:init"
    ```

=== "Java"

    `BaseAgent`を拡張して`StoryFlowAgentExample`を定義します。その**コンストラクタ**では、必要なサブエージェントのインスタンス（パラメータとして渡される）をインスタンスフィールドとして保存します。このカスタムエージェントが直接オーケストレートするこれらのトップレベルのサブエージェントは、リストとして`BaseAgent`の`super`コンストラクタにも渡されます。

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:init"
    ```
---

### パート2: カスタム実行ロジックの定義

=== "Python"

    このメソッドは、標準的なPythonのasync/awaitと制御フローを使用してサブエージェントをオーケストレートします。
    
    ```python
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:executionlogic"
    ```
    **ロジックの説明:**

    1.  最初の`story_generator`が実行されます。その出力は`ctx.session.state["current_story"]`にあることが期待されます。
    2.  `loop_agent`が実行され、内部で`critic`と`reviser`を`max_iterations`回、順次呼び出します。これらは状態から`current_story`と`criticism`を読み書きします。
    3.  `sequential_agent`が実行され、`grammar_check`、次に`tone_check`を呼び出し、状態から`current_story`を読み取り、`grammar_suggestions`と`tone_check_result`を状態に書き込みます。
    4.  **カスタム部分:** `if`文が状態から`tone_check_result`をチェックします。"negative"の場合、`story_generator`が*再度*呼び出され、状態の`current_story`を上書きします。そうでなければ、フローは終了します。


=== "Java"
    
    `runAsyncImpl`メソッドは、RxJavaのFlowableストリームとオペレータを使用して、非同期の制御フローでサブエージェントをオーケストレートします。

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:executionlogic"
    ```
    **ロジックの説明:**

    1.  最初の`storyGenerator.runAsync(invocationContext)` Flowableが実行されます。その出力は`invocationContext.session().state().get("current_story")`にあることが期待されます。
    2.  次に`loopAgent`のFlowableが実行されます（`Flowable.concatArray`と`Flowable.defer`による）。LoopAgentは内部で`critic`と`reviser`サブエージェントを最大`maxIterations`回、順次呼び出します。これらは状態から`current_story`と`criticism`を読み書きします。
    3.  次に`sequentialAgent`のFlowableが実行されます。これは`grammar_check`、次に`tone_check`を呼び出し、状態から`current_story`を読み取り、`grammar_suggestions`と`tone_check_result`を状態に書き込みます。
    4.  **カスタム部分:** `sequentialAgent`が完了した後、`Flowable.defer`内のロジックが`invocationContext.session().state()`から "tone_check_result" をチェックします。"negative"の場合、`storyGenerator`のFlowableが*条件付きで連結*されて再度実行され、"current_story"を上書きします。そうでなければ、空のFlowableが使用され、ワークフロー全体が完了に進みます。

---

### パート3: LLMサブエージェントの定義

これらは標準的な`LlmAgent`の定義であり、特定のタスクを担当します。その`output_key`パラメータは、結果を`session.state`に配置するために不可欠であり、これにより他のエージェントやカスタムオーケストレータがアクセスできるようになります。

=== "Python"

    ```python
    GEMINI_2_FLASH = "gemini-2.0-flash" # モデル定数を定義
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:llmagents"
    ```
=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:llmagents"
    ```

---

### パート4: カスタムエージェントのインスタンス化と実行

最後に、`StoryFlowAgent`をインスタンス化し、通常通り`Runner`を使用します。

=== "Python"

    ```python
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:story_flow_agent"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:story_flow_agent"
    ```

*(注: インポートや実行ロジックを含む完全な実行可能コードは、以下のリンク先にあります。)*

---

## 完全なコード例

???+ "Storyflow Agent"

    === "Python"
    
        ```python
        # StoryFlowAgentの例の完全な実行可能コード
        --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py"
        ```
    
    === "Java"
    
        ```java
        # StoryFlowAgentの例の完全な実行可能コード
        --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:full_code"
        ```