# 関数ツール

## 関数ツールとは？

標準のツールが特定の要件を完全に満たさない場合、開発者はカスタムの関数ツールを作成できます。これにより、独自のデータベースへの接続やユニークなアルゴリズムの実装など、**カスタマイズされた機能**が可能になります。

*例えば、*関数ツール「myfinancetool」は、特定の財務指標を計算する関数かもしれません。ADKは長時間実行される関数もサポートしているため、その計算に時間がかかる場合でも、エージェントは他のタスクの作業を続けることができます。

ADKは、関数ツールを作成するためのいくつかの方法を提供しており、それぞれが異なるレベルの複雑さと制御に適しています：

1.  関数ツール
2.  長時間実行関数ツール
3.  ツールとしてエージェント

## 1. 関数ツール

関数をツールに変換することは、カスタムロジックをエージェントに統合する簡単な方法です。実際、エージェントのツールリストに関数を割り当てると、フレームワークは自動的にそれを関数ツールとしてラップします。このアプローチは、柔軟性と迅速な統合を提供します。

### パラメータ

標準の**JSONシリアライズ可能な型**（例：文字列、整数、リスト、辞書）を使用して関数パラメータを定義します。言語モデル（LLM）は現在、パラメータのデフォルト値を解釈することをサポートしていないため、デフォルト値を設定しないことが重要です。

### 戻り値の型

関数ツールの推奨される戻り値の型は、Pythonでは**辞書（dictionary）**、Javaでは**Map**です。これにより、応答をキーと値のペアで構造化し、LLMにコンテキストと明確さを提供できます。関数が辞書以外の型を返す場合、フレームワークは自動的にそれを**「result」**という単一のキーを持つ辞書にラップします。

戻り値はできるだけ説明的にするように努めてください。*例えば、*数値のエラーコードを返す代わりに、「error_message」キーに人間が読める説明を含む辞書を返します。**コードの一部ではなく、LLMが結果を理解する必要がある**ことを忘れないでください。ベストプラクティスとして、戻り値の辞書に「status」キーを含め、操作全体の成果（例：「success」、「error」、「pending」）を示すことで、LLMに操作の状態に関する明確なシグナルを提供します。

### Docstring / ソースコードのコメント

関数のdocstring（またはその上のコメント）は、ツールの説明として機能し、LLMに送信されます。したがって、LLMがツールを効果的に使用する方法を理解するためには、よく書かれた包括的なdocstringが不可欠です。関数の目的、そのパラメータの意味、および期待される戻り値を明確に説明してください。

