# イベント

イベントは、Agent Development Kit (ADK) 内における情報フローの基本単位です。これらは、最初のユーザー入力から最終的な応答、そしてその間のすべてのステップに至るまで、エージェントの対話ライフサイクル中に発生するすべての重要な出来事を表します。イベントを理解することは、コンポーネントが通信し、状態が管理され、制御フローが指示される主要な方法であるため、非常に重要です。

## イベントとは何か、なぜ重要か

ADKにおける`Event`は、エージェントの実行における特定の時点を表すイミュータブル（不変）な記録です。ユーザーメッセージ、エージェントの返信、ツール使用のリクエスト（関数呼び出し）、ツールの結果、状態の変更、制御シグナル、およびエラーをキャプチャします。

=== "Python"
    技術的には、これは`google.adk.events.Event`クラスのインスタンスであり、基本的な`LlmResponse`構造を基に、ADK固有の重要なメタデータと`actions`ペイロードを追加して構築されています。

    ```python
    # イベントの概念的な構造 (Python)
    # from google.adk.events import Event, EventActions
    # from google.genai import types

    # class Event(LlmResponse): # 簡略化されたビュー
    #     # --- LlmResponse のフィールド ---
    #     content: Optional[types.Content]
    #     partial: Optional[bool]
    #     # ... 他の応答フィールド ...

    #     # --- ADK固有の追加要素 ---
    #     author: str          # 'user' またはエージェント名
    #     invocation_id: str   # 対話全体の実行ID
    #     id: str              # この特定のイベントの一意なID
    #     timestamp: float     # 作成時刻
    #     actions: EventActions # 副作用と制御に重要
    #     branch: Optional[str] # 階層パス
    #     # ...
    ```

=== "Java"
    Javaでは、これは`com.google.adk.events.Event`クラスのインスタンスです。これもまた、基本的な応答構造を基に、ADK固有の重要なメタデータと`actions`ペイロードを追加して構築されています。

    ```java
    // イベントの概念的な構造 (Java - com.google.adk.events.Event.java を参照)
    // 提供された com.google.adk.events.Event.java に基づく簡略化されたビュー
    // public class Event extends JsonBaseModel {
    //     // --- LlmResponse に類似したフィールド ---
    //     private Optional<Content> content;
    //     private Optional<Boolean> partial;
    //     // ... errorCode, errorMessage などの他の応答フィールド ...

    //     // --- ADK固有の追加要素 ---
    //     private String author;         // 'user' またはエージェント名
    //     private String invocationId;   // 対話全体の実行ID
    //     private String id;             // この特定のイベントの一意なID
    //     private long timestamp;        // 作成時刻 (エポックミリ秒)
    //     private EventActions actions;  // 副作用と制御に重要
    //     private Optional<String> branch; // 階層パス
    //     // ... turnComplete, longRunningToolIds などの他のフィールド ...
    // }
    ```

イベントは、いくつかの重要な理由からADKの運用において中心的な役割を果たします：

1.  **通信：** ユーザーインターフェース、`Runner`、エージェント、LLM、ツール間の標準的なメッセージ形式として機能します。すべてが`Event`として流れます。

2.  **状態とアーティファクトの変更のシグナリング：** イベントは状態変更の指示を運び、アーティファクトの更新を追跡します。`SessionService`はこれらのシグナルを使用して永続性を確保します。Pythonでは、変更は`event.actions.state_delta`と`event.actions.artifact_delta`を介して通知されます。

3.  **制御フロー：** `event.actions.transfer_to_agent`や`event.actions.escalate`のような特定のフィールドは、フレームワークを指示するシグナルとして機能し、次にどのエージェントが実行されるか、またはループを終了すべきかを決定します。

4.  **履歴と可観測性：** `session.events`に記録されたイベントのシーケンスは、対話の完全で時系列的な履歴を提供し、デバッグ、監査、およびエージェントの振る舞いをステップバイステップで理解するために非常に価値があります。

