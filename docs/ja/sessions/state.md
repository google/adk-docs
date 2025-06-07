# 状態（State）：セッションのメモ帳

各`セッション`（会話のスレッド）内において、**`state`**属性はその特定の対話のためのエージェント専用のメモ帳のように機能します。`session.events`が完全な履歴を保持するのに対し、`session.state`はエージェントが会話の*最中*に必要な動的な詳細を保存し、更新する場所です。

## `session.state`とは何か？

概念的に、`session.state`はキーと値のペアを保持するコレクション（辞書またはMap）です。エージェントが現在の会話を効果的にするために思い出す、または追跡する必要がある情報のために設計されています：

*   **対話のパーソナライズ：** 以前に言及されたユーザーの好みを記憶する（例：`'user_preference_theme': 'dark'`）。
*   **タスクの進捗追跡：** 複数ターンにわたるプロセスのステップを把握する（例：`'booking_step': 'confirm_payment'`）。
*   **情報の蓄積：** リストや要約を作成する（例：`'shopping_cart_items': ['book', 'pen']`）。
*   **情報に基づいた意思決定：** 次の応答に影響を与えるフラグや値を保存する（例：`'user_is_authenticated': True`）。

### `State`の主な特徴

1.  **構造：シリアライズ可能なキーと値のペア**

    *   データは`key: value`として保存されます。
    *   **キー：** 常に文字列（`str`）です。明確な名前を使用してください（例：`'departure_city'`、`'user:language_preference'`）。
    *   **値：** **シリアライズ可能**でなければなりません。これは、`SessionService`によって簡単に保存および読み込みができることを意味します。文字列、数値、ブール値、およびこれらの基本型*のみ*を含む単純なリストや辞書など、特定の言語（Python/Java）の基本型に固執してください。（正確な詳細についてはAPIドキュメントを参照してください）。
    *   **⚠️ 複雑なオブジェクトを避ける：** **シリアライズ不可能なオブジェクト**（カスタムクラスのインスタンス、関数、接続など）を直接状態に保存しないでください。必要であれば単純な識別子を保存し、複雑なオブジェクトは他の場所で取得してください。

2.  **可変性：変化する**

    *   `state`の内容は、会話が進むにつれて変化することが期待されます。

3.  **永続性：`SessionService`に依存**

    *   状態がアプリケーションの再起動後も存続するかどうかは、選択したサービスに依存します：
        *   `InMemorySessionService`：**永続的ではない。**再起動時に状態は失われます。
        *   `DatabaseSessionService` / `VertexAiSessionService`：**永続的。**状態は確実に保存されます。

!!! Note
    プリミティブの具体的なパラメータやメソッド名は、SDKの言語によって若干異なる場合があります（例：Pythonでは`session.state['current_intent'] = 'book_flight'`、Javaでは`session.state().put("current_intent", "book_flight")`）。詳細は各言語のAPIドキュメントを参照してください。

### プレフィックスによる状態の整理：スコープの重要性

状態キーのプレフィックスは、特に永続的なサービスにおいて、そのスコープと永続性の振る舞いを定義します：

*   **プレフィックスなし（セッション状態）：**

    *   **スコープ：** *現在*のセッション（`id`）に固有。
    *   **永続性：** `SessionService`が永続的（`Database`、`VertexAI`）な場合にのみ永続します。
    *   **ユースケース：** 現在のタスク内の進捗追跡（例：`'current_booking_step'`）、この対話のための一時的なフラグ（例：`'needs_clarification'`）。
    *   **例：** `session.state['current_intent'] = 'book_flight'`

*   **`user:`プレフィックス（ユーザー状態）：**

    *   **スコープ：** `user_id`に紐づけられ、そのユーザーの*すべて*のセッションで共有されます（同じ`app_name`内）。
    *   **永続性：** `Database`または`VertexAI`で永続的。（`InMemory`では保存されるが、再起動時に失われる）。
    *   **ユースケース：** ユーザー設定（例：`'user:theme'`）、プロフィール詳細（例：`'user:name'`）。
    *   **例：** `session.state['user:preferred_language'] = 'fr'`

