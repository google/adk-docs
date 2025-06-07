# メモリ: `MemoryService`による長期的な知識

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="この機能は現在Pythonでのみ利用可能です。Javaのサポートは計画中/近日公開予定です。" }

これまで、`Session`が*単一の進行中の会話*の履歴（`events`）と一時的なデータ（`state`）を追跡する方法を見てきました。しかし、エージェントが*過去*の会話から情報を思い出したり、外部のナレッジベースにアクセスしたりする必要がある場合はどうでしょうか？ここで、**長期的な知識**と**`MemoryService`**の概念が登場します。

このように考えてみてください。

*   **`Session` / `State`:** ある特定のチャット中の短期記憶のようなもの。
*   **長期的な知識 (`MemoryService`)**: エージェントが参照できる、検索可能なアーカイブやナレッジライブラリのようなもの。過去の多くのチャットや他の情報源からの情報を含む可能性があります。

## `MemoryService`の役割

`BaseMemoryService`は、この検索可能な長期的な知識ストアを管理するためのインターフェースを定義します。その主な責務は次のとおりです。

1.  **情報の取り込み (`add_session_to_memory`):** （通常は完了した）`Session`のコンテンツを取得し、関連情報を長期的な知識ストアに追加します。
2.  **情報の検索 (`search_memory`):** エージェントが（通常は`Tool`を介して）知識ストアにクエリを発行し、検索クエリに基づいて関連するスニペットやコンテキストを取得できるようにします。

## `MemoryService`の実装

ADKは、この長期的な知識ストアを実装するためのさまざまな方法を提供します。

1.  **`InMemoryMemoryService`**

    *   **仕組み:** アプリケーションのメモリにセッション情報を保存し、検索には基本的なキーワードマッチングを実行します。
    *   **永続性:** なし。**アプリケーションが再起動すると、保存されているすべての知識は失われます。**
    *   **要件:** 追加のものは何もありません。
    *   **最適な用途:** プロトタイピング、簡単なテスト、基本的なキーワード検索のみが必要で永続性が不要なシナリオ。

    ```py
    from google.adk.memory import InMemoryMemoryService
    memory_service = InMemoryMemoryService()
    ```

2.  **`VertexAiRagMemoryService`**

    *   **仕組み:** Google CloudのVertex AI RAG（Retrieval-Augmented Generation）サービスを活用します。指定されたRAGコーパスにセッションデータを取り込み、強力なセマンティック検索機能を使用して検索します。
    *   **永続性:** あり。知識は、設定されたVertex AI RAGコーパス内に永続的に保存されます。
    *   **要件:** Google Cloudプロジェクト、適切な権限、必要なSDK（`pip install google-adk[vertexai]`）、および事前に設定されたVertex AI RAGコーパスのリソース名/ID。
    *   **最適な用途:** 特にGoogle Cloud上にデプロイする場合に、スケーラブルで永続的、かつ意味的に関連性の高い知識検索が必要な本番アプリケーション。

    ```py
    # 要件: pip install google-adk[vertexai]
    # さらにGCPセットアップ、RAGコーパス、認証が必要
    from google.adk.memory import VertexAiRagMemoryService

    # RAGコーパスの名前またはID
    RAG_CORPUS_RESOURCE_NAME = "projects/your-gcp-project-id/locations/us-central1/ragCorpora/your-corpus-id"
    # 検索のためのオプション設定
    SIMILARITY_TOP_K = 5
    VECTOR_DISTANCE_THRESHOLD = 0.7

    memory_service = VertexAiRagMemoryService(
        rag_corpus=RAG_CORPUS_RESOURCE_NAME,
        similarity_top_k=SIMILARITY_TOP_K,
        vector_distance_threshold=VECTOR_DISTANCE_THRESHOLD
    )
    ```

## 実際のメモリの仕組み

典型的なワークフローは、次のステップを含みます。

1.  **セッションでの対話:** ユーザーは`SessionService`によって管理される`Session`を介してエージェントと対話します。イベントが追加され、状態が更新される可能性があります。
2.  **メモリへの取り込み:** ある時点（多くの場合、セッションが完了したと見なされるか、重要な情報が得られたとき）で、アプリケーションは`memory_service.add_session_to_memory(session)`を呼び出します。これにより、セッションのイベントから関連情報が抽出され、長期的な知識ストア（インメモリ辞書またはRAGコーパス）に追加されます。
3.  **後のクエリ:** *別の*（または同じ）セッションで、ユーザーは過去のコンテキストを必要とする質問をするかもしれません（例: 「先週、プロジェクトXについて何を話しましたか？」）。
4.  **エージェントがメモリツールを使用:** メモリ検索ツール（組み込みの`load_memory`ツールなど）を備えたエージェントは、過去のコンテキストの必要性を認識します。ツールを呼び出し、検索クエリ（例: 「discussion project X last week」）を提供します。
5.  **検索の実行:** ツールは内部で`memory_service.search_memory(app_name, user_id, query)`を呼び出します。
6.  **結果の返却:** `MemoryService`はストアを検索し（キーワードマッチングまたはセマンティック検索を使用）、関連するスニペットを、`MemoryResult`オブジェクトのリストを含む`SearchMemoryResponse`として返します（それぞれが関連する過去のセッションのイベントを含む可能性があります）。
7.  **エージェントが結果を使用:** ツールはこれらの結果を、通常はコンテキストや関数応答の一部としてエージェントに返します。エージェントは、この取得した情報を使用してユーザーへの最終的な回答を作成できます。

