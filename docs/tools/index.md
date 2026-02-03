---
hide:
  - toc
---

# Tools and Integrations for Agents

Check out the following pre-built tools and integrations that you can use with ADK agents:

### Gemini

{{$ render_catalog('tools/gemini-api/*.md') $}}

### Google Cloud

{{$ render_catalog('tools/google-cloud/*.md') $}}

### Third-party

{{$ render_catalog('tools/third-party/*.md') $}}

## Use pre-built tools with ADK agents

Follow these general steps to include tools in your ADK agents:

1. **Import:** Import the desired tool from the tools module. This is
   `agents.tools` in Python, `@google/adk` in TypeScript,
   `google.golang.org/adk/tool` in Go, or `com.google.adk.tools` in Java.
2. **Configure:** Initialize the tool, providing required parameters if any.
3. **Register:** Add the initialized tool to the ***tools*** list of your Agent.

Once added to an agent, the agent can decide to use the tool based on the user
prompt and its instructions. The framework handles the execution of the
tool when the agent calls it.

!!! note "Note: Limitations on using multiple tools"
    Some ADK tools ***cannot be used with other tools in the same agent***.
    For more information on tools with these limitations, see
    [Limitations for ADK tools](/adk-docs/tools/limitations/#one-tool-one-agent).

## Build tools for agents

If the above tools don't meet your needs, you can build tools for your ADK
workflows using the following guides:

*   **[Function Tools](/adk-docs/tools-custom/function-tools/)**: Build custom tools for
    your specific ADK agent needs.
*   **[MCP Tools](/adk-docs/tools-custom/mcp-tools/)**: Connect MCP servers as tools
    for your ADK agents.
*   **[OpenAPI Integration](/adk-docs/tools-custom/openapi-tools/)**:
    Generate callable tools directly from an OpenAPI Specification.
