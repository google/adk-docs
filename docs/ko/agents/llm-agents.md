# LLM 에이전트

`LlmAgent` (종종 `Agent`로 별칭됨)는 ADK의 핵심 구성 요소로, 애플리케이션의 "사고" 부분 역할을 합니다. 거대 언어 모델(LLM)의 힘을 활용하여 추론하고, 자연어를 이해하며, 결정을 내리고, 응답을 생성하고, 도구와 상호 작용합니다.

미리 정의된 실행 경로를 따르는 결정론적인 [워크플로 에이전트](workflow-agents/index.md)와 달리, `LlmAgent`의 동작은 비결정론적입니다. LLM을 사용하여 지침과 컨텍스트를 해석하고, 어떻게 진행할지, 어떤 도구를 사용할지(사용하는 경우), 또는 다른 에이전트로 제어권을 이전할지 동적으로 결정합니다.

효과적인 `LlmAgent`를 구축하려면 그 정체성을 정의하고, 지침을 통해 행동을 명확하게 안내하며, 필요한 도구와 기능을 갖추는 것이 포함됩니다.

## 에이전트의 정체성과 목적 정의하기

먼저, 에이전트가 *무엇이며* *무엇을 위한 것인지* 설정해야 합니다.

*   **`name` (필수):** 모든 에이전트에는 고유한 문자열 식별자가 필요합니다. 이 `name`은 내부 작업, 특히 에이전트가 서로를 참조하거나 작업을 위임해야 하는 멀티 에이전트 시스템에서 매우 중요합니다. 에이전트의 기능을 반영하는 설명적인 이름(예: `customer_support_router`, `billing_inquiry_agent`)을 선택하세요. `user`와 같은 예약된 이름은 피하세요.

*   **`description` (선택 사항, 멀티 에이전트에 권장):** 에이전트의 기능에 대한 간결한 요약을 제공하세요. 이 설명은 주로 *다른* LLM 에이전트가 이 에이전트에게 작업을 라우팅해야 하는지 여부를 결정하는 데 사용됩니다. 동료와 구별될 수 있도록 충분히 구체적으로 작성하세요(예: "현재 청구서에 대한 문의 처리"이지 "청구 에이전트"만이 아님).

*   **`model` (필수):** 이 에이전트의 추론을 담당할 기본 LLM을 지정하세요. 이는 `"gemini-2.0-flash"`와 같은 문자열 식별자입니다. 모델 선택은 에이전트의 기능, 비용 및 성능에 영향을 미칩니다. 사용 가능한 옵션 및 고려 사항은 [모델](models.md) 페이지를 참조하세요.

=== "Python"

    ```python
    # 예제: 기본 정체성 정의
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="주어진 국가의 수도에 대한 사용자 질문에 답변합니다."
        # instruction 및 tools는 다음에 추가됩니다.
    )
    ```

=== "Java"

    ```java
    // 예제: 기본 정체성 정의
    LlmAgent capitalAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("capital_agent")
            .description("주어진 국가의 수도에 대한 사용자 질문에 답변합니다.")
            // instruction 및 tools는 다음에 추가됩니다.
            .build();
    ```


## 에이전트 안내하기: 지침 (`instruction`)

`instruction` 매개변수는 `LlmAgent`의 행동을 형성하는 데 있어 가장 중요한 요소라고 할 수 있습니다. 이는 에이전트에게 다음을 알려주는 문자열(또는 문자열을 반환하는 함수)입니다:

*   핵심 작업 또는 목표.
*   성격 또는 페르소나 (예: "당신은 도움이 되는 어시스턴트입니다.", "당신은 재치 있는 해적입니다.").
*   행동에 대한 제약 (예: "X에 대한 질문에만 답변하세요.", "Y는 절대 공개하지 마세요.").
*   `tools`를 어떻게 그리고 언제 사용해야 하는지. 각 도구의 목적과 호출되어야 하는 상황을 설명하여 도구 자체 내의 설명을 보완해야 합니다.
*   출력의 원하는 형식 (예: "JSON으로 응답하세요.", "글머리 기호 목록으로 제공하세요.").

**효과적인 지침을 위한 팁:**

*   **명확하고 구체적으로:** 모호함을 피하세요. 원하는 행동과 결과를 명확하게 기술하세요.
*   **마크다운 사용:** 제목, 목록 등을 사용하여 복잡한 지침의 가독성을 향상시키세요.
*   **예제 제공 (소수 샷):** 복잡한 작업이나 특정 출력 형식의 경우, 지침에 직접 예제를 포함하세요.
*   **도구 사용 안내:** 도구를 나열하는 것뿐만 아니라, 에이전트가 *언제* 그리고 *왜* 사용해야 하는지 설명하세요.

