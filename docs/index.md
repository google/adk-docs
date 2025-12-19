---
hide:
  - toc
---

<div style="text-align: center;">
  <div class="centered-logo-text-group">
    <img src="assets/agent-development-kit.png" alt="Agent Development Kit Logo" width="100">
    <h1>Agent Development Kit</h1>
  </div>
</div>

Agent Development Kit (ADK) is a flexible and modular framework for **developing
and deploying AI agents**. While optimized for Gemini and the Google ecosystem,
ADK is **model-agnostic**, **deployment-agnostic**, and is built for
**compatibility with other frameworks**. ADK was designed to make agent
development feel more like software development, to make it easier for
developers to create, deploy, and orchestrate agentic architectures that range
from simple tasks to complex workflows.

??? tip "News: ADK TypeScript v0.2.0 released!"

    ADK TypeScript v0.2.0 is officially released! By popular demand, the ADK
    team has brought the power of Agent Development Kit to one of the most
    popular programming languages on the planet. For details, check out the
    [blog post](https://developers.googleblog.com/introducing-agent-development-kit-for-typescript-build-ai-agents-with-the-power-of-a-code-first-approach/).

??? tip "News: ADK Go v0.3.0 released!"

    ADK Go release v0.3.0 includes numerous bug fixes, introduces new features
    such as agent-to-agent request callbacks and extendability, and updates
    dependencies like the GenAI SDK and the ADK Web UI.
    For release details, check out the
    [release notes](https://github.com/google/adk-go/releases/tag/v0.3.0).

??? tip "News: ADK Java v0.5.0 released!"

    The ADK Go v0.5.0 release adds new features for tool execution mode
    configuration and model versioning, along with numerous bug fixes,
    dependency updates, and significant refactoring to improve the agent
    and runner architecture. For release details, check out the
    [release notes](https://github.com/google/adk-java/releases/tag/v0.5.0).

<div id="centered-install-tabs" class="install-command-container" markdown="1">

<p class="get-started-text" style="text-align: center;">Get started:</p>

=== "Python"
    <br>
    <p style="text-align: center;">
    <code>pip install google-adk</code>
    </p>

=== "TypeScript"
    <br>
    <p style="text-align: center;">
    <code>npm install @google/adk</code>
    </p>

=== "Go"
    <br>
    <p style="text-align: center;">
    <code>go get google.golang.org/adk</code>
    </p>

=== "Java"

    ```xml title="pom.xml"
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk</artifactId>
        <version>0.5.0</version>
    </dependency>
    ```

    ```gradle title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:0.5.0'
    }
    ```

</div>

<p style="text-align:center;">
  <a href="/adk-docs/get-started/python/" class="md-button" style="margin:3px">Start with Python</a>
  <a href="/adk-docs/get-started/typescript/" class="md-button" style="margin:3px">Start with TypeScript</a>
  <a href="/adk-docs/get-started/go/" class="md-button" style="margin:3px">Start with Go</a>
  <a href="/adk-docs/get-started/java/" class="md-button" style="margin:3px">Start with Java</a>
</p>

---

## Learn more

[:fontawesome-brands-youtube:{.youtube-red-icon} Watch "Introducing Agent Development Kit"!](https://www.youtube.com/watch?v=zgrOwow_uTQ){:target="_blank" rel="noopener noreferrer"}

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
    Exec), create custom functions, integrate 3rd-party libraries, or even use
    other agents as tools.

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
