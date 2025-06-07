# Model Context Protocol (MCP)

## 모델 컨텍스트 프로토콜(MCP)이란 무엇인가요?

[모델 컨텍스트 프로토콜(MCP)](https://modelcontextprotocol.io/introduction)은 Gemini 및 Claude와 같은 거대 언어 모델(LLM)이 외부 애플리케이션, 데이터 소스 및 도구와 통신하는 방법을 표준화하기 위해 설계된 개방형 표준입니다. 이는 LLM이 컨텍스트를 얻고, 작업을 실행하며, 다양한 시스템과 상호 작용하는 방식을 단순화하는 보편적인 연결 메커니즘으로 생각할 수 있습니다.

## MCP는 어떻게 작동하나요?

MCP는 클라이언트-서버 아키텍처를 따르며, 데이터(리소스), 대화형 템플릿(프롬프트), 실행 가능한 함수(도구)가 MCP 서버에 의해 노출되고 MCP 클라이언트(LLM 호스트 애플리케이션 또는 AI 에이전트일 수 있음)에 의해 소비되는 방식을 정의합니다.

## ADK의 MCP 도구

ADK는 MCP 서비스를 호출하기 위한 도구를 구축하든, 다른 개발자나 에이전트가 여러분의 도구와 상호 작용할 수 있도록 MCP 서버를 노출하든, 에이전트에서 MCP 도구를 사용하고 소비하는 데 도움을 줍니다.

ADK를 MCP 서버와 함께 사용하는 데 도움이 되는 코드 샘플 및 디자인 패턴은 [MCP 도구 문서](../tools/mcp-tools.md)를 참조하세요. 여기에는 다음이 포함됩니다:

-   **ADK 내에서 기존 MCP 서버 사용**: ADK 에이전트는 MCP 클라이언트 역할을 하고 외부 MCP 서버에서 제공하는 도구를 사용할 수 있습니다.
-   **MCP 서버를 통해 ADK 도구 노출**: ADK 도구를 래핑하여 모든 MCP 클라이언트에서 접근할 수 있도록 하는 MCP 서버를 구축하는 방법.

## 데이터베이스용 MCP 도구 상자

[데이터베이스용 MCP 도구 상자](https://github.com/googleapis/genai-toolbox)는 에이전트가 데이터베이스의 데이터에 접근할 수 있도록 Gen AI 도구를 구축하는 데 도움이 되는 오픈 소스 MCP 서버입니다. Google의 Agent Development Kit(ADK)는 데이터베이스용 MCP 도구 상자를 기본적으로 지원합니다.

ADK를 데이터베이스용 MCP 도구 상자와 함께 사용하는 방법에 대한 자세한 내용은 [데이터베이스용 MCP 도구 상자 문서](../tools/google-cloud-tools.md#toolbox-tools-for-databases)를 참조하세요. 데이터베이스용 MCP 도구 상자를 시작하기 위해 블로그 게시물 [튜토리얼: 데이터베이스용 MCP 도구 상자 - BigQuery 데이터 세트 노출](https://medium.com/google-cloud/tutorial-mcp-toolbox-for-databases-exposing-big-query-datasets-9321f0064f4e)과 Codelab [데이터베이스용 MCP 도구 상자: BigQuery 데이터 세트를 MCP 클라이언트에서 사용 가능하게 만들기](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en#0)도 제공됩니다.

![GenAI 도구 상자](../assets/mcp_db_toolbox.png)

## ADK 에이전트와 FastMCP 서버

[FastMCP](https://github.com/jlowin/fastmcp)는 복잡한 MCP 프로토콜 세부 정보와 서버 관리를 모두 처리하므로 훌륭한 도구를 구축하는 데 집중할 수 있습니다. 이는 높은 수준의 Pythonic 방식으로 설계되었으며, 대부분의 경우 함수를 데코레이팅하는 것만으로 충분합니다.

ADK를 Cloud Run에서 실행되는 FastMCP 서버와 함께 사용하는 방법에 대한 자세한 내용은 [MCP 도구 문서](../tools/mcp-tools.md)를 참조하세요.

## Google Cloud Genmedia용 MCP 서버

[Genmedia 서비스용 MCP 도구](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia)는 Imagen, Veo, Chirp 3 HD 음성, Lyria와 같은 Google Cloud 생성형 미디어 서비스를 AI 애플리케이션에 통합할 수 있도록 하는 오픈 소스 MCP 서버 세트입니다.

Agent Development Kit(ADK)와 [Genkit](https://genkit.dev/)은 이러한 MCP 도구를 기본적으로 지원하여 AI 에이전트가 생성형 미디어 워크플로를 효과적으로 조율할 수 있도록 합니다. 구현 지침은 [ADK 예제 에이전트](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/adk)와 [Genkit 예제](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/genkit)를 참조하세요.