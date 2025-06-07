# コールバックの種類

フレームワークは、エージェントの実行のさまざまな段階でトリガーされる異なる種類のコールバックを提供します。各コールバックがいつ発火し、どのコンテキストを受け取るかを理解することが、それらを効果的に使用するための鍵となります。

## エージェントライフサイクルコールバック

これらのコールバックは、`BaseAgent`から継承する*すべて*のエージェントで利用可能です（`LlmAgent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent`などを含む）。

!!! Note
    具体的なメソッド名や戻り値の型は、SDKの言語によって若干異なる場合があります（例：Pythonでは`None`を返す、Javaでは`Optional.empty()`や`Maybe.empty()`を返す）。詳細は各言語のAPIドキュメントを参照してください。

### Before Agent Callback

**いつ：** エージェントの`_run_async_impl`（または`_run_live_impl`）メソッドが実行される*直前*に呼び出されます。エージェントの`InvocationContext`が作成された後、そのコアロジックが開始される*前*に実行されます。

**目的：** この特定のエージェントの実行にのみ必要なリソースや状態をセットアップしたり、実行開始前にセッション状態（callback_context.state）の検証チェックを行ったり、エージェントのアクティビティのエントリーポイントをログに記録したり、コアロジックが使用する前に呼び出しコンテキストを修正したりするのに理想的です。

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_agent_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeAgentCallbackExample.java:init"
        ```

**`before_agent_callback`の例に関する注記：**

*   **何を示しているか：** この例は`before_agent_callback`を示しています。このコールバックは、特定のリクエストに対してエージェントの主要な処理ロジックが開始される*直前*に実行されます。
*   **どのように機能するか：** コールバック関数（`check_if_agent_should_run`）は、セッションの状態にあるフラグ（`skip_llm_agent`）を見ます。
    *   フラグが`True`の場合、コールバックは`types.Content`オブジェクトを返します。これはADKフレームワークに対し、エージェントの主要な実行を完全に**スキップ**し、コールバックが返したコンテンツを最終応答として使用するように指示します。
    *   フラグが`False`（または設定されていない）の場合、コールバックは`None`または空のオブジェクトを返します。これはADKフレームワークに対し、エージェントの通常の実行（この場合はLLMの呼び出し）を**続行**するように指示します。
*   **期待される結果：** 2つのシナリオが見られます：
    1.  `skip_llm_agent: True`の状態を持つセッションでは、エージェントのLLM呼び出しがバイパスされ、出力はコールバックから直接来ます（"Agent... skipped..."）。
    2.  その状態フラグがないセッションでは、コールバックはエージェントの実行を許可し、LLMからの実際の応答（例："Hello!"）が見られます。
*   **コールバックの理解：** これは、`before_`コールバックが**ゲートキーパー**として機能し、主要なステップの*前*に実行を傍受し、チェック（状態、入力検証、権限など）に基づいてそれを防ぐ可能性があることを示しています。

### After Agent Callback

**いつ：** エージェントの`_run_async_impl`（または`_run_live_impl`）メソッドが正常に完了した*直後*に呼び出されます。`before_agent_callback`がコンテンツを返したためにエージェントがスキップされた場合や、エージェントの実行中に`end_invocation`が設定された場合は実行され*ません*。

**目的：** クリーンアップタスク、実行後の検証、エージェントのアクティビティ完了のロギング、最終的な状態の変更、またはエージェントの最終的な出力の拡張/置換に役立ちます。

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/after_agent_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AfterAgentCallbackExample.java:init"
        ```

**`after_agent_callback`の例に関する注記：**

*   **何を示しているか：** この例は`after_agent_callback`を示しています。このコールバックは、エージェントの主要な処理ロジックが終了し、その結果を生成した後、しかしその結果が確定して返される*前*に実行されます。
*   **どのように機能するか：** コールバック関数（`modify_output_after_agent`）は、セッションの状態にあるフラグ（`add_concluding_note`）をチェックします。
    *   フラグが`True`の場合、コールバックは*新しい*`types.Content`オブジェクトを返します。これはADKフレームワークに対し、エージェントの元の出力をコールバックが返したコンテンツで**置き換える**ように指示します。
    *   フラグが`False`（または設定されていない）の場合、コールバックは`None`または空のオブジェクトを返します。これはADKフレームワークに対し、エージェントが生成した元の出力を**使用する**ように指示します。
