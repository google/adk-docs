!!! warning  고급 개념

    `_run_async_impl`(또는 다른 언어의 동등한 메서드)을 직접 구현하여 사용자 정의 에이전트를 구축하는 것은 강력한 제어 기능을 제공하지만, 미리 정의된 `LlmAgent` 또는 표준 `WorkflowAgent` 유형을 사용하는 것보다 더 복잡합니다. 사용자 정의 오케스트레이션 로직을 다루기 전에 이러한 기본 에이전트 유형을 먼저 이해하는 것이 좋습니다.

# 사용자 정의 에이전트

사용자 정의 에이전트는 `BaseAgent`에서 직접 상속받아 자체 제어 흐름을 구현함으로써 **임의의 오케스트레이션 로직**을 정의할 수 있는 ADK의 궁극적인 유연성을 제공합니다. 이는 `SequentialAgent`, `LoopAgent`, `ParallelAgent`의 미리 정의된 패턴을 넘어, 매우 구체적이고 복잡한 에이전트 워크플로를 구축할 수 있게 해줍니다.

## 소개: 미리 정의된 워크플로를 넘어서

### 사용자 정의 에이전트란 무엇인가요?

사용자 정의 에이전트는 본질적으로 `google.adk.agents.BaseAgent`를 상속받아 `_run_async_impl` 비동기 메서드 내에서 핵심 실행 로직을 구현하는 클래스입니다. 이 메서드가 다른 에이전트(하위 에이전트)를 호출하고, 상태를 관리하며, 이벤트를 처리하는 방법을 완전히 제어할 수 있습니다.

!!! Note
    에이전트의 핵심 비동기 로직을 구현하기 위한 특정 메서드 이름은 SDK 언어에 따라 약간 다를 수 있습니다 (예: Java의 `runAsyncImpl`, Python의 `_run_async_impl`). 자세한 내용은 언어별 API 문서를 참조하세요.

### 왜 사용해야 하나요?

표준 [워크플로 에이전트](workflow-agents/index.md)(`SequentialAgent`, `LoopAgent`, `ParallelAgent`)가 일반적인 오케스트레이션 패턴을 다루지만, 요구 사항에 다음이 포함된 경우 사용자 정의 에이전트가 필요합니다:

*   **조건부 로직:** 런타임 조건이나 이전 단계의 결과에 따라 다른 하위 에이전트를 실행하거나 다른 경로를 택합니다.
*   **복잡한 상태 관리:** 단순한 순차적 전달을 넘어 워크플로 전반에 걸쳐 상태를 유지하고 업데이트하기 위한 복잡한 로직을 구현합니다.
*   **외부 통합:** 오케스트레이션 흐름 제어 내에서 직접 외부 API, 데이터베이스 또는 사용자 정의 라이브러리 호출을 통합합니다.
*   **동적 에이전트 선택:** 상황이나 입력에 대한 동적 평가를 기반으로 다음에 실행할 하위 에이전트를 선택합니다.
*   **고유한 워크플로 패턴:** 표준 순차, 병렬 또는 루프 구조에 맞지 않는 오케스트레이션 로직을 구현합니다.


![인트로 구성 요소](../assets/custom-agent-flow.png)


## 사용자 정의 로직 구현:

모든 사용자 정의 에이전트의 핵심은 고유한 비동기 동작을 정의하는 메서드입니다. 이 메서드를 사용하면 하위 에이전트를 조율하고 실행 흐름을 관리할 수 있습니다.

=== "Python"

      모든 사용자 정의 에이전트의 핵심은 `_run_async_impl` 메서드입니다. 여기서 고유한 동작을 정의합니다.
      
      * **시그니처:** `async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:`
      * **비동기 생성기:** `async def` 함수여야 하며 `AsyncGenerator`를 반환해야 합니다. 이를 통해 하위 에이전트나 자체 로직에서 생성된 이벤트를 러너에게 `yield`할 수 있습니다.
      * **`ctx` (InvocationContext):** 중요한 런타임 정보, 특히 사용자 정의 에이전트가 조정하는 단계 간에 데이터를 공유하는 기본 방법인 `ctx.session.state`에 대한 접근을 제공합니다.

