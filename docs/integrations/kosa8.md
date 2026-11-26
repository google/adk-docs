---
catalog_title: kosa8
catalog_description: Run agent-written code in isolated cloud sandboxes with egress allow-lists
catalog_icon: /integrations/assets/kosa8.png
catalog_tags: ["code", "mcp"]
---

# kosa8 plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [kosa8 ADK package](https://github.com/kosa8ai/adk-kosa8) runs the code your
ADK agent writes in [kosa8 Cloud](https://kosa8.com) sandboxes instead of on
your machine. It provides two pieces:

- A code executor, `Kosa8CodeExecutor`, that you pass to an agent as
  `code_executor`. Each Python block the model writes runs in a sandbox, and the
  agent gets stdout, stderr, the exit code and output files (saved as
  artifacts).
- A helper, `kosa8_mcp_toolset()`, that connects the agent to kosa8's remote MCP
  server through `McpToolset`, so the model can create sandboxes, run commands,
  and read and write files itself.

## Use cases

- **Run model-written code away from your host**: Each code block runs in a
  kosa8 sandbox with a time limit, not on the machine that runs the agent, and
  the sandboxes are deleted when you close the executor.

- **Limit what generated code can reach**: Set an egress allow-list, such as
  only `pypi.org`, and every other host is refused. The policy is enforced
  outside the sandbox, so code inside it cannot change it.

- **Notebook-style analysis**: With `stateful=True`, variables and imports carry
  over from one code block to the next, and charts come back as artifacts.

- **Let the agent manage sandboxes**: With the MCP toolset, the model can start
  a sandbox, run shell commands, write and read files, and delete it.

## Prerequisites

- A [kosa8 Cloud](https://app.kosa8.com) account and API key, set as the
  `KOSA8_API_KEY` environment variable
- Python 3.11 or later

## Installation

```bash
pip install adk-kosa8
```

## Use with agent

=== "Code executor"

    ```python
    from adk_kosa8 import Kosa8CodeExecutor
    from google.adk.agents import Agent

    code_executor = Kosa8CodeExecutor(
        # api_key="k8c_live_...",  # Or set the KOSA8_API_KEY environment variable
        allow_hosts=["pypi.org"],  # Only pypi.org is reachable from the sandbox
        timeout_seconds=120,
    )

    root_agent = Agent(
        model="gemini-flash-latest",
        name="python_coder",
        instruction=(
            "Solve problems by writing Python in ```python blocks. "
            "Answer from the code's output."
        ),
        code_executor=code_executor,
    )

    # When your app shuts down, delete the sandboxes the executor made:
    # code_executor.close()
    ```

=== "MCP tools"

    ```python
    from adk_kosa8 import SANDBOX_TOOLS, kosa8_mcp_toolset
    from google.adk.agents import Agent

    root_agent = Agent(
        model="gemini-flash-latest",
        name="kosa8_agent",
        instruction=(
            "Run code with the kosa8 sandbox tools. "
            "Delete every sandbox you create before you answer."
        ),
        tools=[kosa8_mcp_toolset(tool_filter=SANDBOX_TOOLS)],
    )
    ```

By default, the code executor gives each ADK session one sandbox, so files
written by one code block are still there for the next. A code block that runs
past `timeout_seconds` is stopped and returns exit code 124. Files the code
writes to `/workspace/outputs` are returned as output files and saved as
artifacts.

## Available tools

With `tool_filter=SANDBOX_TOOLS`, the MCP toolset offers these tools:

Tool | Description
---- | -----------
`run` | Run a command or code in a fresh sandbox and return its output
`templates_list` | List the sandbox templates the account can use
`sandbox_create` | Start a sandbox
`sandbox_get` | Get a sandbox's state, size and details
`sandbox_list` | List sandboxes
`sandbox_exec` | Run a command in a sandbox
`sandbox_exec_status` | Check a background command
`file_read` | Read a file from a sandbox
`file_write` | Create or replace a file in a sandbox
`file_list` | List a folder in a sandbox
`sandbox_delete` | Delete a sandbox

Leave `tool_filter` out to get every tool the server lists.

## Configuration

The `Kosa8CodeExecutor` takes these options:

Option | Default | Description
------ | ------- | -----------
`api_key` | `KOSA8_API_KEY` | kosa8 Cloud API key
`template` | `"python"` | Sandbox template (needs `python3`)
`size` | Template default | vCPU and memory, such as `"2x4"`
`allow_hosts` | Account policy | Hosts the sandbox can reach (`[]` for no network)
`egress` | Account policy | A full kosa8 egress policy, instead of `allow_hosts`
`sandbox_scope` | `"session"` | `"session"`, `"executor"` (one shared sandbox), or `"call"` (a new sandbox per code block)
`stateful` | `False` | Keep Python variables between code blocks
`timeout_seconds` | 300 (80 when stateful) | Time limit for one code block
`ttl_s` | 3600 | Lifetime of each sandbox, after which kosa8 deletes it

## Additional resources

- [kosa8 ADK package on GitHub](https://github.com/kosa8ai/adk-kosa8)
- [kosa8 ADK package on PyPI](https://pypi.org/project/adk-kosa8/)
- [kosa8 ADK guide](https://docs.kosa8.com/guides/google-adk/)
- [kosa8 egress controls](https://docs.kosa8.com/guides/cloud-egress/)
- [kosa8 MCP server](https://docs.kosa8.com/guides/cloud-mcp/)
