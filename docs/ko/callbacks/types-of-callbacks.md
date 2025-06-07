# 콜백의 종류

프레임워크는 에이전트 실행의 다양한 단계에서 트리거되는 다양한 유형의 콜백을 제공합니다. 각 콜백이 언제 실행되고 어떤 컨텍스트를 받는지 이해하는 것이 효과적으로 사용하는 핵심입니다.

## 에이전트 생명주기 콜백

이러한 콜백은 `BaseAgent`를 상속하는 *모든* 에이전트에서 사용할 수 있습니다 (`LlmAgent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent` 등 포함).

!!! Note
    특정 메서드 이름이나 반환 유형은 SDK 언어에 따라 약간 다를 수 있습니다 (예: Python에서는 `None` 반환, Java에서는 `Optional.empty()` 또는 `Maybe.empty()` 반환). 자세한 내용은 언어별 API 문서를 참조하세요.

### 에이전트 이전 콜백 (Before Agent Callback)

**시기:** 에이전트의 `_run_async_impl`(또는 `_run_live_impl`) 메서드가 실행되기 *직전에* 호출됩니다. 에이전트의 `InvocationContext`가 생성된 후, 핵심 로직이 시작되기 *전에* 실행됩니다.

**목적:** 이 특정 에이전트 실행에만 필요한 리소스나 상태를 설정하거나, 실행이 시작되기 전에 세션 상태(`callback_context.state`)에 대한 유효성 검사를 수행하거나, 에이전트 활동의 진입점을 로깅하거나, 핵심 로직이 사용하기 전에 호출 컨텍스트를 수정하는 데 이상적입니다.

??? "코드"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_agent_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeAgentCallbackExample.java:init"
        ```

**`before_agent_callback` 예제에 대한 참고:**

*   **보여주는 것:** 이 예제는 `before_agent_callback`을 보여줍니다. 이 콜백은 주어진 요청에 대해 에이전트의 주요 처리 로직이 시작되기 *직전에* 실행됩니다.
*   **작동 방식:** 콜백 함수(`check_if_agent_should_run`)는 세션 상태의 플래그(`skip_llm_agent`)를 확인합니다.
    *   플래그가 `True`이면 콜백은 `types.Content` 객체를 반환합니다. 이는 ADK 프레임워크에 에이전트의 주요 실행을 **완전히 건너뛰고** 콜백이 반환한 콘텐츠를 최종 응답으로 사용하도록 지시합니다.
    *   플래그가 `False`(또는 설정되지 않음)이면 콜백은 `None` 또는 빈 객체를 반환합니다. 이는 ADK 프레임워크에 에이전트의 **정상적인 실행을 계속**하도록 지시합니다 (이 경우 LLM 호출).
*   **예상 결과:** 두 가지 시나리오를 볼 수 있습니다:
    1.  `skip_llm_agent: True` 상태를 가진 세션에서는 에이전트의 LLM 호출이 무시되고 출력이 콜백에서 직접 나옵니다 ("에이전트... 건너뜀...").
    2.  해당 상태 플래그가 없는 세션에서는 콜백이 에이전트 실행을 허용하고 LLM의 실제 응답을 볼 수 있습니다 (예: "안녕하세요!").
*   **콜백 이해하기:** 이는 `before_` 콜백이 **게이트키퍼** 역할을 하여, 주요 단계 *전에* 실행을 가로채고 상태, 입력 유효성 검사, 권한과 같은 확인에 따라 잠재적으로 이를 방지할 수 있는 방법을 보여줍니다.

### 에이전트 이후 콜백 (After Agent Callback)

**시기:** 에이전트의 `_run_async_impl`(또는 `_run_live_impl`) 메서드가 성공적으로 완료된 *직후에* 호출됩니다. `before_agent_callback`이 콘텐츠를 반환하여 에이전트가 건너뛰어지거나 에이전트 실행 중에 `end_invocation`이 설정된 경우에는 실행되지 않습니다.

**목적:** 정리 작업, 실행 후 유효성 검사, 에이전트 활동 완료 로깅, 최종 상태 수정 또는 에이전트의 최종 출력 보강/대체에 유용합니다.

??? "코드"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/after_agent_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AfterAgentCallbackExample.java:init"
        ```

**`after_agent_callback` 예제에 대한 참고:**

*   **보여주는 것:** 이 예제는 `after_agent_callback`을 보여줍니다. 이 콜백은 에이전트의 주요 처리 로직이 완료되고 결과를 생성한 *직후*, 하지만 그 결과가 확정되어 반환되기 *전에* 실행됩니다.
*   **작동 방식:** 콜백 함수(`modify_output_after_agent`)는 세션 상태의 플래그(`add_concluding_note`)를 확인합니다.
    *   플래그가 `True`이면 콜백은 *새로운* `types.Content` 객체를 반환합니다. 이는 ADK 프레임워크에 에이전트의 원래 출력을 콜백이 반환한 콘텐츠로 **대체**하도록 지시합니다.
    *   플래그가 `False`(또는 설정되지 않음)이면 콜백은 `None` 또는 빈 객체를 반환합니다. 이는 ADK 프레임워크에 에이전트가 생성한 **원래 출력을 사용**하도록 지시합니다.
