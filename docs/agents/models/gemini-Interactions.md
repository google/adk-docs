Gemini Interactions API {#interactions-api}

<div class="language-support-tag" title="Java ADK currently supports Gemini and Anthropic models.">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.21.0</span>
</div>

The Gemini [Interactions API](https://ai.google.dev/gemini-api/docs/interactions)
is an alternative to the ***generateContent*** inference API, which provides
stateful conversation capabilities, allowing you to chain interactions using a
`previous_interaction_id` instead of sending the full conversation history with
each request. Using this feature can be more efficient for long conversations.

You can enable the Interactions API by setting the `use_interactions_api=True`
parameter in the Gemini model configuration, as shown in the following code
snippet:

```python
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.google_search_tool import GoogleSearchTool

root_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash",
        use_interactions_api=True,  # Enable Interactions API
    ),
    name="interactions_test_agent",
    tools=[
        GoogleSearchTool(bypass_multi_tools_limit=True),  # Converted to function tool
        get_current_weather,  # Custom function tool
    ],
)
```

For a complete code sample, see the
[Interactions API sample](https://github.com/google/adk-python/tree/main/contributing/samples/interactions_api).

### Known limitations

The Interactions API **does not** support mixing custom function calling tools with
built-in tools, such as the
[Google Search](/adk-docs/tools/built-in-tools/#google-search),
tool, within the same agent. You can work around this limitation by configuring the
the built-in tool to operate as a custom tool using the `bypass_multi_tools_limit`
parameter:

```python
# Use bypass_multi_tools_limit=True to convert google_search to a function tool
GoogleSearchTool(bypass_multi_tools_limit=True)
```

In this example, this option converts the built-in google_search to a function
calling tool (via GoogleSearchAgentTool), which allows it to work alongside
custom function tools.