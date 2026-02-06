# Grounding agents with data

Grounding is the process that connects your AI agents to external information sources, allowing them to generate more accurate, current, and verifiable responses. By grounding agent responses in authoritative data, you can reduce hallucinations and provide users with answers backed by reliable sources.

ADK supports multiple grounding approaches:

- **Google Search Grounding**: Connect agents to real-time web information for queries requiring current data like news, weather, or facts that may have changed since the model's training.

- **Vertex AI Search Grounding**: Connect agents to your organization's private documents and enterprise data for queries requiring proprietary information.

- **Agentic RAG**: Build agents that reason about how to search, constructing queries and filters dynamically using Vector Search 2.0, Vertex AI RAG Engine, or other retrieval systems.

- **Google Search Grounding**

  ______________________________________________________________________

  Enable your agents to access real-time, authoritative information from the web. Learn how to set up Google Search grounding, understand the data flow, interpret grounded responses, and display citations to users.

  - [Understanding Google Search Grounding](https://google.github.io/adk-docs/grounding/google_search_grounding/index.md)

- **Vertex AI Search Grounding**

  ______________________________________________________________________

  Connect your agents to indexed enterprise documents and private data repositories. Learn how to configure Vertex AI Search datastores, ground responses in your organization's knowledge base, and provide source attribution.

  - [Understanding Vertex AI Search Grounding](https://google.github.io/adk-docs/grounding/vertex_ai_search_grounding/index.md)

- **Blog post: 10-minute Agentic RAG with Vector Search 2.0 and ADK**

  ______________________________________________________________________

  Learn how to build an Agentic RAG system that goes beyond simple retrieve-then-generate patterns. This article walks through building a travel agent that parses user intent, constructs metadata filters, and searches 2,000 London Airbnb listings using hybrid search with Vector Search 2.0 and ADK.

  - [Blog post: 10-minute Agentic RAG with Vector Search 2.0 and ADK](https://medium.com/google-cloud/10-minute-agentic-rag-with-the-new-vector-search-2-0-and-adk-655fff0bacac)

- **Vector Search 2.0 Travel Agent Notebook**

  ______________________________________________________________________

  A hands-on Jupyter notebook companion to the Agentic RAG blog post. Build an end-to-end travel agent using real Airbnb data, auto-embeddings, hybrid search with RRF ranking, and ADK tool integration.

  - [Vector Search 2.0 Travel Agent Notebook](https://github.com/google/adk-samples/blob/main/python/notebooks/grounding/vectorsearch2_travel_agent.ipynb)

- **Deep Search Agent**

  ______________________________________________________________________

  A production-ready fullstack research agent that transforms topics into comprehensive reports with citations. Features a two-phase workflow with human-in-the-loop plan approval, iterative search refinement, and multi-agent architecture for planning, researching, critiquing, and composing.

  - [Deep Search Agent](https://github.com/google/adk-samples/tree/main/python/agents/deep-search)

- **RAG Agent**

  ______________________________________________________________________

  A document Q&A agent powered by Vertex AI RAG Engine. Upload documents and ask questions to receive accurate answers with citations formatted as URLs pointing to source materials.

  - [RAG Agent](https://github.com/google/adk-samples/tree/main/python/agents/RAG)
