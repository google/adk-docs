---
title: CrewAI and LangChain integrations
---

# CrewAI and LangChain integrations

The ADK provides wrapper classes that allow you to use third-party tools from [CrewAI](https://www.crewai.com/) and [LangChain](https://www.langchain.com/) in your ADK-based agents.

## CrewAI integration

To use a CrewAI tool, you need to wrap it with the `CrewaiTool` class. This adapter class converts the CrewAI tool into a format that is compatible with the ADK.

### Example

The following example shows how to use a CrewAI tool in an ADK agent.

First, define your CrewAI tool:

```python
from crewai_tools import BaseTool

class MyCrewAITool(BaseTool):
    name: str = "My CrewAI Tool"
    description: str = "A description of my CrewAI tool."

    def _run(self, input: str) -> str:
        return f"This is the output of my CrewAI tool with input: {input}"
```

Next, in your agent configuration, define a tool that uses the `CrewaiTool` wrapper to point to your CrewAI tool:

```yaml
tools:
  - id: my_crewai_tool
    tool_class: google.adk.integrations.crewai.CrewaiTool
    tool_args:
      name: "my_crewai_tool"
      description: "A description of my CrewAI tool."
      tool: "path.to.your.crewai_tool.MyCrewAITool"
```

Replace `"path.to.your.crewai_tool.MyCrewAITool"` with the actual import path to your tool.

## LangChain integration

To use a LangChain tool, you need to wrap it with the `LangchainTool` class. This adapter class converts the LangChain tool into a format that is compatible with the ADK.

### Example

The following example shows how to use a LangChain tool in an ADK agent.

First, define your LangChain tool:

```python
from langchain_core.tools import BaseTool

class MyLangChainTool(BaseTool):
    name: str = "My LangChain Tool"
    description: str = "A description of my LangChain tool."

    def _run(self, input: str) -> str:
        return f"This is the output of my LangChain tool with input: {input}"
```

Next, in your agent configuration, define a tool that uses the `LangchainTool` wrapper to point to your LangChain tool:

```yaml
tools:
  - id: my_langchain_tool
    tool_class: google.adk.integrations.langchain.LangchainTool
    tool_args:
      name: "my_langchain_tool"
      description: "A description of my LangChain tool."
      tool: "path.to.your.langchain_tool.MyLangChainTool"
```

Replace `"path.to.your.langchain_tool.MyLangChainTool"` with the actual import path to your tool.
