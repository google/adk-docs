# LLMエージェント

`LlmAgent`（単に`Agent`とエイリアスされることが多い）は、ADKの中核的なコンポーネントであり、アプリケーションの「思考」部分として機能します。大規模言語モデル（LLM）の力を活用して、推論、自然言語の理解、意思決定、応答の生成、ツールとの対話を行います。

事前定義された実行パスに従う決定論的な[ワークフローエージェント](workflow-agents/index.md)とは異なり、`LlmAgent`の振る舞いは非決定的です。LLMを使用して指示とコンテキストを解釈し、どのように進めるか、どのツールを使用するか（もしあれば）、または他のエージェントに制御を移譲するかを動的に決定します。

効果的な`LlmAgent`を構築するには、そのアイデンティティを定義し、指示を通じてその振る舞いを明確に導き、必要なツールと機能を持たせることが含まれます。

## エージェントのアイデンティティと目的の定義

まず、エージェントが*何であるか*、そして*何のため*にあるのかを確立する必要があります。

*   **`name`（必須）：** すべてのエージェントには一意の文字列識別子が必要です。この`name`は、特にエージェントがお互いを参照したりタスクを委任したりする必要があるマルチエージェントシステムにおいて、内部操作にとって非常に重要です。エージェントの機能を反映した説明的な名前を選択してください（例：`customer_support_router`、`billing_inquiry_agent`）。`user`のような予約名は避けてください。

*   **`description`（オプション、マルチエージェントで推奨）：** エージェントの能力の簡潔な要約を提供します。この説明は、主に*他の*LLMエージェントがこのエージェントにタスクをルーティングすべきかどうかを判断するために使用されます。同僚と区別できるほど具体的にしてください（例：「現在の請求書に関する問い合わせを処理します」であり、「請求エージェント」だけではありません）。

*   **`model`（必須）：** このエージェントの推論を動かす基盤となるLLMを指定します。これは`"gemini-2.0-flash"`のような文字列識別子です。モデルの選択は、エージェントの能力、コスト、およびパフォーマンスに影響します。利用可能なオプションと考慮事項については、[モデル](models.md)のページを参照してください。

=== "Python"

    ```python
    # 例：基本的なアイデンティティの定義
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="指定された国の首都に関するユーザーの質問に答えます。"
        # instructionとtoolsは次に追加します
    )
    ```

=== "Java"

    ```java
    // 例：基本的なアイデンティティの定義
    LlmAgent capitalAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("capital_agent")
            .description("指定された国の首都に関するユーザーの質問に答えます。")
            // instructionとtoolsは次に追加します
            .build();
    ```


## エージェントの誘導：指示 (`instruction`)

`instruction`パラメータは、`LlmAgent`の振る舞いを形成する上で間違いなく最も重要な要素です。これは、エージェントに以下を伝える文字列（または文字列を返す関数）です：

*   その中心的なタスクまたは目標。
*   その性格またはペルソナ（例：「あなたは親切なアシスタントです」、「あなたは機知に富んだ海賊です」）。
*   その振る舞いに関する制約（例：「Xに関する質問にのみ答える」、「Yは決して明かさない」）。
*   その`tools`をどのように、いつ使用するか。ツール自体の説明を補足し、各ツールの目的とそれを呼び出すべき状況を説明する必要があります。
*   その出力の望ましい形式（例：「JSONで応答する」、「箇条書きで提供する」）。

**効果的な指示のためのヒント：**

*   **明確かつ具体的にする：** 曖昧さを避けます。望ましいアクションと結果を明確に述べてください。
*   **Markdownを使用する：** 見出しやリストなどを使用して、複雑な指示の可読性を向上させます。
*   **例を提供する（フューショット）：** 複雑なタスクや特定の出力形式については、指示に直接例を含めます。
*   **ツールの使用をガイドする：** ツールをリストアップするだけでなく、エージェントが*いつ*、*なぜ*それらを使用すべきかを説明します。

**状態（State）：**

