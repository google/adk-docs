# Agent Development Kit (ADK)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/google-adk)](https://pypi.org/project/google-adk/)
[![NPM Version](https://img.shields.io/npm/v/@google/adk)](https://www.npmjs.com/package/@google/adk)
[![Go Doc](https://img.shields.io/badge/Go%20Package-Doc-blue.svg)](https://pkg.go.dev/google.golang.org/adk/v2)
[![Maven Central Java](https://img.shields.io/maven-central/v/com.google.adk/google-adk)](https://search.maven.org/artifact/com.google.adk/google-adk)
[![Maven Central Kotlin](https://img.shields.io/maven-central/v/com.google.adk/google-adk-kotlin-core)](https://search.maven.org/artifact/com.google.adk/google-adk-kotlin-core)

[ [English](README.md) | 简体中文 ]

<html>
  <h2 align="center">
    <img src="docs/assets/agent-development-kit.png" width="150"/>
  </h2>
</html>

**开源、代码优先的工具包，助您灵活自如地构建、评估与部署前沿 AI 智能体。**

智能体开发套件（Agent Development Kit，简称 ADK）是一个用于**开发与部署 AI 智能体**的灵活且模块化框架。虽然 ADK 针对 Gemini 与 Google 生态系统进行了深度优化，但它本质上是**模型无关（model-agnostic）**、**部署平台无关（deployment-agnostic）**的，并天然具备**与其他第三方框架的兼容性**。ADK 的设计理念是让智能体开发体验更加贴近传统软件工程开发，使开发者能够更加轻松地创建、部署和编排从单一任务到复杂工作流的各类智能体架构。

---

## ✨ 核心特性

- **丰富的工具生态**：利用预构建工具、自定义函数、OpenAPI 规范，或集成现有工具赋予智能体多样化能力，全面紧密集成 Google 生态系统。

- **代码优先开发**：直接在代码中定义智能体业务逻辑、工具与工作流编排，获得极致的灵活性、可测试性与版本管理能力。

- **模块化多智能体系统**：通过将多个专业化智能体组合成灵活的层级架构，设计具备高扩展性的应用程序。

- **追踪与监控**：内置端到端智能体可观测性（Observability），便于调试排障与优化工作流。

- **随时随地部署**：轻松将智能体容器化并部署至 Cloud Run 或 GKE，或借助 Agent Runtime 实现无缝弹性扩缩容。

## 🚀 使用指南 (Usage)

您可以使用您偏好的编程语言来使用智能体开发套件（ADK）：

- **[快速上手 ADK Python](https://adk.dev/get-started/python/)**

- **[快速上手 ADK TypeScript](https://adk.dev/get-started/typescript/)**

- **[快速上手 ADK Go](https://adk.dev/get-started/go/)**

- **[快速上手 ADK Java](https://adk.dev/get-started/java/)**

- **[快速上手 ADK Kotlin](https://adk.dev/get-started/kotlin/)**

## 📚 官方文档

探索完整官方文档，查阅关于构建、评估与部署智能体的详细指南：

- **[官方文档 (Documentation)](https://adk.dev)**

## ✨ AI 辅助编程 (Coding with AI)

利用 AI 辅助编程加速您的 ADK 智能体开发工作流。ADK 提供了与各类 AI 代码编辑器高度兼容的优化文档上下文：

- **[llms.txt](https://adk.dev/llms.txt)**：结构化的 ADK 文档索引，专门帮助大语言模型导航与检索特定主题和开发指南。
- **[llms-full.txt](https://adk.dev/llms-full.txt)**：详尽全面的全量文档参考，特别适用于复杂架构实现或具备超大上下文窗口的模型。

您还可以访问我们的 **[AI 辅助编程指南 (Coding with AI)](https://adk.dev/tutorials/coding-with-ai/)**，了解如何通过 MCP（Model Context Protocol）服务器在 AI 编码工具中使用这些文档文件。

## 🤝 贡献指南

我们热烈欢迎来自社区的贡献！无论是 Bug 报告、功能建议、文档改进还是代码贡献，都请先参阅我们的**[贡献指南](./CONTRIBUTING.md)**了解如何开始。

## 📄 许可证

本项目基于 Apache 2.0 许可证开源 —— 详情请参阅 **[LICENSE](LICENSE)** 文件。

---

*祝您智能体构建愉快！*

---

> **翻译说明（Translation Disclaimer）**
> 本文档由社区志愿者（[@JasonYeYuhe](https://github.com/JasonYeYuhe)）人工翻译并维护，旨在降低中文开发者的阅读门槛。最后同步日期：2026年11月14日。若译文与英文原版存在任何出入或滞后，请以 [英文原版 (README.md)](README.md) 为准。欢迎通过 PR 协助改进译文！
