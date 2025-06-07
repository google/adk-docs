# ツールでの認証

![python_only](https://img.shields.io/badge/現在サポートされているのは-Python-blue){ title="この機能は現在Pythonで利用可能です。Javaのサポートは計画中/近日公開予定です。" }

## コアコンセプト

多くのツールは、保護されたリソース（Googleカレンダーのユーザーデータ、Salesforceのレコードなど）にアクセスする必要があり、認証を必要とします。ADKは、さまざまな認証方法を安全に処理するためのシステムを提供します。

関与する主要なコンポーネントは以下の通りです：

1.  **`AuthScheme`**: APIが認証情報をどのように期待するかを定義します（例：ヘッダーのAPIキーとして、OAuth 2.0のBearerトークンとして）。ADKはOpenAPI 3.0と同じタイプの認証スキームをサポートしています。各種類の認証情報の詳細については、[OpenAPIドキュメント：認証](https://swagger.io/docs/specification/v3_0/authentication/)を参照してください。ADKは`APIKey`、`HTTPBearer`、`OAuth2`、`OpenIdConnectWithConfig`のような特定のクラスを使用します。
2.  **`AuthCredential`**: 認証プロセスを*開始*するために必要な*初期*情報を保持します（例：アプリケーションのOAuthクライアントID/シークレット、APIキーの値）。これには、認証情報の種類を指定する`auth_type`（`API_KEY`、`OAUTH2`、`SERVICE_ACCOUNT`など）が含まれます。

一般的なフローは、ツールの設定時にこれらの詳細を提供することです。ADKはその後、ツールがAPI呼び出しを行う前に、初期の認証情報を利用可能なもの（アクセストークンなど）に自動的に交換しようとします。ユーザーの操作（OAuthの同意など）が必要なフローについては、エージェントクライアントアプリケーションを巻き込んだ特定の対話型プロセスがトリガーされます。

## サポートされている初期認証情報の種類

*   **API_KEY:** 単純なキー/値の認証用。通常、交換は不要です。
*   **HTTP:** Basic認証（交換は非推奨/非サポート）または既に取得済みのBearerトークンを表すことができます。Bearerトークンの場合、交換は不要です。
*   **OAUTH2:** 標準のOAuth 2.0フロー用。設定（クライアントID、シークレット、スコープ）が必要で、多くの場合、ユーザーの同意のための対話型フローをトリガーします。
*   **OPEN_ID_CONNECT:** OpenID Connectに基づく認証用。OAuth2と同様に、多くの場合、設定とユーザーの操作が必要です。
*   **SERVICE_ACCOUNT:** Google Cloudサービスアカウントの認証情報（JSONキーまたはApplication Default Credentials）用。通常、Bearerトークンに交換されます。

## ツールでの認証設定

ツールの定義時に認証を設定します：

*   **RestApiTool / OpenAPIToolset**: 初期化時に`auth_scheme`と`auth_credential`を渡します。

*   **GoogleApiToolSetツール**: ADKには、Googleカレンダー、BigQueryなどの組み込みの1stパーティツールがあります。ツールセットの特定の方法を使用します。

*   **APIHubToolset / ApplicationIntegrationToolset**: API Hubで管理されているAPI/Application Integrationによって提供されるAPIが認証を必要とする場合、初期化時に`auth_scheme`と`auth_credential`を渡します。

!!! tip "警告" 
    アクセストークンや特にリフレッシュトークンのような機密性の高い認証情報をセッション状態に直接保存することは、セッションストレージのバックエンド（`SessionService`）やアプリケーション全体のセキュリティ体制によっては、セキュリティリスクをもたらす可能性があります。

    *   **`InMemorySessionService`:** テストや開発には適していますが、プロセスが終了するとデータは失われます。一時的なものであるためリスクは少ないです。
    *   **データベース/永続ストレージ:** 堅牢な暗号化ライブラリ（`cryptography`など）を使用してデータベースに保存する前にトークンデータを**暗号化**し、暗号化キーを安全に管理する（キー管理サービスを使用するなど）ことを**強く検討**してください。
    *   **セキュアなシークレットストア:** 本番環境では、機密性の高い認証情報を専用のシークレットマネージャー（Google Cloud Secret ManagerやHashiCorp Vaultなど）に保存することが**最も推奨されるアプローチ**です。ツールは、セッション状態には短期間のアクセストークンや安全な参照のみを保存し（リフレッシュトークン自体は保存しない）、必要なときにセキュアストアから必要なシークレットを取得することができます。

---

## ジャーニー1：認証済みツールを使用したエージェントアプリケーションの構築

このセクションでは、エージェントアプリケーション内で認証が必要な既存のツール（`RestApiTool/OpenAPIToolset`、`APIHubToolset`、`GoogleApiToolSet`など）の使用に焦点を当てます。あなたの主な責任は、ツールの設定と、対話型認証フローのクライアント側の部分（ツールで必要な場合）の処理です。

### 1. 認証付きツールの設定

認証済みツールをエージェントに追加する際には、その必要な`AuthScheme`とアプリケーションの初期`AuthCredential`を提供する必要があります。

**A. OpenAPIベースのツールセットの使用（`OpenAPIToolset`、`APIHubToolset`など）**

ツールセットの初期化時にスキームと認証情報を渡します。ツールセットはそれらを生成されたすべてのツールに適用します。以下は、ADKで認証付きツールを作成するいくつかの方法です。

=== "APIキー"

      APIキーを必要とするツールを作成します。

      ```py
      from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
      from google.adk.tools.apihub_tool.apihub_toolset import APIHubToolset 
      auth_scheme, auth_credential = token_to_scheme_credential(
         "apikey", "query", "apikey", YOUR_API_KEY_STRING
      )
      sample_api_toolset = APIHubToolset(
         name="sample-api-requiring-api-key",
         description="APIキーで保護されたAPIを使用するツール",
         apihub_resource_name="...",
         auth_scheme=auth_scheme,
         auth_credential=auth_credential,
      )
      ```

=== "OAuth2"

      OAuth2を必要とするツールを作成します。

      ```py
      from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset
      from fastapi.openapi.models import OAuth2
      from fastapi.openapi.models import OAuthFlowAuthorizationCode
      from fastapi.openapi.models import OAuthFlows
      from google.adk.auth import AuthCredential
      from google.adk.auth import AuthCredentialTypes
      from google.adk.auth import OAuth2Auth

      auth_scheme = OAuth2(
          flows=OAuthFlows(
              authorizationCode=OAuthFlowAuthorizationCode(
                  authorizationUrl="https://accounts.google.com/o/oauth2/auth",
                  tokenUrl="https://oauth2.googleapis.com/token",
                  scopes={
                      "https://www.googleapis.com/auth/calendar": "calendar scope"
                  },
              )
          )
      )
      auth_credential = AuthCredential(
          auth_type=AuthCredentialTypes.OAUTH2,
          oauth2=OAuth2Auth(
              client_id=YOUR_OAUTH_CLIENT_ID, 
              client_secret=YOUR_OAUTH_CLIENT_SECRET
          ),
      )

      calendar_api_toolset = OpenAPIToolset(
          spec_str=google_calendar_openapi_spec_str, # openapi仕様をここに埋める
          spec_str_type='yaml',
          auth_scheme=auth_scheme,
          auth_credential=auth_credential,
      )
      ```

=== "サービスアカウント"

      サービスアカウントを必要とするツールを作成します。

      ```py
      from google.adk.tools.openapi_tool.auth.auth_helpers import service_account_dict_to_scheme_credential
      from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

      service_account_cred = json.loads(service_account_json_str)
      auth_scheme, auth_credential = service_account_dict_to_scheme_credential(
          config=service_account_cred,
          scopes=["https://www.googleapis.com/auth/cloud-platform"],
      )
      sample_toolset = OpenAPIToolset(
          spec_str=sa_openapi_spec_str, # openapi仕様をここに埋める
          spec_str_type='json',
          auth_scheme=auth_scheme,
          auth_credential=auth_credential,
      )
      ```

=== "OpenID connect"

      OpenID connectを必要とするツールを作成します。

      ```py
      from google.adk.auth.auth_schemes import OpenIdConnectWithConfig
      from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth
      from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

      auth_scheme = OpenIdConnectWithConfig(
          authorization_endpoint=OAUTH2_AUTH_ENDPOINT_URL,
          token_endpoint=OAUTH2_TOKEN_ENDPOINT_URL,
          scopes=['openid', 'YOUR_OAUTH_SCOPES"]
      )
      auth_credential = AuthCredential(
          auth_type=AuthCredentialTypes.OPEN_ID_CONNECT,
          oauth2=OAuth2Auth(
              client_id="...",
              client_secret="...",
          )
      )

      userinfo_toolset = OpenAPIToolset(
          spec_str=content, # 実際の仕様を埋める
          spec_str_type='yaml',
          auth_scheme=auth_scheme,
          auth_credential=auth_credential,
      )
      ```

**B. Google APIツールセットの使用（例：`calendar_tool_set`）**

これらのツールセットには、多くの場合、専用の設定メソッドがあります。

ヒント：Google OAuthクライアントIDとシークレットの作成方法については、このガイドを参照してください：[Google APIクライアントIDの取得](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid#get_your_google_api_client_id)

```py
# 例：Googleカレンダーツールの設定
from google.adk.tools.google_api_tool import calendar_tool_set

client_id = "YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com"
client_secret = "YOUR_GOOGLE_OAUTH_CLIENT_SECRET"

# このツールセットタイプ専用の設定メソッドを使用
calendar_tool_set.configure_auth(
    client_id=oauth_client_id, client_secret=oauth_client_secret
)

# agent = LlmAgent(..., tools=calendar_tool_set.get_tool('calendar_tool_set'))
```

認証リクエストのフローのシーケンス図（ツールが認証情報を要求している場合）は以下のようになります：

![Authentication](../assets/auth_part1.svg) 


### 2. 対話型OAuth/OIDCフローの処理（クライアント側）

ツールがユーザーのログイン/同意を必要とする場合（通常はOAuth 2.0またはOIDC）、ADKフレームワークは実行を一時停止し、**エージェントクライアント**アプリケーションに通知します。2つのケースがあります：

*   **エージェントクライアント**アプリケーションが、同じプロセス内で直接エージェントを実行する場合（`runner.run_async`経由）。例：UIバックエンド、CLIアプリ、Sparkジョブなど。
*   **エージェントクライアント**アプリケーションが、ADKのfastapiサーバーと`/run`または`/run_sse`エンドポイントを介して対話する場合。ADKのfastapiサーバーは、**エージェントクライアント**アプリケーションと同じサーバーまたは異なるサーバーに設定できます。

2番目のケースは1番目のケースの特殊なケースです。なぜなら、`/run`または`/run_sse`エンドポイントも`runner.run_async`を呼び出すからです。唯一の違いは：

*   エージェントを実行するためにPython関数を呼び出すか（1番目のケース）、サービスエンドポイントを呼び出すか（2番目のケース）。
*   結果のイベントがインメモリのオブジェクトか（1番目のケース）、HTTPレスポンス内のシリアライズされたJSON文字列か（2番目のケース）。

以下のセクションでは1番目のケースに焦点を当てており、それを2番目のケースに非常に簡単にマッピングできるはずです。必要に応じて、2番目のケースで処理すべきいくつかの違いについても説明します。

以下は、クライアントアプリケーションのステップバイステップのプロセスです：

**ステップ1：エージェントの実行と認証リクエストの検出**

*   `runner.run_async`を使用してエージェントとの対話を開始します。
*   yieldされたイベントを反復処理します。
*   関数呼び出しの特別な名前`adk_request_credential`を持つ特定の関数呼び出しイベントを探します。このイベントは、ユーザーの操作が必要であることを示します。ヘルパー関数を使用してこのイベントを識別し、必要な情報を抽出できます。（2番目のケースでは、ロジックは似ています。HTTPレスポンスからイベントをデシリアライズします）。

```py
# runner = Runner(...)
# session = await session_service.create_session(...)
# content = types.Content(...) # ユーザーの初期クエリ

print("\nエージェントを実行中...")
events_async = runner.run_async(
    session_id=session.id, user_id='user', new_message=content
)

auth_request_function_call_id, auth_config = None, None

async for event in events_async:
    # ヘルパーを使用して特定の認証リクエストイベントを確認
    if (auth_request_function_call := get_auth_request_function_call(event)):
        print("--> エージェントによる認証が必要です。")
        # 後で応答するために必要なIDを保存
        if not (auth_request_function_call_id := auth_request_function_call.id):
            raise ValueError(f'関数呼び出しから関数呼び出しIDを取得できません: {auth_request_function_call}')
        # auth_uriなどを含むAuthConfigを取得
        auth_config = get_auth_config(auth_request_function_call)
        break # とりあえずイベントの処理を停止し、ユーザーの操作が必要

if not auth_request_function_call_id:
    print("\n認証は不要か、エージェントが終了しました。")
    # return # または、受信した最終応答を処理
```

*ヘルパー関数 `helpers.py`：*

```py
from google.adk.events import Event
from google.adk.auth import AuthConfig # 必要な型をインポート
from google.genai import types

def get_auth_request_function_call(event: Event) -> types.FunctionCall | None:
    # イベントから特別な認証リクエスト関数呼び出しを取得
    if not event.content or not event.content.parts:
        return None
    for part in event.content.parts:
        if (
            part 
            and part.function_call 
            and part.function_call.name == 'adk_request_credential'
            and event.long_running_tool_ids 
            and part.function_call.id in event.long_running_tool_ids
        ):

            return part.function_call
    return None

def get_auth_config(auth_request_function_call: types.FunctionCall) -> AuthConfig:
    # 認証リクエスト関数呼び出しの引数からAuthConfigオブジェクトを抽出
    if not auth_request_function_call.args or not (auth_config := auth_request_function_call.args.get('auth_config')):
        raise ValueError(f'関数呼び出しから認証設定を取得できません: {auth_request_function_call}')
    if not isinstance(auth_config, AuthConfig):
        raise ValueError(f'認証設定 {auth_config} はAuthConfigのインスタンスではありません。')
    return auth_config
```

**ステップ2：認可のためのユーザーリダイレクト**

*   前のステップで抽出した`auth_config`から認可URL（`auth_uri`）を取得します。
*   **重要なこととして、** アプリケーションの`redirect_uri`をこの`auth_uri`にクエリパラメータとして追加します。この`redirect_uri`は、OAuthプロバイダーに事前登録されている必要があります（例：[Google Cloud Console](https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred)、[Okta管理パネル](https://developer.okta.com/docs/guides/sign-into-web-app-redirect/spring-boot/main/#create-an-app-integration-in-the-admin-console)）。
*   ユーザーをこの完全なURLに誘導します（例：ブラウザで開く）。

```py
# （認証が必要と検出された後の続き）

if auth_request_function_call_id and auth_config:
    # AuthConfigからベースの認可URLを取得
    base_auth_uri = auth_config.exchanged_auth_credential.oauth2.auth_uri

    if base_auth_uri:
        redirect_uri = 'http://localhost:8000/callback' # OAuthクライアントアプリの設定と一致させる必要がある
        # redirect_uriを追加（本番環境ではurlencodeを使用）
        auth_request_uri = base_auth_uri + f'&redirect_uri={redirect_uri}'
        # ここで、エンドユーザーをこのauth_request_uriにリダイレクトするか、ブラウザで開くように依頼する必要があります
        # このauth_request_uriは対応する認証プロバイダーによって提供され、エンドユーザーはログインしてアプリケーションが自分のデータにアクセスすることを承認する必要があります
        # その後、認証プロバイダーはエンドユーザーを提供したredirect_uriにリダイレクトします
        # 次のステップ：ユーザーからこのコールバックURLを取得する（またはWebサーバーハンドラから）
    else:
         print("エラー：auth_configにAuth URIが見つかりません。")
         # エラーを処理
```

**ステップ3：リダイレクトコールバックの処理（クライアント）**

*   アプリケーションには、ユーザーがプロバイダーでアプリケーションを承認した後にユーザーを受け取るためのメカニズム（例：`redirect_uri`でのWebサーバールート）が必要です。
*   プロバイダーは、`authorization_code`（および潜在的に`state`、`scope`）をクエリパラメータとしてURLに追加して、ユーザーを`redirect_uri`にリダイレクトします。
*   この着信リクエストから**完全なコールバックURL**をキャプチャします。
*   （このステップは、メインのエージェント実行ループの外で、Webサーバーまたは同等のコールバックハンドラ内で行われます。）

**ステップ4：認証結果をADKに送り返す（クライアント）**

*   完全なコールバックURL（認可コードを含む）を取得したら、クライアントステップ1で保存した`auth_request_function_call_id`と`auth_config`オブジェクトを取得します。
*   キャプチャしたコールバックURLを`exchanged_auth_credential.oauth2.auth_response_uri`フィールドに設定します。また、`exchanged_auth_credential.oauth2.redirect_uri`に使用したリダイレクトURIが含まれていることを確認します。
*   `types.Content`オブジェクトを作成し、`types.Part`に`types.FunctionResponse`を含めます。
      *   `name`を`"adk_request_credential"`に設定します。（注：これはADKが認証を進めるための特別な名前です。他の名前は使用しないでください。）
      *   `id`を保存した`auth_request_function_call_id`に設定します。
      *   `response`に、*更新された*`AuthConfig`オブジェクトの*シリアライズされた*（例：`.model_dump()`）ものを設定します。
*   この`FunctionResponse`コンテンツを`new_message`として渡し、同じセッションに対して`runner.run_async`を**再度**呼び出します。

```py
# （ユーザー操作後の続き）

    # コールバックURLの取得をシミュレート（例：ユーザーのペーストやWebハンドラから）
    auth_response_uri = await get_user_input(
        f'完全なコールバックURLをここに貼り付けてください：\n> '
    )
    auth_response_uri = auth_response_uri.strip() # 入力を整形

    if not auth_response_uri:
        print("コールバックURLが提供されませんでした。中止します。")
        return

    # 受信したAuthConfigをコールバックの詳細で更新
    auth_config.exchanged_auth_credential.oauth2.auth_response_uri = auth_response_uri
    # トークン交換で必要になる可能性があるため、使用したredirect_uriも含める
    auth_config.exchanged_auth_credential.oauth2.redirect_uri = redirect_uri

    # FunctionResponse Contentオブジェクトを作成
    auth_content = types.Content(
        role='user', # FunctionResponseを送信する際のロールは'user'にできる
        parts=[
            types.Part(
                function_response=types.FunctionResponse(
                    id=auth_request_function_call_id,       # 元のリクエストへのリンク
                    name='adk_request_credential', # フレームワークの特別な関数名
                    response=auth_config.model_dump() # *更新された*AuthConfigを送り返す
                )
            )
        ],
    )

    # --- 実行再開 ---
    print("\n認証詳細をエージェントに送り返しています...")
    events_async_after_auth = runner.run_async(
        session_id=session.id,
        user_id='user',
        new_message=auth_content, # FunctionResponseを送り返す
    )

    # --- 最終的なエージェント出力の処理 ---
    print("\n--- 認証後のエージェント応答 ---")
    async for event in events_async_after_auth:
        # イベントを通常通り処理し、ツール呼び出しが成功することを期待する
        print(event) # 検査のために完全なイベントを出力
```

**ステップ5：ADKがトークン交換とツール再試行を処理し、ツールの結果を取得**

*   ADKは`adk_request_credential`に対する`FunctionResponse`を受け取ります。
*   更新された`AuthConfig`内の情報（コードを含むコールバックURLなど）を使用して、プロバイダーのトークンエンドポイントでOAuthの**トークン交換**を実行し、アクセストークン（および場合によってはリフレッシュトークン）を取得します。
*   ADKは、これらのトークンをセッション状態に設定することで内部的に利用可能にします。
*   ADKは、最初に認証が不足していたために失敗した元のツール呼び出しを**自動的に再試行**します。
*   今回は、ツールは（`tool_context.get_auth_response()`を介して）有効なトークンを見つけ、認証されたAPI呼び出しを正常に実行します。
*   エージェントはツールから実際の_resultを受け取り、ユーザーへの最終的な応答を生成します。

---

認証応答フローのシーケンス図（エージェントクライアントが認証応答を送り返し、ADKがツール呼び出しを再試行する場合）は以下のようになります：

![Authentication](../assets/auth_part2.svg)

## ジャーニー2：認証が必要なカスタムツール（`FunctionTool`）の構築

このセクションでは、新しいADKツールを作成する際に、カスタムPython関数*内*で認証ロジックを実装することに焦点を当てます。例として`FunctionTool`を実装します。

### 前提条件

関数のシグネチャには、*必ず*[`tool_context: ToolContext`](../tools/index.md#tool-context)を含める必要があります。ADKは、状態や認証メカニズムへのアクセスを提供するこのオブジェクトを自動的に注入します。

```py
from google.adk.tools import FunctionTool, ToolContext
from typing import Dict

def my_authenticated_tool_function(param1: str, ..., tool_context: ToolContext) -> dict:
    # ... あなたのロジック ...
    pass

my_tool = FunctionTool(func=my_authenticated_tool_function)
```

### ツール関数内の認証ロジック

関数内で以下のステップを実装します：

**ステップ1：キャッシュされた有効な認証情報の確認**

ツール関数内で、まず有効な認証情報（アクセストークン/リフレッシュトークンなど）が、このセッションの以前の実行から既に保存されているかどうかを確認します。現在のセッションの認証情報は`tool_context.invocation_context.session.state`（状態の辞書）に保存されている必要があります。`tool_context.invocation_context.session.state.get(credential_name, None)`をチェックして、既存の認証情報の有無を確認します。

```py
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# ツール関数内
TOKEN_CACHE_KEY = "my_tool_tokens" # 一意のキーを選択
SCOPES = ["scope1", "scope2"] # 必要なスコープを定義

creds = None
cached_token_info = tool_context.state.get(TOKEN_CACHE_KEY)
if cached_token_info:
    try:
        creds = Credentials.from_authorized_user_info(cached_token_info, SCOPES)
        if not creds.valid and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            tool_context.state[TOKEN_CACHE_KEY] = json.loads(creds.to_json()) # キャッシュを更新
        elif not creds.valid:
            creds = None # 無効、再認証が必要
            tool_context.state[TOKEN_CACHE_KEY] = None
    except Exception as e:
        print(f"キャッシュされた認証情報の読み込み/リフレッシュ中にエラーが発生しました: {e}")
        creds = None
        tool_context.state[TOKEN_CACHE_KEY] = None

if creds and creds.valid:
    # ステップ5に進む：認証済みAPI呼び出しを行う
    pass
else:
    # ステップ2に進む...
    pass
```

**ステップ2：クライアントからの認証応答の確認**

*   ステップ1で有効な認証情報が得られなかった場合、クライアントが対話型フローを完了したかどうかを`exchanged_credential = tool_context.get_auth_response()`を呼び出して確認します。
*   これは、クライアントから送り返された更新済みの`exchanged_credential`オブジェクト（`auth_response_uri`にコールバックURLを含む）を返します。

```py
# ツールで設定されたauth_schemeとauth_credentialを使用。
# exchanged_credential: AuthCredential | None

exchanged_credential = tool_context.get_auth_response(AuthConfig(
  auth_scheme=auth_scheme,
  raw_auth_credential=auth_credential,
))
# exchanged_credentialがNoneでない場合、認証応答から交換された認証情報が既に存在する。
if exchanged_credential:
   # ADKは既にアクセストークンを交換済み
        access_token = exchanged_credential.oauth2.access_token
        refresh_token = exchanged_credential.oauth2.refresh_token
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri=auth_scheme.flows.authorizationCode.tokenUrl,
            client_id=auth_credential.oauth2.client_id,
            client_secret=auth_credential.oauth2.client_secret,
            scopes=list(auth_scheme.flows.authorizationCode.scopes.keys()),
        )
    # セッション状態にトークンをキャッシュし、APIを呼び出し、ステップ5に進む
```

**ステップ3：認証リクエストの開始**

有効な認証情報（ステップ1）も認証応答（ステップ2）も見つからない場合、ツールはOAuthフローを開始する必要があります。AuthSchemeと初期のAuthCredentialを定義し、`tool_context.request_credential()`を呼び出します。認可が必要であることを示す応答を返します。

```py
# ツールで設定されたauth_schemeとauth_credentialを使用。

  tool_context.request_credential(AuthConfig(
    auth_scheme=auth_scheme,
    raw_auth_credential=auth_credential,
  ))
  return {'pending': True, 'message': 'ユーザー認証を待っています。'}

# request_credentialを設定することで、ADKは保留中の認証イベントを検出します。実行を一時停止し、エンドユーザーにログインを求めます。
```

**ステップ4：認可コードをトークンに交換**

ADKは自動的にOAuth認可URLを生成し、それをエージェントクライアントアプリケーションに提示します。エージェントクライアントアプリケーションは、ジャーニー1で説明したのと同じ方法で、ユーザーを認可URL（`redirect_uri`が付加された）にリダイレクトする必要があります。ユーザーが認可URLに従ってログインフローを完了し、ADKがエージェントクライアントアプリケーションから認証コールバックURLを抽出すると、自動的に認証コードを解析し、認証トークンを生成します。次のツール呼び出し時に、ステップ2の`tool_context.get_auth_response`には、後続のAPI呼び出しで使用するための有効な認証情報が含まれます。

**ステップ5：取得した認証情報のキャッシュ**

ADKからトークンを正常に取得した後（ステップ2）、またはトークンがまだ有効な場合（ステップ1）、新しい`Credentials`オブジェクトを`tool_context.state`に（シリアライズして、例：JSONとして）キャッシュキーを使用して**直ちに保存**します。

```py
# ツール関数内、'creds'を取得した後（リフレッシュされたか、新しく交換されたか）
# 新しい/リフレッシュされたトークンをキャッシュ
tool_context.state[TOKEN_CACHE_KEY] = json.loads(creds.to_json())
print(f"DEBUG: トークンをキー: {TOKEN_CACHE_KEY} でキャッシュ/更新しました")
# ステップ6に進む（API呼び出し）```

**ステップ6：認証済みAPI呼び出しの実行**

*   有効な`Credentials`オブジェクト（ステップ1またはステップ4からの`creds`）を取得したら、それを使用して、適切なクライアントライブラリ（`googleapiclient`、`requests`など）を使用して保護されたAPIへの実際の呼び出しを行います。`credentials=creds`引数を渡します。
*   エラーハンドリング、特に`HttpError` 401/403を含めます。これは、呼び出しの間にトークンが期限切れになったか失効したことを意味する可能性があります。そのようなエラーが発生した場合は、キャッシュされたトークンをクリアし（`tool_context.state.pop(...)`）、再認証を強制するために`auth_required`ステータスを再度返すことを検討してください。

```py
# ツール関数内、有効な'creds'オブジェクトを使用
# 続行する前にcredsが有効であることを確認
if not creds or not creds.valid:
   return {"status": "error", "error_message": "有効な認証情報なしでは続行できません。"}

try:
   service = build("calendar", "v3", credentials=creds) # 例
   api_result = service.events().list(...).execute()
   # ステップ7に進む
except Exception as e:
   # APIエラーを処理（例：401/403をチェックし、キャッシュをクリアして再認証をリクエストするかもしれない）
   print(f"エラー：API呼び出しが失敗しました: {e}")
   return {"status": "error", "error_message": f"API呼び出しが失敗しました: {e}"}
```

**ステップ7：ツール結果の返却**

*   API呼び出しが成功した後、結果をLLMにとって有用な辞書形式に処理します。
*   **重要なこととして、** データと共に**ステータス**を含めます。

```py
# ツール関数内、API呼び出しが成功した後
    processed_result = [...] # LLM用にapi_resultを処理
    return {"status": "success", "data": processed_result}
```

??? "完全なコード"

    === "ツールとエージェント"

         ```py title="tools_and_agent.py"
         --8<-- "examples/python/snippets/tools/auth/tools_and_agent.py"
         ```
    === "エージェントCLI"

         ```py title="agent_cli.py"
         --8<-- "examples/python/snippets/tools/auth/agent_cli.py"
         ```
    === "ヘルパー"

         ```py title="helpers.py"
         --8<-- "examples/python/snippets/tools/auth/helpers.py"
         ```
    === "仕様"

         ```yaml
         # ... (OpenAPI仕様は変更しないため省略) ...
         ```