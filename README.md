# Agent Development Kit (ADK)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Docs Health](docs-health-badge.svg)](docs_health_report.md)

<img src="docs/assets/agent-development-kit.png" alt="Agent Development Kit Logo" width="150">

**An open-source, code-first toolkit for building, evaluating, and
deploying sophisticated AI agents with flexibility and control.**

Agent Development Kit (ADK) is a flexible and modular framework for **developing
and deploying AI agents**. While optimized for Gemini and the Google ecosystem,
ADK is **model-agnostic**, **deployment-agnostic**, and is built for
**compatibility with other frameworks**. ADK was designed to make agent
development feel more like software development, to make it easier for
developers to create, deploy, and orchestrate agentic architectures that range
from simple tasks to complex workflows.

---

## ✨ Key Features

- **Rich Tool Ecosystem**: Utilize pre-built tools, custom functions,
  OpenAPI specs, or integrate existing tools to give agents diverse
  capabilities, all for tight integration with the Google ecosystem.

- **Code-First Development**: Define agent logic, tools, and orchestration
  directly in Python and Java for ultimate flexibility, testability, and versioning.

- **Modular Multi-Agent Systems**: Design scalable applications by composing
  multiple specialized agents into flexible hierarchies.

- **Tracing and Monitoring**: Built-in agent observability for debugging and optimizing
  workflows with support from external providers like [AgentOps](https://www.agentops.ai).

- **Deploy Anywhere**: Easily containerize and deploy agents on Cloud Run or
  scale seamlessly with Vertex AI Agent Engine.

## 🚀 Installation

You can install the Agent Development Kit (ADK) using your preferred package manager for Python or build tool for Java.

### For Python (pip)

```bash
pip install google-adk
```

### For Java (Maven)

```xml
<dependency>
    <groupId>com.google.adk</groupId>
    <artifactId>google-adk</artifactId>
    <version>0.1.0</version>
</dependency>
```

### For Java (Gradle)

```groovy
dependencies {
    implementation 'com.google.adk:google-adk:0.1.0'
}
```

## 📚 Documentation

Explore the full documentation for detailed guides on building, evaluating, and
deploying agents:

* **[Documentation](https://google.github.io/adk-docs)**

## 🤝 Contributing

We welcome contributions from the community! Whether it's bug reports, feature
requests, documentation improvements, or code contributions, please see our
[**Contributing Guidelines**](./CONTRIBUTING.md) to get started.

## 📄 License

This project is licensed under the Apache 2.0 License - see the
[LICENSE](LICENSE) file for details.

---

*Happy Agent Building!*
