---
catalog_title: Anakin
catalog_description: Scrape websites, search the web, and run deep research from your agent
catalog_icon: /adk-docs/integrations/assets/anakin.png
catalog_tags: ["data"]
---

# Anakin plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [Anakin ADK plugin](https://github.com/Anakin-Inc/anakin-adk) connects your
ADK agent to [Anakin](https://useanakin.com) for web data extraction. This
integration gives your agent the ability to scrape web pages, run AI-powered
searches, batch-scrape multiple URLs, and perform autonomous deep research
across the web.

## Use cases

- **Web Scraping**: Extract clean, structured content from any web page —
  articles, product pages, documentation, or dynamic JavaScript-rendered sites.

- **AI-Powered Search**: Run web searches and get back relevant results with
  titles, URLs, and snippets to answer questions or discover sources.

- **Batch Data Collection**: Scrape up to 10 URLs at once to compare products,
  collect articles, or gather data from multiple sources in a single call.

- **Deep Research**: Launch an autonomous research task that explores the web
  and returns a comprehensive report — ideal for market analysis, technical
  deep-dives, or multi-source investigations.

## Prerequisites

- An [Anakin](https://useanakin.com) account
- `anakin-cli` installed and authenticated (`pip install anakin-cli && anakin auth`)

## Installation

```bash
pip install anakin-adk
```

## Use with agent

```python
from anakin_adk import AnakinToolkit
from google.adk.agents import Agent

agent = Agent(
    model="gemini-2.5-pro",
    name="web_researcher",
    instruction="Help users extract data from the web",
    tools=AnakinToolkit().get_tools(),
)
```

## Available tools

Tool | Description
---- | -----------
`scrape_website` | Scrape a single URL and return clean markdown or structured JSON
`batch_scrape` | Scrape up to 10 URLs at once and return combined results
`search_web` | AI-powered web search returning titles, URLs, and snippets
`deep_research` | Autonomous deep research that explores the web and returns a comprehensive report

## Additional resources

- [Anakin ADK on PyPI](https://pypi.org/project/anakin-adk/)
- [Anakin ADK on GitHub](https://github.com/Anakin-Inc/anakin-adk)
- [Anakin CLI Documentation](https://docs.useanakin.com)
- [Anakin Website](https://useanakin.com)