=== "Java"

    모든 사용자 정의 에이전트의 핵심은 `BaseAgent`에서 재정의하는 `runAsyncImpl` 메서드입니다.

    *   **시그니처:** `protected Flowable<Event> runAsyncImpl(InvocationContext ctx)`
    *   **반응형 스트림 (`Flowable`):** `io.reactivex.rxjava3.core.Flowable<Event>`를 반환해야 합니다. 이 `Flowable`은 사용자 정의 에이전트의 로직에 의해 생성될 이벤트 스트림을 나타내며, 종종 하위 에이전트의 여러 `Flowable`을 결합하거나 변환하여 생성됩니다.
    *   **`ctx` (InvocationContext):** 중요한 런타임 정보, 특히 `java.util.concurrent.ConcurrentMap<String, Object>`인 `ctx.session().state()`에 대한 접근을 제공합니다. 이것이 사용자 정의 에이전트가 조정하는 단계 간에 데이터를 공유하는 기본 방법입니다.

**핵심 비동기 메서드 내의 주요 기능:**

=== "Python"

    1. **하위 에이전트 호출:** `run_async` 메서드를 사용하여 하위 에이전트(일반적으로 `self.my_llm_agent`와 같은 인스턴스 속성으로 저장됨)를 호출하고 해당 이벤트를 생성합니다:

          ```python
          async for event in self.some_sub_agent.run_async(ctx):
              # 선택적으로 이벤트를 검사하거나 로깅
              yield event # 이벤트를 위로 전달
          ```

    2. **상태 관리:** 세션 상태 사전(`ctx.session.state`)에서 읽고 써서 하위 에이전트 호출 간에 데이터를 전달하거나 결정을 내립니다:
          ```python
          # 이전 에이전트가 설정한 데이터 읽기
          previous_result = ctx.session.state.get("some_key")
      
          # 상태에 따라 결정 내리기
          if previous_result == "some_value":
              # ... 특정 하위 에이전트 호출 ...
          else:
              # ... 다른 하위 에이전트 호출 ...
      
          # 나중 단계를 위해 결과 저장 (종종 하위 에이전트의 output_key를 통해 수행됨)
          # ctx.session.state["my_custom_result"] = "calculated_value"
          ```

    3. **제어 흐름 구현:** 표준 Python 구문(`if`/`elif`/`else`, `for`/`while` 루프, `try`/`except`)을 사용하여 하위 에이전트를 포함하는 정교하고 조건부 또는 반복적인 워크플로를 만듭니다.

=== "Java"

    1. **하위 에이전트 호출:** 비동기 실행 메서드를 사용하여 하위 에이전트(일반적으로 인스턴스 속성 또는 객체로 저장됨)를 호출하고 해당 이벤트 스트림을 반환합니다:

           일반적으로 `concatWith`, `flatMapPublisher` 또는 `concatArray`와 같은 RxJava 연산자를 사용하여 하위 에이전트의 `Flowable`을 연결합니다.

           ```java
           // 예제: 하나의 하위 에이전트 실행
           // return someSubAgent.runAsync(ctx);
      
           // 예제: 하위 에이전트를 순차적으로 실행
           Flowable<Event> firstAgentEvents = someSubAgent1.runAsync(ctx)
               .doOnNext(event -> System.out.println("에이전트 1의 이벤트: " + event.id()));
      
           Flowable<Event> secondAgentEvents = Flowable.defer(() ->
               someSubAgent2.runAsync(ctx)
                   .doOnNext(event -> System.out.println("에이전트 2의 이벤트: " + event.id()))
           );
      
           return firstAgentEvents.concatWith(secondAgentEvents);
           ```
           `Flowable.defer()`는 실행이 이전 단계의 완료 또는 상태에 따라 달라지는 후속 단계에 종종 사용됩니다.

    2. **상태 관리:** 세션 상태에서 읽고 써서 하위 에이전트 호출 간에 데이터를 전달하거나 결정을 내립니다. 세션 상태는 `ctx.session().state()`를 통해 얻는 `java.util.concurrent.ConcurrentMap<String, Object>`입니다.
        
        ```java
        // 이전 에이전트가 설정한 데이터 읽기
        Object previousResult = ctx.session().state().get("some_key");

        // 상태에 따라 결정 내리기
        if ("some_value".equals(previousResult)) {
            // ... 특정 하위 에이전트의 Flowable을 포함하는 로직 ...
        } else {
            // ... 다른 하위 에이전트의 Flowable을 포함하는 로직 ...
        }

        // 나중 단계를 위해 결과 저장 (종종 하위 에이전트의 output_key를 통해 수행됨)
        // ctx.session().state().put("my_custom_result", "calculated_value");
        ```

    3. **제어 흐름 구현:** 표준 언어 구문(`if`/`else`, 루프, `try`/`catch`)을 반응형 연산자(RxJava)와 결합하여 정교한 워크플로를 만듭니다.

          *   **조건부:** 조건에 따라 구독할 `Flowable`을 선택하기 위한 `Flowable.defer()` 또는 스트림 내에서 이벤트를 필터링하는 경우 `filter()`.
          *   **반복:** `repeat()`, `retry()`와 같은 연산자 또는 조건에 따라 자체의 일부를 재귀적으로 호출하는 반응형 체인을 구조화하여(종종 `flatMapPublisher` 또는 `concatMap`으로 관리됨).