*   instructionは文字列テンプレートであり、`{var}`構文を使用して動的な値をinstructionに挿入できます。
*   `{var}`は、varという名前の状態変数の値を挿入するために使用されます。
*   `{artifact.var}`は、varという名前のアーティファクトのテキストコンテンツを挿入するために使用されます。
*   状態変数またはアーティファクトが存在しない場合、エージェントはエラーを発生させます。エラーを無視したい場合は、`{var?}`のように変数名に`?`を追加できます。

=== "Python"

    ```python
    # 例：指示の追加
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="指定された国の首都に関するユーザーの質問に答えます。",
        instruction="""あなたは国の首都を提供するエージェントです。
    ユーザーが国の首都を尋ねたとき：
    1. ユーザーのクエリから国名を特定します。
    2. `get_capital_city`ツールを使用して首都を見つけます。
    3. ユーザーに明確に応答し、首都を述べます。
    クエリの例: "What's the capital of {country}?"
    応答の例: "The capital of France is Paris."
    """,
        # toolsは次に追加します
    )
    ```

=== "Java"

    ```java
    // 例：指示の追加
    LlmAgent capitalAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("capital_agent")
            .description("指定された国の首都に関するユーザーの質問に答えます。")
            .instruction(
                """
                あなたは国の首都を提供するエージェントです。
                ユーザーが国の首都を尋ねたとき：
                1. ユーザーのクエリから国名を特定します。
                2. `get_capital_city`ツールを使用して首都を見つけます。
                3. ユーザーに明確に応答し、首都を述べます。
                クエリの例: "What's the capital of {country}?"
                応答の例: "The capital of France is Paris."
                """)
            // toolsは次に追加します
            .build();
    ```

*（注：システム内の*すべて*のエージェントに適用される指示については、ルートエージェントで`global_instruction`を使用することを検討してください。詳細は[マルチエージェント](multi-agents.md)セクションで説明します。）*

## エージェントの装備：ツール (`tools`)

ツールは、LLMの組み込み知識や推論能力を超えた機能を`LlmAgent`に与えます。これにより、エージェントは外部の世界と対話し、計算を実行し、リアルタイムのデータを取得し、または特定のアクションを実行できます。

*   **`tools`（オプション）：** エージェントが使用できるツールのリストを提供します。リストの各項目は以下のいずれかです：
    *   ネイティブ関数またはメソッド（`FunctionTool`としてラップされます）。Python ADKはネイティブ関数を自動的に`FunctionTool`にラップしますが、Javaメソッドは`FunctionTool.create(...)`を使用して明示的にラップする必要があります。
    *   `BaseTool`から継承したクラスのインスタンス。
    *   別のエージェントのインスタンス（`AgentTool`、エージェント間の委任を可能にする - [マルチエージェント](multi-agents.md)を参照）。

LLMは、関数/ツール名、説明（docstringまたは`description`フィールドから）、およびパラメータスキーマを使用して、会話とその指示に基づいてどのツールを呼び出すかを決定します。

=== "Python"

    ```python
    # ツール関数を定義
    def get_capital_city(country: str) -> str:
      """指定された国の首都を取得します。"""
      # 実際のロジックに置き換える（例：API呼び出し、データベース検索）
      capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
      return capitals.get(country.lower(), f"申し訳ありませんが、{country}の首都はわかりません。")
    
    # ツールをエージェントに追加
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="指定された国の首都に関するユーザーの質問に答えます。",
        instruction="""あなたは国の首都を提供するエージェントです...（前の指示テキスト）""",
        tools=[get_capital_city] # 関数を直接提供
    )
    ```

