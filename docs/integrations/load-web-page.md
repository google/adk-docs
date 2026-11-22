---
catalog_title: Load Web Page
catalog_description: Fetch a public URL and extract its readable text content
catalog_icon: /integrations/assets/adk.png
catalog_tags: ["google"]
---

# Load Web Page tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v1.5.0</span>
</div>

The Load Web Page tool fetches a single public HTTP or HTTPS web page and
returns its readable plain text. It strips HTML markup and short noise lines,
letting your agent read articles, documentation pages, or reference URLs
provided by a user or discovered during a workflow. Because the tool runs as a
standard function tool in your application, it works with any model supported by
Agent Development Kit (ADK) and applies built-in URL validation checks to help
mitigate server-side request forgery (SSRF).

## Use cases

- **Page summarization**: Fetch an article, blog post, or documentation URL and
  summarize its key points for the user.
- **Reference lookup**: Read a specific release note, specification, or FAQ page
  so the agent answers questions from current page text.
- **Multi-step web research**: Pair URL fetching with a search tool so the agent
  can locate relevant links and then read individual pages in detail.

## Prerequisites

- A supported runtime: Python 3.11 or later, or Node.js for ADK TypeScript. The
  ADK TypeScript tool requires Node.js networking modules and runs only in
  Node.js environments.
- Model credentials configured for ADK, such as a Gemini API key in
  `GOOGLE_API_KEY`, or a Google Cloud project with the Vertex AI API enabled.

## Installation

=== "Python"

    The `load_web_page` function requires `beautifulsoup4` and `lxml`, which the
    base `google-adk` package does not install. Install ADK with the
    `extensions` extra:

    ```bash
    pip install "google-adk[extensions]"
    ```

    If you prefer not to install the full `extensions` extra, install the parser
    packages directly alongside `google-adk`:

    ```bash
    pip install google-adk beautifulsoup4 lxml
    ```

=== "TypeScript"

    The core `@google/adk` package includes the Load Web Page tool with no
    additional dependencies:

    ```bash
    npm install @google/adk
    ```

## Use with agent

Attach the tool to an agent's `tools` list so the model can fetch public URLs on
demand.

=== "Python"

    Import `load_web_page` from `google.adk.tools.load_web_page`. The top-level
    `google.adk.tools` package does not re-export this function. Passing the
    function directly in `tools` wraps it automatically as a `FunctionTool`.

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.load_web_page import load_web_page

    root_agent = Agent(
        model="gemini-flash-latest",
        name="web_reader_agent",
        instruction=(
            "You are a helpful assistant that reads public web pages. "
            "Use the load_web_page tool to fetch a URL and answer questions "
            "based on its text."
        ),
        tools=[load_web_page],
    )
    ```

=== "TypeScript"

    Import the pre-configured `LOAD_WEB_PAGE` `FunctionTool` from `@google/adk`
    and add it to your `LlmAgent`.

    ```typescript
    import { LlmAgent, LOAD_WEB_PAGE } from "@google/adk";

    const rootAgent = new LlmAgent({
      model: "gemini-flash-latest",
      name: "web_reader_agent",
      instruction:
        "You are a helpful assistant that reads public web pages. " +
        "Use the load_web_page tool to fetch a URL and answer questions " +
        "based on its text.",
      tools: [LOAD_WEB_PAGE],
    });

    export { rootAgent };
    ```

### Call directly or set a custom timeout

You can also call the underlying fetch function directly in application code. In
TypeScript, you can pass `LoadWebPageOptions` to customize the request timeout
or wrap `loadWebPage` in a custom `FunctionTool` for an agent.

=== "Python"

    ```python
    from google.adk.tools.load_web_page import load_web_page

    page_text = load_web_page("https://example.com")
    print(page_text)
    ```

=== "TypeScript"

    Call `loadWebPage` directly in an async function with a custom timeout:

    ```typescript
    import { loadWebPage } from "@google/adk";

    async function fetchSummarySource() {
      const pageText = await loadWebPage("https://example.com", {
        timeoutMs: 10_000,
      });
      console.log(pageText);
    }

    fetchSummarySource();
    ```

    To use a custom timeout with an agent, wrap `loadWebPage` in a
    `FunctionTool`. Install `zod` in your project if your package manager does
    not hoist transitive dependencies:

    ```typescript
    import { FunctionTool, LlmAgent, loadWebPage } from "@google/adk";
    import { z } from "zod";

    const customLoadWebPage = new FunctionTool({
      name: "load_web_page",
      description:
        "Fetches the content at the given URL and returns the readable text extracted from the page.",
      parameters: z.object({
        url: z.string().describe("The URL to fetch and extract text from."),
      }),
      execute: ({ url }) => loadWebPage(url, { timeoutMs: 10_000 }),
    });

    const rootAgent = new LlmAgent({
      model: "gemini-flash-latest",
      name: "web_reader_agent",
      instruction: "Fetch public web pages and summarize them for the user.",
      tools: [customLoadWebPage],
    });

    export { rootAgent };
    ```

## Available tools

| Tool | Parameter | Description |
| :--- | :--- | :--- |
| `load_web_page` | `url` (`string`) | Fetches a public HTTP or HTTPS URL and returns the extracted plain text from the page. |

## Configuration

Request limits and timeout options depend on the runtime:

=== "Python"

    The `load_web_page(url: str) -> str` function exposes only the `url`
    argument so timeout settings stay out of the model's function-calling
    schema. The tool enforces a 30-second connect and inter-chunk socket
    timeout, a 60-second total body-read deadline, and a 10 MiB streamed
    response size limit.

=== "TypeScript"

    The `loadWebPage` function accepts an optional `LoadWebPageOptions` object:

    | Option | Type | Default | Description |
    | :--- | :--- | :--- | :--- |
    | `timeoutMs` | `number` | `30000` | Request timeout in milliseconds. Defaults to 30 seconds. |

    The pre-configured `LOAD_WEB_PAGE` tool uses the default 30-second timeout.
    To set a different timeout for an agent, wrap `loadWebPage` in a custom
    `FunctionTool` as shown in [Call directly or set a custom
    timeout](#call-directly-or-set-a-custom-timeout).

## Request validation and extraction behavior

Because a model can supply untrusted URLs, the Load Web Page tool applies URL
validation checks to help mitigate server-side request forgery (SSRF) and
normalizes output before returning it to the agent.

!!! note "Defense in depth"

    The built-in URL and IP checks are application-level controls, not a full
    network sandbox. In production or restricted environments, combine this tool
    with network-level egress policies, and treat fetched web page text as
    untrusted input to your agent.

- **Public HTTP and HTTPS URLs only**: Accepts `http` and `https` URLs that
  resolve to globally routable public IP addresses. The tool rejects non-HTTP
  schemes such as `file://`, loopback and private networks, cloud metadata
  endpoints such as `169.254.169.254`, and internal hostnames such as
  `localhost` before connecting. ADK Python also blocks `*.local`, `*.internal`,
  and `*.metadata.goog` hostnames.