??? "例"

    === "Python"
    
        このツールは、指定された株式のティッカー/シンボルの株価を取得するPython関数です。
    
        <u>注</u>：このツールを使用する前に、`pip install yfinance`ライブラリをインストールする必要があります。
    
        ```py
        --8<-- "examples/python/snippets/tools/function-tools/func_tool.py"
        ```
    
        このツールからの戻り値は辞書にラップされます。
    
        ```json
        {"result": "$123"}
        ```
    
    === "Java"
    
        このツールは、株価のモック値を取得します。
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/tools/StockPriceAgent.java:full_code"
        ```
    
        このツールからの戻り値はMap<String, Object>にラップされます。
    
        ```json
        入力`GOOG`の場合：{"symbol": "GOOG", "price": "1.0"}
        ```

### ベストプラクティス

関数の定義にはかなりの柔軟性がありますが、シンプルさがLLMの使いやすさを向上させることを忘れないでください。以下のガイドラインを考慮してください：

*   **パラメータは少ない方が良い：** 複雑さを減らすためにパラメータの数を最小限に抑えます。
*   **単純なデータ型：** 可能な限り、カスタムクラスよりも`str`や`int`のようなプリミティブなデータ型を優先します。
*   **意味のある名前：** 関数の名前とパラメータ名は、LLMがツールをどのように解釈し、利用するかに大きく影響します。関数の目的とその入力の意味を明確に反映する名前を選択してください。`do_stuff()`や`beAgent()`のような一般的な名前は避けてください。

## 2. 長時間実行関数ツール

エージェントの実行をブロックすることなく、かなりの処理時間を必要とするタスクのために設計されています。このツールは`FunctionTool`のサブクラスです。

`LongRunningFunctionTool`を使用する場合、関数は長時間実行される操作を開始し、オプションで**初期結果**（例：長時間実行操作ID）を返すことができます。長時間実行関数ツールが呼び出されると、エージェントランナーはエージェントの実行を一時停止し、エージェントクライアントに続行するか、長時間実行操作が終了するまで待つかを決定させます。エージェントクライアントは長時間実行操作の進捗を照会し、中間または最終的な応答を送り返すことができます。その後、エージェントは他のタスクを続行できます。例としては、エージェントがタスクを進める前に人間の承認が必要なヒューマンインザループのシナリオがあります。

### 仕組み

Pythonでは、関数を`LongRunningFunctionTool`でラップします。Javaでは、メソッド名を`LongRunningFunctionTool.create()`に渡します。

1.  **開始：** LLMがツールを呼び出すと、関数が長時間実行操作を開始します。

2.  **初期更新：** 関数はオプションで初期結果（例：長時間実行操作ID）を返す必要があります。ADKフレームワークはその結果を受け取り、`FunctionResponse`にパッケージ化してLLMに送り返します。これにより、LLMはユーザーに（例：ステータス、完了率、メッセージ）を通知できます。そして、エージェントの実行は終了/一時停止されます。

3.  **続行または待機：** 各エージェントの実行が完了した後。エージェントクライアントは長時間実行操作の進捗を照会し、中間応答でエージェントの実行を続行するか（進捗を更新するため）、最終的な応答が取得されるまで待つかを決定できます。エージェントクライアントは、次回の実行のために中間または最終的な応答をエージェントに送り返す必要があります。

4.  **フレームワークの処理：** ADKフレームワークは実行を管理します。エージェントクライアントから送信された中間または最終的な`FunctionResponse`をLLMに送信し、ユーザーフレンドリーなメッセージを生成します。

### ツールの作成

ツール関数を定義し、`LongRunningFunctionTool`クラスを使用してラップします：

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py:define_long_running_function"
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.LongRunningFunctionTool;
    import java.util.HashMap;
    import java.util.Map;
    
    public class ExampleLongRunningFunction {
    
      // 長時間実行関数を定義します。
      // 払い戻しの承認を求めます。
      public static Map<String, Object> askForApproval(String purpose, double amount) {
        // チケット作成と通知送信をシミュレート
        System.out.println(
            "目的：" + purpose + "、金額：" + amount + "のチケット作成をシミュレート中");
    
        // 承認者にチケットのリンク付きで通知を送信
        Map<String, Object> result = new HashMap<>();
        result.put("status", "pending");
        result.put("approver", "Sean Zhou");
        result.put("purpose", purpose);
        result.put("amount", amount);
        result.put("ticket-id", "approval-ticket-1");
        return result;
      }
    
      public static void main(String[] args) throws NoSuchMethodException {
        // メソッドをLongRunningFunctionTool.createに渡す
        LongRunningFunctionTool approveTool =
            LongRunningFunctionTool.create(ExampleLongRunningFunction.class, "askForApproval");
    
        // ツールをエージェントに含める
        LlmAgent approverAgent =
            LlmAgent.builder()
                // ...
                .tools(approveTool)
                .build();
      }
    }
    ```

### 中間/最終結果の更新

エージェントクライアントは、長時間実行関数呼び出しを含むイベントを受け取り、チケットのステータスを確認します。その後、エージェントクライアントは進捗を更新するために中間または最終的な応答を送り返すことができます。フレームワークはこの値（Noneであっても）を`FunctionResponse`のコンテンツにパッケージ化してLLMに送り返します。