**상태:**

*   지침은 문자열 템플릿이며, `{var}` 구문을 사용하여 동적 값을 지침에 삽입할 수 있습니다.
*   `{var}`는 var라는 이름의 상태 변수 값을 삽입하는 데 사용됩니다.
*   `{artifact.var}`는 var라는 이름의 아티팩트의 텍스트 내용을 삽입하는 데 사용됩니다.
*   상태 변수나 아티팩트가 존재하지 않으면 에이전트는 오류를 발생시킵니다. 오류를 무시하려면 `{var?}`와 같이 변수 이름에 `?`를 추가할 수 있습니다.

=== "Python"

    ```python
    # 예제: 지침 추가
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="주어진 국가의 수도에 대한 사용자 질문에 답변합니다.",
        instruction="""당신은 국가의 수도를 제공하는 에이전트입니다.
    사용자가 국가의 수도를 물을 때:
    1. 사용자의 쿼리에서 국가 이름을 식별합니다.
    2. `get_capital_city` 도구를 사용하여 수도를 찾습니다.
    3. 수도를 명확하게 언급하며 사용자에게 응답합니다.
    예제 쿼리: "{country}의 수도는 어디인가요?"
    예제 응답: "프랑스의 수도는 파리입니다."
    """,
        # tools는 다음에 추가됩니다.
    )
    ```

=== "Java"

    ```java
    // 예제: 지침 추가
    LlmAgent capitalAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("capital_agent")
            .description("주어진 국가의 수도에 대한 사용자 질문에 답변합니다.")
            .instruction(
                """
                당신은 국가의 수도를 제공하는 에이전트입니다.
                사용자가 국가의 수도를 물을 때:
                1. 사용자의 쿼리에서 국가 이름을 식별합니다.
                2. `get_capital_city` 도구를 사용하여 수도를 찾습니다.
                3. 수도를 명확하게 언급하며 사용자에게 응답합니다.
                예제 쿼리: "{country}의 수도는 어디인가요?"
                예제 응답: "프랑스의 수도는 파리입니다."
                """)
            // tools는 다음에 추가됩니다.
            .build();
    ```

*(참고: 시스템의 *모든* 에이전트에 적용되는 지침의 경우, 루트 에이전트에서 `global_instruction`을 사용하는 것을 고려하세요. 자세한 내용은 [멀티 에이전트](multi-agents.md) 섹션을 참조하세요.)*

## 에이전트 장착하기: 도구 (`tools`)

도구는 LLM의 내장 지식이나 추론 능력을 넘어서는 기능을 `LlmAgent`에 제공합니다. 이를 통해 에이전트는 외부 세계와 상호 작용하고, 계산을 수행하며, 실시간 데이터를 가져오거나, 특정 작업을 실행할 수 있습니다.

*   **`tools` (선택 사항):** 에이전트가 사용할 수 있는 도구 목록을 제공하세요. 목록의 각 항목은 다음 중 하나일 수 있습니다:
    *   네이티브 함수 또는 메서드 (`FunctionTool`로 래핑됨). Python ADK는 네이티브 함수를 자동으로 `FunctionTool`로 래핑하는 반면, Java 메서드는 `FunctionTool.create(...)`를 사용하여 명시적으로 래핑해야 합니다.
    *   `BaseTool`을 상속하는 클래스의 인스턴스.
    *   다른 에이전트의 인스턴스 (`AgentTool`, 에이전트 간 위임 가능 - [멀티 에이전트](multi-agents.md) 참조).

LLM은 함수/도구 이름, 설명(독스트링 또는 `description` 필드에서), 매개변수 스키마를 사용하여 대화와 지침에 따라 어떤 도구를 호출할지 결정합니다.

=== "Python"

    ```python
    # 도구 함수 정의
    def get_capital_city(country: str) -> str:
      """주어진 국가의 수도를 검색합니다."""
      # 실제 로직으로 교체 (예: API 호출, 데이터베이스 조회)
      capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
      return capitals.get(country.lower(), f"죄송합니다, {country}의 수도를 모릅니다.")
    
    # 에이전트에 도구 추가
    capital_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="capital_agent",
        description="주어진 국가의 수도에 대한 사용자 질문에 답변합니다.",
        instruction="""당신은 국가의 수도를 제공하는 에이전트입니다... (이전 지침 텍스트)""",
        tools=[get_capital_city] # 함수를 직접 제공
    )
    ```