本質的に、ユーザーのクエリからエージェントの最終的な回答までの全プロセスは、`Event`オブジェクトの生成、解釈、および処理を通じて調整されます。


## イベントの理解と使用

開発者として、あなたは主に`Runner`から生成（yield）されるイベントのストリームと対話します。それらを理解し、情報を抽出する方法は次のとおりです：

!!! Note
    プリミティブの具体的なパラメータやメソッド名は、SDKの言語によって若干異なる場合があります（例：Pythonでは`event.content()`、Javaでは`event.content().get().parts()`）。詳細は各言語のAPIドキュメントを参照してください。

### イベントの出所と種類の特定

イベントが何を表しているかを素早く判断するには、以下を確認します：

*   **誰が送信したか？ (`event.author`)**
    *   `'user'`: エンドユーザーからの直接の入力を示します。
    *   `'AgentName'`: 特定のエージェント（例：`'WeatherAgent'`、`'SummarizerAgent'`）からの出力またはアクションを示します。
*   **主なペイロードは何か？ (`event.content`および`event.content.parts`)**
    *   **テキスト：** 会話メッセージを示します。Pythonでは`event.content.parts[0].text`が存在するかどうかを確認します。Javaでは`event.content()`が存在し、その`parts()`が存在して空でなく、最初のパートの`text()`が存在するかどうかを確認します。
    *   **ツール呼び出しリクエスト：** `event.get_function_calls()`をチェックします。空でなければ、LLMが1つ以上のツールの実行を要求しています。リストの各項目には`.name`と`.args`があります。
    *   **ツールの結果：** `event.get_function_responses()`をチェックします。空でなければ、このイベントはツール実行の結果を運んでいます。各項目には`.name`と`.response`（ツールが返した辞書）があります。*注意：* 履歴の構造上、`content`内の`role`はしばしば`'user'`ですが、イベントの`author`は通常、ツール呼び出しを要求したエージェントです。

*   **ストリーミング出力か？ (`event.partial`)**
    これがLLMからの一部不完全なテキストのチャンクであるかどうかを示します。
    *   `True`: さらにテキストが続きます。
    *   `False`または`None`/`Optional.empty()`: このコンテンツの部分は完了しています（ただし、`turn_complete`もfalseの場合、全体的なターンは終了していない可能性があります）。

=== "Python"
    ```python
    # 疑似コード：基本的なイベントの識別 (Python)
    # async for event in runner.run_async(...):
    #     print(f"イベントの送信元: {event.author}")
    #
    #     if event.content and event.content.parts:
    #         if event.get_function_calls():
    #             print("  タイプ: ツール呼び出しリクエスト")
    #         elif event.get_function_responses():
    #             print("  タイプ: ツールの結果")
    #         elif event.content.parts.text:
    #             if event.partial:
    #                 print("  タイプ: ストリーミングテキストチャンク")
    #             else:
    #                 print("  タイプ: 完全なテキストメッセージ")
    #         else:
    #             print("  タイプ: その他のコンテンツ (例: コード結果)")
    #     elif event.actions and (event.actions.state_delta or event.actions.artifact_delta):
    #         print("  タイプ: 状態/アーティファクト更新")
    #     else:
    #         print("  タイプ: 制御シグナルまたはその他")
    ```

