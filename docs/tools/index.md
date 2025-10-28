---
hide:
  - toc
---

# Tools for Agents

Check out the following pre-built tools that you can use with ADK agents:

### Gemini tools

<div class="tool-card-grid">

  <a href="/adk-docs/tools/built-in-tools/#google-search" class="tool-card">
    <div class="tool-card-image-wrapper">
      <img src="../assets/tools-google-search.png" alt="Google Search">
    </div>
    <div class="tool-card-content">
      <h3>Google Search</h3>
      <p>Perform web searches using Google Search with Gemini</p>
    </div>
  </a>

  <a href="/adk-docs/tools/built-in-tools/#code-execution" class="tool-card">
    <div class="tool-card-image-wrapper">
      <img src="../assets/tools-gemini.png" alt="Gemini">
    </div>
    <div class="tool-card-content">
      <h3>Code Execution</h3>
      <p>Execute code using Gemini models</p>
    </div>
  </a>

</div>

### Google Cloud tools

<div class="tool-card-grid">

  <a href="/adk-docs/tools/google-cloud-tools/#apigee-api-hub-tools" class="tool-card">
    <div class="tool-card-image-wrapper">
      <img src="../assets/tools-apigee.png" alt="Apigee">
    </div>
    <div class="tool-card-content">
      <h3>Apigee API Hub</h3>
      <p>Turn any documented API from Apigee API hub into a tool</p>
    </div>
  </a>

  <a href="/adk-docs/tools/google-cloud-tools/#application-integration-tools" class="tool-card">
    <div class="tool-card-image-wrapper">
      <img src="../assets/tools-apigee-integration.png" alt="Apigee Integration">
    </div>
    <div class="tool-card-content">
      <h3>Application Integration</h3>
      <p>Link your agents to enterprise applications using Integration Connectors</p>
    </div>
  </a>

  <a href="/adk-docs/tools/built-in-tools/#bigquery" class="tool-card">
    <div class="tool-card-image-wrapper">
      <img src="../assets/tools-bigquery.png" alt="BigQuery">
    </div>
    <div class="tool-card-content">
      <h3>BigQuery Tools</h3>
      <p>Connect with BigQuery to retrieve data and perform analysis</p>
    </div>
  </a>

  <a href="/adk-docs/tools/built-in-tools/#bigtable" class="tool-card">
    <div class="tool-card-image-wrapper">
      <img src="../assets/tools-bigtable.png" alt="Bigtable">
    </div>
    <div class="tool-card-content">
      <h3>Bigtable Tools</h3>
      <p>Interact with Bigtable to retrieve data and and execute SQL</p>
    </div>
  </a>

  <a href="/adk-docs/tools/built-in-tools/#gke-code-executor" class="tool-card">
    <div class="tool-card-image-wrapper">
      <img src="../assets/tools-gke.png" alt="Google Kubernetes Engine">
    </div>
    <div class="tool-card-content">
      <h3>GKE Code Executor</h3>
      <p>Run AI-generated code in a secure and scalable GKE Sandbox environment</p>
    </div>
  </a>

  <a href="/adk-docs/tools/built-in-tools/#spanner" class="tool-card">
    <div class="tool-card-image-wrapper">
      <img src="../assets/tools-spanner.png" alt="Spanner">
    </div>
    <div class="tool-card-content">
      <h3>Spanner Tools</h3>
      <p>Interact with Spanner to retrieve data, search, and execute SQL</p>
    </div>
  </a>

  <a href="/adk-docs/tools/google-cloud/mcp-toolbox-for-databases/" class="tool-card">
    <div class="tool-card-image-wrapper">
      <img src="../assets/tools-mcp-toolbox-for-databases.png" alt="MCP Toolbox for Databases">
    </div>
    <div class="tool-card-content">
      <h3>MCP Toolbox for Databases</h3>
      <p>Connect over 30 different data sources to your agents</p>
    </div>
  </a>

  <a href="/adk-docs/tools/built-in-tools/#vertex-ai-rag-engine" class="tool-card">
    <div class="tool-card-image-wrapper">
      <img src="../assets/tools-vertex-ai.png" alt="Vertex AI">
    </div>
    <div class="tool-card-content">
      <h3>Vertex AI RAG Engine</h3>
      <p>Perform private data retrieval using Vertex AI RAG Engine</p>
    </div>
  </a>

  <a href="/adk-docs/tools/built-in-tools/#vertex-ai-search" class="tool-card">
    <div class="tool-card-image-wrapper">
      <img src="../assets/tools-vertex-ai.png" alt="Vertex AI">
    </div>
    <div class="tool-card-content">
      <h3>Vertex AI Search</h3>
      <p>Search across your private, configured data stores in Vertex AI Search</p>
    </div>
  </a>

</div>

### Third-party tools

<div class="tool-card-grid">

  <a href="/adk-docs/tools/third-party/github/" class="tool-card">
    <div class="tool-card-image-wrapper">
      <img src="../assets/tools-github.png" alt="GitHub">
    </div>
    <div class="tool-card-content">
      <h3>GitHub</h3>
      <p>Analyze code, manage issues and PRs, and automate workflows</p>
    </div>
  </a>

  <a href="/adk-docs/tools/third-party/hugging-face/" class="tool-card">
    <div class="tool-card-image-wrapper">
      <img src="../assets/tools-hugging-face.png" alt="Hugging Face">
    </div>
    <div class="tool-card-content">
      <h3>Hugging Face</h3>
      <p>Access models, datasets, research papers, and AI tools</p>
    </div>
  </a>

</div>

## Integrate with existing tools

ADK provides wrappers that can be used to integrate with existing tools from the
LangChain and CrewAI ecosystems:

*   **[LangChain Tools](/adk-docs/tools/third-party/langchain/)**:
    Integrate tools from the LangChain ecosystem.
*   **[CrewAI Tools](/adk-docs/tools/third-party/crewai/)**:
    Integrate tools from the CrewAI library.

## Build your tools

If the above tools don't meet your needs, you can build tools for your ADK
workflows using the following guides:

*   **[Function Tools](/adk-docs/tools/function-tools/)**: Build custom tools for
    your specific ADK agent needs.
*   **[MCP Tools](/adk-docs/tools/function-tools/)**: Connect MCP servers as tools
    for your ADK agents.
*   **[OpenAPI Integration](/adk-docs/tools-custom/openapi-tools/)**:
    Generate callable tools directly from an OpenAPI Specification.