=== "Java"

    ```java
    
    // 도구 함수 정의
    // 주어진 국가의 수도를 검색합니다.
    public static Map<String, Object> getCapitalCity(
            @Schema(name = "country", description = "수도를 가져올 국가")
            String country) {
      // 실제 로직으로 교체 (예: API 호출, 데이터베이스 조회)
      Map<String, String> countryCapitals = new HashMap<>();
      countryCapitals.put("canada", "Ottawa");
      countryCapitals.put("france", "Paris");
      countryCapitals.put("japan", "Tokyo");
    
      String result =
              countryCapitals.getOrDefault(
                      country.toLowerCase(), "죄송합니다, " + country + "의 수도를 찾을 수 없습니다.");
      return Map.of("result", result); // 도구는 맵을 반환해야 합니다
    }
    
    // 에이전트에 도구 추가
    FunctionTool capitalTool = FunctionTool.create(experiment.getClass(), "getCapitalCity");
    LlmAgent capitalAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("capital_agent")
            .description("주어진 국가의 수도에 대한 사용자 질문에 답변합니다.")
            .instruction("당신은 국가의 수도를 제공하는 에이전트입니다... (이전 지침 텍스트)")
            .tools(capitalTool) // 함수를 FunctionTool로 래핑하여 제공
            .build();
    ```

도구에 대한 자세한 내용은 [도구](../tools/index.md) 섹션을 참조하세요.

## 고급 구성 및 제어

핵심 매개변수 외에도 `LlmAgent`는 더 세밀한 제어를 위한 여러 옵션을 제공합니다:

### LLM 생성 미세 조정 (`generate_content_config`)

`generate_content_config`를 사용하여 기본 LLM이 응답을 생성하는 방식을 조정할 수 있습니다.

*   **`generate_content_config` (선택 사항):** `google.genai.types.GenerateContentConfig`의 인스턴스를 전달하여 `temperature`(무작위성), `max_output_tokens`(응답 길이), `top_p`, `top_k`, 안전 설정과 같은 매개변수를 제어합니다.

=== "Python"

    ```python
    from google.genai import types

    agent = LlmAgent(
        # ... 기타 매개변수
        generate_content_config=types.GenerateContentConfig(
            temperature=0.2, # 더 결정론적인 출력
            max_output_tokens=250
        )
    )
    ```

=== "Java"

    ```java
    import com.google.genai.types.GenerateContentConfig;

    LlmAgent agent =
        LlmAgent.builder()
            // ... 기타 매개변수
            .generateContentConfig(GenerateContentConfig.builder()
                .temperature(0.2F) // 더 결정론적인 출력
                .maxOutputTokens(250)
                .build())
            .build();
    ```

### 데이터 구조화 (`input_schema`, `output_schema`, `output_key`)

`LLM 에이전트`와 구조화된 데이터 교환이 필요한 시나리오를 위해 ADK는 스키마 정의를 사용하여 예상 입력 및 원하는 출력 형식을 정의하는 메커니즘을 제공합니다.

*   **`input_schema` (선택 사항):** 예상 입력 구조를 나타내는 스키마를 정의합니다. 설정하면 이 에이전트에 전달되는 사용자 메시지 콘텐츠는 *반드시* 이 스키마를 준수하는 JSON 문자열이어야 합니다. 지침은 그에 따라 사용자 또는 이전 에이전트를 안내해야 합니다.

*   **`output_schema` (선택 사항):** 원하는 출력 구조를 나타내는 스키마를 정의합니다. 설정하면 에이전트의 최종 응답은 *반드시* 이 스키마를 준수하는 JSON 문자열이어야 합니다.
    *   **제약:** `output_schema`를 사용하면 LLM 내에서 제어된 생성이 가능하지만 **에이전트가 도구를 사용하거나 다른 에이전트로 제어권을 이전하는 기능은 비활성화됩니다**. 지침은 LLM이 스키마와 일치하는 JSON을 직접 생성하도록 안내해야 합니다.

*   **`output_key` (선택 사항):** 문자열 키를 제공합니다. 설정하면 에이전트의 *최종* 응답 텍스트 콘텐츠가 이 키 아래의 세션 상태 딕셔너리에 자동으로 저장됩니다. 이는 에이전트 간 또는 워크플로 단계 간에 결과를 전달하는 데 유용합니다.
    *   Python에서는 `session.state[output_key] = agent_response_text`와 같이 보일 수 있습니다.
    *   Java에서는 `session.state().put(outputKey, agentResponseText)`입니다.