=== "Java"
    ```java
    // 疑似コード：基本的なイベントの識別 (Java)
    // import com.google.genai.types.Content;
    // import com.google.adk.events.Event;
    // import com.google.adk.events.EventActions;

    // runner.runAsync(...).forEach(event -> { // 同期ストリームまたはリアクティブストリームを想定
    //     System.out.println("イベントの送信元: " + event.author());
    //
    //     if (event.content().isPresent()) {
    //         Content content = event.content().get();
    //         if (!event.functionCalls().isEmpty()) {
    //             System.out.println("  タイプ: ツール呼び出しリクエスト");
    //         } else if (!event.functionResponses().isEmpty()) {
    //             System.out.println("  タイプ: ツールの結果");
    //         } else if (content.parts().isPresent() && !content.parts().get().isEmpty() &&
    //                    content.parts().get().get(0).text().isPresent()) {
    //             if (event.partial().orElse(false)) {
    //                 System.out.println("  タイプ: ストリーミングテキストチャンク");
    //             } else {
    //                 System.out.println("  タイプ: 完全なテキストメッセージ");
    //             }
    //         } else {
    //             System.out.println("  タイプ: その他のコンテンツ (例: コード結果)");
    //         }
    //     } else if (event.actions() != null &&
    //                ((event.actions().stateDelta() != null && !event.actions().stateDelta().isEmpty()) ||
    //                 (event.actions().artifactDelta() != null && !event.actions().artifactDelta().isEmpty()))) {
    //         System.out.println("  タイプ: 状態/アーティファクト更新");
    //     } else {
    //         System.out.println("  タイプ: 制御シグナルまたはその他");
    //     }
    // });
    ```

### 主要な情報の抽出

イベントの種類がわかったら、関連データにアクセスします：

*   **テキストコンテンツ：**
    テキストにアクセスする前に、常にコンテンツとパートの存在を確認してください。Pythonでは `text = event.content.parts[0].text` です。

*   **関数呼び出しの詳細：**
    
    === "Python"
        ```python
        calls = event.get_function_calls()
        if calls:
            for call in calls:
                tool_name = call.name
                arguments = call.args # これは通常辞書です
                print(f"  ツール: {tool_name}, 引数: {arguments}")
                # アプリケーションはこれに基づいて実行をディスパッチするかもしれません
        ```
    === "Java"

        ```java
        import com.google.genai.types.FunctionCall;
        import com.google.common.collect.ImmutableList;
        import java.util.Map;
    
        ImmutableList<FunctionCall> calls = event.functionCalls(); // Event.java から
        if (!calls.isEmpty()) {
          for (FunctionCall call : calls) {
            String toolName = call.name().get();
            // args は Optional<Map<String, Object>> です
            Map<String, Object> arguments = call.args().get();
                   System.out.println("  ツール: " + toolName + ", 引数: " + arguments);
            // アプリケーションはこれに基づいて実行をディスパッチするかもしれません
          }
        }
        ```

*   **関数応答の詳細：**
    
    === "Python"
        ```python
        responses = event.get_function_responses()
        if responses:
            for response in responses:
                tool_name = response.name
                result_dict = response.response # ツールが返した辞書
                print(f"  ツールの結果: {tool_name} -> {result_dict}")
        ```
    === "Java"

        ```java
        import com.google.genai.types.FunctionResponse;
        import com.google.common.collect.ImmutableList;
        import java.util.Map; 

        ImmutableList<FunctionResponse> responses = event.functionResponses(); // Event.java から
        if (!responses.isEmpty()) {
            for (FunctionResponse response : responses) {
                String toolName = response.name().get();
                Map<String, Object> result = response.response().get(); // responseを取得する前に確認
                System.out.println("  ツールの結果: " + toolName + " -> " + result);
            }
        }
        ```

*   **識別子：**
    *   `event.id`: この特定のイベントインスタンスの一意なID。
    *   `event.invocation_id`: このイベントが属する、ユーザーリクエストから最終応答までの一連のサイクル全体のID。ロギングやトレースに役立ちます。

### アクションと副作用の検出

`event.actions`オブジェクトは、発生した、または発生すべき変更を通知します。アクセスする前に、常に`event.actions`とそのフィールド/メソッドが存在するかどうかを確認してください。