## 하위 에이전트 및 상태 관리

일반적으로 사용자 정의 에이전트는 다른 에이전트(예: `LlmAgent`, `LoopAgent` 등)를 조율합니다.

*   **초기화:** 일반적으로 이러한 하위 에이전트의 인스턴스를 사용자 정의 에이전트의 생성자에 전달하고 인스턴스 필드/속성(예: `this.story_generator = story_generator_instance` 또는 `self.story_generator = story_generator_instance`)으로 저장합니다. 이렇게 하면 사용자 정의 에이전트의 핵심 비동기 실행 로직(예: `_run_async_impl` 메서드) 내에서 접근할 수 있습니다.
*   **하위 에이전트 목록:** `super()` 생성자를 사용하여 `BaseAgent`를 초기화할 때 `sub agents` 목록을 전달해야 합니다. 이 목록은 이 사용자 정의 에이전트의 즉각적인 계층 구조의 일부인 에이전트에 대해 ADK 프레임워크에 알립니다. 핵심 실행 로직(`_run_async_impl`)이 `self.xxx_agent`를 통해 에이전트를 직접 호출하더라도 수명 주기 관리, 내부 검사 및 잠재적인 향후 라우팅 기능과 같은 프레임워크 기능에 중요합니다. 사용자 정의 로직이 최상위 수준에서 직접 호출하는 에이전트를 포함하세요.
*   **상태:** 언급했듯이, `ctx.session.state`는 하위 에이전트(특히 `output key`를 사용하는 `LlmAgent`s)가 오케스트레이터에게 결과를 전달하고 오케스트레이터가 필요한 입력을 아래로 전달하는 표준 방법입니다.

## 디자인 패턴 예제: `StoryFlowAgent`

사용자 정의 에이전트의 힘을 조건부 로직을 사용한 다단계 콘텐츠 생성 워크플로 예제 패턴으로 설명해 보겠습니다.

**목표:** 이야기를 생성하고, 비평과 수정을 통해 반복적으로 개선하며, 최종 확인을 수행하고, 결정적으로 *최종 톤 확인에 실패하면 이야기를 다시 생성*하는 시스템을 만듭니다.

**왜 사용자 정의인가?** 여기서 사용자 정의 에이전트가 필요한 핵심 요구 사항은 **톤 확인 결과에 따른 조건부 재생성**입니다. 표준 워크플로 에이전트에는 하위 에이전트 작업의 결과에 따른 내장된 조건부 분기 기능이 없습니다. 오케스트레이터 내에 사용자 정의 로직(`if tone == "negative": ...`)이 필요합니다.

---

### 1부: 간소화된 사용자 정의 에이전트 초기화

=== "Python"

    `BaseAgent`를 상속하는 `StoryFlowAgent`를 정의합니다. `__init__`에서 필요한 하위 에이전트(전달됨)를 인스턴스 속성으로 저장하고 이 사용자 정의 에이전트가 직접 조율할 최상위 에이전트에 대해 `BaseAgent` 프레임워크에 알립니다.
    
    ```python
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:init"
    ```

