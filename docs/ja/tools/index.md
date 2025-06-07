# ツール

## ツールとは？

ADKの文脈において、ツールとはAIエージェントに提供される特定の能力を表し、エージェントが中核となるテキスト生成や推論能力を超えて、アクションを実行したり世界と対話したりすることを可能にします。有能なエージェントを基本的な言語モデルと区別するのは、多くの場合、ツールの効果的な使用方法です。

技術的には、ツールは通常、モジュール化されたコードコンポーネントです。例えば、**Python/Javaの関数**、クラスメソッド、あるいは別の特化したエージェントなど、明確に定義されたタスクを実行するように設計されています。これらのタスクは、多くの場合、外部システムやデータとの対話を伴います。

<img src="../assets/agent-tool-call.png" alt="エージェントによるツール呼び出し">

### 主な特徴

**アクション指向:** ツールは、次のような特定のアクションを実行します。

*   データベースへのクエリ発行
*   APIリクエストの作成（例: 天気データの取得、予約システム）
*   ウェブ検索
*   コードスニペットの実行
*   ドキュメントからの情報取得（RAG）
*   他のソフトウェアやサービスとの対話

**エージェントの能力拡張:** ツールは、エージェントがリアルタイム情報にアクセスし、外部システムに影響を与え、訓練データに固有の知識の限界を克服することを可能にします。

**事前定義されたロジックの実行:** 重要なのは、ツールは開発者が定義した特定のロジックを実行する点です。エージェントの中核となる大規模言語モデル（LLM）のように、独自の独立した推論能力は持っていません。LLMは、どのツールを、いつ、どのような入力で使うかを推論しますが、ツール自体はその指定された関数を実行するだけです。

## エージェントによるツールの使用方法

エージェントは、多くの場合、関数呼び出しを含むメカニズムを通じて動的にツールを活用します。このプロセスは一般的に次のステップに従います。

1.  **推論:** エージェントのLLMが、システム指示、会話履歴、およびユーザーのリクエストを分析します。
2.  **選択:** 分析に基づき、LLMはエージェントが利用可能なツールと各ツールを説明するdocstringを基に、実行するツールを（もしあれば）決定します。
3.  **呼び出し:** LLMは、選択されたツールに必要な引数（入力）を生成し、その実行をトリガーします。
4.  **観察:** エージェントは、ツールから返された出力（結果）を受け取ります。
5.  **最終化:** エージェントは、ツールの出力を進行中の推論プロセスに組み込み、次の応答を形成したり、後続のステップを決定したり、目標が達成されたかどうかを判断したりします。

ツールは、エージェントの知的な中核（LLM）が複雑なタスクを達成するために必要に応じてアクセスし利用できる、専門的なツールキットのようなものだと考えてください。

## ADKのツールタイプ

ADKは、いくつかのタイプのツールをサポートすることで柔軟性を提供します。