=== "Java"

    ```java
    import com.google.genai.types.Schema;
    import java.util.HashMap;
    import java.util.Map;

    // ツール関数を定義
    // 指定された国の首都を取得します。
    public static Map<String, Object> getCapitalCity(
            @Schema(name = "country", description = "首都を取得する国")
            String country) {
      // 実際のロジックに置き換える（例：API呼び出し、データベース検索）
      Map<String, String> countryCapitals = new HashMap<>();
      countryCapitals.put("canada", "Ottawa");
      countryCapitals.put("france", "Paris");
      countryCapitals.put("japan", "Tokyo");
    
      String result =
              countryCapitals.getOrDefault(
                      country.toLowerCase(), "申し訳ありませんが、" + country + "の首都は見つかりませんでした。");
      return Map.of("result", result); // ツールはMapを返さなければならない
    }
    
    // ツールをエージェントに追加
    FunctionTool capitalTool = FunctionTool.create(experiment.getClass(), "getCapitalCity");
    LlmAgent capitalAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("capital_agent")
            .description("指定された国の首都に関するユーザーの質問に答えます。")
            .instruction("あなたは国の首都を提供するエージェントです...（前の指示テキスト）")
            .tools(capitalTool) // FunctionToolとしてラップされた関数を提供
            .build();
    ```

ツールの詳細については、[ツール](../tools/index.md)セクションを参照してください。

## 高度な設定と制御

主要なパラメータに加えて、`LlmAgent`はより細かい制御のためのいくつかのオプションを提供します：

### LLM生成の微調整 (`generate_content_config`)

`generate_content_config`を使用して、基盤となるLLMが応答を生成する方法を調整できます。

*   **`generate_content_config`（オプション）：** `google.genai.types.GenerateContentConfig`のインスタンスを渡して、`temperature`（ランダム性）、`max_output_tokens`（応答の長さ）、`top_p`、`top_k`、および安全設定などのパラメータを制御します。

=== "Python"

    ```python
    from google.genai import types

    agent = LlmAgent(
        # ... 他のパラメータ
        generate_content_config=types.GenerateContentConfig(
            temperature=0.2, # より決定論的な出力
            max_output_tokens=250
        )
    )
    ```

=== "Java"

    ```java
    import com.google.genai.types.GenerateContentConfig;

    LlmAgent agent =
        LlmAgent.builder()
            // ... 他のパラメータ
            .generateContentConfig(GenerateContentConfig.builder()
                .temperature(0.2F) // より決定論的な出力
                .maxOutputTokens(250)
                .build())
            .build();
    ```

### データの構造化 (`input_schema`, `output_schema`, `output_key`)

`LLM Agent`との構造化されたデータ交換を必要とするシナリオのために、ADKはスキーマ定義を使用して、期待される入力と望ましい出力形式を定義するメカニズムを提供します。

*   **`input_schema`（オプション）：** 期待される入力構造を表すスキーマを定義します。設定されている場合、このエージェントに渡されるユーザーメッセージのコンテンツは、このスキーマに準拠したJSON文字列で*なければなりません*。あなたの指示は、ユーザーまたは先行するエージェントをそれに応じて誘導する必要があります。

*   **`output_schema`（オプション）：** 望ましい出力構造を表すスキーマを定義します。設定されている場合、エージェントの最終応答は、このスキーマに準拠したJSON文字列で*なければなりません*。
    *   **制約：** `output_schema`を使用すると、LLM内での制御された生成が可能になりますが、**エージェントがツールを使用したり、他のエージェントに制御を移譲したりする能力が無効になります**。あなたの指示は、LLMが直接スキーマに一致するJSONを生成するように導く必要があります。

*   **`output_key`（オプション）：** 文字列キーを提供します。設定されている場合、エージェントの*最終的な*応答のテキストコンテンツは、このキーの下でセッションの状態辞書に自動的に保存されます。これは、エージェントやワークフローのステップ間で結果を渡すのに役立ちます。
    *   Pythonでは、これは次のようになります：`session.state[output_key] = agent_response_text`
    *   Javaでは：`session.state().put(outputKey, agentResponseText)`

=== "Python"

    入力および出力スキーマは通常、`Pydantic`のBaseModelです。

    ```python
    from pydantic import BaseModel, Field
    
    class CapitalOutput(BaseModel):
        capital: str = Field(description="国の首都。")
    
    structured_capital_agent = LlmAgent(
        # ... name, model, description
        instruction="""あなたは首都情報エージェントです。国が与えられたら、首都を含むJSONオブジェクトのみで応答してください。フォーマット: {"capital": "capital_name"}""",
        output_schema=CapitalOutput, # JSON出力を強制
        output_key="found_capital"  # 結果をstate['found_capital']に保存
        # ここではtools=[get_capital_city]を効果的に使用できない
    )
    ```

