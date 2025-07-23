# Authentication with A2A

Now that you know how to connect remote agents, the next step is to secure
them. This guide explains how to protect your remote A2A agent using OAuth 2.0.

## The Core Concept: The `AuthTool`

The key to requiring authentication is the `AuthTool`. This is a special tool
that you use in your **remote agent's** definition. It acts as a security
guard, wrapping the tool you want to protect.

When a calling agent tries to use a protected tool, the remote agent sends back
a special "authentication required" signal. The ADK on the client side
intercepts this signal and automatically starts the OAuth 2.0 login flow in the
user's browser. This way, the calling agent doesn't need complex auth logic.

## The Scenario: Protecting Our Prime Checker

Let's continue our previous example. Instead of a complex `BigQueryToolset`, we
will add authentication to our simple `check_prime` tool. This keeps the example
focused on the authentication mechanism itself.

### Step 1: Protecting the Remote Agent

In our remote `prime_checker` agent, we will import `AuthTool` and wrap our
`check_prime` function with it.

```python title="my_prime_agent/agent.py"
from google.adk import Agent
from google.adk.tools import AuthTool

async def check_prime(num: int) -> str:
  # ... (prime checking logic) ...
  return f"{num} is a prime number."

# We wrap our simple function with AuthTool to protect it.
protected_prime_tool = AuthTool(
    name="check_prime",
    description="A tool that can check if a number is prime.",
    tool=check_prime,
    # We also define the permissions our agent needs.
    # For this example, we'll use a generic 'email' scope.
    scopes=["https://www.googleapis.com/auth/userinfo.email"],
)

# The remote agent is defined with the protected tool.
root_agent = Agent(
    name="prime_checker",
    tools=[protected_prime_tool],
    # ...
)
```

> **Note on Naming:** In this example, we've given the `AuthTool` the same name
> as the function it's protecting (`check_prime`). This is a common convention,
> but you can also give the tool a different name. The important thing is that
> the `name` you specify in the `AuthTool` is the name that the calling agent
> will use.

### Step 2: The User Experience

1.  **Create OAuth 2.0 Credentials:**

    - Go to the [Credentials page](https://console.cloud.google.com/apis/credentials) in the Google Cloud Console.
    - Click **Create credentials** and select **OAuth client ID**.
    - Select **Web application** for the application type.
    - Under **Authorized redirect URIs**, you **must** add the ADK's callback URL.

      > **Important:** The port number in the redirect URI must exactly match the port your `adk api_server` is running on. If you use a different port (e.g., `--port 9000`), you must update the URI here accordingly.

      For a server running on `localhost` at port `8001`, the URI is:
      ```
      http://localhost:8001/a2a/oauth/callback
      ```
    - Click **Create** and copy your **Client ID** and **Client Secret**.

2.  **Provide OAuth Credentials to the ADK:** For the login flow to work, the
    ADK server needs the OAuth Client ID and Secret. You must provide these as
    environment variables before starting the server.

    ```bash
    export OAUTH_CLIENT_ID="your-client-id.apps.googleusercontent.com"
    export OAUTH_CLIENT_SECRET="your-client-secret"
    ```

3.  **Run the Agents:** Start your remote `prime_checker` and your local
    `root_agent` as you learned in the previous guides.

4.  **Trigger the Flow:** When the user asks the `root_agent` to
    `"check if 13 is prime"`, the authentication flow will now be triggered
    automatically, prompting the user to log in and consent before the tool is
    executed.

## Next Steps

You have now learned how to secure your remote agents. For more advanced A2A
patterns, see the next guides.

- **Continue to the next guide:** [Human-in-the-Loop (HITL)](./human-in-the-loop.md)