*   **状態の変更：** このイベントを生成したステップ中にセッション状態で変更されたキーと値のペアのコレクションを提供します。
    
    === "Python"
        `delta = event.actions.state_delta` (`{key: value}`ペアの辞書)。
        ```python
        if event.actions and event.actions.state_delta:
            print(f"  状態の変更: {event.actions.state_delta}")
            # 必要に応じてローカルUIやアプリケーションの状態を更新する
        ```
    === "Java"
        `ConcurrentMap<String, Object> delta = event.actions().stateDelta();`

        ```java
        import java.util.concurrent.ConcurrentMap;
        import com.google.adk.events.EventActions;

        EventActions actions = event.actions(); // event.actions()がnullでないと仮定
        if (actions != null && actions.stateDelta() != null && !actions.stateDelta().isEmpty()) {
            ConcurrentMap<String, Object> stateChanges = actions.stateDelta();
            System.out.println("  状態の変更: " + stateChanges);
            // 必要に応じてローカルUIやアプリケーションの状態を更新する
        }
        ```

*   **アーティファクトの保存：** どのアーティファクトが保存され、その新しいバージョン番号（または関連する`Part`情報）が何かを示すコレクションを提供します。
    
    === "Python"
        `artifact_changes = event.actions.artifact_delta` (`{filename: version}`の辞書)。
        ```python
        if event.actions and event.actions.artifact_delta:
            print(f"  保存されたアーティファクト: {event.actions.artifact_delta}")
            # UIがアーティファクトリストを更新するかもしれない
        ```
    === "Java"
        `ConcurrentMap<String, Part> artifactChanges = event.actions().artifactDelta();`
        
        ```java
        import java.util.concurrent.ConcurrentMap;
        import com.google.genai.types.Part;
        import com.google.adk.events.EventActions;

        EventActions actions = event.actions(); // event.actions()がnullでないと仮定
        if (actions != null && actions.artifactDelta() != null && !actions.artifactDelta().isEmpty()) {
            ConcurrentMap<String, Part> artifactChanges = actions.artifactDelta();
            System.out.println("  保存されたアーティファクト: " + artifactChanges);
            // UIがアーティファクトリストを更新するかもしれない
            // artifactChanges.entrySet()をループしてファイル名とPartの詳細を取得する
        }
        ```

*   **制御フローシグナル：** ブール値のフラグまたは文字列の値をチェックします：
    
    === "Python"
        *   `event.actions.transfer_to_agent` (string): 制御が指定されたエージェントに渡されるべきです。
        *   `event.actions.escalate` (bool): ループが終了すべきです。
        *   `event.actions.skip_summarization` (bool): ツールの結果がLLMによって要約されるべきではありません。
        ```python
        if event.actions:
            if event.actions.transfer_to_agent:
                print(f"  シグナル: {event.actions.transfer_to_agent}へ転送")
            if event.actions.escalate:
                print("  シグナル: エスカレーション（ループ終了）")
            if event.actions.skip_summarization:
                print("  シグナル: ツール結果の要約をスキップ")
        ```
    === "Java"
        *   `event.actions().transferToAgent()` (`Optional<String>`を返す): 制御が指定されたエージェントに渡されるべきです。
        *   `event.actions().escalate()` (`Optional<Boolean>`を返す): ループが終了すべきです。
        *   `event.actions().skipSummarization()` (`Optional<Boolean>`を返す): ツールの結果がLLMによって要約されるべきではありません。

        ```java
        import com.google.adk.events.EventActions;
        import java.util.Optional;

        EventActions actions = event.actions(); // event.actions()がnullでないと仮定
        if (actions != null) {
            Optional<String> transferAgent = actions.transferToAgent();
            if (transferAgent.isPresent()) {
                System.out.println("  シグナル: " + transferAgent.get() + "へ転送");
            }

            Optional<Boolean> escalate = actions.escalate();
            if (escalate.orElse(false)) { // または escalate.isPresent() && escalate.get()
                System.out.println("  シグナル: エスカレーション（ループ終了）");
            }

            Optional<Boolean> skipSummarization = actions.skipSummarization();
            if (skipSummarization.orElse(false)) { // または skipSummarization.isPresent() && skipSummarization.get()
                System.out.println("  シグナル: ツール結果の要約をスキップ");
            }
        }
        ```