=== "Java"

     入力および出力スキーマは`google.genai.types.Schema`オブジェクトです。

    ```java
    private static final Schema CAPITAL_OUTPUT =
        Schema.builder()
            .type("OBJECT")
            .description("首都情報のためのスキーマ。")
            .properties(
                Map.of(
                    "capital",
                    Schema.builder()
                        .type("STRING")
                        .description("国の首都。")
                        .build()))
            .build();
    
    LlmAgent structuredCapitalAgent =
        LlmAgent.builder()
            // ... name, model, description
            .instruction(
                    "あなたは首都情報エージェントです。国が与えられたら、首都を含むJSONオブジェクトのみで応答してください。フォーマット: {\"capital\": \"capital_name\"}")
            .outputSchema(CAPITAL_OUTPUT) // JSON出力を強制
            .outputKey("found_capital") // 結果をstate.get("found_capital")に保存
            // ここではtools(getCapitalCity)を効果的に使用できない
            .build();
    ```

### コンテキストの管理 (`include_contents`)

エージェントが以前の会話履歴を受け取るかどうかを制御します。

*   **`include_contents`（オプション、デフォルト：`'default'`）：** `contents`（履歴）がLLMに送信されるかどうかを決定します。
    *   `'default'`: エージェントは関連する会話履歴を受け取ります。
    *   `'none'`: エージェントは以前の`contents`を一切受け取りません。*現在の*ターンで提供された指示と入力のみに基づいて動作します（ステートレスタスクや特定のコンテキストの強制に役立ちます）。

=== "Python"

    ```python
    stateless_agent = LlmAgent(
        # ... 他のパラメータ
        include_contents='none'
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent.IncludeContents;
    
    LlmAgent statelessAgent =
        LlmAgent.builder()
            // ... 他のパラメータ
            .includeContents(IncludeContents.NONE)
            .build();
    ```

### プランニングとコード実行

![python_only](https://img.shields.io/badge/現在サポートされているのは-Python-blue){ title="この機能は現在Pythonで利用可能です。Javaのサポートは計画中/近日公開予定です。" }

複数のステップを含むより複雑な推論やコードの実行のために：

*   **`planner`（オプション）：** `BasePlanner`インスタンスを割り当てて、実行前の複数ステップの推論とプランニングを有効にします。（[マルチエージェント](multi-agents.md)のパターンを参照）。
*   **`code_executor`（オプション）：** `BaseCodeExecutor`インスタンスを提供して、エージェントがLLMの応答で見つかったコードブロック（例：Python）を実行できるようにします。（[ツール/組み込みツール](../tools/built-in-tools.md)を参照）。

## まとめ：例

??? "Code"
    以下は、基本的な`capital_agent`の完全な例です：

    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/agents/llm-agent/capital_agent.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/LlmAgentExample.java:full_code"
        ```

*（この例はコアコンセプトを示しています。より複雑なエージェントは、スキーマ、コンテキスト制御、プランニングなどを組み込む場合があります。）*

## 関連コンセプト（後述のトピック）

このページでは`LlmAgent`のコア設定について説明しましたが、いくつかの関連コンセプトがより高度な制御を提供し、他の場所で詳しく説明されています：

*   **コールバック：** `before_model_callback`、`after_model_callback`などを使用して実行ポイント（モデル呼び出しの前後、ツール呼び出しの前後）を傍受します。[コールバック](../callbacks/types-of-callbacks.md)を参照してください。
*   **マルチエージェント制御：** プランニング（`planner`）、エージェント転送の制御（`disallow_transfer_to_parent`、`disallow_transfer_to_peers`）、およびシステム全体の指示（`global_instruction`）を含む、エージェント対話のための高度な戦略。[マルチエージェント](multi-agents.md)を参照してください。