# Authenticating with tools

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span><span class="lst-kotlin">Kotlin</span>
</div>

Tools often connect to external APIs and services that require credentials. ADK provides a unified authentication framework that separates **what** authentication an API requires `AuthScheme` from **how** credentials are supplied or exchanged `AuthCredential`, orchestrated by `AuthConfig`, in Python, TypeScript, and Kotlin, or `auth.CredentialProvider`, in Go.

This guide progresses from the **simplest static configurations** to the **most advanced custom authentication providers**:

1. [How ADK authentication works](#how-adk-authentication-works): Security principals, runtime lifecycle, and credential storage strategies.
2. [Static and non-interactive authentication](#static-and-non-interactive-authentication): API keys, Bearer tokens, OAuth 2.0 Client Credentials (2LO), Service Accounts, and Google Cloud ID tokens.
3. [Pre-built toolsets and external frontend tokens](#pre-built-toolsets-and-external-frontend-tokens): Attaching credentials to `OpenAPIToolset`, `GoogleApiToolset`, `McpToolset`, and reusing frontend tokens with `external_access_token_key`.
4. [Interactive user authentication (3LO OAuth 2.0 and OIDC)](#interactive-user-authentication-3lo-oauth-20-and-oidc): Pausing tool execution with `adk_request_credential` to collect user consent and exchange authorization codes.
5. [Custom authenticated tools](#custom-authenticated-tools): Building custom tools with `AuthenticatedFunctionTool`, `BaseToolset.get_auth_config()`, or manual `ToolContext` / `Context` helpers.
6. [Managed authentication and custom auth providers](#managed-authentication-and-custom-auth-providers): Delegating token lifecycles to Google Cloud Agent Identity or registering a custom `BaseAuthProvider` / `auth.CredentialProvider`.
7. [Framework components and SDK support](#framework-components-and-sdk-support): Class reference, credential types, and multi-language SDK support matrix.

!!! note "Securing tool inputs and action confirmations"
    Authentication verifies identity and access permissions, but does not validate the safety of LLM-generated tool arguments. To protect authenticated tools against prompt injection or require human approval before executing high-impact actions, see [Safety and Security](/safety/) and [Action confirmations](/tools-custom/confirmation/).

---

## How ADK authentication works

### Security principals and identity models

ADK separates authentication responsibility between two principals and supports two runtime identity models:

| Principal / Identity Model | When It Applies | How It Works | Example Artifacts |
| :--- | :--- | :--- | :--- |
| **Developer (Configuration principal)** | Before the agent runs | Registers OAuth clients, configures workload identities or vaults, defines scopes, and attaches `AuthScheme` and `AuthCredential` (or `auth.CredentialProvider` in Go) to tools. | `client_id`, `client_secret`, OpenAPI security definitions, `AuthConfig`, `GcpAuthProviderScheme` |
| **Agent Identity (Machine-to-machine / 2LO)** | Runtime-non/interactive | The agent authenticates using its own workload identity or service credentials without prompting the user. | OAuth 2.0 `clientCredentials` (2LO), Application Default Credentials (ADC), OIDC ID tokens, Agent Identity 2LO connectors |
| **End-User Identity (Delegated / 3LO & OIDC)** | Runtime/interactive | The end user grants consent during an interactive session so the agent receives a short-lived, user-scoped token to act on their behalf. | Authorization codes, `adk_request_credential`, user-scoped `access_token` and `refresh_token`, Agent Identity 3LO connectors |

### Runtime authentication lifecycle

When an agent calls a protected tool, ADK resolves credentials outside the LLM context window so raw tokens and secrets are never exposed to the model:

- **Non-interactive flows (API keys, Bearer tokens, 2LO, Service Accounts):** ADK resolves and injects the credential into the outbound request immediately without pausing the agent turn.
- **Interactive flows (3LO OAuth 2.0, OIDC):** If no valid user token exists in the session state, ADK pauses the tool call and emits a system `FunctionCall` named `adk_request_credential`, or returns `*auth.ConsentRequiredError` in Go. Your client application redirects the user to the identity provider, captures the callback URL or token, and sends it back in a `FunctionResponse` to resume the tool.

```mermaid
sequenceDiagram
    autonumber
    participant User as End User
    participant App as Client Application
    participant Runner as ADK Runner & Session
    participant LLM as Gemini LLM
    participant Tool as Protected Tool
    participant API as External Service

    User->>App: Sends prompt requiring protected data
    App->>Runner: runner.run_async() / runner.runAsync()
    Runner->>LLM: Generates turn with tool declarations
    LLM-->>Runner: FunctionCall (protected_tool)
    Runner->>Tool: Invokes tool with ToolContext / Context

    alt Non-interactive or cached token available
        Tool->>API: Executes authenticated request
        API-->>Tool: Returns resource payload
    else Interactive 3LO consent required
        Tool-->>Runner: Calls request_credential(auth_config)
        Runner-->>App: Emits Event (FunctionCall: adk_request_credential)
        App->>User: Redirects to Identity Provider consent URL
        User->>App: Grants consent & returns redirect URI / code
        App->>Runner: Sends FunctionResponse (adk_request_credential)
        Runner->>Tool: Exchanges code, caches token in session, and retries tool
        Tool->>API: Executes authenticated request with access_token
        API-->>Tool: Returns resource payload
    end

    Tool-->>Runner: Tool result
    Runner->>LLM: Summarizes tool output
    LLM-->>App: Final response
```

### Choosing a credential management strategy

| Strategy | Relative Credential Exposure | Best For | Trade-off |
| :--- | :--- | :--- | :--- |
| **Managed authentication provider**, such as Google Cloud Agent Identity | **Minimal** | Production enterprise deployments | Requires cloud infrastructure setup and IAM bindings. |
| **Self-managed with a secrets manager**, such as Secret Manager + `BaseAuthProvider` | **Low** | Multi-cloud or custom enterprise environments | You must implement secret retrieval, caching, and token rotation. |
| **Local environment variables** (`.env` files) | **Medium** | Local development and CLI prototypes | Not suitable for multi-user or production deployments. |
| **In-memory session state** (default ADK session storage) | **High** | Quick local testing of interactive 3LO flows | Tokens live in process memory and are lost on restart; do not use unencrypted in-memory storage for production credentials. |

!!! warning "Avoid storing credentials in agent memory and scrub accidental leaks"
    **Never** store long-lived secrets or refresh tokens in unencrypted in-memory session state in production, and never pass raw credentials through LLM prompts or tool return payloads where they are recorded in conversation history. If a user message or external tool output could accidentally introduce a token or secret into agent memory, prune or redact sensitive values before they are persisted using `before_model_callback` / `after_tool_callback` hooks and [Google Cloud Sensitive Data Protection (Cloud DLP)](https://cloud.google.com/sensitive-data-protection/docs).

---

## Static and non-interactive authentication

Non-interactive authentication requires no end-user prompts at runtime.

!!! warning "Prefer OAuth 2.0 and credential vaults over static API keys and downloaded service account keys"
    Static API keys and downloaded service account JSON keys (`service_account_dict` / `JSONKey`) are long-lived credentials that increase the blast radius of a leak. Reserve static API keys for legacy APIs that offer no alternative, prefer keyless **Application Default Credentials (ADC)** over downloaded JSON keys, and use **OAuth 2.0** or a **managed credential vault** ([Google Cloud Agent Identity](#managed-authentication-with-google-cloud-agent-identity-preview) or a custom [`BaseAuthProvider`](#custom-authentication-providers-baseauthprovider-and-providerfunc)) in production.

- **ADK Python:** Use the helper functions in `google.adk.tools.openapi_tool.auth.auth_helpers` (`token_to_scheme_credential`, `service_account_dict_to_scheme_credential`, `service_account_scheme_credential`) or construct `fastapi.openapi.models` schemes and `AuthCredential` objects directly.
- **ADK TypeScript:** Construct `AuthScheme` (OpenAPI 3.0 `SecuritySchemeObject`) and `AuthCredential` objects using `@google/adk`.
- **ADK Go:** Use the `CredentialProvider` constructors in `google.golang.org/adk/v2/auth` (`auth.APIKey`, `auth.StaticToken`, `auth.TokenSourceProvider`, `auth.ADC`, `auth.ServiceAccount`).
- **ADK Kotlin (Experimental):** Opt in with `@OptIn(ExperimentalAuthApi::class)` (`com.google.adk.kt.annotations.ExperimentalAuthApi`) and construct `AuthScheme` and `AuthCredential` subtypes in `com.google.adk.kt.auth` (wrapping secret strings in `Secret(...)`).

### API keys

Use an API key scheme when an external service expects a static key in a request header, query parameter, or cookie.

=== "Python"

    ```python
    from google.adk.tools.openapi_tool import OpenAPIToolset
    from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential

    auth_scheme, auth_credential = token_to_scheme_credential(
        token_type="apikey",
        location="header",  # "header", "query", or "cookie"
        name="X-Api-Key",
        credential_value="YOUR_API_KEY_STRING",
    )

    toolset = OpenAPIToolset(
        spec_str=openapi_spec_string,
        spec_str_type="yaml",
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
    )
    ```

=== "TypeScript"

    ```typescript
    import { AuthCredential, AuthCredentialTypes, AuthScheme, OpenAPIToolset } from '@google/adk';

    const authScheme: AuthScheme = {
      type: 'apiKey',
      in: 'header', // 'header', 'query', or 'cookie'
      name: 'X-Api-Key',
    };

    const authCredential: AuthCredential = {
      authType: AuthCredentialTypes.API_KEY,
      apiKey: 'YOUR_API_KEY_STRING',
    };

    const toolset = new OpenAPIToolset({
      specStr: openapiSpecString,
      specType: 'yaml',
      authScheme,
      authCredential,
    });
    ```

=== "Go"

    ```go
    import (
        "io"
        "os"

        "google.golang.org/adk/v2/auth"
        "google.golang.org/adk/v2/tool/mcptoolset"
    )

    apiKeyProvider := auth.APIKey("X-Api-Key", os.Getenv("SERVICE_API_KEY"))

    mcpTools, err := mcptoolset.New(mcptoolset.Config{
        Endpoint: "https://example.com/mcp",
        Auth:     apiKeyProvider,
    })
    if err != nil {
        return err
    }
    defer mcpTools.(io.Closer).Close()
    ```

=== "Kotlin"

    ```kotlin
    import com.google.adk.kt.annotations.ExperimentalAuthApi
    import com.google.adk.kt.auth.AuthConfig
    import com.google.adk.kt.auth.AuthCredential
    import com.google.adk.kt.auth.AuthScheme
    import com.google.adk.kt.auth.Secret

    @OptIn(ExperimentalAuthApi::class)
    val apiKeyAuthConfig = AuthConfig(
        authScheme = AuthScheme.ApiKey(
            name = "X-Api-Key",
            location = AuthScheme.ApiKey.Location.HEADER, // HEADER, QUERY, or COOKIE
        ),
        rawAuthCredential = AuthCredential.ApiKey(
            apiKey = Secret(System.getenv("SERVICE_API_KEY")),
        ),
    )
    ```

### Bearer and HTTP tokens

Use an HTTP Bearer token when you have a pre-generated token string.

=== "Python"

    ```python
    from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential

    # In ADK Python, pass token_type="oauth2Token" to create an HTTPBearer scheme
    # paired with an AuthCredentialTypes.HTTP bearer credential:
    auth_scheme, auth_credential = token_to_scheme_credential(
        token_type="oauth2Token",
        location="header",
        name="Authorization",
        credential_value="YOUR_BEARER_TOKEN",
    )
    ```

=== "TypeScript"

    ```typescript
    import { AuthCredential, AuthCredentialTypes, AuthScheme } from '@google/adk';

    const authScheme: AuthScheme = {
      type: 'http',
      scheme: 'bearer',
    };

    const authCredential: AuthCredential = {
      authType: AuthCredentialTypes.HTTP,
      http: {
        scheme: 'bearer',
        credentials: {
          token: 'YOUR_BEARER_TOKEN',
        },
      },
    };
    ```

=== "Go"

    ```go
    import (
        "os"

        "google.golang.org/adk/v2/auth"
    )

    // Static Bearer token ("Authorization: Bearer <token>")
    bearerProvider := auth.StaticToken(os.Getenv("BEARER_TOKEN"))
    ```

=== "Kotlin"

    ```kotlin
    import com.google.adk.kt.annotations.ExperimentalAuthApi
    import com.google.adk.kt.auth.AuthConfig
    import com.google.adk.kt.auth.AuthCredential
    import com.google.adk.kt.auth.AuthScheme

    @OptIn(ExperimentalAuthApi::class)
    val bearerAuthConfig = AuthConfig(
        authScheme = AuthScheme.Http.bearer(bearerFormat = "JWT"),
        rawAuthCredential = AuthCredential.Http.bearer(
            token = System.getenv("BEARER_TOKEN"),
        ),
    )
    ```

### OAuth 2.0 Client Credentials (2LO)

Use the OAuth 2.0 Client Credentials grant `clientCredentials` for machine-to-machine communication where the agent authenticates with its own `client_id` and `client_secret` rather than acting on behalf of an end user.

=== "Python"

    ```python
    from fastapi.openapi.models import OAuth2, OAuthFlowClientCredentials, OAuthFlows
    from google.adk.auth import AuthCredential, AuthCredentialTypes, OAuth2Auth
    from google.adk.tools.openapi_tool import OpenAPIToolset

    auth_scheme = OAuth2(
        flows=OAuthFlows(
            clientCredentials=OAuthFlowClientCredentials(
                tokenUrl="https://example.com/oauth2/token",
                scopes={"read:data": "Read service data"},
            )
        )
    )

    auth_credential = AuthCredential(
        auth_type=AuthCredentialTypes.OAUTH2,
        oauth2=OAuth2Auth(
            client_id="YOUR_CLIENT_ID",
            client_secret="YOUR_CLIENT_SECRET",
        ),
    )

    toolset = OpenAPIToolset(
        spec_str=openapi_spec_string,
        spec_str_type="yaml",
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
    )
    ```

=== "TypeScript"

    ```typescript
    import { AuthCredential, AuthCredentialTypes, AuthScheme, OpenAPIToolset } from '@google/adk';

    const authScheme: AuthScheme = {
      type: 'oauth2',
      flows: {
        clientCredentials: {
          tokenUrl: 'https://example.com/oauth2/token',
          scopes: { 'read:data': 'Read service data' },
        },
      },
    };

    const authCredential: AuthCredential = {
      authType: AuthCredentialTypes.OAUTH2,
      oauth2: {
        clientId: 'YOUR_CLIENT_ID',
        clientSecret: 'YOUR_CLIENT_SECRET',
      },
    };

    const toolset = new OpenAPIToolset({
      specStr: openapiSpecString,
      specType: 'yaml',
      authScheme,
      authCredential,
    });
    ```

=== "Go"

    ```go
    import (
        "context"
        "os"

        "golang.org/x/oauth2/clientcredentials"
        "google.golang.org/adk/v2/auth"
    )

    ccConfig := &clientcredentials.Config{
        ClientID:     os.Getenv("OAUTH_CLIENT_ID"),
        ClientSecret: os.Getenv("OAUTH_CLIENT_SECRET"),
        TokenURL:     "https://example.com/oauth2/token",
        Scopes:       []string{"read:data"},
    }

    oauthProvider := auth.TokenSourceProvider(ccConfig.TokenSource(context.Background()))
    ```

=== "Kotlin"

    ```kotlin
    import com.google.adk.kt.annotations.ExperimentalAuthApi
    import com.google.adk.kt.auth.AuthConfig
    import com.google.adk.kt.auth.AuthCredential
    import com.google.adk.kt.auth.AuthScheme
    import com.google.adk.kt.auth.Secret

    @OptIn(ExperimentalAuthApi::class)
    val clientCredentialsAuthConfig = AuthConfig(
        authScheme = AuthScheme.OAuth2.clientCredentials(
            tokenUrl = "https://example.com/oauth2/token",
            scopes = mapOf("read:data" to "Read service data"),
        ),
        rawAuthCredential = AuthCredential.OAuth2(
            clientId = System.getenv("OAUTH_CLIENT_ID"),
            clientSecret = Secret(System.getenv("OAUTH_CLIENT_SECRET")),
        ),
    )
    ```

### Service accounts and Application Default Credentials (ADC)

For Google Cloud APIs and internal services, authenticate using Application Default Credentials (ADC) or an explicit Google Cloud Service Account key.

=== "Python"

    ```python
    import json
    from google.adk.auth.auth_credential import ServiceAccount
    from google.adk.tools.openapi_tool import OpenAPIToolset
    from google.adk.tools.openapi_tool.auth.auth_helpers import (
        service_account_dict_to_scheme_credential,
        service_account_scheme_credential,
    )

    # Option 1: Use Application Default Credentials (ADC)
    adc_scheme, adc_credential = service_account_scheme_credential(
        ServiceAccount(
            use_default_credential=True,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
    )

    # Option 2: Use a Service Account JSON dictionary
    service_account_dict = json.loads(service_account_json_str)
    sa_scheme, sa_credential = service_account_dict_to_scheme_credential(
        config=service_account_dict,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    toolset = OpenAPIToolset(
        spec_str=openapi_spec_string,
        spec_str_type="json",
        auth_scheme=adc_scheme,
        auth_credential=adc_credential,
    )
    ```

=== "TypeScript"

    ```typescript
    import { AuthCredential, AuthCredentialTypes, AuthScheme, OpenAPIToolset } from '@google/adk';

    const authScheme: AuthScheme = {
      type: 'http',
      scheme: 'bearer',
    };

    // Option 1: Use Application Default Credentials (ADC)
    const adcCredential: AuthCredential = {
      authType: AuthCredentialTypes.SERVICE_ACCOUNT,
      serviceAccount: {
        useDefaultCredential: true,
        scopes: ['https://www.googleapis.com/auth/cloud-platform'],
      },
    };

    // Option 2: Use an explicit ServiceAccountCredential object
    const explicitSaCredential: AuthCredential = {
      authType: AuthCredentialTypes.SERVICE_ACCOUNT,
      serviceAccount: {
        scopes: ['https://www.googleapis.com/auth/cloud-platform'],
        serviceAccountCredential: {
          type: 'service_account',
          projectId: 'your-project-id',
          privateKeyId: 'your-key-id',
          privateKey: '-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n',
          clientEmail: 'your-sa@your-project.iam.gserviceaccount.com',
          clientId: '1234567890',
          authUri: 'https://accounts.google.com/o/oauth2/auth',
          tokenUri: 'https://oauth2.googleapis.com/token',
          authProviderX509CertUrl: 'https://www.googleapis.com/oauth2/v1/certs',
          clientX509CertUrl: 'https://www.googleapis.com/robot/v1/metadata/x509/...',
          universeDomain: 'googleapis.com',
        },
      },
    };

    const toolset = new OpenAPIToolset({
      specStr: openapiSpecString,
      specType: 'json',
      authScheme,
      authCredential: adcCredential,
    });
    ```

=== "Go"

    ```go
    import "google.golang.org/adk/v2/auth"

    // Option 1: Application Default Credentials (ADC)
    adcProvider := auth.ADC("https://www.googleapis.com/auth/cloud-platform")

    // Option 2: Explicit Service Account JSON key
    saProvider := auth.ServiceAccount(auth.ServiceAccountConfig{
        JSONKey: serviceAccountJSONBytes,
        Scopes:  []string{"https://www.googleapis.com/auth/cloud-platform"},
    })
    ```

=== "Kotlin"

    ```kotlin
    import com.google.adk.kt.annotations.ExperimentalAuthApi
    import com.google.adk.kt.auth.AuthCredential

    // Option 1: Application Default Credentials (ADC)
    @OptIn(ExperimentalAuthApi::class)
    val adcCredential = AuthCredential.ServiceAccount.applicationDefault(
        scopes = listOf("https://www.googleapis.com/auth/cloud-platform"),
    )

    // Option 2: Explicit ServiceAccount.Credential key
    @OptIn(ExperimentalAuthApi::class)
    val saCredential = AuthCredential.ServiceAccount.fromKey(
        key = serviceAccountKey, // AuthCredential.ServiceAccount.Credential
        scopes = listOf("https://www.googleapis.com/auth/cloud-platform"),
    )
    ```

### Google Cloud Access Tokens vs. ID Tokens

When configuring Service Account credentials in **ADK Python**, **ADK Go**, or **ADK Kotlin**, choose between an **OAuth 2.0 Access Token**, the default, and an **OpenID Connect (OIDC) ID Token** based on the target service:

| Feature | OAuth 2.0 Access Token (Default) | OIDC ID Token (`use_id_token=True` / `Audience` / `forIdToken`) |
| :--- | :--- | :--- |
| **Primary Purpose** | **Authorization:** Grants permission to call Google APIs. | **Authentication:** Proves the caller's identity to a target service. |
| **Typical Targets** | Google Cloud APIs, such as BigQuery, Cloud Storage, Agent Platform or Calendar. | Cloud Run services, Cloud Run functions, Identity-Aware Proxy (IAP), and custom IAM-secured endpoints. |
| **Required Parameter** | `scopes` / `Scopes`, list of OAuth scope URIs. | `audience` / `Audience`, the base URL or OAuth client ID of the receiving service). |
| **Token Format** | Opaque bearer string `ya29...`. | Signed JSON Web Token (JWT) verifiable by the target service. |

To mint an ID token for a Cloud Run service or IAP-protected endpoint, enable ID token mode and specify the target `audience` URL:

=== "Python"

    ```python
    from google.adk.auth.auth_credential import ServiceAccount
    from google.adk.tools.openapi_tool import OpenAPIToolset
    from google.adk.tools.openapi_tool.auth.auth_helpers import (
        service_account_scheme_credential,
    )

    sa_config = ServiceAccount(
        use_default_credential=True,
        use_id_token=True,
        audience="https://my-cloud-run-service-xyz.a.run.app",
    )

    auth_scheme, auth_credential = service_account_scheme_credential(sa_config)

    toolset = OpenAPIToolset(
        spec_str=openapi_spec_string,
        spec_str_type="json",
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
    )
    ```

=== "Go"

    ```go
    import (
        "net/http"

        "google.golang.org/adk/v2/auth"
    )

    // Setting Audience requests a Google-signed ID token instead of an access token.
    // Omit JSONKey to use Application Default Credentials (ADC).
    idTokenProvider := auth.ServiceAccount(auth.ServiceAccountConfig{
        Audience: "https://my-cloud-run-service-xyz.a.run.app",
    })

    // Wrap an http.Client or pass to mcptoolset.Config{Auth: idTokenProvider}:
    httpClient := &http.Client{
        Transport: &auth.Transport{Provider: idTokenProvider},
    }
    ```

=== "Kotlin"

    ```kotlin
    import com.google.adk.kt.annotations.ExperimentalAuthApi
    import com.google.adk.kt.auth.AuthCredential

    // Mint an OIDC ID token using Application Default Credentials (ADC)
    @OptIn(ExperimentalAuthApi::class)
    val idTokenCredential = AuthCredential.ServiceAccount.forIdToken(
        audience = "https://my-cloud-run-service-xyz.a.run.app",
    )
    ```

#### `ServiceAccount` parameter reference

| Python (`ServiceAccount`) | TypeScript (`ServiceAccount`) | Go (`ServiceAccountConfig`) | Kotlin (`AuthCredential.ServiceAccount`) | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `use_default_credential` | `useDefaultCredential` | Omit `JSONKey` | `useDefaultCredential` / `ServiceAccount.applicationDefault()` | `False` | When `True`, or when `JSONKey` is empty in Go, uses Application Default Credentials (ADC). |
| `service_account_credential` | `serviceAccountCredential` | `JSONKey` (`[]byte`) | `serviceAccountCredential` / `ServiceAccount.fromKey()` | `None` | Explicit service account key payload. Required when not using ADC. |
| `scopes` | `scopes` | `Scopes` (`[]string`) | `scopes` (`List<String>`) | `None` | OAuth 2.0 scopes for access tokens. Required when requesting access tokens with an explicit key; ignored when requesting an ID token. |
| `use_id_token` | `useIdToken`, interface field only; not exchanged by `ServiceAccountCredentialExchanger` | Inferred when `Audience != ""` | `useIdToken` / `ServiceAccount.forIdToken()` | `False` | When `True`, or when `Audience` is not empty in Go, mints an OIDC ID token instead of an access token. |
| `audience` | `audience`, interface field only; not exchanged by `ServiceAccountCredentialExchanger` | `Audience` (`string`) | `audience` (`String`) | `None` | Target audience URI for the ID token. Required when `use_id_token` / `useIdToken` is `True`. |

---

## Pre-built toolsets and external frontend tokens

ADK toolsets accept authentication configuration directly in their constructors or helper methods:

| Toolset | How to Configure Authentication | Supported SDKs |
| :--- | :--- | :--- |
| **`OpenAPIToolset` / `RestApiTool`** | Pass `auth_scheme` and `auth_credential` (`authScheme` and `authCredential` in TypeScript) to the constructor. | Python, TypeScript |
| **`GoogleApiToolset` subclasses** (`CalendarToolset`, `GmailToolset`, `DocsToolset`, `SheetsToolset`, `SlidesToolset`, `YoutubeToolset`) | Pass `client_id` and `client_secret` to the constructor, or call `.configure_auth(client_id, client_secret)` on the toolset instance. | Python |
| **`McpToolset` / `mcptoolset`** | Pass `auth_scheme` and `auth_credential` to `McpToolset` in Python, or `Auth` (`auth.CredentialProvider`) to `mcptoolset.Config` in Go. | Python, Go |
| **`BigQueryToolset` / `SpannerToolset`** | Pass a credentials config (such as `BigQueryCredentialsConfig`) with client credentials or `external_access_token_key`. | Python |
| **`ApplicationIntegrationToolset`** | Uses Application Default Credentials by default, or accepts a `service_account_json` / `serviceAccountJson` string. | Python, Java |

### Configuring Google API toolsets (Python)

Pre-built Google Workspace and Google API toolsets in ADK Python include a built-in OAuth 2.0 scheme and provide `.configure_auth()` to register your OAuth client credentials:

```python
from google.adk.tools.google_api_tool import CalendarToolset

calendar_toolset = CalendarToolset(
    client_id="YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com",
    client_secret="YOUR_GOOGLE_CLIENT_SECRET",
)

# Or update credentials on an existing toolset instance:
calendar_toolset.configure_auth(
    client_id="YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com",
    client_secret="YOUR_GOOGLE_CLIENT_SECRET",
)
```

### Reusing frontend tokens from session state (`external_access_token_key`)

When your web or mobile frontend already authenticates the user and holds a valid OAuth access token, you can pass that token directly into the ADK session state in Python instead of running a second OAuth redirect inside the agent.

The `external_access_token_key` parameter on Google tool credentials configs, such as `BigQueryCredentialsConfig`, instructs the toolset to read the bearer token from `tool_context.state[key]` on each tool invocation. It is mutually exclusive with `credentials`, `client_id`, `client_secret`, and `scopes`:

```python
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.genai import types

TOKEN_STATE_KEY = "temp:user_bigquery_access_token"

# 1. Point the toolset at the session state key holding the frontend token
credentials_config = BigQueryCredentialsConfig(
    external_access_token_key=TOKEN_STATE_KEY
)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)

agent = Agent(
    name="bigquery_agent",
    model="gemini-2.5-flash",
    instruction="Use BigQuery tools to answer questions about user datasets.",
    tools=[bigquery_toolset],
)

# 2. Seed or update the token in session state before running the turn
async def run_with_frontend_token(user_id: str, frontend_oauth_token: str):
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="analytics_app",
        user_id=user_id,
        state={TOKEN_STATE_KEY: frontend_oauth_token},
    )
    runner = Runner(
        agent=agent,
        app_name="analytics_app",
        session_service=session_service,
    )
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text="List the datasets in my project.")],
    )
    async for event in runner.run_async(
        user_id=user_id, session_id=session.id, new_message=content
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)
```

!!! tip "Use the `temp:` prefix for short-lived tokens"
    Prefixing the state key with `temp:`; for example, `temp:user_bigquery_access_token` scopes the token to the current invocation so it is not written to persistent database storage.

---

## Interactive user authentication (3LO OAuth 2.0 and OIDC)

When a tool requires 3-legged OAuth 2.0 `authorizationCode` or OpenID Connect (OIDC) user consent, ADK coordinates a 4-step interactive handshake between your agent and your client application.

### Configuring 3LO OAuth 2.0 or OpenID Connect on a toolset

Configure `OpenAPIToolset`, or `AuthConfig` in Kotlin, with an OAuth 2.0 `authorizationCode` flow or an OpenID Connect scheme:

=== "Python (OAuth 2.0 3LO)"

    ```python
    from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
    from google.adk.auth import AuthCredential, AuthCredentialTypes, OAuth2Auth
    from google.adk.tools.openapi_tool import OpenAPIToolset

    auth_scheme = OAuth2(
        flows=OAuthFlows(
            authorizationCode=OAuthFlowAuthorizationCode(
                authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
                tokenUrl="https://oauth2.googleapis.com/token",
                scopes={
                    "https://www.googleapis.com/auth/calendar.readonly": "Read calendar events"
                },
            )
        )
    )

    auth_credential = AuthCredential(
        auth_type=AuthCredentialTypes.OAUTH2,
        oauth2=OAuth2Auth(
            client_id="YOUR_CLIENT_ID",
            client_secret="YOUR_CLIENT_SECRET",
        ),
    )

    toolset = OpenAPIToolset(
        spec_str=openapi_spec_string,
        spec_str_type="yaml",
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
    )
    ```

=== "TypeScript (OAuth 2.0 3LO)"

    ```typescript
    import { AuthCredential, AuthCredentialTypes, AuthScheme, OpenAPIToolset } from '@google/adk';

    const authScheme: AuthScheme = {
      type: 'oauth2',
      flows: {
        authorizationCode: {
          authorizationUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
          tokenUrl: 'https://oauth2.googleapis.com/token',
          scopes: {
            'https://www.googleapis.com/auth/calendar.readonly': 'Read calendar events',
          },
        },
      },
    };

    const authCredential: AuthCredential = {
      authType: AuthCredentialTypes.OAUTH2,
      oauth2: {
        clientId: 'YOUR_CLIENT_ID',
        clientSecret: 'YOUR_CLIENT_SECRET',
      },
    };

    const toolset = new OpenAPIToolset({
      specStr: openapiSpecString,
      specType: 'yaml',
      authScheme,
      authCredential,
    });
    ```

=== "Kotlin (OAuth 2.0 3LO)"

    ```kotlin
    import com.google.adk.kt.annotations.ExperimentalAuthApi
    import com.google.adk.kt.auth.AuthConfig
    import com.google.adk.kt.auth.AuthCredential
    import com.google.adk.kt.auth.AuthScheme
    import com.google.adk.kt.auth.Secret

    @OptIn(ExperimentalAuthApi::class)
    val calendarAuthConfig = AuthConfig(
        authScheme = AuthScheme.OAuth2.authorizationCode(
            authorizationUrl = "https://accounts.google.com/o/oauth2/v2/auth",
            tokenUrl = "https://oauth2.googleapis.com/token",
            scopes = mapOf(
                "https://www.googleapis.com/auth/calendar.readonly" to "Read calendar events"
            ),
        ),
        rawAuthCredential = AuthCredential.OAuth2(
            clientId = System.getenv("GOOGLE_OAUTH_CLIENT_ID"),
            clientSecret = Secret(System.getenv("GOOGLE_OAUTH_CLIENT_SECRET")),
        ),
    )
    ```

=== "Python (OpenID Connect)"

    ```python
    from google.adk.auth import (
        AuthCredential,
        AuthCredentialTypes,
        OAuth2Auth,
        OpenIdConnectWithConfig,
    )
    from google.adk.tools.openapi_tool import OpenAPIToolset

    auth_scheme = OpenIdConnectWithConfig(
        openIdConnectUrl="https://accounts.google.com/.well-known/openid-configuration",
        authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
        token_endpoint="https://oauth2.googleapis.com/token",
        scopes=["openid", "email", "profile"],
    )

    auth_credential = AuthCredential(
        auth_type=AuthCredentialTypes.OPEN_ID_CONNECT,
        oauth2=OAuth2Auth(
            client_id="YOUR_CLIENT_ID",
            client_secret="YOUR_CLIENT_SECRET",
        ),
    )

    toolset = OpenAPIToolset(
        spec_str=openapi_spec_string,
        spec_str_type="yaml",
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
    )
    ```

=== "TypeScript (OpenID Connect)"

    ```typescript
    import {
      AuthCredential,
      AuthCredentialTypes,
      OpenAPIToolset,
      OpenIdConnectWithConfig,
    } from '@google/adk';

    const authScheme: OpenIdConnectWithConfig = {
      type: 'openIdConnect',
      openIdConnectUrl: 'https://accounts.google.com/.well-known/openid-configuration',
      authorizationEndpoint: 'https://accounts.google.com/o/oauth2/v2/auth',
      tokenEndpoint: 'https://oauth2.googleapis.com/token',
      scopes: ['openid', 'email', 'profile'],
    };

    const authCredential: AuthCredential = {
      authType: AuthCredentialTypes.OPEN_ID_CONNECT,
      oauth2: {
        clientId: 'YOUR_CLIENT_ID',
        clientSecret: 'YOUR_CLIENT_SECRET',
      },
    };

    const toolset = new OpenAPIToolset({
      specStr: openapiSpecString,
      specType: 'yaml',
      authScheme,
      authCredential,
    });
    ```

=== "Kotlin (OpenID Connect)"

    ```kotlin
    import com.google.adk.kt.annotations.ExperimentalAuthApi
    import com.google.adk.kt.auth.AuthConfig
    import com.google.adk.kt.auth.AuthCredential
    import com.google.adk.kt.auth.AuthScheme
    import com.google.adk.kt.auth.Secret

    @OptIn(ExperimentalAuthApi::class)
    val oidcAuthConfig = AuthConfig(
        authScheme = AuthScheme.OpenIdConnect(
            authorizationEndpoint = "https://accounts.google.com/o/oauth2/v2/auth",
            tokenEndpoint = "https://oauth2.googleapis.com/token",
            scopes = listOf("openid", "email", "profile"),
        ),
        rawAuthCredential = AuthCredential.OAuth2(
            variant = AuthCredential.OAuth2.Variant.OPEN_ID_CONNECT,
            clientId = System.getenv("OIDC_CLIENT_ID"),
            clientSecret = Secret(System.getenv("OIDC_CLIENT_SECRET")),
        ),
    )
    ```

### Handling the interactive `adk_request_credential` flow in your client

When testing locally with `adk web`, the browser UI handles the OAuth popup automatically (provided `http://localhost:8000/dev-ui` is registered as an authorized redirect URI on your OAuth client). When building a custom web, CLI, or backend application, implement the 4-step loop below:

1. **Detect `adk_request_credential`:** Inspect events returned by `runner.run_async()` (`runner.runAsync()` in TypeScript) for a `FunctionCall` with `name == "adk_request_credential"` (`REQUEST_CREDENTIAL_FUNCTION_CALL_NAME`).
2. **Extract `auth_uri` and redirect the user:** Read `exchanged_auth_credential.oauth2.auth_uri` (`exchangedAuthCredential.oauth2.authUri` in TypeScript) from the function call arguments, append your application's `redirect_uri`, and direct the user to that URL to grant consent.
3. **Send the callback URL in a `FunctionResponse`:** Capture the full redirect URL returned by the identity provider (containing the `code` and `state` parameters), attach it to `auth_config.exchanged_auth_credential.oauth2.auth_response_uri` (`authResponseUri`), and send a `FunctionResponse` matching the original `adk_request_credential` call ID.
4. **Resume execution:** Pass the `FunctionResponse` message into `runner.run_async()`. ADK exchanges the authorization code for tokens, stores them in the session, retries the tool, and streams the final answer.

=== "Python"

    ```python
    from google.adk.auth import AuthConfig
    from google.genai import types

    # Steps 1 & 2: Detect adk_request_credential and extract the consent URL
    auth_request_call_id = None
    auth_config_dict = None

    async for event in runner.run_async(
        user_id=user_id, session_id=session.id, new_message=user_message
    ):
        for fn_call in event.get_function_calls():
            if fn_call.name == "adk_request_credential":
                auth_request_call_id = fn_call.id
                auth_config_dict = fn_call.args.get("auth_config")
                break

    if auth_config_dict:
        auth_config = AuthConfig.model_validate(auth_config_dict)
        base_auth_uri = auth_config.exchanged_auth_credential.oauth2.auth_uri
        redirect_uri = "http://localhost:8000/callback"

        # Redirect the user to: f"{base_auth_uri}&redirect_uri={redirect_uri}"
        # After the user grants consent, capture the full callback URL:
        full_callback_url = await wait_for_oauth_callback()

        # Step 3: Populate the callback URL and construct the FunctionResponse
        auth_config.exchanged_auth_credential.oauth2.auth_response_uri = full_callback_url
        auth_config.exchanged_auth_credential.oauth2.redirect_uri = redirect_uri

        auth_content = types.Content(
            role="user",
            parts=[
                types.Part(
                    function_response=types.FunctionResponse(
                        id=auth_request_call_id,
                        name="adk_request_credential",
                        response=auth_config.model_dump(),
                    )
                )
            ],
        )

        # Step 4: Resume the runner with the completed credentials
        async for event in runner.run_async(
            user_id=user_id, session_id=session.id, new_message=auth_content
        ):
            if event.is_final_response():
                print(event.content.parts[0].text)
    ```

=== "TypeScript"

    ```typescript
    import {
      AuthConfig,
      getFunctionCalls,
      isFinalResponse,
      REQUEST_CREDENTIAL_FUNCTION_CALL_NAME,
    } from '@google/adk';
    import { Content } from '@google/genai';

    // Steps 1 & 2: Detect adk_request_credential and extract the consent URL
    let authRequestCallId: string | undefined;
    let authConfig: AuthConfig | undefined;

    for await (const event of runner.runAsync({
      userId,
      sessionId: session.id,
      newMessage: userMessage,
    })) {
      for (const fnCall of getFunctionCalls(event)) {
        if (fnCall.name === REQUEST_CREDENTIAL_FUNCTION_CALL_NAME) {
          authRequestCallId = fnCall.id;
          authConfig = fnCall.args?.['authConfig'] as unknown as AuthConfig;
          break;
        }
      }
    }

    if (authConfig && authRequestCallId && authConfig.exchangedAuthCredential?.oauth2) {
      const baseAuthUri = authConfig.exchangedAuthCredential.oauth2.authUri;
      const redirectUri = 'http://localhost:8000/callback';

      // Redirect the user to `${baseAuthUri}&redirect_uri=${encodeURIComponent(redirectUri)}`
      // Capture the full callback URL returned after user consent:
      const fullCallbackUrl = await waitForOAuthCallback();

      // Step 3: Populate the callback URL and construct the FunctionResponse
      authConfig.exchangedAuthCredential.oauth2.authResponseUri = fullCallbackUrl;
      authConfig.exchangedAuthCredential.oauth2.redirectUri = redirectUri;

      const authContent: Content = {
        role: 'user',
        parts: [
          {
            functionResponse: {
              id: authRequestCallId,
              name: REQUEST_CREDENTIAL_FUNCTION_CALL_NAME,
              response: authConfig as unknown as Record<string, unknown>,
            },
          },
        ],
      };

      // Step 4: Resume the runner with the completed credentials
      for await (const event of runner.runAsync({
        userId,
        sessionId: session.id,
        newMessage: authContent,
      })) {
        if (isFinalResponse(event)) {
          console.log(event.content?.parts?.[0]?.text);
        }
      }
    }
    ```

??? example "Complete runnable Python CLI example (`tools_and_agent.py`, `agent_cli.py`, `helpers.py`)"

    The following complete sample demonstrates an interactive OAuth 2.0 / OIDC CLI flow in Python:

    === "`tools_and_agent.py`"

        ```python
        --8<-- "examples/python/snippets/tools/auth/tools_and_agent.py"
        ```

    === "`agent_cli.py`"

        ```python
        --8<-- "examples/python/snippets/tools/auth/agent_cli.py"
        ```

    === "`helpers.py`"

        ```python
        --8<-- "examples/python/snippets/tools/auth/helpers.py"
        ```

---

## Custom authenticated tools

When building your own tools instead of using `OpenAPIToolset`, ADK provides three patterns depending on how much control you need over the credential lifecycle.

### Option A: Declarative `AuthenticatedFunctionTool` (Python, Experimental)

In ADK Python, `AuthenticatedFunctionTool` wraps a function and manages credential lookup and `request_credential` automatically. Define a `credential: AuthCredential` parameter on your function, and ADK hides `credential` from the LLM schema and injects the resolved `AuthCredential` only after authentication succeeds:

```python
import httpx
from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
from google.adk.auth import AuthConfig, AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.tools.authenticated_function_tool import AuthenticatedFunctionTool

auth_scheme = OAuth2(
    flows=OAuthFlows(
        authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl="https://github.com/login/oauth/authorize",
            tokenUrl="https://github.com/login/oauth/access_token",
            scopes={"read:user": "Read GitHub user profile"},
        )
    )
)

auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(
        client_id="YOUR_GITHUB_CLIENT_ID",
        client_secret="YOUR_GITHUB_CLIENT_SECRET",
    ),
)

async def get_github_profile(credential: AuthCredential) -> dict:
    """Fetches the authenticated user's GitHub profile."""
    # After CredentialManager exchanges the OAuth code, the bearer token is
    # available on credential.http.credentials.token:
    token = credential.http.credentials.token
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()

github_profile_tool = AuthenticatedFunctionTool(
    func=get_github_profile,
    auth_config=AuthConfig(
        auth_scheme=auth_scheme,
        raw_auth_credential=auth_credential,
    ),
)
```

### Option B: Custom `BaseToolset` with `get_auth_config()` (Python)

When packaging multiple related tools into a custom `BaseToolset` subclass in Python, override `get_auth_config()`. ADK resolves the toolset's `AuthConfig` and populates `exchanged_auth_credential` before calling `get_tools()` or executing tools in the toolset:

```python
from typing import Optional
from fastapi.openapi.models import OAuth2, OAuthFlowClientCredentials, OAuthFlows
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.auth import AuthConfig, AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import BaseToolset

class InternalCrmToolset(BaseToolset):
    def __init__(self, client_id: str, client_secret: str):
        super().__init__()
        scheme = OAuth2(
            flows=OAuthFlows(
                clientCredentials=OAuthFlowClientCredentials(
                    tokenUrl="https://crm.example.com/oauth/token",
                    scopes={"crm:read": "Read CRM records"},
                )
            )
        )
        credential = AuthCredential(
            auth_type=AuthCredentialTypes.OAUTH2,
            oauth2=OAuth2Auth(client_id=client_id, client_secret=client_secret),
        )
        self._auth_config = AuthConfig(
            auth_scheme=scheme,
            raw_auth_credential=credential,
        )

    def get_auth_config(self) -> Optional[AuthConfig]:
        return self._auth_config

    async def get_tools(
        self, readonly_context: Optional[ReadonlyContext] = None
    ) -> list[BaseTool]:
        # ADK populates self._auth_config.exchanged_auth_credential before calling get_tools()
        return []
```

### Option C: Manual `FunctionTool` inspection via `ToolContext` / `Context`

If you need custom branching logic (for example, returning a fallback response when the user has not authenticated), call `tool_context.get_auth_response()` (`toolContext.getAuthResponse()` in TypeScript, `context.getAuthResponse()` in Kotlin) and `tool_context.request_credential()` (`toolContext.requestCredential()` in TypeScript, `context.requestCredential()` in Kotlin) directly inside a `FunctionTool`:

=== "Python"

    ```python
    from google.adk.auth import AuthConfig
    from google.adk.tools import FunctionTool, ToolContext

    def fetch_protected_orders(
        order_id: str,
        tool_context: ToolContext,
    ) -> dict:
        """Retrieves order details using manual ToolContext credential checks."""
        # 1. Check whether the session already holds a resolved credential
        cred = tool_context.get_auth_response(my_auth_config)

        if not cred or not cred.oauth2 or not cred.oauth2.access_token:
            # 2. Pause execution and emit adk_request_credential
            tool_context.request_credential(my_auth_config)
            return {"status": "pending", "message": "User authorization required."}

        # 3. Use the resolved access token
        access_token = cred.oauth2.access_token
        return {"status": "ok", "order_id": order_id, "authenticated": bool(access_token)}

    order_tool = FunctionTool(func=fetch_protected_orders)
    ```

=== "TypeScript"

    ```typescript
    import { AuthConfig, Context, FunctionTool } from '@google/adk';
    import { z } from 'zod';

    const fetchProtectedOrders = new FunctionTool({
      name: 'fetch_protected_orders',
      description: 'Retrieves order details using manual Context credential checks.',
      parameters: z.object({
        orderId: z.string(),
      }),
      execute: async ({ orderId }, toolContext?: Context) => {
        if (!toolContext) {
          throw new Error('Tool execution Context is required.');
        }

        // 1. Check whether the session already holds a resolved credential
        const cred = toolContext.getAuthResponse(myAuthConfig as AuthConfig);
        const accessToken = cred?.oauth2?.accessToken;

        if (!accessToken) {
          // 2. Pause execution and emit adk_request_credential
          toolContext.requestCredential(myAuthConfig as AuthConfig);
          return { status: 'pending', message: 'User authorization required.' };
        }

        // 3. Use the resolved access token
        return { status: 'ok', orderId, authenticated: true };
      },
    });
    ```

=== "Kotlin"

    ```kotlin
    import com.google.adk.kt.agents.Context
    import com.google.adk.kt.annotations.ExperimentalAuthApi
    import com.google.adk.kt.annotations.SecretAccess
    import com.google.adk.kt.auth.AuthConfig
    import com.google.adk.kt.auth.AuthCredential

    @OptIn(ExperimentalAuthApi::class, SecretAccess::class)
    suspend fun fetchProtectedOrders(
        orderId: String,
        context: Context,
        myAuthConfig: AuthConfig,
    ): Map<String, Any> {
        // 1. Check whether the session already holds a credential returned by the app
        val cred = context.getAuthResponse(myAuthConfig) as? AuthCredential.OAuth2
        val accessToken = cred?.accessToken?.reveal()

        if (accessToken.isNullOrEmpty()) {
            // 2. Record the sign-in request on the current tool call's EventActions
            context.requestCredential(myAuthConfig)
            return mapOf("status" to "pending", "message" to "User authorization required.")
        }

        // 3. Use the resolved access token
        return mapOf("status" to "ok", "orderId" to orderId, "authenticated" to true)
    }
    ```

---

## Managed authentication and custom auth providers

For enterprise deployments, you can offload token storage, refresh, and secret rotation to **Google Cloud Agent Identity** or register your own **`BaseAuthProvider`** (or `auth.ProviderFunc` in Go).

### Managed authentication with Google Cloud Agent Identity (Preview)

!!! note "Preview feature"
    Google Cloud Agent Identity and IAM Connector integration (`GcpAuthProvider` in Python and `google.golang.org/adk/v2/auth/gcp` in Go) is currently in **Preview**. For full setup instructions on provisioning agent identities and IAM bindings, see [Google Cloud Agent Identity](/integrations/agent-identity/), [Manage auth providers](https://cloud.google.com/iam/docs/manage-auth-providers), [Authenticate with 2LO](https://cloud.google.com/iam/docs/auth-with-2lo), and [Authenticate with 3LO](https://cloud.google.com/iam/docs/auth-with-3lo).

Google Cloud Agent Identity and IAM Connectors manage OAuth 2.0 (2LO and 3LO) and API key credentials in a managed cloud vault without storing client secrets or refresh tokens in your agent code or session state:

- **In ADK Python (`pip install "google-adk[agent-identity]"`):** Register `GcpAuthProvider()` with `CredentialManager` and pass `GcpAuthProviderScheme` to `AuthConfig` or directly to `McpToolset(auth_scheme=...)`.
- **How 3LO callback finalization works with `GcpAuthProvider`:** When 3LO user consent is required, ADK emits `adk_request_credential` containing `oauth2.auth_uri` and `oauth2.nonce`. After the user grants consent, the connector redirects to your `continue_uri` with `user_id_validation_state` and `connector_name` (or `auth_provider_name`). The ADK web server (`adk web` / `adk api_server`) exposes a built-in `POST /agent-identity/finalize` endpoint (using `FinalizeCredentialsRequest`) that completes the token exchange directly into the cloud vault before your client resumes the agent turn. For a complete working 2LO, 3LO, and MCP sample with a custom FastAPI web client, see [`contributing/samples/integrations/gcp_auth`](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/gcp_auth).

=== "Python"

    ```python
    from google.adk.auth import AuthConfig, CredentialManager
    from google.adk.integrations.agent_identity import (
        GcpAuthProvider,
        GcpAuthProviderScheme,
    )

    # 1. Install extra: pip install "google-adk[agent-identity]"
    # 2. Register GcpAuthProvider with CredentialManager once at startup
    CredentialManager.register_auth_provider(GcpAuthProvider())

    # 3. Reference your Agent Identity AuthProvider or IAM Connector resource name:
    #    - Agent Identity: "projects/{project}/locations/{location}/authProviders/{id}"
    #    - IAM Connector:  "projects/{project}/locations/{location}/connectors/{id}"
    scheme = GcpAuthProviderScheme(
        name="projects/my-project/locations/us-central1/authProviders/my-oauth-provider",
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
        continue_uri="https://my-app.example.com/commit",  # Required for 3LO flows
    )

    auth_config = AuthConfig(auth_scheme=scheme)
    ```

=== "Go"

    ```go
    import (
        "context"
        "errors"

        "google.golang.org/adk/v2/auth"
        "google.golang.org/adk/v2/auth/gcp"
        "google.golang.org/adk/v2/tool/mcptoolset"
    )

    // 1. Create a managed GCP CredentialProvider (resolves the acting user via
    //    agent.IdentityFromContext and caches tokens in InMemoryCredentialStore).
    gcpProvider, err := gcp.NewProvider(context.Background(), gcp.ProviderConfig{
        Scheme: gcp.ProviderScheme{
            // Agent Identity ("authProviders/*") or IAM Connector ("connectors/*")
            Name:        "projects/my-project/locations/us-central1/authProviders/my-oauth-provider",
            Scopes:      []string{"https://www.googleapis.com/auth/drive.readonly"},
            ContinueURI: "https://my-app.example.com/commit",
        },
        Store: auth.NewInMemoryCredentialStore(),
    })
    if err != nil {
        return err
    }

    // 2. Attach the provider to mcptoolset.Config or auth.Transport.
    mcpTools, err := mcptoolset.New(mcptoolset.Config{
        Endpoint: "https://example.com/mcp",
        Auth:     gcpProvider,
    })

    // When 3-legged user consent is required, Credential() returns an error
    // wrapping *auth.ConsentRequiredError:
    var consentErr *auth.ConsentRequiredError
    if errors.As(err, &consentErr) {
        // Redirect the end user to consentErr.AuthURI
    }
    ```

### Custom authentication providers (`BaseAuthProvider` and `ProviderFunc`)

When integrating with a custom enterprise secret vault (such as HashiCorp Vault, AWS Secrets Manager, or an internal token exchange service), implement a custom authentication provider and register it with ADK:

=== "Python"

    ```python
    from typing import Literal
    from pydantic import Field
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.auth import (
        AuthConfig,
        AuthCredential,
        AuthCredentialTypes,
        BaseAuthProvider,
        CredentialManager,
        CustomAuthScheme,
        HttpAuth,
        HttpCredentials,
    )

    class VaultBearerScheme(CustomAuthScheme):
        """Custom AuthScheme identifying tokens fetched from an enterprise vault."""
        type_: Literal["vaultBearerScheme"] = Field(
            default="vaultBearerScheme", alias="type"
        )
        vault_secret_path: str

    class VaultAuthProvider(BaseAuthProvider):
        """Fetches short-lived bearer tokens from an enterprise secret manager."""

        @property
        def supported_auth_schemes(self) -> tuple[type[VaultBearerScheme], ...]:
            return (VaultBearerScheme,)

        async def get_auth_credential(
            self, auth_config: AuthConfig, context: CallbackContext | None = None
        ) -> AuthCredential | None:
            scheme = auth_config.auth_scheme
            if not isinstance(scheme, VaultBearerScheme):
                raise TypeError(f"Unsupported scheme: {type(scheme)}")

            # Replace with your asynchronous secret manager or token exchange call
            token = await fetch_token_from_vault(scheme.vault_secret_path)

            return AuthCredential(
                auth_type=AuthCredentialTypes.HTTP,
                http=HttpAuth(
                    scheme="bearer",
                    credentials=HttpCredentials(token=token),
                ),
            )

    # Register the custom provider (reads provider.supported_auth_schemes automatically)
    CredentialManager.register_auth_provider(VaultAuthProvider())
    ```

=== "TypeScript"

    ```typescript
    import {
      AuthConfig,
      AuthCredential,
      AuthCredentialTypes,
      AuthProviderRegistry,
      BaseAuthProvider,
    } from '@google/adk';

    class VaultAuthProvider implements BaseAuthProvider {
      async getAuthCredential(
        authConfig: AuthConfig,
        context?: unknown
      ): Promise<AuthCredential | undefined> {
        // Replace with your asynchronous secret manager or token exchange call
        const token = await fetchTokenFromVault(authConfig.credentialKey);

        return {
          authType: AuthCredentialTypes.HTTP,
          http: {
            scheme: 'bearer',
            credentials: { token },
          },
        };
      }
    }

    // Register the custom provider for the target scheme type
    const registry = new AuthProviderRegistry();
    registry.register('http', new VaultAuthProvider());
    ```

=== "Go"

    ```go
    import (
        "context"
        "errors"

        "google.golang.org/adk/v2/agent"
        "google.golang.org/adk/v2/auth"
    )

    // Use auth.ProviderFunc to adapt any function into an auth.CredentialProvider.
    // Recover the acting user's identity from ctx via agent.IdentityFromContext.
    vaultProvider := auth.ProviderFunc(func(ctx context.Context) (auth.Credential, error) {
        id, ok := agent.IdentityFromContext(ctx)
        if !ok || id.UserID == "" {
            return nil, errors.New("vault: missing acting user identity")
        }
        token, err := fetchTokenFromVault(ctx, "secret/data/api-token", id.UserID)
        if err != nil {
            return nil, err
        }
        return auth.BearerCredential{Token: token}, nil
    })
    ```

---

## Framework components and SDK support

| Component | Python (`google.adk.auth`) | TypeScript (`@google/adk`) | Go (`google.golang.org/adk/v2/auth`) | Kotlin (`com.google.adk.kt.auth`) | Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Authentication Scheme** | `AuthScheme` (`SecurityScheme`, `OpenIdConnectWithConfig`, `CustomAuthScheme`) | `AuthScheme` (`OpenAPIV3.SecuritySchemeObject`, `OpenIdConnectWithConfig`) | Built into `CredentialProvider` constructors (`gcp.ProviderScheme` for Agent Identity) | `AuthScheme` (`ApiKey`, `Http`, `OAuth2`, `OpenIdConnect`, `OpenIdConnectUrl`) | Declares the security protocol required by the target API (such as header API key, OAuth2 flows, or OIDC endpoints). |
| **Authentication Credential** | `AuthCredential` & `AuthCredentialTypes` | `AuthCredential` & `AuthCredentialTypes` | `Credential` interface (`APIKeyCredential`, `BearerCredential`, `BasicCredential`, `OAuth2Credential`) | `AuthCredential` (`ApiKey`, `Http`, `OAuth2`, `ServiceAccount`) & `Secret` | Holds the secret material, client ID/secret, service account key, or exchanged access token. |
| **OAuth 2.0 Payload** | `OAuth2Auth` | `OAuth2Auth` | `oauth2.TokenSource` / `*auth.ConsentRequiredError` | `AuthCredential.OAuth2` (`Variant.OAUTH2`, `Variant.OPEN_ID_CONNECT`) | Stores OAuth 2.0 client credentials, redirect URIs, authorization codes, and exchanged access/refresh tokens. |
| **Authentication Configuration** | `AuthConfig` | `AuthConfig` | Passed via `mcptoolset.Config.Auth` or `auth.Transport` | `AuthConfig` & `CredentialKey` | Binds an `AuthScheme` to a raw `AuthCredential`, tracks `exchanged_auth_credential`, and computes a `credential_key`. |
| **Authentication Provider** | `BaseAuthProvider` & `CredentialManager` | `BaseAuthProvider` & `AuthProviderRegistry` | `CredentialProvider`, `RefreshingProvider`, & `ProviderFunc` | Not supported | Pluggable interface that resolves an `AuthConfig` into a ready-to-use credential at runtime. |
| **Runtime Handler** | `AuthHandler` & `CredentialManager` | `AuthHandler` & `ToolAuthHandler` | `auth.Transport`, `auth.InMemoryCredentialStore`, & `auth/gcp.NewProvider` | `AuthHandler` (internal) & `Context` (`requestCredential`, `getAuthResponse`) | Manages token caching in session state, generates 3LO consent URIs, and exchanges authorization codes for access tokens. |

### Supported credential types

| Credential Type (`AuthCredentialTypes`) | OpenAPI / Protocol Mapping | Interactive User Prompt? | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **`API_KEY`** (`"apiKey"`) | OpenAPI `apiKey` (`header`, `query`, `cookie`) | No | Calling third-party REST APIs authenticated by a static key. |
| **`HTTP`** (`"http"`) | OpenAPI `http` (`bearer`, `basic`) | No | Injecting pre-existing Bearer JWTs or HTTP Basic credentials. |
| **`OAUTH2`** (`"oauth2"` — 2LO `clientCredentials`) | OpenAPI `oauth2` (`clientCredentials`) | No | Service-to-service OAuth 2.0 where the agent authenticates with its own client ID and secret. |
| **`OAUTH2`** (`"oauth2"` — 3LO `authorizationCode` / `implicit`) | OpenAPI `oauth2` (`authorizationCode`, `implicit`) | **Yes** (`adk_request_credential`) | Accessing end-user resources (such as Google Calendar, GitHub, or Jira) with user consent. |
| **`OPEN_ID_CONNECT`** (`"openIdConnect"`) | OpenAPI `openIdConnect` (`OpenIdConnectWithConfig`) | **Yes** (`adk_request_credential`) | Authenticating users through an OIDC identity provider with automatic endpoint discovery. |
| **`SERVICE_ACCOUNT`** (`"serviceAccount"`) | Google Cloud Service Account / ADC | No | Calling Google Cloud APIs (with access tokens) or Cloud Run / IAP endpoints (with ID tokens in Python, Go, and Kotlin). |

### Multi-language SDK support matrix

| Capability | Python | TypeScript | Go | Java | Kotlin |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **API Key & Static Bearer/Basic Tokens** | Supported (`token_to_scheme_credential`, `AuthCredential`) | Supported (`AuthScheme`, `AuthCredential`) | Supported (`auth.APIKey`, `auth.StaticToken`, `auth.BasicCredential`) | Not supported | Experimental (`AuthScheme.ApiKey`, `AuthScheme.Http`, `AuthCredential`) |
| **OAuth 2.0 Client Credentials (2LO)** | Supported (`OAuthFlowClientCredentials`, `OAuth2Auth`) | Supported (`AuthScheme`, `OAuth2Auth`) | Supported (`auth.TokenSourceProvider`) | Not supported | Experimental (`AuthScheme.OAuth2.clientCredentials`, `AuthCredential.OAuth2`) |
| **Interactive 3LO OAuth 2.0 & OIDC (`adk_request_credential`)** | Supported (`AuthHandler`, `ToolContext`) | Supported (`AuthHandler`, `Context`) | Supported (`*auth.ConsentRequiredError`) | Not supported | Experimental (`Context.requestCredential`, `Context.getAuthResponse`) |
| **Service Account & Application Default Credentials (ADC)** | Supported (`service_account_dict_to_scheme_credential`, `service_account_scheme_credential`) | Supported (`ServiceAccountCredentialExchanger` for access tokens) | Supported (`auth.ADC`, `auth.ServiceAccount`) | Supported on `ApplicationIntegrationToolset` (`serviceAccountJson` / ADC) | Experimental (`AuthCredential.ServiceAccount.applicationDefault`, `fromKey`) |
| **Service Account OIDC ID Tokens (`use_id_token` / `Audience` / `forIdToken`)** | Supported (`ServiceAccount(use_id_token=True, audience=...)`) | Not supported | Supported (`ServiceAccountConfig{Audience: ...}`) | Not supported | Experimental (`AuthCredential.ServiceAccount.forIdToken`) |
| **Declarative `AuthenticatedFunctionTool`** | Supported (`AuthenticatedFunctionTool`) | Not supported (use `FunctionTool` with `Context`) | Not supported | Not supported | Not supported (use `FunctionTool` with `Context`) |
| **Toolset-level `get_auth_config()`** | Supported (`BaseToolset.get_auth_config`) | Not supported | Not supported | Not supported | Not supported |
| **External Token Injection (`external_access_token_key`)** | Supported (`BigQueryCredentialsConfig`) | Not supported | Not supported | Not supported | Not supported |
| **Google Cloud Agent Identity & IAM Connectors (Preview)** | Supported (`GcpAuthProvider`, `GcpAuthProviderScheme`) | Not supported | Supported (`auth/gcp.NewProvider`, `auth/gcp.NewClient`) | Not supported | Not supported |
| **Custom Auth Providers (`BaseAuthProvider` / `ProviderFunc`)** | Supported (`BaseAuthProvider`, `CredentialManager.register_auth_provider`) | Supported (`BaseAuthProvider`, `AuthProviderRegistry.register`) | Supported (`auth.CredentialProvider`, `auth.ProviderFunc`) | Not supported | Not supported |

### Additional resources

For comprehensive checklists covering prompt safety, memory integrity, output guardrails, and organizational governance, consult:

* [ADK Safety and Security Guide](/safety/)
* [OWASP AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html)
* [Google Secure AI Framework (SAIF)](https://safety.google/cybersecurity-advancements/saif/)
* [IBM AI Agent Security Guide](https://www.ibm.com/think/tutorials/ai-agent-security)
