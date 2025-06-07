# 내장 도구

이러한 내장 도구는 Google 검색이나 코드 실행기와 같이 에이전트에게 일반적인 기능을 제공하는 바로 사용 가능한 기능을 제공합니다. 예를 들어, 웹에서 정보를 검색해야 하는 에이전트는 추가 설정 없이 **google_search** 도구를 직접 사용할 수 있습니다.

## 사용 방법

1.  **가져오기:** 도구 모듈에서 원하는 도구를 가져옵니다. Python에서는 `agents.tools`이고 Java에서는 `com.google.adk.tools`입니다.
2.  **구성:** 필요한 매개변수가 있는 경우 제공하여 도구를 초기화합니다.
3.  **등록:** 초기화된 도구를 에이전트의 **도구** 목록에 추가합니다.

에이전트에 추가되면, 에이전트는 **사용자 프롬프트**와 **지침**을 기반으로 도구 사용을 결정할 수 있습니다. 프레임워크는 에이전트가 도구를 호출할 때 도구 실행을 처리합니다. 중요: 이 페이지의 ***제한 사항*** 섹션을 확인하세요.

## 사용 가능한 내장 도구

참고: Java는 현재 Google 검색 및 코드 실행 도구만 지원합니다.

### Google 검색

`google_search` 도구는 에이전트가 Google 검색을 사용하여 웹 검색을 수행할 수 있도록 합니다. `google_search` 도구는 Gemini 2 모델과만 호환됩니다.