1.  **[関数ツール](../tools/function-tools.md):** アプリケーションの特定のニーズに合わせて、あなたが作成するツール。
    *   **[関数/メソッド](../tools/function-tools.md#1-function-tool):** コード内で標準的な同期関数やメソッドを定義します（例: Pythonの`def`）。
    *   **[ツールとしてのエージェント](../tools/function-tools.md#3-agent-as-a-tool):** 別の、場合によっては特化したエージェントを、親エージェントのツールとして使用します。
    *   **[長時間実行関数ツール](../tools/function-tools.md#2-long-running-function-tool):** 非同期操作や完了までに時間がかかるタスクを実行するツールをサポートします。
2.  **[組み込みツール](../tools/built-in-tools.md):** 一般的なタスクのためにフレームワークによって提供される、すぐに使えるツール。
        例: Google検索、コード実行、Retrieval-Augmented Generation (RAG)。
3.  **[サードパーティ製ツール](../tools/third-party-tools.md):** 人気のある外部ライブラリからツールをシームレスに統合します。
        例: LangChainツール、CrewAIツール。

各ツールタイプの詳細情報と例については、上記の各ドキュメントページへのリンクをたどってください。

## エージェントの指示におけるツールの参照

エージェントの指示の中で、ツールの**関数名**を使って直接参照することができます。ツールの**関数名**と**docstring**が十分に説明的であれば、あなたの指示は主に**大規模言語モデル（LLM）がいつツールを利用すべきか**に焦点を当てることができます。これにより、明確さが促進され、モデルが各ツールの意図された使用方法を理解するのに役立ちます。

ツールが生成する可能性のある**異なる戻り値をエージェントがどのように処理するかを明確に指示することが非常に重要**です。例えば、ツールがエラーメッセージを返す場合、エージェントが操作を再試行すべきか、タスクをあきらめるべきか、あるいはユーザーに追加情報を要求すべきかを指示で指定する必要があります。

さらに、ADKはツールの連続使用をサポートしており、あるツールの出力が別のツールの入力として機能することができます。このようなワークフローを実装する場合、モデルが必要なステップを導くために、エージェントの指示内で**意図されたツールの使用順序を記述する**ことが重要です。

### 例

次の例は、エージェントが**指示の中で関数名を参照する**ことでツールを使用する方法を示しています。また、成功メッセージやエラーメッセージなど、**ツールからの異なる戻り値を処理する**ようにエージェントを誘導する方法や、タスクを達成するために**複数のツールを連続して使用する**方法を編成する方法も示しています。

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/weather_sentiment.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/WeatherSentimentAgentApp.java:full_code"
    ```

## ツールコンテキスト

より高度なシナリオのために、ADKでは特別なパラメータ`tool_context: ToolContext`を含めることで、ツール関数内から追加のコンテキスト情報にアクセスできます。これを関数シグネチャに含めることで、エージェントの実行中にツールが呼び出されると、ADKは**自動的に****ToolContext**クラスの**インスタンスを提供**します。

**ToolContext**は、いくつかの重要な情報と制御レバーへのアクセスを提供します。

*   `state: State`: 現在のセッションの状態を読み書きします。ここで行われた変更は追跡され、永続化されます。

*   `actions: EventActions`: ツール実行後のエージェントの後続アクションに影響を与えます（例: 要約のスキップ、別のエージェントへの移譲）。

*   `function_call_id: str`: この特定のツール呼び出しに対してフレームワークによって割り当てられた一意の識別子。認証応答との追跡や相関に役立ちます。これは、単一のモデル応答内で複数のツールが呼び出される場合にも役立ちます。

*   `function_call_event_id: str`: この属性は、現在のツール呼び出しをトリガーした**イベント**の一意の識別子を提供します。これは、追跡やロギングの目的で役立ちます。

*   `auth_response: Any`: このツール呼び出しの前に認証フローが完了した場合の認証応答/資格情報を含みます。

*   サービスへのアクセス: ArtifactsやMemoryなどの設定済みサービスと対話するためのメソッド。

ツール関数のdocstringに`tool_context`パラメータを含めるべきではないことに注意してください。`ToolContext`は、LLMがツール関数を呼び出すことを決定した*後*にADKフレームワークによって自動的に注入されるため、LLMの意思決定には関係なく、含めるとLLMを混乱させる可能性があります。

### **状態管理**

`tool_context.state`属性は、現在のセッションに関連付けられた状態への直接的な読み書きアクセスを提供します。これは辞書のように動作しますが、すべての変更が差分として追跡され、セッションサービスによって永続化されることを保証します。これにより、ツールは異なる対話やエージェントのステップ間で情報を維持および共有できます。

*   **状態の読み取り**: 標準的な辞書アクセス (`tool_context.state['my_key']`) または `.get()` メソッド (`tool_context.state.get('my_key', default_value)`) を使用します。

*   **状態への書き込み**: 値を直接割り当てます (`tool_context.state['new_key'] = 'new_value'`)。これらの変更は、結果として得られるイベントの`state_delta`に記録されます。

*   **状態プレフィックス**: 標準の状態プレフィックスを覚えておいてください。

    *   `app:*`: アプリケーションのすべてのユーザーで共有されます。

    *   `user:*`: 現在のユーザーに固有で、すべてのセッションで共有されます。

    *   (プレフィックスなし): 現在のセッションに固有です。

    *   `temp:*`: 一時的で、呼び出し間で永続化されません（単一の`run`呼び出し内でデータを渡すのに役立ちますが、LLM呼び出し間で動作するツールコンテキスト内では一般的にあまり有用ではありません）。

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/user_preference.py"
    ```

=== "Java"

    ```java
    import com.google.adk.tools.FunctionTool;
    import com.google.adk.tools.ToolContext;

    // ユーザー固有のテーマ設定を更新します。
    public Map<String, String> updateUserThemePreference(String value, ToolContext toolContext) {
      String userPrefsKey = "user:preferences:theme";
  
      // 現在の設定を取得、なければ初期化
      String preference = toolContext.state().getOrDefault(userPrefsKey, "").toString();
      if (preference.isEmpty()) {
        preference = value;
      }
  
      // 更新された辞書を状態に書き戻す
      toolContext.state().put("user:preferences", preference);
      System.out.printf("ツール: ユーザー設定 %s を %s に更新しました", userPrefsKey, preference);
  
      return Map.of("status", "success", "updated_preference", toolContext.state().get(userPrefsKey).toString());
      // LLMがupdateUserThemePreference("dark")を呼び出すと:
      // toolContext.stateが更新され、その変更は結果として得られる
      // ツール応答イベントのactions.stateDeltaの一部となります。
    }
    ```

### **エージェントフローの制御**

`tool_context.actions`属性（Javaでは`ToolContext.actions()`）は、**EventActions**オブジェクトを保持します。このオブジェクトの属性を変更することで、ツールは実行完了後のエージェントやフレームワークの動作に影響を与えることができます。

*   **`skip_summarization: bool`**: (デフォルト: `False`) `True`に設定すると、通常ツールの出力を要約するLLM呼び出しをバイパスするようにADKに指示します。これは、ツールの戻り値がすでにユーザー向けのメッセージである場合に便利です。

*   **`transfer_to_agent: str`**: これを別のエージェントの名前に設定します。フレームワークは現在のエージェントの実行を停止し、**会話の制御を指定されたエージェントに移譲**します。これにより、ツールは動的により専門的なエージェントにタスクを引き渡すことができます。

*   **`escalate: bool`**: (デフォルト: `False`) これを`True`に設定すると、現在のエージェントがリクエストを処理できず、制御を親エージェントに（階層内にある場合）渡すべきであることを示します。`LoopAgent`では、サブエージェントのツールで**`escalate=True`**を設定するとループが終了します。

#### 例

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/customer_support_agent.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CustomerSupportAgentApp.java:full_code"
    ```

##### 解説

*   `main_agent`と`support_agent`の2つのエージェントを定義します。`main_agent`は最初の接点となるように設計されています。
*   `check_and_transfer`ツールは、`main_agent`によって呼び出されると、ユーザーのクエリを調べます。
*   クエリに "urgent" という単語が含まれている場合、ツールは`tool_context`、具体的には**`tool_context.actions`**にアクセスし、`transfer_to_agent`属性を`support_agent`に設定します。
*   このアクションは、フレームワークに対して**会話の制御を`support_agent`という名前のエージェントに移譲する**よう指示します。
*   `main_agent`が緊急のクエリを処理すると、`check_and_transfer`ツールが移譲をトリガーします。その後の応答は、理想的には`support_agent`から来ることになります。
*   緊急性のない通常のクエリの場合、ツールは移譲をトリガーせずに単に処理します。

この例は、ツールが`ToolContext`内の`EventActions`を通じて、別の専門エージェントに制御を移譲することによって、会話の流れに動的に影響を与える方法を示しています。

### **認証**

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="この機能は現在Pythonで利用可能です。Javaのサポートは計画中/近日公開予定です。" }

ToolContextは、認証が必要なAPIと対話するツールにメカニズムを提供します。ツールが認証を処理する必要がある場合、以下を使用することがあります。

*   **`auth_response`**: ツールが呼び出される前にフレームワークによって認証がすでに処理されていた場合（`RestApiTool`やOpenAPIのセキュリティスキームで一般的）の資格情報（例: トークン）を含みます。

*   **`request_credential(auth_config: dict)`**: ツールが認証が必要であると判断したが、資格情報が利用できない場合にこのメソッドを呼び出します。これは、提供された`auth_config`に基づいて認証フローを開始するようフレームワークに指示します。

*   **`get_auth_response()`**: 後続の呼び出しで（`request_credential`が正常に処理された後）、ユーザーが提供した資格情報を取得するためにこのメソッドを呼び出します。

認証フロー、設定、および例の詳細な説明については、専用のツール認証ドキュメントページを参照してください。

### **コンテキストを意識したデータアクセス方法**

これらのメソッドは、ツールが設定済みのサービスによって管理される、セッションやユーザーに関連付けられた永続的なデータと対話するための便利な方法を提供します。

*   **`list_artifacts()`** (またはJavaでは **`listArtifacts()`**): `artifact_service`を介して現在セッションに保存されているすべてのアーティファクトのファイル名（またはキー）のリストを返します。アーティファクトは通常、ユーザーによってアップロードされたり、ツール/エージェントによって生成されたりするファイル（画像、ドキュメントなど）です。

*   **`load_artifact(filename: str)`**: **`artifact_service`**からファイル名で特定のアーティファクトを取得します。オプションでバージョンを指定できます。省略した場合は最新バージョンが返されます。アーティファクトデータとMIMEタイプを含む`google.genai.types.Part`オブジェクトを返します。見つからない場合は`None`を返します。

*   **`save_artifact(filename: str, artifact: types.Part)`**: アーティファクトの新しいバージョンを`artifact_service`に保存します。新しいバージョン番号（0から始まる）を返します。

*   **`search_memory(query: str)`** ![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="この機能は現在Pythonで利用可能です。Javaのサポートは計画中/近日公開予定です。" }

       設定された`memory_service`を使用してユーザーの長期記憶をクエリします。これは、過去の対話や保存された知識から関連情報を取得するのに役立ちます。**SearchMemoryResponse**の構造は特定のメモリサービスの実装に依存しますが、通常は関連するテキストのスニペットや会話の抜粋を含みます。

#### 例

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/doc_analysis.py"
    ```

=== "Java"

    ```java
    // メモリからのコンテキストを使用してドキュメントを分析します。
    // Callback ContextやLoadArtifactsツールを使用して、アーティファクトを一覧表示、読み込み、保存することもできます。
    public static @NonNull Maybe<ImmutableMap<String, Object>> processDocument(
        @Annotations.Schema(description = "分析するドキュメントの名前。") String documentName,
        @Annotations.Schema(description = "分析のためのクエリ。") String analysisQuery,
        ToolContext toolContext) {
  
      // 1. 利用可能なすべてのアーティファクトを一覧表示
      System.out.printf(
          "利用可能なすべてのアーティファクトを一覧表示: %s:", toolContext.listArtifacts().blockingGet());
  
      // 2. アーティファクトをメモリに読み込む
      System.out.println("ツール: アーティファクトの読み込み試行: " + documentName);
      Part documentPart = toolContext.loadArtifact(documentName, Optional.empty()).blockingGet();
      if (documentPart == null) {
        System.out.println("ツール: ドキュメント '" + documentName + "' が見つかりません。");
        return Maybe.just(
            ImmutableMap.<String, Object>of(
                "status", "error", "message", "ドキュメント '" + documentName + "' が見つかりません。"));
      }
      String documentText = documentPart.text().orElse("");
      System.out.println(
          "ツール: ドキュメント '" + documentName + "' (" + documentText.length() + " 文字) を読み込みました。");
  
      // 3. 分析の実行（プレースホルダー）
      String analysisResult =
          "'"
              + documentName
              + "' の '"
              + analysisQuery
              + "' に関する分析 [プレースホルダー分析結果]";
      System.out.println("ツール: 分析を実行しました。");
  
      // 4. 分析結果を新しいアーティファクトとして保存
      Part analysisPart = Part.fromText(analysisResult);
      String newArtifactName = "analysis_" + documentName;
  
      toolContext.saveArtifact(newArtifactName, analysisPart);
  
      return Maybe.just(
          ImmutableMap.<String, Object>builder()
              .put("status", "success")
              .put("analysis_artifact", newArtifactName)
              .build());
    }
    // FunctionTool processDocumentTool =
    //      FunctionTool.create(ToolContextArtifactExample.class, "processDocument");
    // エージェントに、この関数ツールを含めます。
    // LlmAgent agent = LlmAgent().builder().tools(processDocumentTool).build();
    ```

**ToolContext**を活用することで、開発者はADKのアーキテクチャとシームレスに統合し、エージェント全体の能力を向上させる、より洗練されたコンテキスト対応のカスタムツールを作成できます。

## 効果的なツール関数の定義

メソッドや関数をADKツールとして使用する場合、その定義方法がエージェントの正しい使用能力に大きく影響します。エージェントの大規模言語モデル（LLM）は、関数の**名前**、**パラメータ（引数）**、**型ヒント**、そして**docstring** / **ソースコードコメント**に大きく依存して、その目的を理解し、正しい呼び出しを生成します。

効果的なツール関数を定義するための主要なガイドラインは次のとおりです。

*   **関数名:**
    *   アクションを明確に示す、動詞-名詞ベースの記述的な名前を使用します（例: `get_weather`、`searchDocuments`、`schedule_meeting`）。
    *   `run`、`process`、`handle_data`のような一般的な名前や、`doStuff`のような過度に曖昧な名前は避けてください。良い説明があっても、`do_stuff`のような名前は、例えば`cancelFlight`といつ使い分けるべきかモデルを混乱させる可能性があります。
    *   LLMは、ツール選択時に主要な識別子として関数名を使用します。

*   **パラメータ（引数）:**
    *   関数は任意の数のパラメータを持つことができます。
    *   明確で記述的な名前を使用します（例: `c`ではなく`city`、`q`ではなく`search_query`）。
    *   **Pythonではすべてのパラメータに型ヒントを提供します**（例: `city: str`、`user_id: int`、`items: list[str]`）。これは、ADKがLLMのために正しいスキーマを生成するために不可欠です。
    *   すべてのパラメータ型が**JSONシリアライズ可能**であることを確認してください。`str`、`int`、`float`、`bool`、`list`、`dict`のような標準的なPython型とその組み合わせは一般的に安全です。複雑なカスタムクラスインスタンスは、明確なJSON表現がない限り、直接のパラメータとして避けてください。
    *   パラメータに**デフォルト値を設定しないでください**。例: `def my_func(param1: str = "default")`。デフォルト値は、関数呼び出し生成時に基盤となるモデルによって確実にサポートまたは使用されるわけではありません。すべての必要な情報は、LLMがコンテキストから導き出すか、不足している場合は明示的に要求する必要があります。
    *   **`self` / `cls`は自動的に処理されます:** `self`（インスタンスメソッド用）や`cls`（クラスメソッド用）のような暗黙のパラメータは、ADKによって自動的に処理され、LLMに示されるスキーマから除外されます。ツールがLLMに提供を要求する論理的なパラメータに対してのみ、型ヒントと説明を定義する必要があります。

*   **戻り値の型:**
    *   関数の戻り値は、Pythonでは**辞書（`dict`）**、Javaでは**Map**で**なければなりません**。
    *   関数が辞書以外の型（例: 文字列、数値、リスト）を返す場合、ADKフレームワークは結果をモデルに返す前に、自動的に`{'result': your_original_return_value}`のような辞書/Mapにラップします。
    *   辞書/Mapのキーと値を、***LLMが*簡単に理解できるように記述的に**設計してください。モデルが次のステップを決定するためにこの出力を読むことを忘れないでください。
    *   意味のあるキーを含めてください。例えば、`500`のようなエラーコードだけを返すのではなく、`{'status': 'error', 'error_message': 'Database connection failed'}`のように返します。
    *   モデルに対してツール実行の結果を明確に示すために、`status`キー（例: `'success'`、`'error'`、`'pending'`、`'ambiguous'`）を含めることは**強く推奨される実践**です。

*   **Docstring / ソースコードコメント:**
    *   **これは非常に重要です。** docstringは、LLMにとっての主要な説明情報源です。
    *   **ツールが*何をするか*を明確に記述してください。** その目的と制限について具体的に説明してください。
    *   **ツールを*いつ*使用すべきかを説明してください。** LLMの意思決定を導くためのコンテキストや使用例を提供してください。
    *   ***各パラメータ*を明確に説明してください。** LLMがその引数にどのような情報を提供する必要があるかを説明してください。
    *   期待される`dict`の戻り値の**構造と意味**、特に異なる`status`の値と関連するデータキーについて説明してください。
    *   **注入されるToolContextパラメータは記述しないでください**。オプションの`tool_context: ToolContext`パラメータは、LLMが知る必要のあるパラメータではないため、docstringの説明内では言及を避けてください。`ToolContext`は、LLMがそれを呼び出すことを決定した*後*にADKによって注入されます。

    **良い定義の例:**

=== "Python"
    
    ```python
    def lookup_order_status(order_id: str) -> dict:
      """IDを使用して顧客の注文の現在のステータスを取得します。

      ユーザーが特定の注文のステータスを明示的に尋ね、注文IDを
      提供した場合にのみ、このツールを使用してください。一般的な問い合わせには
      使用しないでください。

      Args:
          order_id: 検索する注文の一意の識別子。

      Returns:
          注文ステータスを含む辞書。
          考えられるステータス: 'shipped', 'processing', 'pending', 'error'。
          成功例: {'status': 'shipped', 'tracking_number': '1Z9...'}
          エラー例: {'status': 'error', 'error_message': '注文IDが見つかりません。'}
      """
      # ... ステータスを取得する関数の実装 ...
      if status := fetch_status_from_backend(order_id):
           return {"status": status.state, "tracking_number": status.tracking} # 構造の例
      else:
           return {"status": "error", "error_message": f"注文ID {order_id} が見つかりません。"}

    ```

=== "Java"

    ```java
    /**
     * 指定された都市の現在の天気予報を取得します。
     *
     * @param city 天気予報を取得する都市。
     * @param toolContext ツールのコンテキスト。
     * @return 天気情報を含む辞書。
     */
    public static Map<String, Object> getWeatherReport(String city, ToolContext toolContext) {
        Map<String, Object> response = new HashMap<>();
        if (city.toLowerCase(Locale.ROOT).equals("london")) {
            response.put("status", "success");
            response.put(
                    "report",
                    "ロンドンの現在の天気は曇りで、気温は18度、雨の可能性があります。");
        } else if (city.toLowerCase(Locale.ROOT).equals("paris")) {
            response.put("status", "success");
            response.put("report", "パリの天気は晴れで、気温は25度です。");
        } else {
            response.put("status", "error");
            response.put("error_message", String.format("'%s'の天気情報は利用できません。", city));
        }
        return response;
    }
    ```

*   **単純さと焦点:**
    *   **ツールは焦点を絞る:** 各ツールは、理想的には1つの明確に定義されたタスクを実行すべきです。
    *   **パラメータは少ない方が良い:** モデルは一般的に、多くのオプションや複雑なパラメータを持つツールよりも、少数の明確に定義されたパラメータを持つツールをより確実に扱います。
    *   **単純なデータ型を使用する:** 可能な限り、パラメータとして複雑なカスタムクラスや深くネストされた構造よりも、基本的な型（Pythonでは`str`, `int`, `bool`, `float`, `List[str]`、Javaでは`int`, `byte`, `short`, `long`, `float`, `double`, `boolean`, `char`）を優先してください。
    *   **複雑なタスクを分解する:** 複数の異なる論理ステップを実行する関数を、より小さく、より焦点の合ったツールに分割します。例えば、単一の`update_user_profile(profile: ProfileObject)`ツールの代わりに、`update_user_name(name: str)`、`update_user_address(address: str)`、`update_user_preferences(preferences: list[str])`などの個別のツールを検討してください。これにより、LLMが正しい能力を選択して使用することが容易になります。

これらのガイドラインに従うことで、LLMがカスタム関数ツールを効果的に活用するために必要な明確さと構造を提供し、より有能で信頼性の高いエージェントの振る舞いにつながります。

## ツールセット: ツールのグループ化と動的な提供 ![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="この機能は現在Pythonで利用可能です。Javaのサポートは計画中/近日公開予定です。" }

個々のツールを超えて、ADKは`BaseToolset`インターフェース（`google.adk.tools.base_toolset`で定義）を介して**ツールセット**の概念を導入します。ツールセットを使用すると、`BaseTool`インスタンスのコレクションを、多くの場合動的に、エージェントに管理および提供できます。

このアプローチは、次のような場合に有益です。

*   **関連ツールの整理:** 共通の目的を果たすツールをグループ化します（例: 数学演算のためのすべてのツール、または特定のAPIと対話するすべてのツール）。
*   **動的なツールの可用性:** エージェントが現在のコンテキスト（例: ユーザーの権限、セッションの状態、またはその他の実行時条件）に基づいて異なるツールを利用できるようにします。ツールセットの`get_tools`メソッドは、どのツールを公開するかを決定できます。
*   **外部ツールプロバイダーの統合:** ツールセットは、OpenAPI仕様やMCPサーバーのような外部システムからのツールのアダプターとして機能し、それらをADK互換の`BaseTool`オブジェクトに変換できます。

### `BaseToolset`インターフェース

ADKでツールセットとして機能するクラスは、`BaseToolset`抽象基底クラスを実装する必要があります。このインターフェースは主に2つのメソッドを定義します。

*   **`async def get_tools(...) -> list[BaseTool]:`**
    これはツールセットのコアメソッドです。ADKエージェントが利用可能なツールを知る必要がある場合、その`tools`リストで提供される各`BaseToolset`インスタンスに対して`get_tools()`を呼び出します。
    *   オプションの`readonly_context`（`ReadonlyContext`のインスタンス）を受け取ります。このコンテキストは、現在のセッション状態（`readonly_context.state`）、エージェント名、呼び出しIDなどの情報への読み取り専用アクセスを提供します。ツールセットはこのコンテキストを使用して、どのツールを返すかを動的に決定できます。
    *   `BaseTool`インスタンスの`list`を**返さなければなりません**（例: `FunctionTool`、`RestApiTool`）。

*   **`async def close(self) -> None:`**
    この非同期メソッドは、ツールセットが不要になったとき、例えばエージェントサーバーがシャットダウンするときや`Runner`が閉じられるときに、ADKフレームワークによって呼び出されます。ネットワーク接続のクローズ、ファイルハンドルの解放、またはツールセットによって管理される他のリソースのクリーンアップなど、必要なクリーンアップ処理を実行するためにこのメソッドを実装します。

### エージェントでのツールセットの使用

`LlmAgent`の`tools`リストに、個々の`BaseTool`インスタンスと並べて、`BaseToolset`実装のインスタンスを直接含めることができます。

エージェントが初期化されるとき、または利用可能な能力を決定する必要があるとき、ADKフレームワークは`tools`リストを反復処理します。

*   アイテムが`BaseTool`インスタンスの場合、直接使用されます。
*   アイテムが`BaseToolset`インスタンスの場合、その`get_tools()`メソッドが（現在の`ReadonlyContext`で）呼び出され、返された`BaseTool`のリストがエージェントの利用可能なツールに追加されます。

### 例: 簡単な数学ツールセット

簡単な算術演算を提供するツールセットの基本的な例を作成しましょう。

```py
--8<-- "examples/python/snippets/tools/overview/toolset_example.py:init"
```

この例では:

*   `SimpleMathToolset`は`BaseToolset`を実装し、その`get_tools()`メソッドは`add_numbers`と`subtract_numbers`のための`FunctionTool`インスタンスを返します。また、プレフィックスを使用してそれらの名前をカスタマイズします。
*   `calculator_agent`は、個々の`greet_tool`と`SimpleMathToolset`のインスタンスの両方で構成されています。
*   `calculator_agent`が実行されると、ADKは`math_toolset_instance.get_tools()`を呼び出します。エージェントのLLMは、ユーザーのリクエストを処理するために`greet_user`、`calculator_add_numbers`、および`calculator_subtract_numbers`にアクセスできるようになります。
*   `add_numbers`ツールは`tool_context.state`への書き込みを示し、エージェントの指示ではこの状態の読み取りについて言及しています。
*   `close()`メソッドが呼び出され、ツールセットが保持するリソースが確実に解放されます。

ツールセットは、ADKエージェントにツールのコレクションを整理、管理、動的に提供する強力な方法を提供し、よりモジュール化され、保守可能で、適応性のあるエージェントアプリケーションにつながります。