=== "Python"

    입력 및 출력 스키마는 일반적으로 `Pydantic` BaseModel입니다.

    ```python
    from pydantic import BaseModel, Field
    
    class CapitalOutput(BaseModel):
        capital: str = Field(description="국가의 수도입니다.")
    
    structured_capital_agent = LlmAgent(
        # ... 이름, 모델, 설명
        instruction="""당신은 수도 정보 에이전트입니다. 국가가 주어지면 수도를 포함하는 JSON 객체로만 응답하세요. 형식: {"capital": "capital_name"}""",
        output_schema=CapitalOutput, # JSON 출력 강제
        output_key="found_capital"  # 결과를 state['found_capital']에 저장
        # 여기서 tools=[get_capital_city]를 효과적으로 사용할 수 없음
    )
    ```

=== "Java"

     입력 및 출력 스키마는 `google.genai.types.Schema` 객체입니다.

    ```java
    private static final Schema CAPITAL_OUTPUT =
        Schema.builder()
            .type("OBJECT")
            .description("수도 정보에 대한 스키마입니다.")
            .properties(
                Map.of(
                    "capital",
                    Schema.builder()
                        .type("STRING")
                        .description("국가의 수도입니다.")
                        .build()))
            .build();
    
    LlmAgent structuredCapitalAgent =
        LlmAgent.builder()
            // ... 이름, 모델, 설명
            .instruction(
                    "당신은 수도 정보 에이전트입니다. 국가가 주어지면 수도를 포함하는 JSON 객체로만 응답하세요. 형식: {\"capital\": \"capital_name\"}")
            .outputSchema(capitalOutput) // JSON 출력 강제
            .outputKey("found_capital") // 결과를 state.get("found_capital")에 저장
            // 여기서 tools(getCapitalCity)를 효과적으로 사용할 수 없음
            .build();
    ```

### 컨텍스트 관리 (`include_contents`)

에이전트가 이전 대화 기록을 받는지 여부를 제어합니다.

*   **`include_contents` (선택 사항, 기본값: `'default'`):** `contents`(기록)가 LLM으로 전송되는지 여부를 결정합니다.
    *   `'default'`: 에이전트가 관련 대화 기록을 받습니다.
    *   `'none'`: 에이전트가 이전 `contents`를 받지 않습니다. 현재 지침과 *현재* 턴에 제공된 입력만으로 작동합니다(상태 비저장 작업 또는 특정 컨텍스트 강제에 유용).

=== "Python"

    ```python
    stateless_agent = LlmAgent(
        # ... 기타 매개변수
        include_contents='none'
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent.IncludeContents;
    
    LlmAgent statelessAgent =
        LlmAgent.builder()
            // ... 기타 매개변수
            .includeContents(IncludeContents.NONE)
            .build();
    ```

### 계획 및 코드 실행

![python_only](https://img.shields.io/badge/현재_지원되는_언어-Python-blue){ title="이 기능은 현재 Python에서만 사용할 수 있습니다. Java 지원은 계획 중이거나 곧 제공될 예정입니다."}

여러 단계를 포함하거나 코드를 실행하는 더 복잡한 추론의 경우:

*   **`planner` (선택 사항):** `BasePlanner` 인스턴스를 할당하여 실행 전에 다단계 추론 및 계획을 활성화합니다. ([멀티 에이전트](multi-agents.md) 패턴 참조).
*   **`code_executor` (선택 사항):** `BaseCodeExecutor` 인스턴스를 제공하여 에이전트가 LLM의 응답에서 찾은 코드 블록(예: Python)을 실행할 수 있도록 합니다. ([도구/내장 도구](../tools/built-in-tools.md) 참조).

## 종합 예제

??? "코드"
    다음은 완전한 기본 `capital_agent`입니다:

    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/agents/llm-agent/capital_agent.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/LlmAgentExample.java:full_code"
        ```

_(이 예제는 핵심 개념을 보여줍니다. 더 복잡한 에이전트는 스키마, 컨텍스트 제어, 계획 등을 포함할 수 있습니다.)_

## 관련 개념 (나중에 다룰 주제)

이 페이지에서는 `LlmAgent`의 핵심 구성을 다루지만, 몇 가지 관련 개념은 더 고급 제어를 제공하며 다른 곳에서 자세히 설명합니다:

*   **콜백:** `before_model_callback`, `after_model_callback` 등을 사용하여 실행 지점(모델 호출 전/후, 도구 호출 전/후)을 가로챕니다. [콜백](../callbacks/types-of-callbacks.md)을 참조하세요.
*   **멀티 에이전트 제어:** 계획(`planner`), 에이전트 이전 제어(`disallow_transfer_to_parent`, `disallow_transfer_to_peers`), 시스템 전체 지침(`global_instruction`)을 포함한 에이전트 상호 작용에 대한 고급 전략. [멀티 에이전트](multi-agents.md)를 참조하세요.