### イベントが「最終」応答かどうかの判定

`event.is_final_response()`という組み込みのヘルパーメソッドを使用して、ターンのエージェントの完全な出力として表示するのに適したイベントを識別します。

*   **目的：** 中間ステップ（ツール呼び出し、部分的なストリーミングテキスト、内部の状態更新など）を、最終的なユーザー向けのメッセージから除外します。
*   **いつ`True`になるか？**
    1.  イベントにツールの結果（`function_response`）が含まれ、`skip_summarization`が`True`である。
    2.  イベントに`is_long_running=True`とマークされたツールのツール呼び出し（`function_call`）が含まれている。Javaでは、`longRunningToolIds`リストが空でないか確認します：
        *   `event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()` が `true` である。
    3.  または、以下の**すべて**が満たされる場合：
        *   関数呼び出しがない（`get_function_calls()`が空）。
        *   関数応答がない（`get_function_responses()`が空）。
        *   部分的なストリームチャンクではない（`partial`が`True`でない）。
        *   さらなる処理/表示が必要な可能性のあるコード実行結果で終わらない。
*   **使用法：** アプリケーションロジックでイベントストリームをフィルタリングします。

    === "Python"
        ```python
        # 疑似コード：アプリケーションでの最終応答の処理 (Python)
        # full_response_text = ""
        # async for event in runner.run_async(...):
        #     # 必要に応じてストリーミングテキストを蓄積...
        #     if event.partial and event.content and event.content.parts and event.content.parts.text:
        #         full_response_text += event.content.parts.text
        #
        #     # 表示可能な最終イベントかどうかを確認
        #     if event.is_final_response():
        #         print("\n--- 最終出力検出 ---")
        #         if event.content and event.content.parts and event.content.parts.text:
        #              # ストリームの最後の部分であれば、蓄積したテキストを使用
        #              final_text = full_response_text + (event.content.parts.text if not event.partial else "")
        #              print(f"ユーザーに表示: {final_text.strip()}")
        #              full_response_text = "" # アキュムレータをリセット
        #         elif event.actions and event.actions.skip_summarization and event.get_function_responses():
        #              # 必要に応じて生のツール結果を表示する処理
        #              response_data = event.get_function_responses().response
        #              print(f"生のツール結果を表示: {response_data}")
        #         elif hasattr(event, 'long_running_tool_ids') and event.long_running_tool_ids:
        #              print("メッセージを表示: ツールはバックグラウンドで実行中です...")
        #         else:
        #              # 該当する場合、他の種類の最終応答を処理
        #              print("表示: 最終的な非テキスト応答またはシグナル。")
        ```
    === "Java"
        ```java
        // 疑似コード：アプリケーションでの最終応答の処理 (Java)
        import com.google.adk.events.Event;
        import com.google.genai.types.Content;
        import com.google.genai.types.FunctionResponse;
        import java.util.Map;

        StringBuilder fullResponseText = new StringBuilder();
        runner.run(...).forEach(event -> { // イベントのストリームを想定
             // 必要に応じてストリーミングテキストを蓄積...
             if (event.partial().orElse(false) && event.content().isPresent()) {
                 event.content().flatMap(Content::parts).ifPresent(parts -> {
                     if (!parts.isEmpty() && parts.get(0).text().isPresent()) {
                         fullResponseText.append(parts.get(0).text().get());
                    }
                 });
             }
        
             // 表示可能な最終イベントかどうかを確認
             if (event.finalResponse()) { // Event.java のメソッドを使用
                 System.out.println("\n--- 最終出力検出 ---");
                 if (event.content().isPresent() &&
                     event.content().flatMap(Content::parts).map(parts -> !parts.isEmpty() && parts.get(0).text().isPresent()).orElse(false)) {
                     // ストリームの最後の部分であれば、蓄積したテキストを使用
                     String eventText = event.content().get().parts().get().get(0).text().get();
                     String finalText = fullResponseText.toString() + (event.partial().orElse(false) ? "" : eventText);
                     System.out.println("ユーザーに表示: " + finalText.trim());
                     fullResponseText.setLength(0); // アキュムレータをリセット
                 } else if (event.actions() != null && event.actions().skipSummarization().orElse(false)
                            && !event.functionResponses().isEmpty()) {
                     // 必要に応じて生のツール結果を表示する処理、
                     // 特に finalResponse() が他の条件で true だった場合や、
                     // finalResponse() に関係なく要約がスキップされた結果を表示したい場合
                     Map<String, Object> responseData = (Map<String, Object>) event.functionResponses().get(0).response().get();
                     System.out.println("生のツール結果を表示: " + responseData);
                 } else if (event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()) {
                     // このケースは event.finalResponse() でカバーされる
                     System.out.println("メッセージを表示: ツールはバックグラウンドで実行中です...");
                 } else {
                     // 該当する場合、他の種類の最終応答を処理
                     System.out.println("表示: 最終的な非テキスト応答またはシグナル。");
                 }
             }
         });
        ```