!!! Tip "Java ADKにのみ適用"

    Function Toolsで`ToolContext`を渡す場合、以下のいずれかが真であることを確認してください：

    *   スキーマが関数シグネチャのToolContextパラメータと一緒に渡されている。例：
      ```
      @com.google.adk.tools.Annotations.Schema(name = "toolContext") ToolContext toolContext
      ```
    または

    *   以下の`-parameters`フラグがmvnコンパイラプラグインに設定されている。

    ```
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.14.0</version> <!-- またはそれ以降 -->
                <configuration>
                    <compilerArgs>
                        <arg>-parameters</arg>
                    </compilerArgs>
                </configuration>
            </plugin>
        </plugins>
    </build>
    ```
    この制約は一時的なものであり、削除される予定です。


=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py:call_reimbursement_tool"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/LongRunningFunctionExample.java:full_code"
    ```

??? "Pythonの完全な例：ファイル処理シミュレーション"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py"
    ```

#### この例の重要な側面

*   **`LongRunningFunctionTool`**: 提供されたメソッド/関数をラップします。フレームワークは、yieldされた更新と最終的な戻り値をシーケンシャルなFunctionResponseとして送信する処理を担当します。

*   **エージェントの指示**: LLMにツールを使用させ、ユーザーへの更新のために受信するFunctionResponseストリーム（進捗 vs 完了）を理解させます。

*   **最終的な戻り値**: 関数は最終的な結果の辞書を返し、それが完了を示すための最後のFunctionResponseで送信されます。

## 3. ツールとしてのエージェント

この強力な機能により、システム内の他のエージェントをツールとして呼び出すことで、その能力を活用できます。ツールとしてのエージェントは、別のエージェントを呼び出して特定のタスクを実行させることができ、効果的に**責任を委任**します。これは概念的に、別のエージェントを呼び出し、そのエージェントの応答を関数の戻り値として使用するPython関数を作成するのと似ています。

### サブエージェントとの主な違い

ツールとしてのエージェントとサブエージェントを区別することが重要です。

*   **ツールとしてのエージェント:** エージェントAがエージェントBをツールとして呼び出すと（ツールとしてのエージェントを使用）、エージェントBの回答はエージェントAに**返され**、エージェントAはその回答を要約してユーザーへの応答を生成します。エージェントAは制御を保持し、将来のユーザー入力を処理し続けます。

*   **サブエージェント:** エージェントAがエージェントBをサブエージェントとして呼び出すと、ユーザーに答える責任は完全に**エージェントBに移譲されます**。エージェントAは事実上ループの外に出ます。以降のすべてのユーザー入力はエージェントBによって回答されます。

### 使用法

エージェントをツールとして使用するには、エージェントをAgentToolクラスでラップします。

=== "Python"

    ```py
    tools=[AgentTool(agent=agent_b)]
    ```

=== "Java"

    ```java
    AgentTool.create(agent)
    ```

### カスタマイズ

`AgentTool`クラスは、その振る舞いをカスタマイズするための以下の属性を提供します：

*   **skip_summarization: bool:** Trueに設定すると、フレームワークはツールエージェントの応答の**LLMベースの要約をバイパス**します。これは、ツールの応答が既によくフォーマットされており、さらなる処理が不要な場合に役立ちます。

??? "例"

    === "Python"

        ```py
        --8<-- "examples/python/snippets/tools/function-tools/summarizer.py"
        ```
  
    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/tools/AgentToolCustomization.java:full_code"
        ```

### 仕組み

1.  `main_agent`が長いテキストを受け取ると、その指示は長いテキストに対して'summarize'ツールを使用するように指示します。
2.  フレームワークは'summarize'を`summary_agent`をラップする`AgentTool`として認識します。
3.  舞台裏では、`main_agent`は長いテキストを入力として`summary_agent`を呼び出します。
4.  `summary_agent`はその指示に従ってテキストを処理し、要約を生成します。
5.  **`summary_agent`からの応答は、`main_agent`に返されます。**
6.  `main_agent`はその要約を受け取り、ユーザーへの最終的な応答を（例：「テキストの要約はこちらです：...」）を組み立てることができます。