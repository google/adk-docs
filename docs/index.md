---
hide:
  - toc
---

!!! tip "Google I/O'25 - ADK updates"

    Big news! 

    - Introducing **[Java ADK v0.1.0](https://github.com/google/adk-java/)**, extending agent capabilities to the Java ecosystem.

    - **[Python ADK](https://github.com/google/adk-python/)** is officially v1.0.0 offering stability for production-ready agents.

<div style="text-align: center;">
  <div class="centered-logo-text-group">
    <img src="assets/agent-development-kit.png" alt="Agent Development Kit Logo" width="100">
    <h1>Agent Development Kit</h1>
  </div>
</div>

## What is Agent Development Kit?

Agent Development Kit (ADK) is a flexible and modular framework for **developing
and deploying AI agents**. While optimized for Gemini and the Google ecosystem,
ADK is **model-agnostic**, **deployment-agnostic**, and is built for
**compatibility with other frameworks**. ADK was designed to make agent
development feel more like software development, to make it easier for
developers to create, deploy, and orchestrate agentic architectures that range
from simple tasks to complex workflows.

<div id="centered-install-tabs" class="install-command-container" markdown="1">

<p class="get-started-text" style="text-align: center;">Get started:</p>

=== "Python"
    <br>
    <p style="text-align: center;">
    <code>pip install google-adk</code>
    </p>

=== "Java"

    ```xml title="pom.xml"
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk</artifactId>
        <version>0.1.0</version>
    </dependency>
    ```

    ```gradle title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:0.1.0'
    }
    ```
</div>


<p style="text-align:center;">
  <a href="get-started/quickstart/" class="md-button" style="margin:3px">Quickstart</a>
  <a href="tutorials/" class="md-button" style="margin:3px">Tutorials</a>
  <a href="http://github.com/google/adk-samples" class="md-button" target="_blank" style="margin:3px">Sample Agents</a>
  <a href="api-reference/" class="md-button" style="margin:3px">API Reference</a>
  <a href="contributing-guide/" class="md-button" style="margin:3px">Contribute ❤️</a>
</p>

---

## Learn more

[:fontawesome-brands-youtube:{.youtube-red-icon} Watch "Introducing Agent Development Kit"!](https://www.youtube.com/watch?v=zgrOwow_uTQ target="_blank" rel="noopener noreferrer")

<div class="grid cards" markdown>

-   :material-transit-connection-variant: **Flexible Orchestration**

    ---

    Define workflows using workflow agents (`Sequential`, `Parallel`, `Loop`)
    for predictable pipelines, or leverage LLM-driven dynamic routing
    (`LlmAgent` transfer) for adaptive behavior.

    [**Learn about agents**](agents/index.md)

-   :material-graph: **Multi-Agent Architecture**

    ---

    Build modular and scalable applications by composing multiple specialized
    agents in a hierarchy. Enable complex coordination and delegation.

    [**Explore multi-agent systems**](agents/multi-agents.md)

-   :material-toolbox-outline: **Rich Tool Ecosystem**

    ---

    Equip agents with diverse capabilities: use pre-built tools (Search, Code
    Exec), create custom functions, integrate 3rd-party libraries (LangChain,
    CrewAI), or even use other agents as tools.

    [**Browse tools**](tools/index.md)

-   :material-rocket-launch-outline: **Deployment Ready**

    ---

    Containerize and deploy your agents anywhere – run locally, scale with
    Vertex AI Agent Engine, or integrate into custom infrastructure using Cloud
    Run or Docker.

    [**Deploy agents**](deploy/index.md)

-   :material-clipboard-check-outline: **Built-in Evaluation**

    ---

    Systematically assess agent performance by evaluating both the final
    response quality and the step-by-step execution trajectory against
    predefined test cases.

    [**Evaluate agents**](evaluate/index.md)

-   :material-console-line: **Building Safe and Secure Agents**

    ---

    Learn how to building powerful and trustworthy agents by implementing
    security and safety patterns and best practices into your agent's design.

    [**Safety and Security**](safety/index.md)

</div>