!!! warning "`google_search` 도구 사용 시 추가 요구 사항"
    Google 검색으로 그라운딩을 사용하고 응답에서 검색 제안을 받는 경우, 프로덕션 및 애플리케이션에 검색 제안을 표시해야 합니다. Google 검색으로 그라운딩에 대한 자세한 내용은 [Google AI Studio](https://ai.google.dev/gemini-api/docs/grounding/search-suggestions) 또는 [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions)의 Google 검색으로 그라운딩 문서를 참조하세요. UI 코드(HTML)는 Gemini 응답에서 `renderedContent`로 반환되며, 정책에 따라 앱에 HTML을 표시해야 합니다.

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/google_search.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/GoogleSearchAgentApp.java:full_code"
    ```

### 코드 실행

`built_in_code_execution` 도구는 에이전트가 코드를 실행할 수 있게 하며, 특히 Gemini 2 모델을 사용할 때 그렇습니다. 이를 통해 모델은 계산, 데이터 조작 또는 작은 스크립트 실행과 같은 작업을 수행할 수 있습니다.

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/code_execution.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CodeExecutionAgentApp.java:full_code"
    ```


### Vertex AI 검색

`vertex_ai_search_tool`은 Google Cloud의 Vertex AI Search를 사용하여 에이전트가 비공개로 구성된 데이터 저장소(예: 내부 문서, 회사 정책, 지식 기반)를 검색할 수 있도록 합니다. 이 내장 도구는 구성 중에 특정 데이터 저장소 ID를 제공해야 합니다.



```py
--8<-- "examples/python/snippets/tools/built-in-tools/vertexai_search.py"
```

## 다른 도구와 함께 내장 도구 사용하기

다음 코드 샘플은 여러 내장 도구를 사용하거나 여러 에이전트를 사용하여 다른 도구와 함께 내장 도구를 사용하는 방법을 보여줍니다:

=== "Python"

    ```py
    from google.adk.tools import agent_tool
    from google.adk.agents import Agent
    from google.adk.tools import google_search
    from google.adk.code_executors import BuiltInCodeExecutor
    

    search_agent = Agent(
        model='gemini-2.0-flash',
        name='SearchAgent',
        instruction="""
        당신은 Google 검색 전문가입니다.
        """,
        tools=[google_search],
    )
    coding_agent = Agent(
        model='gemini-2.0-flash',
        name='CodeAgent',
        instruction="""
        당신은 코드 실행 전문가입니다.
        """,
        code_executor=[BuiltInCodeExecutor],
    )
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="루트 에이전트",
        tools=[agent_tool.AgentTool(agent=search_agent), agent_tool.AgentTool(agent=coding_agent)],
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;
    import com.google.adk.tools.BuiltInCodeExecutionTool;
    import com.google.adk.tools.GoogleSearchTool;
    import com.google.common.collect.ImmutableList;
    
    public class NestedAgentApp {
    
      private static final String MODEL_ID = "gemini-2.0-flash";
    
      public static void main(String[] args) {

        // 검색 에이전트 정의
        LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("당신은 Google 검색 전문가입니다.")
                .tools(new GoogleSearchTool()) // GoogleSearchTool 인스턴스화
                .build();
    

        // 코딩 에이전트 정의
        LlmAgent codingAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("CodeAgent")
                .instruction("당신은 코드 실행 전문가입니다.")
                .tools(new BuiltInCodeExecutionTool()) // BuiltInCodeExecutionTool 인스턴스화
                .build();

        // 루트 에이전트 정의, AgentTool.create()를 사용하여 검색 에이전트와 코딩 에이전트를 래핑
        BaseAgent rootAgent =
            LlmAgent.builder()
                .name("RootAgent")
                .model(MODEL_ID)
                .description("루트 에이전트")
                .tools(
                    AgentTool.create(searchAgent), // create 메서드 사용
                    AgentTool.create(codingAgent)   // create 메서드 사용
                 )
                .build();

        // 참고: 이 샘플은 에이전트 정의만 보여줍니다.
        // 이 에이전트들을 실행하려면 Runner와 SessionService와 통합해야 합니다.
        // 이전 예제와 유사하게.
        System.out.println("에이전트가 성공적으로 정의되었습니다:");
        System.out.println("  루트 에이전트: " + rootAgent.name());
        System.out.println("  검색 에이전트 (중첩됨): " + searchAgent.name());
        System.out.println("  코드 에이전트 (중첩됨): " + codingAgent.name());
      }
    }
    ```


### 제한 사항

!!! warning

    현재 각 루트 에이전트 또는 단일 에이전트당 하나의 내장 도구만 지원됩니다. 동일한 에이전트에서 다른 유형의 도구를 사용할 수 없습니다.

 예를 들어, 단일 에이전트 내에서 ***다른 도구와 함께 내장 도구***를 사용하는 다음 접근 방식은 현재 지원되지 **않습니다**:

=== "Python"

    ```py
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="루트 에이전트",
        tools=[custom_function], 
        executor=[BuiltInCodeExecutor] # <-- 도구와 함께 사용할 때 지원되지 않음
    )
    ```

=== "Java"

    ```java
     LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("당신은 Google 검색 전문가입니다.")
                .tools(new GoogleSearchTool(), new YourCustomTool()) // <-- 지원되지 않음
                .build();
    ```

!!! warning

    내장 도구는 하위 에이전트 내에서 사용할 수 없습니다.

예를 들어, 하위 에이전트 내에서 내장 도구를 사용하는 다음 접근 방식은 현재 지원되지 **않습니다**:

=== "Python"

    ```py
    search_agent = Agent(
        model='gemini-2.0-flash',
        name='SearchAgent',
        instruction="""
        당신은 Google 검색 전문가입니다.
        """,
        tools=[google_search],
    )
    coding_agent = Agent(
        model='gemini-2.0-flash',
        name='CodeAgent',
        instruction="""
        당신은 코드 실행 전문가입니다.
        """,
        executor=[BuiltInCodeExecutor],
    )
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="루트 에이전트",
        sub_agents=[
            search_agent,
            coding_agent
        ],
    )
    ```

=== "Java"

    ```java
    LlmAgent searchAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("SearchAgent")
            .instruction("당신은 Google 검색 전문가입니다.")
            .tools(new GoogleSearchTool())
            .build();

    LlmAgent codingAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("CodeAgent")
            .instruction("당신은 코드 실행 전문가입니다.")
            .tools(new BuiltInCodeExecutionTool())
            .build();
    

    LlmAgent rootAgent =
        LlmAgent.builder()
            .name("RootAgent")
            .model("gemini-2.0-flash")
            .description("루트 에이전트")
            .subAgents(searchAgent, codingAgent) // 지원되지 않음, 하위 에이전트가 내장 도구를 사용하기 때문.
            .build();
    ```