- **Text extraction**: Strips HTML markup and removes lines with three words or
  fewer to filter out navigation links, short headings, and boilerplate labels.
  In ADK Python v2.15.0 and later, the word counter counts characters
  individually in unspaced scripts such as Chinese, Japanese, and Thai so it
  preserves pages in those languages.
- **Uniform failure response**: Returns `"Failed to fetch url: <url>"` instead
  of raising an exception for blocked targets, unsupported schemes, non-200 HTTP
  statuses, timeouts, oversized responses, or network errors. Missing
  `beautifulsoup4` or `lxml` dependencies in Python still raise `ImportError`.

## Limitations

- **Static HTML only**: Fetches the raw HTTP response without executing
  JavaScript, so client-side rendered pages may return incomplete or empty text.
- **No redirects or authentication**: Does not follow HTTP `3xx` redirects, such
  as `http://` to `https://` redirects or shortened URLs, and does not send
  custom headers or cookies. Any non-200 response returns the failure string.
- **TypeScript runtime considerations**: Runs only in Node.js, not in browser
  builds. Global `fetch` performs its own DNS lookup at connect time, leaving a
  residual DNS-rebinding window, and does not enforce a response body byte cap.
- **Python proxy considerations**: For direct connections, ADK Python pins the
  connection to the vetted IP address. When you configure an outbound proxy,
  such as through `HTTP_PROXY` or `HTTPS_PROXY`, the proxy resolves hostnames
  remotely and connection IP pinning does not apply. Enforce egress rules in
  your proxy policy for proxy-only hostnames.

## Additional resources

- [Google Search tool for ADK](/integrations/google-search/)
- [Enterprise Web Search tool for ADK](/integrations/enterprise-web-search/)
- [Configure ADK agents as MCP servers](/tools-custom/mcp-tools/agent-as-server/): Includes an example that exposes `load_web_page` through Model Context Protocol (MCP).
- [Python API reference: `google.adk.tools.load_web_page`](/api-reference/python/google-adk.html#google-adk-tools-load-web-page-module)
- [TypeScript API reference: `LOAD_WEB_PAGE`](/api-reference/typescript/variables/LOAD_WEB_PAGE.html)