=== "Java"

    `BaseAgent`를 확장하여 `StoryFlowAgentExample`을 정의합니다. **생성자**에서 필요한 하위 에이전트 인스턴스(매개변수로 전달됨)를 인스턴스 필드로 저장합니다. 이 사용자 정의 에이전트가 직접 조율할 이러한 최상위 하위 에이전트는 목록으로 `BaseAgent`의 `super` 생성자에도 전달됩니다.

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:init"
    ```
---

### 2부: 사용자 정의 실행 로직 정의

=== "Python"

    이 메서드는 표준 Python async/await 및 제어 흐름을 사용하여 하위 에이전트를 조율합니다.
    
    ```python
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:executionlogic"
    ```
    **로직 설명:**

    1. 초기 `story_generator`가 실행됩니다. 출력은 `ctx.session.state["current_story"]`에 있을 것으로 예상됩니다.
    2. `loop_agent`가 실행되어 내부적으로 `critic`과 `reviser`를 `max_iterations` 횟수만큼 순차적으로 호출합니다. 이들은 상태에서 `current_story`와 `criticism`을 읽고 씁니다.
    3. `sequential_agent`가 실행되어 `grammar_check`를 호출한 다음 `tone_check`를 호출하여 `current_story`를 읽고 `grammar_suggestions`와 `tone_check_result`를 상태에 씁니다.
    4. **사용자 정의 부분:** `if` 문은 상태에서 `tone_check_result`를 확인합니다. "negative"이면 `story_generator`가 *다시* 호출되어 상태의 `current_story`를 덮어씁니다. 그렇지 않으면 흐름이 종료됩니다.


=== "Java"
    
    `runAsyncImpl` 메서드는 비동기 제어 흐름을 위해 RxJava의 Flowable 스트림과 연산자를 사용하여 하위 에이전트를 조율합니다.

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:executionlogic"
    ```
    **로직 설명:**

    1. 초기 `storyGenerator.runAsync(invocationContext)` Flowable이 실행됩니다. 출력은 `invocationContext.session().state().get("current_story")`에 있을 것으로 예상됩니다.
    2. `loopAgent`의 Flowable이 다음에 실행됩니다(`Flowable.concatArray` 및 `Flowable.defer`로 인해). LoopAgent는 `critic` 및 `reviser` 하위 에이전트를 `maxIterations`까지 순차적으로 호출합니다. 이들은 상태에서 `current_story`와 `criticism`을 읽고 씁니다.
    3. 그런 다음 `sequentialAgent`의 Flowable이 실행됩니다. `grammar_check`를 호출한 다음 `tone_check`를 호출하여 `current_story`를 읽고 `grammar_suggestions`와 `tone_check_result`를 상태에 씁니다.
    4. **사용자 정의 부분:** sequentialAgent가 완료된 후 `Flowable.defer` 내의 로직이 `invocationContext.session().state()`에서 "tone_check_result"를 확인합니다. "negative"이면 `storyGenerator` Flowable이 *조건부로 연결*되어 다시 실행되어 "current_story"를 덮어씁니다. 그렇지 않으면 빈 Flowable이 사용되고 전체 워크플로가 완료로 진행됩니다.

---

### 3부: LLM 하위 에이전트 정의하기

이들은 특정 작업을 담당하는 표준 `LlmAgent` 정의입니다. `output key` 매개변수는 결과를 다른 에이전트나 사용자 정의 오케스트레이터가 접근할 수 있는 `session.state`에 배치하는 데 중요합니다.

=== "Python"

    ```python
    GEMINI_2_FLASH = "gemini-2.0-flash" # 모델 상수 정의
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:llmagents"
    ```
=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:llmagents"
    ```

---

### 4부: 사용자 정의 에이전트 인스턴스화 및 실행

마지막으로, `StoryFlowAgent`를 인스턴스화하고 평소와 같이 `Runner`를 사용합니다.

=== "Python"

    ```python
    --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py:story_flow_agent"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:story_flow_agent"
    ```

*(참고: 가져오기 및 실행 로직을 포함한 전체 실행 가능한 코드는 아래에 링크되어 있습니다.)*

---

## 전체 코드 예제

???+ "Storyflow 에이전트"

    === "Python"
    
        ```python
        # StoryFlowAgent 예제의 전체 실행 가능한 코드
        --8<-- "examples/python/snippets/agents/custom-agent/storyflow_agent.py"
        ```
    
    === "Java"
    
        ```java
        # StoryFlowAgent 예제의 전체 실행 가능한 코드
        --8<-- "examples/java/snippets/src/main/java/agents/StoryFlowAgentExample.java:full_code"
        ```