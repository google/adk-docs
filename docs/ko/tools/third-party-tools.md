# 서드파티 도구

![python_only](https://img.shields.io/badge/현재_지원되는_언어-Python-blue){ title="이 기능은 현재 Python에서만 사용할 수 있습니다. Java 지원은 계획 중이거나 곧 제공될 예정입니다."}

ADK는 CrewAI 및 LangChain과 같은 다른 AI 에이전트 프레임워크의 도구를 원활하게 통합할 수 있도록 **매우 확장 가능하게 설계**되었습니다. 이러한 상호 운용성은 개발 시간을 단축하고 기존 도구를 재사용할 수 있게 해주므로 매우 중요합니다.

## 1. LangChain 도구 사용

ADK는 LangChain 생태계의 도구를 에이전트에 통합하기 위해 `LangchainTool` 래퍼를 제공합니다.

### 예제: LangChain의 Tavily 도구를 사용한 웹 검색

[Tavily](https://tavily.com/)는 AI 에이전트와 같은 애플리케이션에서 사용하기 위한 실시간 검색 결과에서 파생된 답변을 반환하는 검색 API를 제공합니다.

1. [ADK 설치 및 설정](../get-started/installation.md) 가이드를 따릅니다.

2. **종속성 설치:** 필요한 LangChain 패키지가 설치되어 있는지 확인합니다. 예를 들어, Tavily 검색 도구를 사용하려면 특정 종속성을 설치해야 합니다:

    ```bash
    pip install langchain_community tavily-python
    ```

3. [Tavily](https://tavily.com/) API KEY를 얻고 환경 변수로 내보냅니다.

    ```bash
    export TAVILY_API_KEY=<API_KEY로_교체>
    ```

4. **가져오기:** ADK에서 `LangchainTool` 래퍼를 가져오고 사용하려는 특정 `LangChain` 도구(예: `TavilySearchResults`)를 가져옵니다.

    ```py
    from google.adk.tools.langchain_tool import LangchainTool
    from langchain_community.tools import TavilySearchResults
    ```

5. **인스턴스화 및 래핑:** LangChain 도구의 인스턴스를 만들고 `LangchainTool` 생성자에 전달합니다.

    ```py
    # LangChain 도구 인스턴스화
    tavily_tool_instance = TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True,
        include_images=True,
    )

    # ADK용 LangchainTool로 래핑
    adk_tavily_tool = LangchainTool(tool=tavily_tool_instance)
    ```

6. **에이전트에 추가:** 래핑된 `LangchainTool` 인스턴스를 에이전트 정의 중 `tools` 목록에 포함합니다.

    ```py
    from google.adk import Agent

    # 래핑된 도구를 포함하여 ADK 에이전트 정의
    my_agent = Agent(
        name="langchain_tool_agent",
        model="gemini-2.0-flash",
        description="TavilySearch를 사용하여 질문에 답하는 에이전트.",
        instruction="인터넷을 검색하여 질문에 답할 수 있습니다. 무엇이든 물어보세요!",
        tools=[adk_tavily_tool] # 여기에 래핑된 도구 추가
    )
    ```

### 전체 예제: Tavily 검색

다음은 LangChain Tavily 검색 도구를 사용하여 에이전트를 만들고 실행하는 위의 단계를 결합한 전체 코드입니다.

```py
--8<-- "examples/python/snippets/tools/third-party/langchain_tavily_search.py"
```

## 2. CrewAI 도구 사용

ADK는 CrewAI 라이브러리의 도구를 통합하기 위해 `CrewaiTool` 래퍼를 제공합니다.

### 예제: CrewAI의 Serper API를 사용한 웹 검색

[Serper API](https://serper.dev/)는 프로그래밍 방식으로 Google 검색 결과에 대한 접근을 제공합니다. 이를 통해 AI 에이전트와 같은 애플리케이션은 웹 페이지를 직접 스크래핑할 필요 없이 실시간 Google 검색(뉴스, 이미지 등 포함)을 수행하고 구조화된 데이터를 다시 얻을 수 있습니다.

1. [ADK 설치 및 설정](../get-started/installation.md) 가이드를 따릅니다.

2. **종속성 설치:** 필요한 CrewAI 도구 패키지를 설치합니다. 예를 들어, SerperDevTool을 사용하려면 다음을 설치합니다:

    ```bash
    pip install crewai-tools
    ```

3. [Serper API KEY](https://serper.dev/)를 얻고 환경 변수로 내보냅니다.

    ```bash
    export SERPER_API_KEY=<API_KEY로_교체>
    ```

4. **가져오기:** ADK에서 `CrewaiTool`을 가져오고 원하는 CrewAI 도구(예: `SerperDevTool`)를 가져옵니다.

    ```py
    from google.adk.tools.crewai_tool import CrewaiTool
    from crewai_tools import SerperDevTool
    ```

5. **인스턴스화 및 래핑:** CrewAI 도구의 인스턴스를 만듭니다. 이를 `CrewaiTool` 생성자에 전달합니다. **결정적으로, ADK의 기본 모델이 언제 도구를 사용해야 하는지 이해하는 데 사용되므로 ADK 래퍼에 이름과 설명을 제공해야 합니다.**

    ```py
    # CrewAI 도구 인스턴스화
    serper_tool_instance = SerperDevTool(
        n_results=10,
        save_file=False,
        search_type="news",
    )

    # 이름과 설명을 제공하여 ADK용 CrewaiTool로 래핑
    adk_serper_tool = CrewaiTool(
        name="InternetNewsSearch",
        description="Serper를 사용하여 최근 뉴스 기사를 구체적으로 검색합니다.",
        tool=serper_tool_instance
    )
    ```

6. **에이전트에 추가:** 래핑된 `CrewaiTool` 인스턴스를 에이전트의 `tools` 목록에 포함합니다.

    ```py
    from google.adk import Agent
 
    # ADK 에이전트 정의
    my_agent = Agent(
        name="crewai_search_agent",
        model="gemini-2.0-flash",
        description="Serper 검색 도구를 사용하여 최근 뉴스를 찾는 에이전트.",
        instruction="최신 뉴스를 찾아드릴 수 있습니다. 어떤 주제에 관심이 있으신가요?",
        tools=[adk_serper_tool] # 여기에 래핑된 도구 추가
    )
    ```

### 전체 예제: Serper API

다음은 CrewAI Serper API 검색 도구를 사용하여 에이전트를 만들고 실행하는 위의 단계를 결합한 전체 코드입니다.

```py
--8<-- "examples/python/snippets/tools/third-party/crewai_serper_search.py"
```