イベントのこれらの側面を注意深く調べることで、ADKシステムを流れる豊富な情報に適切に反応する堅牢なアプリケーションを構築できます。

## イベントのフロー：生成と処理

イベントは異なる時点で作成され、フレームワークによって体系的に処理されます。このフローを理解することは、アクションと履歴がどのように管理されるかを明確にするのに役立ちます。

*   **生成元：**
    *   **ユーザー入力：** `Runner`は通常、最初のユーザーメッセージや会話の途中の入力を`author='user'`を持つ`Event`にラップします。
    *   **エージェントロジック：** エージェント（`BaseAgent`、`LlmAgent`）は、応答を伝えたりアクションを通知したりするために、明示的に`Event(...)`オブジェクトを`yield`します（`author=self.name`を設定）。
    *   **LLM応答：** ADKのモデル統合レイヤーは、生のLLM出力（テキスト、関数呼び出し、エラー）を、呼び出し元エージェントを作者とする`Event`オブジェクトに変換します。
    *   **ツールの結果：** ツールが実行された後、フレームワークは`function_response`を含む`Event`を生成します。`author`は通常、ツールをリクエストしたエージェントですが、`content`内の`role`はLLMの履歴のために`'user'`に設定されます。


*   **処理フロー：**
    1.  **Yield/Return:** イベントが生成され、そのソースによってyield（Python）またはreturn/emit（Java）されます。
    2.  **Runnerが受信：** エージェントを実行しているメインの`Runner`がイベントを受け取ります。
    3.  **SessionServiceによる処理：** `Runner`はイベントを設定済みの`SessionService`に送信します。これは重要なステップです：
        *   **差分の適用：** サービスは`event.actions.state_delta`を`session.state`にマージし、`event.actions.artifact_delta`に基づいて内部レコードを更新します。（注意：実際のアーティファクトの*保存*は、通常、`context.save_artifact`が呼び出されたときに既に行われています）。
        *   **メタデータの確定：** まだ存在しない場合は一意の`event.id`を割り当て、`event.timestamp`を更新する場合があります。
        *   **履歴への永続化：** 処理されたイベントを`session.events`リストに追加します。
    4.  **外部へのYield：** `Runner`は処理されたイベントを外部の呼び出し元アプリケーション（例：`runner.run_async`を呼び出したコード）にyield（Python）またはreturn/emit（Java）します。

このフローにより、状態の変更と履歴が各イベントの通信内容とともに一貫して記録されることが保証されます。


## 一般的なイベントの例（説明のためのパターン）

ストリームで見られる典型的なイベントの簡潔な例を以下に示します：