## 例: メモリの追加と検索

この例では、簡単にするために`InMemory`サービスを使用した基本的なフローを示します。

???+ "完全なコード"

    ```py
    import asyncio
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.memory import InMemoryMemoryService # MemoryServiceをインポート
    from google.adk.runners import Runner
    from google.adk.tools import load_memory # メモリにクエリするためのツール
    from google.genai.types import Content, Part

    # --- 定数 ---
    APP_NAME = "memory_example_app"
    USER_ID = "mem_user"
    MODEL = "gemini-2.0-flash" # 有効なモデルを使用

    # --- エージェントの定義 ---
    # エージェント1: 情報をキャプチャする単純なエージェント
    info_capture_agent = LlmAgent(
        model=MODEL,
        name="InfoCaptureAgent",
        instruction="ユーザーの発言を認識します。",
        # output_key="captured_info" # オプションで状態にも保存可能
    )

    # エージェント2: メモリを使用できるエージェント
    memory_recall_agent = LlmAgent(
        model=MODEL,
        name="MemoryRecallAgent",
        instruction="ユーザーの質問に答えます。答えが過去の会話にある可能性がある場合は、"
                    "'load_memory'ツールを使用してください。",
        tools=[load_memory] # エージェントにツールを与える
    )

    # --- サービスとランナー ---
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService() # デモ用にインメモリを使用

    runner = Runner(
        # 情報キャプチャエージェントから開始
        agent=info_capture_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service # ランナーにメモリサービスを提供する
    )

    # --- シナリオ ---

    # ターン1: セッションで情報をキャプチャする
    print("--- ターン1: 情報のキャプチャ ---")
    session1_id = "session_info"
    session1 = await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)
    user_input1 = Content(parts=[Part(text="私のお気に入りのプロジェクトはプロジェクトアルファです。")], role="user")

    # エージェントを実行
    final_response_text = "(最終応答なし)"
    async for event in runner.run_async(user_id=USER_ID, session_id=session1_id, new_message=user_input1):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_text = event.content.parts[0].text
    print(f"エージェント1の応答: {final_response_text}")

    # 完了したセッションを取得
    completed_session1 = await runner.session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)

    # このセッションのコンテンツをメモリサービスに追加
    print("\n--- セッション1をメモリに追加 ---")
    memory_service = await memory_service.add_session_to_memory(completed_session1)
    print("セッションがメモリに追加されました。")

    # ターン2: *新しい*（または同じ）セッションで、メモリを必要とする質問をする
    print("\n--- ターン2: 情報の想起 ---")
    session2_id = "session_recall" # 同じでも異なるセッションIDでも可
    session2 = await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session2_id)

    # ランナーを想起エージェントに切り替え
    runner.agent = memory_recall_agent
    user_input2 = Content(parts=[Part(text="私のお気に入りのプロジェクトは何ですか？")], role="user")

    # 想起エージェントを実行
    print("MemoryRecallAgentを実行中...")
    final_response_text_2 = "(最終応答なし)"
    async for event in runner.run_async(user_id=USER_ID, session_id=session2_id, new_message=user_input2):
        print(f"  イベント: {event.author} - タイプ: {'Text' if event.content and event.content.parts and event.content.parts[0].text else ''}"
            f"{'FuncCall' if event.get_function_calls() else ''}"
            f"{'FuncResp' if event.get_function_responses() else ''}")
        if event.is_final_response() and event.content and event.content.parts:
            final_response_text_2 = event.content.parts[0].text
            print(f"エージェント2の最終応答: {final_response_text_2}")
            break # 最終応答後に停止

    # ターン2で期待されるイベントシーケンス:
    # 1. ユーザーが「私のお気に入りのプロジェクトは何ですか？」を送信。
    # 2. エージェント（LLM）が「favorite project」のようなクエリで`load_memory`ツールを呼び出すことを決定。
    # 3. ランナーが`load_memory`ツールを実行し、それが`memory_service.search_memory`を呼び出す。
    # 4. `InMemoryMemoryService`がsession1から関連テキスト（「私のお気に入りのプロジェクトはプロジェクトアルファです。」）を見つける。
    # 5. ツールがこのテキストをFunctionResponseイベントで返す。
    # 6. エージェント（LLM）が関数応答を受け取り、取得したテキストを処理する。
    # 7. エージェントが最終的な答え（例: 「あなたのお気に入りのプロジェクトはプロジェクトアルファです。」）を生成する。
    ```