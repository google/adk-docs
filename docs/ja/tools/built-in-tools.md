# 組み込みツール

これらの組み込みツールは、Google検索やコード実行など、すぐに使える機能を提供し、エージェントに共通の能力を付与します。例えば、ウェブから情報を取得する必要があるエージェントは、追加の設定なしで直接**google\_search**ツールを使用できます。

## 使用方法

1.  **インポート:** ツールモジュールから目的のツールをインポートします。これはPythonでは`agents.tools`、Javaでは`com.google.adk.tools`です。
2.  **設定:** ツールを初期化し、必要であれば必須パラメータを提供します。
3.  **登録:** 初期化されたツールをエージェントの**tools**リストに追加します。

エージェントに追加されると、エージェントは**ユーザープロンプト**と自身の**指示**に基づいてツールを使用するかどうかを決定できます。エージェントがツールを呼び出すと、フレームワークがその実行を処理します。重要：このページの***制限事項***セクションを確認してください。

## 利用可能な組み込みツール

注：現在、JavaはGoogle検索とコード実行ツールのみをサポートしています。

### Google検索

`google_search`ツールを使用すると、エージェントはGoogle検索を使用してウェブ検索を実行できます。`google_search`ツールはGemini 2モデルとのみ互換性があります。

!!! warning " `google_search`ツール使用時の追加要件"
    Google検索によるグラウンディングを使用し、レスポンスで検索候補を受け取った場合、本番環境およびアプリケーションで検索候補を表示する必要があります。
    Google検索によるグラウンディングの詳細については、[Google AI Studio](https://ai.google.dev/gemini-api/docs/grounding/search-suggestions)または[Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions)のドキュメントを参照してください。UIコード（HTML）はGeminiレスポンスの`renderedContent`として返されるため、ポリシーに従ってアプリにHTMLを表示する必要があります。

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/google_search.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/GoogleSearchAgentApp.java:full_code"
    ```

### コード実行

`built_in_code_execution`ツールは、特にGemini 2モデルを使用する場合に、エージェントがコードを実行できるようにします。これにより、モデルは計算、データ操作、小さなスクリプトの実行などのタスクを実行できます。

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/code_execution.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CodeExecutionAgentApp.java:full_code"
    ```


### Vertex AI Search

`vertex_ai_search_tool`はGoogle CloudのVertex AI Searchを使用し、エージェントがプライベートに設定されたデータストア（例: 社内ドキュメント、企業ポリシー、ナレッジベース）を検索できるようにします。この組み込みツールでは、設定時に特定のデータストアIDを提供する必要があります。

```py
--8<-- "examples/python/snippets/tools/built-in-tools/vertexai_search.py"
```

## 組み込みツールを他のツールと使用する

以下のコードサンプルは、複数の組み込みツールを使用する方法、または複数のエージェントを使用して組み込みツールを他のツールと組み合わせる方法を示しています。

=== "Python"

    ```py
    from google.adk.tools import agent_tool
    from google.adk.agents import Agent
    from google.adk.tools import google_search
    from google.adk.code_executors import BuiltInCodeExecutor
    

    search_agent = Agent(
        model='gemini-2.0-flash',
        name='SearchAgent',
        instruction="""
        あなたはGoogle検索のスペシャリストです
        """,
        tools=[google_search],
    )
    coding_agent = Agent(
        model='gemini-2.0-flash',
        name='CodeAgent',
        instruction="""
        あなたはコード実行のスペシャリストです
        """,
        code_executor=[BuiltInCodeExecutor],
    )
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="ルートエージェント",
        tools=[agent_tool.AgentTool(agent=search_agent), agent_tool.AgentTool(agent=coding_agent)],
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;
    import com.google.adk.tools.BuiltInCodeExecutionTool;
    import com.google.adk.tools.GoogleSearchTool;
    import com.google.common.collect.ImmutableList;
    
    public class NestedAgentApp {
    
      private static final String MODEL_ID = "gemini-2.0-flash";
    
      public static void main(String[] args) {

        // SearchAgentを定義
        LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("あなたはGoogle検索のスペシャリストです")
                .tools(new GoogleSearchTool()) // GoogleSearchToolをインスタンス化
                .build();
    

        // CodingAgentを定義
        LlmAgent codingAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("CodeAgent")
                .instruction("あなたはコード実行のスペシャリストです")
                .tools(new BuiltInCodeExecutionTool()) // BuiltInCodeExecutionToolをインスタンス化
                .build();

        // RootAgentを定義。AgentTool.create()を使用してSearchAgentとCodingAgentをラップ
        BaseAgent rootAgent =
            LlmAgent.builder()
                .name("RootAgent")
                .model(MODEL_ID)
                .description("ルートエージェント")
                .tools(
                    AgentTool.create(searchAgent), // createメソッドを使用
                    AgentTool.create(codingAgent)   // createメソッドを使用
                 )
                .build();

        // 注：このサンプルはエージェントの定義のみを示しています。
        // これらのエージェントを実行するには、前の例と同様に、
        // RunnerとSessionServiceに統合する必要があります。
        System.out.println("エージェントが正常に定義されました:");
        System.out.println("  ルートエージェント: " + rootAgent.name());
        System.out.println("  検索エージェント（ネスト）: " + searchAgent.name());
        System.out.println("  コードエージェント（ネスト）: " + codingAgent.name());
      }
    }
    ```


### 制限事項

!!! warning

    現在、各ルートエージェントまたは単一のエージェントに対して、サポートされている組み込みツールは1つだけです。同じエージェント内で他のどのタイプのツールも使用することはできません。

 例えば、単一のエージェント内で***組み込みツールを他のツールと一緒に***使用する以下のアプローチは、現在サポートされて**いません**。

=== "Python"

    ```py
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="Root Agent",
        tools=[custom_function], 
        executor=[BuiltInCodeExecutor] # <-- toolsと併用する場合はサポートされていません
    )
    ```

=== "Java"

    ```java
     LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("あなたはGoogle検索のスペシャリストです")
                .tools(new GoogleSearchTool(), new YourCustomTool()) // <-- サポートされていません
                .build();
    ```

!!! warning

    組み込みツールはサブエージェント内では使用できません。

例えば、サブエージェント内で組み込みツールを使用する以下のアプローチは、現在サポートされて**いません**。

=== "Python"

    ```py
    search_agent = Agent(
        model='gemini-2.0-flash',
        name='SearchAgent',
        instruction="""
        あなたはGoogle検索のスペシャリストです
        """,
        tools=[google_search],
    )
    coding_agent = Agent(
        model='gemini-2.0-flash',
        name='CodeAgent',
        instruction="""
        あなたはコード実行のスペシャリストです
        """,
        executor=[BuiltInCodeExecutor],
    )
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="Root Agent",
        sub_agents=[
            search_agent,
            coding_agent
        ],
    )
    ```

=== "Java"

    ```java
    LlmAgent searchAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("SearchAgent")
            .instruction("あなたはGoogle検索のスペシャリストです")
            .tools(new GoogleSearchTool())
            .build();

    LlmAgent codingAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("CodeAgent")
            .instruction("あなたはコード実行のスペシャリストです")
            .tools(new BuiltInCodeExecutionTool())
            .build();
    

    LlmAgent rootAgent =
        LlmAgent.builder()
            .name("RootAgent")
            .model("gemini-2.0-flash")
            .description("Root Agent")
            .subAgents(searchAgent, codingAgent) // サブエージェントが組み込みツールを使用しているため、サポートされていません。
            .build();
    ```