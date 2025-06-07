# OpenAPI連携

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="この機能は現在Pythonでのみ利用可能です。Javaのサポートは計画中/近日公開予定です。" }

## OpenAPIによるREST APIの連携

ADKは、[OpenAPI Specification (v3.x)](https://swagger.io/specification/)から直接呼び出し可能なツールを自動的に生成することで、外部REST APIとの対話を簡素化します。これにより、各APIエンドポイントに対して個別の関数ツールを手動で定義する必要がなくなります。

!!! tip "主な利点"
    `OpenAPIToolset`を使用すると、既存のAPIドキュメント（OpenAPI仕様）からエージェントツール（`RestApiTool`）を即座に作成でき、エージェントがWebサービスをシームレスに呼び出すことが可能になります。

## 主要コンポーネント

*   **`OpenAPIToolset`**: これが主に使用するクラスです。OpenAPI仕様で初期化すると、ツールの解析と生成を処理します。
*   **`RestApiTool`**: このクラスは、単一の呼び出し可能なAPI操作（例: `GET /pets/{petId}`や`POST /pets`）を表します。`OpenAPIToolset`は、仕様で定義された各操作に対して1つの`RestApiTool`インスタンスを作成します。

## 仕組み

`OpenAPIToolset`を使用する場合、プロセスは主に次のステップを含みます。

1.  **初期化と解析**:
    *   OpenAPI仕様をPythonの辞書、JSON文字列、またはYAML文字列として`OpenAPIToolset`に提供します。
    *   ツールセットは内部で仕様を解析し、内部参照（`$ref`）を解決して完全なAPI構造を理解します。

2.  **操作の発見**:
    *   仕様の`paths`オブジェクト内で定義されたすべての有効なAPI操作（例: `GET`, `POST`, `PUT`, `DELETE`）を識別します。

3.  **ツールの生成**:
    *   発見された各操作に対して、`OpenAPIToolset`は対応する`RestApiTool`インスタンスを自動的に作成します。
    *   **ツール名**: 仕様の`operationId`から派生します（`snake_case`に変換、最大60文字）。`operationId`がない場合は、メソッドとパスから名前が生成されます。
    *   **ツールの説明**: LLMのために、操作の`summary`または`description`を使用します。
    *   **API詳細**: 必要なHTTPメソッド、パス、サーバーのベースURL、パラメータ（パス、クエリ、ヘッダー、クッキー）、およびリクエストボディのスキーマを内部に保存します。

4.  **`RestApiTool`の機能**: 生成された各`RestApiTool`は次のようになります。
    *   **スキーマ生成**: 操作のパラメータとリクエストボディに基づいて`FunctionDeclaration`を動的に作成します。このスキーマは、LLMにツールの呼び出し方（どの引数が期待されるか）を伝えます。
    *   **実行**: LLMによって呼び出されると、LLMから提供された引数とOpenAPI仕様の詳細を使用して、正しいHTTPリクエスト（URL、ヘッダー、クエリパラメータ、ボディ）を構築します。認証を（設定されていれば）処理し、`requests`ライブラリを使用してAPI呼び出しを実行します。
    *   **レスポンス処理**: APIレスポンス（通常はJSON）をエージェントのフローに返します。

5.  **認証**: `OpenAPIToolset`を初期化する際に、グローバルな認証（APIキーやOAuthなど - 詳細は[認証](../tools/authentication.md)を参照）を設定できます。この認証設定は、生成されたすべての`RestApiTool`インスタンスに自動的に適用されます。

## 利用ワークフロー

OpenAPI仕様をエージェントに統合するには、次の手順に従います。

1.  **仕様の取得**: OpenAPI仕様ドキュメントを取得します（例: `.json`や`.yaml`ファイルから読み込む、URLから取得する）。
2.  **ツールセットのインスタンス化**: `OpenAPIToolset`インスタンスを作成し、仕様のコンテンツとタイプ（`spec_str`/`spec_dict`, `spec_str_type`）を渡します。APIで必要な場合は、認証情報（`auth_scheme`, `auth_credential`）を提供します。

    ```python
    from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

    # JSON文字列の例
    openapi_spec_json = '...' # あなたのOpenAPI JSON文字列
    toolset = OpenAPIToolset(spec_str=openapi_spec_json, spec_str_type="json")

    # 辞書の例
    # openapi_spec_dict = {...} # dictとしてのあなたのOpenAPI仕様
    # toolset = OpenAPIToolset(spec_dict=openapi_spec_dict)
    ```

3.  **エージェントに追加**: 取得したツールを`LlmAgent`の`tools`リストに含めます。

    ```python
    from google.adk.agents import LlmAgent

    my_agent = LlmAgent(
        name="api_interacting_agent",
        model="gemini-2.0-flash", # または希望のモデル
        tools=[toolset], # ツールセットを渡す
        # ... その他のエージェント設定 ...
    )
    ```

4.  **エージェントへの指示**: エージェントの指示を更新し、新しいAPIの能力と使用できるツールの名前（例: `list_pets`, `create_pet`）を伝えます。仕様から生成されたツールの説明もLLMの助けになります。
5.  **エージェントの実行**: `Runner`を使用してエージェントを実行します。LLMがいずれかのAPIを呼び出す必要があると判断すると、適切な`RestApiTool`をターゲットとする関数呼び出しを生成し、それが自動的にHTTPリクエストを処理します。

## 例

この例は、簡単なペットストアのOpenAPI仕様からツールを生成し（モックレスポンスに`httpbin.org`を使用）、エージェントを介してそれらと対話する方法を示しています。

???+ "コード: ペットストアAPI"

    ```python title="openapi_example.py"
    --8<-- "examples/python/snippets/tools/openapi_tool.py"
    ```