*   **예상 결과:** 두 가지 시나리오를 볼 수 있습니다:
    1.  `add_concluding_note: True` 상태가 없는 세션에서는 콜백이 에이전트의 원래 출력("처리 완료!")을 사용하도록 허용합니다.
    2.  해당 상태 플래그가 있는 세션에서는 콜백이 에이전트의 원래 출력을 가로채고 자체 메시지("마무리 메모 추가됨...")로 대체합니다.
*   **콜백 이해하기:** 이는 `after_` 콜백이 **후처리** 또는 **수정**을 허용하는 방법을 보여줍니다. 단계(에이전트 실행)의 결과를 검사하고 로직에 따라 통과시키거나, 변경하거나, 완전히 대체할지 결정할 수 있습니다.

## LLM 상호작용 콜백

이러한 콜백은 `LlmAgent`에 특화되어 있으며 거대 언어 모델과의 상호작용 주변에 연결 고리를 제공합니다.

### 모델 이전 콜백 (Before Model Callback)

**시기:** `LlmAgent`의 흐름 내에서 `generate_content_async`(또는 동등한) 요청이 LLM으로 전송되기 직전에 호출됩니다.

**목적:** LLM으로 가는 요청을 검사하고 수정할 수 있습니다. 사용 사례에는 동적 지침 추가, 상태에 기반한 소수 샷 예제 주입, 모델 구성 수정, 가드레일 구현(욕설 필터 등) 또는 요청 수준 캐싱 구현이 포함됩니다.

**반환 값 효과:**
콜백이 `None`(또는 Java에서 `Maybe.empty()` 객체)을 반환하면 LLM은 정상적인 워크플로우를 계속합니다. 콜백이 `LlmResponse` 객체를 반환하면 LLM에 대한 호출이 **건너뛰어집니다**. 반환된 `LlmResponse`는 모델에서 직접 온 것처럼 사용됩니다. 이는 가드레일이나 캐싱을 구현하는 데 강력합니다.

??? "코드"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_model_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeModelCallbackExample.java:init"
        ```

### 모델 이후 콜백 (After Model Callback)

**시기:** LLM에서 응답(`LlmResponse`)을 받은 직후, 호출 에이전트가 추가로 처리하기 전에 호출됩니다.

**목적:** 원시 LLM 응답을 검사하거나 수정할 수 있습니다. 사용 사례에는 다음이 포함됩니다:

*   모델 출력 로깅,
*   응답 서식 재지정,
*   모델이 생성한 민감한 정보 검열,
*   LLM 응답에서 구조화된 데이터를 구문 분석하여 `callback_context.state`에 저장
*   또는 특정 오류 코드 처리.

??? "코드"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/after_model_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AfterModelCallbackExample.java:init"
        ```

## 도구 실행 콜백

이러한 콜백 또한 `LlmAgent`에 특화되어 있으며 LLM이 요청할 수 있는 도구(`FunctionTool`, `AgentTool` 등 포함) 실행 주변에서 트리거됩니다.

### 도구 이전 콜백 (Before Tool Callback)

**시기:** LLM이 함수 호출을 생성한 후, 특정 도구의 `run_async` 메서드가 호출되기 직전에 호출됩니다.

**목적:** 도구 인수 검사 및 수정, 실행 전 권한 부여 확인, 도구 사용 시도 로깅 또는 도구 수준 캐싱 구현을 허용합니다.

**반환 값 효과:**

1.  콜백이 `None`(또는 Java에서 `Maybe.empty()` 객체)을 반환하면 도구의 `run_async` 메서드가 (잠재적으로 수정된) `args`로 실행됩니다.
2.  사전(또는 Java의 `Map`)이 반환되면 도구의 `run_async` 메서드가 **건너뛰어집니다**. 반환된 사전은 도구 호출의 결과로 직접 사용됩니다. 이는 캐싱이나 도구 동작을 재정의하는 데 유용합니다.


??? "코드"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_tool_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeToolCallbackExample.java:init"
        ```

### 도구 이후 콜백 (After Tool Callback)

**시기:** 도구의 `run_async` 메서드가 성공적으로 완료된 직후에 호출됩니다.

**목적:** (잠재적으로 요약 후) LLM으로 다시 전송되기 전에 도구의 결과를 검사하고 수정할 수 있습니다. 도구 결과 로깅, 결과 후처리 또는 서식 지정, 또는 결과의 특정 부분을 세션 상태에 저장하는 데 유용합니다.

**반환 값 효과:**

1.  콜백이 `None`(또는 Java에서 `Maybe.empty()` 객체)을 반환하면 원래 `tool_response`가 사용됩니다.
2.  새 사전이 반환되면 원래 `tool_response`를 **대체**합니다. 이를 통해 LLM이 보는 결과를 수정하거나 필터링할 수 있습니다.

??? "코드"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/after_tool_callback.py"
        ```
    
    === "Java"
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AfterToolCallbackExample.java:init"
        ```