*   **`app:`プレフィックス（アプリ状態）：**

    *   **スコープ：** `app_name`に紐づけられ、そのアプリケーションの*すべて*のユーザーとセッションで共有されます。
    *   **永続性：** `Database`または`VertexAI`で永続的。（`InMemory`では保存されるが、再起動時に失われる）。
    *   **ユースケース：** グローバル設定（例：`'app:api_endpoint'`）、共有テンプレート。
    *   **例：** `session.state['app:global_discount_code'] = 'SAVE10'`

*   **`temp:`プレフィックス（一時的なセッション状態）：**

    *   **スコープ：** *現在*のセッション処理ターンに固有。
    *   **永続性：** **決して永続しない。**永続的なサービスでも破棄されることが保証されます。
    *   **ユースケース：** 直後にのみ必要な中間結果、明示的に保存したくないデータ。
    *   **例：** `session.state['temp:raw_api_response'] = {...}`

**エージェントから見た場合：** エージェントのコードは、単一の`session.state`コレクション（dict/Map）を介して、*結合された*状態と対話します。`SessionService`は、プレフィックスに基づいて適切な基盤となるストレージから状態を取得/マージする処理をします。

### 状態の更新方法：推奨されるメソッド

状態は**常に**、`session_service.append_event()`を使用してセッション履歴に`Event`を追加する一環として更新されるべきです。これにより、変更が追跡され、永続性が正しく機能し、更新がスレッドセーフであることが保証されます。

**1. 簡単な方法：`output_key`（エージェントのテキスト応答用）**

これは、エージェントの最終的なテキスト応答を直接状態に保存する最も簡単な方法です。`LlmAgent`を定義する際に、`output_key`を指定します：

=== "Python"

    ```python
    # ...(Pythonコードは変更しないため省略)...
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/state/GreetingAgentExample.java:full_code"
    ```

舞台裏では、`Runner`が`output_key`を使用して、`state_delta`を持つ必要な`EventActions`を作成し、`append_event`を呼び出します。

**2. 標準的な方法：`EventActions.state_delta`（複雑な更新用）**

より複雑なシナリオ（複数のキーの更新、文字列以外の値、`user:`や`app:`のような特定のスコープ、またはエージェントの最終テキストに直接結びつかない更新）では、`EventActions`内で`state_delta`を手動で構築します。

=== "Python"

    ```python
    # ...(Pythonコードは変更しないため省略)...
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/state/ManualStateUpdateExample.java:full_code"
    ```

**3. `CallbackContext`または`ToolContext`経由（コールバックとツールに推奨）**

エージェントのコールバック（例：`on_before_agent_call`、`on_after_agent_call`）やツール関数内で状態を変更する場合、関数に提供される`CallbackContext`または`ToolContext`の`state`属性を使用するのが最善です。

*   `callback_context.state['my_key'] = my_value`
*   `tool_context.state['my_key'] = my_value`

これらのコンテキストオブジェクトは、それぞれの実行スコープ内で状態の変更を管理するために特別に設計されています。`context.state`を変更すると、ADKフレームワークはこれらの変更が自動的にキャプチャされ、コールバックやツールによって生成されるイベントの`EventActions.state_delta`に正しくルーティングされるようにします。この差分は、イベントが追加されるときに`SessionService`によって処理され、適切な永続性と追跡が保証されます。

この方法は、コールバックやツール内のほとんどの一般的な状態更新シナリオで、`EventActions`や`state_delta`の手動作成を抽象化し、コードをよりクリーンでエラーが発生しにくくします。

コンテキストオブジェクトに関するより包括的な詳細については、[コンテキストのドキュメント](docs/context/index.md)を参照してください。

