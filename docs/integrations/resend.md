---
catalog_title: Resend
catalog_description: Send emails, manage inboxes, contacts, broadcasts, and domains
catalog_icon: /integrations/assets/resend.svg
catalog_tags: ["mcp"]
---

# Resend MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span><span class="lst-java">Java</span><span class="lst-kotlin">Kotlin</span>
</div>

The [Resend MCP Server](https://resend.com/docs/mcp-server) connects your ADK
agent to [Resend](https://resend.com/), an email platform for developers. This
integration gives your agent the ability to send and receive emails, manage
its own inbox, manage contacts, broadcasts, and automations, and configure
domains and webhooks using natural language.

Resend hosts a remote MCP server at `https://mcp.resend.com/mcp` that uses the
Streamable HTTP transport. There is also an open-source server published to npm
as [`resend-mcp`](https://www.npmjs.com/package/resend-mcp) if you prefer to
run it yourself.

## Use cases

- **Send transactional emails**: Send single or batch emails with attachments,
  CC and BCC, scheduling, and tags, then check delivery status and engagement
  metrics.

- **Give agents their own inbox**: Search inbox threads, read messages, draft
  and send replies, forward emails, and organize threads with labels.

- **Run email campaigns**: Manage contacts, segments, and topics, then create,
  schedule, and send broadcasts to an audience.

- **Manage sending infrastructure**: Add and verify sender domains, configure
  webhooks, rotate signing secrets, and inspect API request logs.

## Prerequisites

- Create a [Resend account](https://resend.com/signup)
- To authenticate with an API key, create one in the
  [Resend Dashboard](https://resend.com/api-keys)
- To send emails, add and verify a
  [domain](https://resend.com/docs/dashboard/domains/introduction)
- For Python, install ADK with the MCP extra, which the `McpToolset` class
  needs: `pip install "google-adk[mcp]"`
- For TypeScript, install the MCP SDK alongside ADK, which the `MCPToolset`
  class needs: `npm install @google/adk @modelcontextprotocol/sdk`

## Use with agent

The remote server accepts two kinds of credentials:

- **API key**: Pass a Resend API key as a Bearer token. This works in every ADK
  language and suits servers, CI jobs, and other headless environments.
- **OAuth**: The user signs in to Resend in a browser and approves access, and
  the agent receives a short-lived access token that refreshes automatically.
  ADK for Python runs this flow for MCP tools, as the Python example below
  shows. ADK for TypeScript, Go, Java, and Kotlin doesn't, so use an API key
  with those languages.

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        RESEND_API_KEY = "YOUR_RESEND_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="resend_agent",
            instruction="Help users send emails and manage their Resend account",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.resend.com/mcp",
                        headers={
                            "Authorization": f"Bearer {RESEND_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

    === "Remote MCP Server (OAuth)"

        ADK runs the OAuth flow for you: when the agent first needs the Resend
        tools, it asks the client app to send the user to Resend to sign in.
        The [ADK web UI](/runtime/web-interface/) handles this with a pop-up
        window.

        First, register an OAuth client with Resend. The redirect URI must
        match where your client app receives the callback. For the ADK web UI
        running on the default port, that's `http://localhost:8000/dev-ui/`:

        ```bash
        curl -X POST 'https://api.resend.com/oauth/register' \
             -H 'Content-Type: application/json' \
             -d '{
                  "client_name": "ADK Resend agent",
                  "redirect_uris": ["http://localhost:8000/dev-ui/"],
                  "grant_types": ["authorization_code", "refresh_token"],
                  "response_types": ["code"],
                  "token_endpoint_auth_method": "none",
                  "scope": "full_access"
                }'
        ```

        Use the `client_id` from the response in your agent:

        ```python
        from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
        from google.adk.agents import Agent
        from google.adk.auth import AuthCredential, AuthCredentialTypes, OAuth2Auth
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        RESEND_OAUTH_CLIENT_ID = "YOUR_RESEND_OAUTH_CLIENT_ID"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="resend_agent",
            instruction="Help users send emails and manage their Resend account",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.resend.com/mcp",
                    ),
                    auth_scheme=OAuth2(
                        flows=OAuthFlows(
                            authorizationCode=OAuthFlowAuthorizationCode(
                                authorizationUrl="https://api.resend.com/oauth/authorize",
                                tokenUrl="https://api.resend.com/oauth/token",
                                scopes={"full_access": "Full access to your Resend account"},
                            )
                        )
                    ),
                    auth_credential=AuthCredential(
                        auth_type=AuthCredentialTypes.OAUTH2,
                        oauth2=OAuth2Auth(
                            client_id=RESEND_OAUTH_CLIENT_ID,
                            # A public client: no secret, so PKCE protects the code exchange.
                            code_challenge_method="S256",
                        ),
                    ),
                )
            ],
        )
        ```

        !!! note

            To handle the sign-in from your own app instead of the ADK web UI,
            see [Authenticating with tools](/tools-custom/authentication/).

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        RESEND_API_KEY = "YOUR_RESEND_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="resend_agent",
            instruction="Help users send emails and manage their Resend account",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "resend-mcp",
                            ],
                            env={
                                "RESEND_API_KEY": RESEND_API_KEY,
                                # "SENDER_EMAIL_ADDRESS": "agent@example.com",  # Optional
                            }
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const RESEND_API_KEY = "YOUR_RESEND_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "resend_agent",
            instruction: "Help users send emails and manage their Resend account",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.resend.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${RESEND_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const RESEND_API_KEY = "YOUR_RESEND_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "resend_agent",
            instruction: "Help users send emails and manage their Resend account",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "resend-mcp"],
                        env: {
                            RESEND_API_KEY: RESEND_API_KEY,
                            // SENDER_EMAIL_ADDRESS: "agent@example.com",  // Optional
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

=== "Go"

    === "Remote MCP Server"

        ```go
        package main

        import (
        	"context"
        	"log"
        	"os"

        	"google.golang.org/genai"

        	"google.golang.org/adk/v2/agent"
        	"google.golang.org/adk/v2/agent/llmagent"
        	"google.golang.org/adk/v2/auth"
        	"google.golang.org/adk/v2/cmd/launcher"
        	"google.golang.org/adk/v2/cmd/launcher/full"
        	"google.golang.org/adk/v2/model/gemini"
        	"google.golang.org/adk/v2/tool"
        	"google.golang.org/adk/v2/tool/mcptoolset"
        )

        const resendAPIKey = "YOUR_RESEND_API_KEY"

        func main() {
        	ctx := context.Background()

        	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{
        		APIKey: os.Getenv("GOOGLE_API_KEY"),
        	})
        	if err != nil {
        		log.Fatalf("Failed to create the model: %v", err)
        	}

        	resend, err := mcptoolset.New(mcptoolset.Config{
        		Endpoint: "https://mcp.resend.com/mcp",
        		// Auth sets "Authorization: Bearer <key>" on every request.
        		Auth: auth.StaticToken(resendAPIKey),
        	})
        	if err != nil {
        		log.Fatalf("Failed to create the Resend tool set: %v", err)
        	}

        	rootAgent, err := llmagent.New(llmagent.Config{
        		Model:       model,
        		Name:        "resend_agent",
        		Instruction: "Help users send emails and manage their Resend account",
        		Toolsets:    []tool.Toolset{resend},
        	})
        	if err != nil {
        		log.Fatalf("Failed to create the agent: %v", err)
        	}

        	l := full.NewLauncher()
        	cfg := &launcher.Config{AgentLoader: agent.NewSingleLoader(rootAgent)}
        	if err := l.Execute(ctx, cfg, os.Args[1:]); err != nil {
        		log.Fatalf("Run failed: %v\n\n%s", err, l.CommandLineSyntax())
        	}
        }
        ```

    === "Local MCP Server"

        ```go
        package main

        import (
        	"context"
        	"log"
        	"os"
        	"os/exec"

        	"github.com/modelcontextprotocol/go-sdk/mcp"
        	"google.golang.org/genai"

        	"google.golang.org/adk/v2/agent"
        	"google.golang.org/adk/v2/agent/llmagent"
        	"google.golang.org/adk/v2/cmd/launcher"
        	"google.golang.org/adk/v2/cmd/launcher/full"
        	"google.golang.org/adk/v2/model/gemini"
        	"google.golang.org/adk/v2/tool"
        	"google.golang.org/adk/v2/tool/mcptoolset"
        )

        const resendAPIKey = "YOUR_RESEND_API_KEY"

        func main() {
        	ctx := context.Background()

        	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{
        		APIKey: os.Getenv("GOOGLE_API_KEY"),
        	})
        	if err != nil {
        		log.Fatalf("Failed to create the model: %v", err)
        	}

        	server := exec.CommandContext(ctx, "npx", "-y", "resend-mcp")
        	// Forward only what npx needs, plus the Resend key. The parent environment
        	// may hold unrelated secrets, such as the GOOGLE_API_KEY read above.
        	server.Env = []string{
        		"RESEND_API_KEY=" + resendAPIKey,
        		// "SENDER_EMAIL_ADDRESS=agent@example.com", // Optional
        	}
        	for _, k := range []string{
        		"PATH", "HOME", // POSIX
        		"APPDATA", "LOCALAPPDATA", "TEMP", "USERPROFILE", // Windows
        	} {
        		if v, ok := os.LookupEnv(k); ok {
        			server.Env = append(server.Env, k+"="+v)
        		}
        	}

        	resend, err := mcptoolset.New(mcptoolset.Config{
        		Transport: &mcp.CommandTransport{Command: server},
        	})
        	if err != nil {
        		log.Fatalf("Failed to create the Resend tool set: %v", err)
        	}

        	rootAgent, err := llmagent.New(llmagent.Config{
        		Model:       model,
        		Name:        "resend_agent",
        		Instruction: "Help users send emails and manage their Resend account",
        		Toolsets:    []tool.Toolset{resend},
        	})
        	if err != nil {
        		log.Fatalf("Failed to create the agent: %v", err)
        	}

        	l := full.NewLauncher()
        	cfg := &launcher.Config{AgentLoader: agent.NewSingleLoader(rootAgent)}
        	if err := l.Execute(ctx, cfg, os.Args[1:]); err != nil {
        		log.Fatalf("Run failed: %v\n\n%s", err, l.CommandLineSyntax())
        	}
        }
        ```

=== "Java"

    === "Remote MCP Server"

        ```java
        package com.example.agent;

        import com.google.adk.agents.BaseAgent;
        import com.google.adk.agents.LlmAgent;
        import com.google.adk.tools.mcp.McpToolset;
        import com.google.adk.tools.mcp.StreamableHttpServerParameters;
        import java.util.Map;

        public class ResendAgent {

            private static final String RESEND_API_KEY = "YOUR_RESEND_API_KEY";

            public static BaseAgent ROOT_AGENT = initAgent();

            private static BaseAgent initAgent() {
                StreamableHttpServerParameters resendParams = StreamableHttpServerParameters.builder()
                    .url("https://mcp.resend.com/mcp")
                    .headers(Map.of("Authorization", "Bearer " + RESEND_API_KEY))
                    .build();

                return LlmAgent.builder()
                    .name("resend_agent")
                    .model("gemini-flash-latest")
                    .instruction("Help users send emails and manage their Resend account")
                    .tools(new McpToolset(resendParams))
                    .build();
            }
        }
        ```

=== "Kotlin"

    === "Remote MCP Server"

        ```kotlin
        package com.example.agent

        import com.google.adk.kt.agents.Instruction
        import com.google.adk.kt.agents.LlmAgent
        import com.google.adk.kt.models.Gemini
        import com.google.adk.kt.tools.mcp.McpTransportConfig
        import com.google.adk.kt.tools.mcp.RemoteMcpToolsetConfig

        const val RESEND_API_KEY = "YOUR_RESEND_API_KEY"

        object ResendAgent {
            @JvmField
            val rootAgent = LlmAgent(
                name = "resend_agent",
                model = Gemini(
                    name = "gemini-flash-latest",
                    apiKey = System.getenv("GOOGLE_API_KEY")
                        ?: error("GOOGLE_API_KEY environment variable not set."),
                ),
                instruction = Instruction("Help users send emails and manage their Resend account"),
                toolsets = listOf(
                    RemoteMcpToolsetConfig(
                        transport = McpTransportConfig.StreamableHttp(
                            url = "https://mcp.resend.com/mcp",
                            headers = mapOf("Authorization" to "Bearer $RESEND_API_KEY"),
                        ),
                    ).toToolset(),
                ),
            )
        }
        ```

## Available tools

The remote and local servers expose the following tools.

### Emails

| Tool                          | Description                                                                        |
| ----------------------------- | ---------------------------------------------------------------------------------- |
| `send-email`                  | Send an email with attachments, CC and BCC, reply-to, scheduling, tags, and topics |
| `send-batch-emails`           | Send multiple emails in a single request                                           |
| `list-emails`                 | List sent emails                                                                   |
| `get-email`                   | Get the details and status of a sent email                                         |
| `update-email`                | Reschedule a scheduled email                                                       |
| `cancel-email`                | Cancel a scheduled email                                                           |
| `share-email`                 | Create a temporary shareable link to a sent or received email                      |
| `get-email-metrics`           | Get delivery and engagement metrics                                                |
| `list-sent-email-attachments` | List the attachments of a sent email                                               |
| `get-sent-email-attachment`   | Download an attachment from a sent email                                           |

### Received emails

| Tool                              | Description                                  |
| --------------------------------- | -------------------------------------------- |
| `list-received-emails`            | List inbound emails                          |
| `get-received-email`              | Read an inbound email                        |
| `list-received-email-attachments` | List the attachments of an inbound email     |
| `get-received-email-attachment`   | Download an attachment from an inbound email |

### Inboxes

| Tool                                                                                                                         | Description                                                |
| ---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `create-inbox`, `list-inboxes`, `get-inbox`, `update-inbox`, `remove-inbox`                                                  | Manage inboxes                                             |
| `get-inbox-agent`, `update-inbox-agent`                                                                                      | View and configure an inbox's AI agent settings            |
| `list-inbox-threads`, `search-inbox-threads`, `get-inbox-thread`                                                             | Find and read threads                                      |
| `update-inbox-thread`                                                                                                        | Mark a thread read or unread, or move it to another folder |
| `remove-inbox-thread`                                                                                                        | Delete a thread                                            |
| `list-inbox-thread-emails`, `get-inbox-thread-email`                                                                         | Read the emails in a thread                                |
| `reply-to-inbox-thread-email`, `forward-inbox-thread-email`                                                                  | Reply to or forward an email in a thread                   |
| `send-new-inbox-email`                                                                                                       | Start a new thread from an inbox                           |
| `create-inbox-draft`, `list-inbox-drafts`, `get-inbox-draft`, `update-inbox-draft`, `remove-inbox-draft`, `send-inbox-draft` | Manage and send drafts                                     |
| `create-inbox-label`, `list-inbox-labels`, `update-inbox-label`, `remove-inbox-label`                                        | Manage labels                                              |
| `add-inbox-thread-labels`, `set-inbox-thread-labels`, `remove-inbox-thread-label`                                            | Label threads                                              |

### Templates

| Tool                                                                                      | Description                                                      |
| ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `create-template`, `list-templates`, `get-template`, `update-template`, `remove-template` | Manage email templates                                           |
| `duplicate-template`                                                                      | Copy an existing template                                        |
| `publish-template`                                                                        | Publish a template so it can be used to send emails              |
| `compose-template`                                                                        | Set a template's content for editing in the Resend visual editor |

### Contacts

| Tool                                                                                 | Description                            |
| ------------------------------------------------------------------------------------ | -------------------------------------- |
| `create-contact`, `list-contacts`, `get-contact`, `update-contact`, `remove-contact` | Manage contacts                        |
| `list-contact-segments`, `add-contact-to-segment`, `remove-contact-from-segment`     | Manage a contact's segment memberships |
| `list-contact-topics`, `update-contact-topics`                                       | Manage a contact's topic subscriptions |
| `create-contact-import`, `list-contact-imports`, `get-contact-import`                | Import contacts from a CSV file        |

### Contact properties

| Tool                                                                                                                               | Description                      |
| ---------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `create-contact-property`, `list-contact-properties`, `get-contact-property`, `update-contact-property`, `remove-contact-property` | Manage custom contact attributes |

### Segments and topics

| Tool                                                                                 | Description                |
| ------------------------------------------------------------------------------------ | -------------------------- |
| `create-segment`, `list-segments`, `get-segment`, `update-segment`, `remove-segment` | Manage audience segments   |
| `create-topic`, `list-topics`, `get-topic`, `update-topic`, `remove-topic`           | Manage subscription topics |

### Broadcasts

| Tool                                                                                           | Description                                                       |
| ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `create-broadcast`, `list-broadcasts`, `get-broadcast`, `update-broadcast`, `remove-broadcast` | Manage broadcast campaigns                                        |
| `duplicate-broadcast`                                                                          | Copy an existing broadcast                                        |
| `compose-broadcast`                                                                            | Set a broadcast's content for editing in the Resend visual editor |
| `send-broadcast`, `cancel-broadcast`                                                           | Send, schedule, or cancel a broadcast                             |
| `list-broadcast-recipients`, `list-broadcast-clicked-links`                                    | Review recipients and clicked links                               |

### Automations and events

| Tool                                                          | Description                                            |
| ------------------------------------------------------------- | ------------------------------------------------------ |
| `create-automation`, `update-automation`, `remove-automation` | Manage automations                                     |
| `get-automation`                                              | List automations or get one with its workflow          |
| `duplicate-automation`                                        | Copy an existing automation                            |
| `update-automation-step`                                      | Update a single step in an automation's workflow       |
| `get-automation-runs`                                         | Review automation runs                                 |
| `cancel-automation-run`                                       | Cancel an automation run                               |
| `manage-events`                                               | Create, list, get, update, or remove event definitions |
| `send-event`                                                  | Send an event to trigger automations for a contact     |

### Domains

| Tool                                                                            | Description                                                                        |
| ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `create-domain`, `list-domains`, `get-domain`, `update-domain`, `remove-domain` | Manage sender domains, including tracking, TLS, and sending and receiving settings |
| `verify-domain`                                                                 | Verify a domain's DNS records                                                      |
| `enable-forge`                                                                  | Enable Forge on a domain and verify only the Forge record                          |
| `create-domain-claim`, `get-domain-claim`, `verify-domain-claim`                | Claim a domain that another Resend account has already verified                    |

### Suppressions

| Tool                                                                            | Description                        |
| ------------------------------------------------------------------------------- | ---------------------------------- |
| `add-suppression`, `list-suppressions`, `get-suppression`, `remove-suppression` | Manage suppression list entries    |
| `batch-add-suppressions`, `batch-remove-suppressions`                           | Add or remove suppressions in bulk |

### Webhooks

| Tool                                                                                 | Description                       |
| ------------------------------------------------------------------------------------ | --------------------------------- |
| `create-webhook`, `list-webhooks`, `get-webhook`, `update-webhook`, `remove-webhook` | Manage webhooks                   |
| `list-webhook-events`, `get-webhook-event`, `list-webhook-event-attempts`            | Inspect webhook delivery history  |
| `replay-webhook-event`                                                               | Redeliver a webhook event         |
| `rotate-webhook-signing-secret`                                                      | Rotate a webhook's signing secret |

### API keys and access

| Tool                                                                  | Description                                     |
| --------------------------------------------------------------------- | ----------------------------------------------- |
| `create-api-key`, `list-api-keys`, `update-api-key`, `remove-api-key` | Manage API keys                                 |
| `list-oauth-grants`, `revoke-oauth-grant`                             | Review and revoke apps authorized through OAuth |

### Logs and usage

| Tool                   | Description                                                              |
| ---------------------- | ------------------------------------------------------------------------ |
| `list-logs`, `get-log` | List and inspect API request logs, including request and response bodies |
| `get-usage`            | View account usage, quotas, and the API rate limit                       |

### Editor

| Tool                                          | Description                                                   |
| --------------------------------------------- | ------------------------------------------------------------- |
| `get-tiptap-json-content`                     | Read the draft content of a broadcast or template             |
| `connect-to-editor`, `disconnect-from-editor` | Show or hide the agent's presence in the Resend visual editor |

### File uploads

| Tool                                    | Description                                        |
| --------------------------------------- | -------------------------------------------------- |
| `create-file-upload`, `get-file-upload` | Upload a local file to attach to emails and drafts |

## Configuration

### Remote server authentication

The remote server accepts a Resend API key or an OAuth access token as a Bearer
token in the `Authorization` header. OAuth clients request one of these scopes:

| Scope         | Access                                                    |
| ------------- | --------------------------------------------------------- |
| `full_access` | All tools. Required for anything other than sending email |
| `emails:send` | Sending emails only                                       |

Access tokens expire after 15 minutes, and refresh tokens rotate each time
they're used. For details on registering clients, see
[Building an OAuth client for Resend](https://resend.com/docs/guides/building-a-resend-oauth-client).

### Local server environment variables

The local server reads its configuration from the following environment
variables:

| Variable                   | Required | Description                                   |
| -------------------------- | -------- | --------------------------------------------- |
| `RESEND_API_KEY`           | Yes      | Your Resend API key                           |
| `SENDER_EMAIL_ADDRESS`     | No       | Default sender address from a verified domain |
| `REPLY_TO_EMAIL_ADDRESSES` | No       | Default reply-to addresses, comma-separated   |

If `SENDER_EMAIL_ADDRESS` isn't set, the server asks for a sender address each
time the agent sends an email. The sender must use a domain you have verified
in Resend.

## Additional resources

- [Resend MCP Server Documentation](https://resend.com/docs/mcp-server)
- [Resend MCP Server Repository](https://github.com/resend/resend-mcp)
- [resend-mcp on npm](https://www.npmjs.com/package/resend-mcp)
- [Building an OAuth client for Resend](https://resend.com/docs/guides/building-a-resend-oauth-client)
- [Resend Documentation](https://resend.com/docs)
