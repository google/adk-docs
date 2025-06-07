# コールバックの設計パターンとベストプラクティス

コールバックは、エージェントのライフサイクルに強力なフックを提供します。ここでは、ADKでそれらを効果的に活用する方法を示す一般的な設計パターンと、実装のためのベストプラクティスを紹介します。

## 設計パターン

これらのパターンは、コールバックを使用してエージェントの振る舞いを強化または制御する典型的な方法を示しています：

### 1. ガードレールとポリシー適用

*   **パターン：** LLMやツールに到達する前にリクエストを傍受し、ルールを強制します。
*   **方法：** `before_model_callback`を使用して`LlmRequest`プロンプトを検査するか、`before_tool_callback`を使用してツール引数を検査します。ポリシー違反が検出された場合（例：禁止されたトピック、不適切な表現）、事前定義された応答（`LlmResponse`または`dict`/`Map`）を返して操作をブロックし、オプションで`context.state`を更新して違反をログに記録します。
*   **例：** `before_model_callback`が`llm_request.contents`で機密キーワードをチェックし、見つかった場合は標準の「このリクエストは処理できません」という`LlmResponse`を返し、LLMの呼び出しを防ぎます。

### 2. 動的な状態管理

*   **パターン：** コールバック内でセッション状態を読み書きして、エージェントの振る舞いを文脈に応じて変化させ、ステップ間でデータを渡します。
*   **方法：** `callback_context.state`または`tool_context.state`にアクセスします。変更（`state['key'] = value`）は、`SessionService`による永続化のために、後続の`Event.actions.state_delta`で自動的に追跡されます。
*   **例：** `after_tool_callback`がツールの結果から`transaction_id`を`tool_context.state['last_transaction_id']`に保存します。後の`before_agent_callback`が`state['user_tier']`を読み取ってエージェントの挨拶をカスタマイズするかもしれません。

### 3. ロギングとモニタリング

*   **パターン：** 可観測性とデバッグのために、特定のライフサイクルポイントで詳細なログを追加します。
*   **方法：** コールバック（例：`before_agent_callback`、`after_tool_callback`、`after_model_callback`）を実装して、エージェント名、ツール名、呼び出しID、コンテキストや引数からの関連データを含む構造化されたログを出力または送信します。
*   **例：** `INFO: [Invocation: e-123] Before Tool: search_api - Args: {'query': 'ADK'}`のようなログメッセージ。

### 4. キャッシング

*   **パターン：** 結果をキャッシュすることで、冗長なLLM呼び出しやツール実行を回避します。
*   **方法：** `before_model_callback`または`before_tool_callback`で、リクエスト/引数に基づいてキャッシュキーを生成します。このキーについて`context.state`（または外部キャッシュ）を確認します。見つかった場合は、キャッシュされた`LlmResponse`または結果を直接返し、実際の操作をスキップします。見つからなかった場合は、操作を続行させ、対応する`after_`コールバック（`after_model_callback`、`after_tool_callback`）を使用して、キーを使って新しい結果をキャッシュに保存します。
*   **例：** `get_stock_price(symbol)`の`before_tool_callback`が`state[f"cache:stock:{symbol}"]`をチェックします。存在する場合はキャッシュされた価格を返し、それ以外の場合はAPI呼び出しを許可し、`after_tool_callback`が結果を状態キーに保存します。

### 5. リクエスト/レスポンスの変更

*   **パターン：** LLM/ツールに送信される直前、または受信した直後にデータを変更します。
*   **方法：**
    *   `before_model_callback`：`llm_request`を変更します（例：`state`に基づいてシステム指示を追加）。
    *   `after_model_callback`：返された`LlmResponse`を変更します（例：テキストのフォーマット、コンテンツのフィルタリング）。
    *   `before_tool_callback`：ツールの`args`辞書（またはJavaではMap）を変更します。
    *   `after_tool_callback`：`tool_response`辞書（またはJavaではMap）を変更します。
*   **例：** `context.state['lang'] == 'es'`の場合、`before_model_callback`が`llm_request.config.system_instruction`に「ユーザーの言語設定：スペイン語」を追加します。

### 6. ステップの条件付きスキップ

*   **パターン：** 特定の条件に基づいて標準的な操作（エージェントの実行、LLM呼び出し、ツール実行）を防ぎます。
*   **方法：** `before_`コールバックから値を返します（`before_agent_callback`から`Content`、`before_model_callback`から`LlmResponse`、`before_tool_callback`から`dict`）。フレームワークはこの返された値をそのステップの結果として解釈し、通常の実行をスキップします。
*   **例：** `before_tool_callback`が`tool_context.state['api_quota_exceeded']`をチェックします。`True`の場合、`{'error': 'APIクォータを超えました'}`を返し、実際のツール関数の実行を防ぎます。

