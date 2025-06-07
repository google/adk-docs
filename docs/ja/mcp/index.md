# Model Context Protocol (MCP)

## Model Context Protocol (MCP)とは？

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction)は、GeminiやClaudeのような大規模言語モデル（LLM）が外部のアプリケーション、データソース、ツールとどのように通信するかを標準化するために設計されたオープンスタンダードです。LLMがコンテキストを取得し、アクションを実行し、様々なシステムと対話する方法を簡素化する、普遍的な接続メカニズムと考えることができます。

## MCPはどのように機能しますか？

MCPはクライアントサーバーアーキテクチャに従い、データ（リソース）、対話型テンプレート（プロンプト）、および実行可能な関数（ツール）がMCPサーバーによってどのように公開され、MCPクライアント（LLMホストアプリケーションやAIエージェントなど）によってどのように消費されるかを定義します。

## ADKにおけるMCPツール

ADKは、MCPサービスを呼び出すためのツールを構築しようとしている場合でも、他の開発者やエージェントがあなたのツールと対話できるようにMCPサーバーを公開している場合でも、エージェントでMCPツールを使用および消費する両方を支援します。

ADKをMCPサーバーと一緒に使用するのに役立つコードサンプルや設計パターンについては、[MCPツールのドキュメント](../tools/mcp-tools.md)を参照してください。以下を含みます：

- **ADK内での既存のMCPサーバーの使用**：ADKエージェントはMCPクライアントとして機能し、外部のMCPサーバーによって提供されるツールを使用できます。
- **MCPサーバーを介したADKツールの公開**：ADKツールをラップし、任意のMCPクライアントからアクセス可能にするMCPサーバーを構築する方法。

## MCP Toolbox for Databases

[MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox)は、エージェントがデータベースのデータにアクセスできるようにするためのGen AIツールを構築するのに役立つオープンソースのMCPサーバーです。GoogleのAgent Development Kit（ADK）は、MCP Toolbox for Databasesを組み込みでサポートしています。

ADKをMCP Toolbox for Databasesと一緒に使用する方法については、[MCP Toolbox for Databasesのドキュメント](../tools/google-cloud-tools.md#toolbox-tools-for-databases)を参照してください。MCP Toolbox for Databasesを始めるにあたり、ブログ投稿[チュートリアル：MCP Toolbox for Databases - Big Queryデータセットの公開](https://medium.com/google-cloud/tutorial-mcp-toolbox-for-databases-exposing-big-query-datasets-9321f0064f4e)およびCodelab[MCP Toolbox for Databases：MCPクライアントがBigQueryデータセットを利用できるようにする](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en#0)も利用可能です。

![GenAI Toolbox](../assets/mcp_db_toolbox.png)

## ADKエージェントとFastMCPサーバー
[FastMCP](https://github.com/jlowin/fastmcp)は、複雑なMCPプロトコルの詳細とサーバー管理のすべてを処理するため、あなたは優れたツールの構築に集中できます。これは高レベルでPythonicに設計されており、ほとんどの場合、関数をデコレートするだけで済みます。

Cloud Runで実行されているFastMCPサーバーとADKを一緒に使用する方法については、[MCPツールのドキュメント](../tools/mcp-tools.md)を参照してください。

## Google Cloud Genmedia向けMCPサーバー

[MCP Tools for Genmedia Services](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia)は、Google Cloudの生成メディアサービス（Imagen、Veo、Chirp 3 HDボイス、Lyriaなど）をAIアプリケーションに統合できるようにする、オープンソースのMCPサーバーのセットです。

Agent Development Kit（ADK）と[Genkit](https://genkit.dev/)は、これらのMCPツールを組み込みでサポートしており、AIエージェントが生成メディアのワークフローを効果的に調整できるようにします。実装ガイダンスについては、[ADKのサンプルエージェント](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/adk)および[Genkitのサンプル](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/genkit)を参照してください。