*   **期待される結果：** 2つのシナリオが見られます：
    1.  `add_concluding_note: True`の状態がないセッションでは、コールバックはエージェントの元の出力（"Processing complete!"）の使用を許可します。
    2.  その状態フラグがあるセッションでは、コールバックはエージェントの元の出力を傍受し、自身のメッセージ（"Concluding note added..."）で置き換えます。
*   **コールバックの理解：** これは、`after_`コールバックが**後処理**や**変更**を可能にすることを示しています。ステップの結果（エージェントの実行）を検査し、それを通過させるか、変更するか、ロジックに基づいて完全に置き換えるかを決定できます。

## LLMインタラクションコールバック

これらのコールバックは`LlmAgent`に固有であり、大規模言語モデルとのインタラクションの前後でフックを提供します。

### Before Model Callback

**いつ：** `LlmAgent`のフロー内で、`generate_content_async`（または同等の）リクエストがLLMに送信される直前に呼び出されます。

**目的：** LLMに送られるリクエストの検査と変更を可能にします。ユースケースには、動的な指示の追加、状態に基づいたフューショット例の注入、モデル設定の変更、ガードレールの実装（不適切な表現のフィルタリングなど）、またはリクエストレベルのキャッシングの実装が含まれます。

**戻り値の効果：**
コールバックが`None`（またはJavaでは`Maybe.empty()`オブジェクト）を返した場合、LLMは通常のワークフローを続行します。コールバックが`LlmResponse`オブジェクトを返した場合、LLMへの呼び出しは**スキップ**されます。返された`LlmResponse`は、モデルから直接来たかのように使用されます。これはガードレールやキャッシングを実装するのに強力です。

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_model_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeModelCallbackExample.java:init"
        ```

### After Model Callback

**いつ：** LLMから応答（`LlmResponse`）を受け取った直後、それが呼び出し元エージェントによってさらに処理される前に呼び出されます。

**目的：** 生のLLM応答の検査または変更を可能にします。ユースケースには以下が含まれます：

*   モデル出力のロギング
*   応答の再フォーマット
*   モデルによって生成された機密情報の検閲
*   LLM応答から構造化データを解析し、それを`callback_context.state`に保存する
*   または特定のエラーコードの処理

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/after_model_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AfterModelCallbackExample.java:init"
        ```

## ツール実行コールバック

これらのコールバックも`LlmAgent`に固有であり、LLMがリクエストする可能性のあるツール（`FunctionTool`、`AgentTool`などを含む）の実行の前後でトリガーされます。

### Before Tool Callback

**いつ：** LLMがそれに対する関数呼び出しを生成した後、特定のツールの`run_async`メソッドが呼び出される直前に呼び出されます。

**目的：** ツール引数の検査と変更、実行前の認証チェックの実行、ツール使用試行のロギング、またはツールレベルのキャッシングの実装を可能にします。

**戻り値の効果：**

1.  コールバックが`None`（またはJavaでは`Maybe.empty()`オブジェクト）を返した場合、ツールの`run_async`メソッドは（潜在的に変更された）`args`で実行されます。
2.  辞書（またはJavaでは`Map`）が返された場合、ツールの`run_async`メソッドは**スキップ**されます。返された辞書は、ツール呼び出しの結果として直接使用されます。これはキャッシングやツールの振る舞いのオーバーライドに役立ちます。

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_tool_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeToolCallbackExample.java:init"
        ```

### After Tool Callback

**いつ：** ツールの`run_async`メソッドが正常に完了した直後に呼び出されます。

**目的：** （潜在的に要約された後）LLMに返される前に、ツールの結果を検査および変更することを可能にします。ツールの結果のロギング、結果の後処理やフォーマット、または結果の特定の部分をセッション状態に保存するのに役立ちます。

**戻り値の効果：**

1.  コールバックが`None`（またはJavaでは`Maybe.empty()`オブジェクト）を返した場合、元の`tool_response`が使用されます。
2.  新しい辞書が返された場合、それは元の`tool_response`を**置き換え**ます。これにより、LLMが見る結果を変更またはフィルタリングすることができます。

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/after_tool_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AfterToolCallbackExample.java:init"
        ```