### 7. ツール固有のアクション（認証と要約制御）

*   **パターン：** 主に認証とツール結果のLLM要約の制御など、ツールのライフサイクルに固有のアクションを処理します。
*   **方法：** ツールコールバック（`before_tool_callback`、`after_tool_callback`）内で`ToolContext`を使用します。
    *   **認証：** 認証情報が必要で、見つからない場合（例：`tool_context.get_auth_response`や状態チェック経由）、`before_tool_callback`で`tool_context.request_credential(auth_config)`を呼び出します。これにより認証フローが開始されます。
    *   **要約：** ツールの生の辞書出力がLLMにそのまま返されるべきか、または直接表示される可能性がある場合、デフォルトのLLM要約ステップをバイパスするために`tool_context.actions.skip_summarization = True`を設定します。
*   **例：** 安全なAPIの`before_tool_callback`が状態内の認証トークンをチェックし、ない場合は`request_credential`を呼び出します。構造化JSONを返すツールの`after_tool_callback`が`skip_summarization = True`を設定するかもしれません。

### 8. アーティファクトの処理

*   **パターン：** エージェントのライフサイクル中に、セッション関連のファイルや大きなデータBLOBを保存または読み込みます。
*   **方法：** `callback_context.save_artifact` / `await tool_context.save_artifact`を使用してデータ（例：生成されたレポート、ログ、中間データ）を保存します。`load_artifact`を使用して以前に保存したアーティファクトを取得します。変更は`Event.actions.artifact_delta`を介して追跡されます。
*   **例：** 「generate_report」ツールの`after_tool_callback`が`await tool_context.save_artifact("report.pdf", report_part)`を使用して出力ファイルを保存します。`before_agent_callback`が`callback_context.load_artifact("agent_config.json")`を使用して設定アーティファクトを読み込むかもしれません。

## コールバックのベストプラクティス

*   **焦点を絞る：** 各コールバックを単一の、明確に定義された目的（例：ロギングのみ、検証のみ）のために設計します。モノリシックなコールバックは避けてください。
*   **パフォーマンスを意識する：** コールバックはエージェントの処理ループ内で同期的に実行されます。長時間の実行やブロッキング操作（ネットワーク呼び出し、重い計算）は避けてください。必要に応じてオフロードしますが、これにより複雑さが増すことに注意してください。
*   **エラーを適切に処理する：** コールバック関数内で`try...except/catch`ブロックを使用します。エラーを適切にログに記録し、エージェントの呼び出しを停止するか、回復を試みるかを決定します。コールバックのエラーでプロセス全体がクラッシュしないようにしてください。
*   **状態を慎重に管理する：**
    *   `context.state`からの読み取りと書き込みを意図的に行います。変更は*現在*の呼び出し内ですぐに表示され、イベント処理の最後に永続化されます。
    *   意図しない副作用を避けるために、広範な構造を変更するのではなく、特定の状態キーを使用します。
    *   特に永続的な`SessionService`実装では、明確さのために状態プレフィックス（`State.APP_PREFIX`, `State.USER_PREFIX`, `State.TEMP_PREFIX`）の使用を検討してください。
*   **べき等性を考慮する：** コールバックが外部の副作用を伴うアクション（例：外部カウンターのインクリメント）を実行する場合、フレームワークやアプリケーションでの潜在的な再試行を処理するために、可能であればべき等（同じ入力で複数回実行しても安全）になるように設計します。
*   **徹底的にテストする：** モックコンテキストオブジェクトを使用してコールバック関数を単体テストします。完全なエージェントフロー内でコールバックが正しく機能することを確認するために統合テストを実行します。
*   **明確さを確保する：** コールバック関数には説明的な名前を使用します。その目的、いつ実行されるか、および副作用（特に状態の変更）を説明する明確なdocstringを追加します。
*   **正しいコンテキストタイプを使用する：** 常に提供される特定のコンテキストタイプ（エージェント/モデルには`CallbackContext`、ツールには`ToolContext`）を使用して、適切なメソッドとプロパティへのアクセスを確保します。

これらのパターンとベストプラクティスを適用することで、ADKでより堅牢で、観測可能で、カスタマイズされたエージェントの振る舞いを作成するために、コールバックを効果的に使用できます。