*   **ユーザー入力：**
    ```json
    {
      "author": "user",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"text": "来週の火曜日のロンドン行きのフライトを予約して"}]}
      // actions は通常空
    }
    ```
*   **エージェントの最終テキスト応答：** (`is_final_response() == True`)
    ```json
    {
      "author": "TravelAgent",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"text": "はい、承知いたしました。出発都市を確認していただけますか？"}]},
      "partial": false,
      "turn_complete": true
      // actions には state delta などが含まれる可能性がある
    }
    ```
*   **エージェントのストリーミングテキスト応答：** (`is_final_response() == False`)
    ```json
    {
      "author": "SummaryAgent",
      "invocation_id": "e-abc...",
      "content": {"parts": [{"text": "この文書では、主に3つの点について議論しています："}]},
      "partial": true,
      "turn_complete": false
    }
    // ... さらに partial=True のイベントが続く ...
    ```
*   **ツール呼び出しリクエスト（LLMによる）：** (`is_final_response() == False`)
    ```json
    {
      "author": "TravelAgent",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"function_call": {"name": "find_airports", "args": {"city": "London"}}}]}
      // actions は通常空
    }
    ```
*   **ツールの結果提供（LLMへ）：** (`is_final_response()`は`skip_summarization`に依存）
    ```json
    {
      "author": "TravelAgent", // 作者は呼び出しをリクエストしたエージェント
      "invocation_id": "e-xyz...",
      "content": {
        "role": "user", // LLM履歴用のロール
        "parts": [{"function_response": {"name": "find_airports", "response": {"result": ["LHR", "LGW", "STN"]}}}]
      }
      // actions には skip_summarization=True が含まれる可能性がある
    }
    ```
*   **状態/アーティファクトの更新のみ：** (`is_final_response() == False`)
    ```json
    {
      "author": "InternalUpdater",
      "invocation_id": "e-def...",
      "content": null,
      "actions": {
        "state_delta": {"user_status": "verified"},
        "artifact_delta": {"verification_doc.pdf": 2}
      }
    }
    ```
*   **エージェント転送シグナル：** (`is_final_response() == False`)
    ```json
    {
      "author": "OrchestratorAgent",
      "invocation_id": "e-789...",
      "content": {"parts": [{"function_call": {"name": "transfer_to_agent", "args": {"agent_name": "BillingAgent"}}}]},
      "actions": {"transfer_to_agent": "BillingAgent"} // フレームワークによって追加
    }
    ```
*   **ループエスカレーションシグナル：** (`is_final_response() == False`)
    ```json
    {
      "author": "CheckerAgent",
      "invocation_id": "e-loop...",
      "content": {"parts": [{"text": "最大再試行回数に達しました。"}]}, // オプションのコンテンツ
      "actions": {"escalate": true}
    }
    ```

## 追加のコンテキストとイベントの詳細

コアコンセプトを超えて、特定のユースケースで重要となるコンテキストとイベントに関するいくつかの詳細を以下に示します：

1.  **`ToolContext.function_call_id`（ツールアクションのリンク）：**
    *   LLMがツールをリクエストする（FunctionCall）と、そのリクエストにはIDがあります。ツール関数に提供される`ToolContext`には、この`function_call_id`が含まれています。
    *   **重要性：** このIDは、特に1ターンで複数のツールが呼び出される場合に、認証のようなアクションを、それを開始した特定のツールリクエストにリンクするために不可欠です。フレームワークはこのIDを内部的に使用します。

2.  **状態/アーティファクトの変更が記録される方法：**
    *   `CallbackContext`または`ToolContext`を使用して状態を変更したりアーティファクトを保存したりしても、これらの変更はすぐには永続ストレージに書き込まれません。
    *   代わりに、それらは`EventActions`オブジェクト内の`state_delta`および`artifact_delta`フィールドに移入されます。
    *   この`EventActions`オブジェクトは、変更後に生成された*次*のイベント（例：エージェントの応答やツールの結果イベント）に添付されます。
    *   `SessionService.append_event`メソッドは、入ってくるイベントからこれらのデルタを読み取り、セッションの永続的な状態とアーティファクトレコードに適用します。これにより、変更がイベントストリームと時系列で結び付けられることが保証されます。

3.  **状態スコープのプレフィックス（`app:`、`user:`、`temp:`）：**
    *   `context.state`を介して状態を管理する際、オプションでプレフィックスを使用できます：
        *   `app:my_setting`: アプリケーション全体に関連する状態を示唆します（永続的な`SessionService`が必要）。
        *   `user:user_preference`: セッションをまたいで特定のユーザーに関連する状態を示唆します（永続的な`SessionService`が必要）。
        *   `temp:intermediate_result`またはプレフィックスなし: 通常はセッション固有または現在の呼び出しのための一時的な状態。
    *   基盤となる`SessionService`が、永続化のためにこれらのプレフィックスをどのように処理するかを決定します。

4.  **エラーイベント：**
    *   `Event`はエラーを表すことがあります。`event.error_code`および`event.error_message`フィールド（`LlmResponse`から継承）を確認してください。
    *   エラーはLLM（例：安全フィルター、リソース制限）から発生する場合もあれば、ツールが致命的に失敗した場合にフレームワークによってパッケージ化される可能性もあります。典型的なツール固有のエラーについては、ツールの`FunctionResponse`コンテンツを確認してください。
    ```json
    // エラーイベントの例（概念的）
    {
      "author": "LLMAgent",
      "invocation_id": "e-err...",
      "content": null,
      "error_code": "SAFETY_FILTER_TRIGGERED",
      "error_message": "安全設定により応答がブロックされました。",
      "actions": {}
    }
    ```

これらの詳細は、ツールの認証、状態の永続性スコープ、およびイベントストリーム内のエラー処理を含む高度なユースケースのためのより完全な像を提供します。

## イベントを扱う際のベストプラクティス

ADKアプリケーションでイベントを効果的に使用するために：

*   **明確な作者情報：** カスタムエージェントを構築する際は、履歴内のエージェントアクションの帰属が正しいことを確認してください。フレームワークは通常、LLM/ツールイベントの作者情報を正しく処理します。
    
    === "Python"
        `BaseAgent`のサブクラスで`yield Event(author=self.name, ...)`を使用します。
    === "Java"
        カスタムエージェントロジックで`Event`を構築する際に、作者を設定します。例：`Event.builder().author(this.getAgentName()) // ... .build();`

*   **意味的なコンテンツとアクション：** `event.content`を中核的なメッセージ/データ（テキスト、関数呼び出し/応答）に使用します。`event.actions`を副作用（状態/アーティファクトの差分）や制御フロー（`transfer`、`escalate`、`skip_summarization`）の通知に特化して使用します。
*   **べき等性の意識：** `SessionService`が`event.actions`で通知された状態/アーティファクトの変更を適用する責任があることを理解してください。ADKサービスは一貫性を目指していますが、アプリケーションロジックがイベントを再処理する場合の潜在的な下流への影響を考慮してください。
*   **`is_final_response()`の使用：** アプリケーション/UIレイヤーでこのヘルパーメソッドに依存して、完全なユーザー向けのテキスト応答を識別します。そのロジックを手動で複製することは避けてください。
*   **履歴の活用：** セッションのイベントリストは、主要なデバッグツールです。実行をトレースし、問題を診断するために、作者、コンテンツ、アクションのシーケンスを調べてください。
*   **メタデータの使用：** `invocation_id`を使用して、単一のユーザーインタラクション内のすべてのイベントを関連付けます。`event.id`を使用して、特定のユニークな発生を参照します。

イベントを、そのコンテンツとアクションに明確な目的を持つ構造化されたメッセージとして扱うことが、ADKで複雑なエージェントの振る舞いを構築、デバッグ、管理するための鍵です。