=== "Python"

    ```python
    # エージェントのコールバックまたはツール関数内
    from google.adk.agents import CallbackContext # または ToolContext

    def my_callback_or_tool_function(context: CallbackContext, # または ToolContext
                                     # ... 他のパラメータ ...
                                    ):
        # 既存の状態を更新
        count = context.state.get("user_action_count", 0)
        context.state["user_action_count"] = count + 1

        # 新しい状態を追加
        context.state["temp:last_operation_status"] = "success"

        # 状態の変更は自動的にイベントのstate_deltaの一部となる
        # ... コールバック/ツールの残りのロジック ...
    ```

=== "Java"

    ```java
    // エージェントのコールバックまたはツールメソッド内
    import com.google.adk.agents.CallbackContext; // または ToolContext
    // ... 他のインポート ...

    public class MyAgentCallbacks {
        public void onAfterAgent(CallbackContext callbackContext) {
            // 既存の状態を更新
            Integer count = (Integer) callbackContext.state().getOrDefault("user_action_count", 0);
            callbackContext.state().put("user_action_count", count + 1);

            // 新しい状態を追加
            callbackContext.state().put("temp:last_operation_status", "success");

            // 状態の変更は自動的にイベントのstate_deltaの一部となる
            // ... コールバックの残りのロジック ...
        }
    }
    ```

**`append_event`の役割：**

*   `Event`を`session.events`に追加します。
*   イベントの`actions`から`state_delta`を読み取ります。
*   `SessionService`によって管理される状態にこれらの変更を適用し、サービスタイプに基づいてプレフィックスと永続性を正しく処理します。
*   セッションの`last_update_time`を更新します。
*   同時更新に対するスレッドセーフを保証します。

### ⚠️ 直接的な状態変更に関する警告

エージェントの呼び出しの管理されたライフサイクルの*外*で（つまり、`CallbackContext`や`ToolContext`を介さずに）、`SessionService`から直接取得した`Session`オブジェクトの`session.state`コレクション（辞書/Map）を直接変更することは避けてください。例えば、`retrieved_session = await session_service.get_session(...); retrieved_session.state['key'] = value`のようなコードは問題があります。

コールバックやツール内で`CallbackContext.state`や`ToolContext.state`を使用して状態を変更することが、変更が追跡されることを保証する正しい方法です。これらのコンテキストオブジェクトは、イベントシステムとの必要な統合を処理します。

**なぜ直接的な変更（コンテキスト外）が強く非推奨なのか：**

1.  **イベント履歴をバイパスする：** 変更が`Event`として記録されず、監査可能性が失われます。
2.  **永続性を壊す：** このように行われた変更は、`DatabaseSessionService`や`VertexAiSessionService`によって**保存されない可能性が高い**です。これらは保存をトリガーするために`append_event`に依存しています。
3.  **スレッドセーフではない：** 競合状態や更新の喪失につながる可能性があります。
4.  **タイムスタンプ/ロジックを無視する：** `last_update_time`を更新したり、関連するイベントロジックをトリガーしたりしません。

**推奨事項：** `output_key`、`EventActions.state_delta`（イベントを手動で作成する場合）、またはそれぞれのスコープ内で`CallbackContext`または`ToolContext`オブジェクトの`state`プロパティを変更することで、状態を更新することに固執してください。これらの方法は、信頼性が高く、追跡可能で、永続的な状態管理を保証します。`SessionService`から取得したセッションの`session.state`への直接アクセスは、状態の*読み取り*にのみ使用してください。

### 状態設計のベストプラクティスのまとめ

*   **ミニマリズム：** 不可欠で動的なデータのみを保存します。
*   **シリアライズ：** 基本的でシリアライズ可能な型を使用します。
*   **説明的なキーとプレフィックス：** 明確な名前と適切なプレフィックス（`user:`、`app:`、`temp:`、またはなし）を使用します。
*   **浅い構造：** 可能な限り深いネストを避けます。
*   **標準的な更新フロー：** `append_event`に依存します。