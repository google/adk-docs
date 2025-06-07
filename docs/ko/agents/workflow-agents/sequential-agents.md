# 순차 에이전트

## `SequentialAgent`

`SequentialAgent`는 목록에 지정된 순서대로 하위 에이전트를 실행하는 [워크플로 에이전트](index.md)입니다.

실행이 고정되고 엄격한 순서로 이루어지기를 원할 때 `SequentialAgent`를 사용하세요.

### 예제

*   두 가지 도구, 즉 `페이지 내용 가져오기`와 `페이지 요약하기`를 사용하여 모든 웹페이지를 요약할 수 있는 에이전트를 만들고 싶다고 가정해 봅시다. 에이전트는 항상 `페이지 요약하기`를 호출하기 전에 `페이지 내용 가져오기`를 호출해야 하므로(아무것도 없는 것을 요약할 수는 없으므로!), `SequentialAgent`를 사용하여 에이전트를 구축해야 합니다.

다른 [워크플로 에이전트](index.md)와 마찬가지로 `SequentialAgent`는 LLM으로 구동되지 않으므로 실행 방식이 결정적입니다. 즉, 워크플로 에이전트는 실행(즉, 순차적으로)에만 관련이 있고 내부 로직에는 관련이 없습니다. 워크플로 에이전트의 도구나 하위 에이전트는 LLM을 활용할 수도 있고 그렇지 않을 수도 있습니다.

### 작동 방식

`SequentialAgent`의 `Run Async` 메서드가 호출되면 다음 작업을 수행합니다:

1.  **반복:** 제공된 순서대로 하위 에이전트 목록을 반복합니다.
2.  **하위 에이전트 실행:** 목록의 각 하위 에이전트에 대해 하위 에이전트의 `Run Async` 메서드를 호출합니다.

![순차 에이전트](../../assets/sequential-agent.png){: width="600"}

### 전체 예제: 코드 개발 파이프라인

간소화된 코드 개발 파이프라인을 생각해 보세요:

*   **코드 작성자 에이전트:** 사양에 따라 초기 코드를 생성하는 LLM 에이전트입니다.
*   **코드 검토자 에이전트:** 생성된 코드의 오류, 스타일 문제 및 모범 사례 준수 여부를 검토하는 LLM 에이전트입니다. 코드 작성자 에이전트의 출력을 받습니다.
*   **코드 리팩터러 에이전트:** 검토된 코드(및 검토자의 의견)를 가져와 품질을 개선하고 문제를 해결하기 위해 리팩터링하는 LLM 에이전트입니다.

`SequentialAgent`는 이에 완벽합니다:

```py
SequentialAgent(sub_agents=[CodeWriterAgent, CodeReviewerAgent, CodeRefactorerAgent])
```

이렇게 하면 코드가 작성된 *후* 검토되고 *마지막으로* 리팩터링되는 것이 엄격하고 신뢰할 수 있는 순서로 보장됩니다. **각 하위 에이전트의 출력은 [출력 키](../llm-agents.md#structuring-data-input_schema-output_schema-output_key)를 통해 상태에 저장되어 다음 에이전트로 전달됩니다.**

???+ "코드"

    === "Python"
        ```py
        --8<-- "examples/python/snippets/agents/workflow-agents/sequential_agent_code_development_agent.py:init"
        ```

    === "Java"
        ```java
        --8<-- "examples/java/snippets/src/main/java/agents/workflow/SequentialAgentExample.java:init"
        ```