# シーケンシャル エージェント

## `SequentialAgent`

`SequentialAgent`は、リストで指定された順序でサブエージェントを実行する[ワークフローエージェント](index.md)です。

実行を固定的で厳密な順序で行いたい場合に`SequentialAgent`を使用します。

### 例

*   あなたは、ウェブページを要約できるエージェントを構築したいと考えています。これには`Get Page Contents`と`Summarize Page`という2つのツールを使用します。エージェントは常に`Summarize Page`を呼び出す前に`Get Page Contents`を呼び出す必要があります（何もないところから要約はできないため！）。したがって、`SequentialAgent`を使用してエージェントを構築すべきです。

他の[ワークフローエージェント](index.md)と同様に、`SequentialAgent`はLLMによって駆動されるのではなく、その実行方法は決定的です。とはいえ、ワークフローエージェントは、その内部ロジックではなく、実行（つまりシーケンス）のみに関心があります。ワークフローエージェントのツールやサブエージェントは、LLMを利用する場合もあれば、しない場合もあります。

### 仕組み

`SequentialAgent`の`Run Async`メソッドが呼び出されると、以下のアクションを実行します：

1.  **反復処理：** 提供された順序でサブエージェントのリストを反復処理します。
2.  **サブエージェントの実行：** リスト内の各サブエージェントに対して、そのサブエージェントの`Run Async`メソッドを呼び出します。

![Sequential Agent](../../assets/sequential-agent.png){: width="600"}

### 完全な例：コード開発パイプライン

簡略化されたコード開発パイプラインを考えてみましょう：

*   **コードライターエージェント：** 仕様に基づいて初期コードを生成するLLMエージェント。
*   **コードレビューアエージェント：** 生成されたコードのエラー、スタイル上の問題、ベストプラクティスへの準拠をレビューするLLMエージェント。コードライターエージェントの出力を受け取ります。
*   **コードリファクタリングエージェント：** レビューされたコード（およびレビュー担当者のコメント）を受け取り、品質を向上させ、問題に対処するためにリファクタリングするLLMエージェント。

`SequentialAgent`はこれに最適です：

```py
SequentialAgent(sub_agents=[CodeWriterAgent, CodeReviewerAgent, CodeRefactorerAgent])
```

これにより、コードが書かれ、*次に*レビューされ、*最後に*リファクタリングされるという、厳密で信頼性の高い順序が保証されます。**各サブエージェントからの出力は、[出力キー (Output Key)](../llm-agents.md#structuring-data-input_schema-output_schema-output_key)を介して状態（state）に保存されることで、次のエージェントに渡されます**。

???+ "Code"

    === "Python"
        ```py
        --8<-- "examples/python/snippets/agents/workflow-agents/sequential_agent_code_development_agent.py:init"
        ```

    === "Java"
        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/workflow/SequentialAgentExample.java:init"
        ```