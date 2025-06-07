# 함수 도구

## 함수 도구란 무엇인가요?

기본 제공 도구가 특정 요구 사항을 완전히 충족하지 못하는 경우, 개발자는 사용자 정의 함수 도구를 만들 수 있습니다. 이를 통해 독점 데이터베이스에 연결하거나 고유한 알고리즘을 구현하는 등 **맞춤형 기능**을 구현할 수 있습니다.

*예를 들어,* 함수 도구 "myfinancetool"은 특정 재무 지표를 계산하는 함수일 수 있습니다. ADK는 장기 실행 함수도 지원하므로, 해당 계산에 시간이 걸리는 경우 에이전트는 다른 작업을 계속할 수 있습니다.

ADK는 복잡성과 제어 수준에 따라 각각 다른 함수 도구를 만드는 여러 가지 방법을 제공합니다:

1. 함수 도구
2. 장기 실행 함수 도구
3. 도구로서의 에이전트

## 1. 함수 도구

함수를 도구로 변환하는 것은 사용자 정의 로직을 에이전트에 통합하는 간단한 방법입니다. 실제로, 함수를 에이전트의 도구 목록에 할당하면 프레임워크가 자동으로 함수 도구로 래핑합니다. 이 접근 방식은 유연성과 빠른 통합을 제공합니다.

### 매개변수

표준 **JSON 직렬화 가능 유형**(예: 문자열, 정수, 리스트, 딕셔너리)을 사용하여 함수 매개변수를 정의하세요. 언어 모델(LLM)이 현재 매개변수의 기본값을 해석하는 것을 지원하지 않으므로 매개변수에 기본값을 설정하지 않는 것이 중요합니다.

### 반환 유형

함수 도구의 기본 반환 유형은 Python에서는 **딕셔너리**, Java에서는 **맵**입니다. 이를 통해 키-값 쌍으로 응답을 구조화하여 LLM에 컨텍스트와 명확성을 제공할 수 있습니다. 함수가 딕셔너리 이외의 유형을 반환하는 경우, 프레임워크는 이를 **"result"**라는 단일 키를 가진 딕셔너리로 자동으로 래핑합니다.

반환 값을 최대한 설명적으로 만드세요. *예를 들어,* 숫자 오류 코드를 반환하는 대신, 사람이 읽을 수 있는 설명이 포함된 "error\_message" 키를 가진 딕셔너리를 반환하세요. **코드가 아닌 LLM이 결과를 이해해야 한다는 것을 기억하세요.** 모범 사례로, 반환 딕셔너리에 "status" 키를 포함하여 작업의 상태에 대한 명확한 신호를 LLM에 제공하는 전체 결과(예: "success", "error", "pending")를 나타내세요.

### Docstring / 소스 코드 주석

함수의 docstring(또는 위의 주석)은 도구의 설명 역할을 하며 LLM으로 전송됩니다. 따라서 잘 작성되고 포괄적인 docstring은 LLM이 도구를 효과적으로 사용하는 방법을 이해하는 데 중요합니다. 함수의 목적, 매개변수의 의미, 예상 반환 값을 명확하게 설명하세요.

??? "예제"

    === "Python"
    
        이 도구는 주어진 주식 티커/기호의 주가를 얻는 파이썬 함수입니다.
    
        <u>참고</u>: 이 도구를 사용하기 전에 `pip install yfinance` 라이브러리를 설치해야 합니다.
    
        ```py
        --8<-- "examples/python/snippets/tools/function-tools/func_tool.py"
        ```
    
        이 도구의 반환 값은 딕셔너리로 래핑됩니다.
    
        ```json
        {"result": "$123"}
        ```
    
    === "Java"
    
        이 도구는 주가의 모의 값을 검색합니다.
    
        ```java
        --8<-- "examples/java/snippets/src/main/java/tools/StockPriceAgent.java:full_code"
        ```
    
        이 도구의 반환 값은 Map<String, Object>로 래핑됩니다.
    
        ```json
        입력 `GOOG`에 대해: {"symbol": "GOOG", "price": "1.0"}
        ```

### 모범 사례

함수를 정의하는 데 상당한 유연성이 있지만, 단순함이 LLM의 사용성을 향상시킨다는 점을 기억하세요. 다음 지침을 고려하세요:

*   **더 적은 매개변수가 더 좋습니다:** 복잡성을 줄이기 위해 매개변수 수를 최소화하세요.
*   **간단한 데이터 유형:** 가능한 경우 사용자 정의 클래스보다 `str` 및 `int`와 같은 기본 데이터 유형을 선호하세요.
*   **의미 있는 이름:** 함수의 이름과 매개변수 이름은 LLM이 도구를 해석하고 활용하는 방식에 큰 영향을 미칩니다. 함수의 목적과 입력의 의미를 명확하게 반영하는 이름을 선택하세요. `do_stuff()` 또는 `beAgent()`와 같은 일반적인 이름은 피하세요.

## 2. 장기 실행 함수 도구

에이전트의 실행을 차단하지 않고 상당한 처리 시간이 필요한 작업을 위해 설계되었습니다. 이 도구는 `FunctionTool`의 하위 클래스입니다.

`LongRunningFunctionTool`을 사용할 때, 함수는 장기 실행 작업을 시작하고 선택적으로 **초기 결과**(예: 장기 실행 작업 ID)를 반환할 수 있습니다. 장기 실행 함수 도구가 호출되면 에이전트 러너는 에이전트 실행을 일시 중지하고 에이전트 클라이언트가 계속할지 또는 장기 실행 작업이 끝날 때까지 기다릴지 결정하도록 합니다. 에이전트 클라이언트는 장기 실행 작업의 진행 상황을 쿼리하고 중간 또는 최종 응답을 다시 보낼 수 있습니다. 그런 다음 에이전트는 다른 작업을 계속할 수 있습니다. 예를 들어, 에이전트가 작업을 진행하기 전에 사람의 승인이 필요한 인간 참여 시나리오가 있습니다.

### 작동 방식

Python에서는 함수를 `LongRunningFunctionTool`로 래핑합니다. Java에서는 메서드 이름을 `LongRunningFunctionTool.create()`에 전달합니다.


1. **시작:** LLM이 도구를 호출하면 함수가 장기 실행 작업을 시작합니다.

2. **초기 업데이트:** 함수는 선택적으로 초기 결과(예: 장기 실행 작업 ID)를 반환해야 합니다. ADK 프레임워크는 결과를 가져와 `FunctionResponse` 내에 패키징하여 LLM에 다시 보냅니다. 이를 통해 LLM은 사용자에게 알릴 수 있습니다(예: 상태, 완료율, 메시지). 그런 다음 에이전트 실행이 종료/일시 중지됩니다.

3. **계속 또는 대기:** 각 에이전트 실행이 완료된 후. 에이전트 클라이언트는 장기 실행 작업의 진행 상황을 쿼리하고 중간 응답으로 에이전트 실행을 계속할지(진행 상황 업데이트) 또는 최종 응답이 검색될 때까지 기다릴지 결정할 수 있습니다. 에이전트 클라이언트는 다음 실행을 위해 중간 또는 최종 응답을 에이전트에 다시 보내야 합니다.

4. **프레임워크 처리:** ADK 프레임워크는 실행을 관리합니다. 에이전트 클라이언트가 보낸 중간 또는 최종 `FunctionResponse`를 LLM에 보내 사용자 친화적인 메시지를 생성합니다.

### 도구 만들기

도구 함수를 정의하고 `LongRunningFunctionTool` 클래스를 사용하여 래핑합니다:

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py:define_long_running_function"
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.LongRunningFunctionTool;
    import java.util.HashMap;
    import java.util.Map;
    
    public class ExampleLongRunningFunction {
    
      // 장기 실행 함수를 정의합니다.
      // 상환에 대한 승인을 요청합니다.
      public static Map<String, Object> askForApproval(String purpose, double amount) {
        // 티켓 생성 및 알림 전송 시뮬레이션
        System.out.println(
            "목적에 대한 티켓 생성 시뮬레이션: " + purpose + ", 금액: " + amount);
    
        // 승인자에게 티켓 링크와 함께 알림 전송
        Map<String, Object> result = new HashMap<>();
        result.put("status", "pending");
        result.put("approver", "Sean Zhou");
        result.put("purpose", purpose);
        result.put("amount", amount);
        result.put("ticket-id", "approval-ticket-1");
        return result;
      }
    
      public static void main(String[] args) throws NoSuchMethodException {
        // 메서드를 LongRunningFunctionTool.create에 전달
        LongRunningFunctionTool approveTool =
            LongRunningFunctionTool.create(ExampleLongRunningFunction.class, "askForApproval");
    
        // 에이전트에 도구 포함
        LlmAgent approverAgent =
            LlmAgent.builder()
                // ...
                .tools(approveTool)
                .build();
      }
    }
    ```

### 중간 / 최종 결과 업데이트

에이전트 클라이언트는 장기 실행 함수 호출이 포함된 이벤트를 받고 티켓의 상태를 확인합니다. 그런 다음 에이전트 클라이언트는 진행 상황을 업데이트하기 위해 중간 또는 최종 응답을 다시 보낼 수 있습니다. 프레임워크는 이 값(None인 경우에도)을 `FunctionResponse`의 콘텐츠에 패키징하여 LLM에 다시 보냅니다.

!!! Tip "Java ADK에만 적용됨"

    함수 도구와 함께 `ToolContext`를 전달할 때 다음 중 하나가 참인지 확인하세요:

    *   스키마가 함수 서명의 ToolContext 매개변수와 함께 전달됩니다. 예:
      ```
      @com.google.adk.tools.Annotations.Schema(name = "toolContext") ToolContext toolContext
      ```
    또는

    *   다음 `-parameters` 플래그가 mvn 컴파일러 플러그인에 설정됩니다.

    ```
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.14.0</version> <!-- 또는 최신 버전 -->
                <configuration>
                    <compilerArgs>
                        <arg>-parameters</arg>
                    </compilerArgs>
                </configuration>
            </plugin>
        </plugins>
    </build>
    ```
    이 제약 조건은 일시적이며 제거될 것입니다.


=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py:call_reimbursement_tool"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/LongRunningFunctionExample.java:full_code"
    ```


??? "Python 전체 예제: 파일 처리 시뮬레이션"

    ```py
    --8<-- "examples/python/snippets/tools/function-tools/human_in_the_loop.py"
    ```

#### 이 예제의 주요 측면

*   **`LongRunningFunctionTool`**: 제공된 메서드/함수를 래핑합니다. 프레임워크는 생성된 업데이트와 최종 반환 값을 순차적인 FunctionResponses로 전송하는 것을 처리합니다.

*   **에이전트 지침**: LLM에게 도구를 사용하고 사용자 업데이트를 위해 들어오는 FunctionResponse 스트림(진행률 대 완료)을 이해하도록 지시합니다.

*   **최종 반환**: 함수는 최종 결과 딕셔셔너리를 반환하며, 이는 완료를 나타내기 위해 마무리 FunctionResponse에서 전송됩니다.

## 3. 도구로서의 에이전트

이 강력한 기능은 다른 에이전트의 기능을 도구로 호출하여 시스템 내에서 활용할 수 있게 해줍니다. 도구로서의 에이전트를 사용하면 다른 에이전트를 호출하여 특정 작업을 수행하게 하여 효과적으로 **책임을 위임**할 수 있습니다. 이는 개념적으로 다른 에이전트를 호출하고 에이전트의 응답을 함수의 반환 값으로 사용하는 Python 함수를 만드는 것과 유사합니다.

### 하위 에이전트와의 주요 차이점

도구로서의 에이전트와 하위 에이전트를 구별하는 것이 중요합니다.

*   **도구로서의 에이전트:** 에이전트 A가 에이전트 B를 도구로 호출하면(도구로서의 에이전트 사용), 에이전트 B의 답변은 에이전트 A에게 **다시 전달**되며, 에이전트 A는 답변을 요약하고 사용자에게 응답을 생성합니다. 에이전트 A는 제어권을 유지하고 향후 사용자 입력을 계속 처리합니다.

*   **하위 에이전트:** 에이전트 A가 에이전트 B를 하위 에이전트로 호출하면, 사용자에게 응답하는 책임은 완전히 **에이전트 B에게 이전**됩니다. 에이전트 A는 사실상 루프에서 벗어납니다. 모든 후속 사용자 입력은 에이전트 B에 의해 답변됩니다.

### 사용법

에이전트를 도구로 사용하려면 에이전트를 AgentTool 클래스로 래핑하세요.

=== "Python"

    ```py
    tools=[AgentTool(agent=agent_b)]
    ```

=== "Java"

    ```java
    AgentTool.create(agent)
    ```

### 맞춤 설정

`AgentTool` 클래스는 동작을 맞춤 설정하기 위한 다음 속성을 제공합니다:

*   **skip\_summarization: bool:** True로 설정하면 프레임워크는 도구 에이전트의 응답에 대한 **LLM 기반 요약을 건너뜁니다**. 이는 도구의 응답이 이미 잘 형식화되어 있고 추가 처리가 필요하지 않은 경우에 유용할 수 있습니다.

??? "예제"

    === "Python"

        ```py
        --8<-- "examples/python/snippets/tools/function-tools/summarizer.py"
        ```
  
    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/tools/AgentToolCustomization.java:full_code"
        ```

### 작동 방식

1. `main_agent`가 긴 텍스트를 받으면, 지침에 따라 긴 텍스트에 대해 'summarize' 도구를 사용하라고 지시합니다.
2. 프레임워크는 'summarize'를 `summary_agent`를 래핑하는 `AgentTool`로 인식합니다.
3. 내부적으로 `main_agent`는 긴 텍스트를 입력으로 `summary_agent`를 호출합니다.
4. `summary_agent`는 지침에 따라 텍스트를 처리하고 요약을 생성합니다.
5. **`summary_agent`의 응답은 `main_agent`에게 다시 전달됩니다.**
6. `main_agent`는 요약을 가져와 사용자에게 최종 응답을 구성할 수 있습니다(예: "텍스트 요약은 다음과 같습니다: ...").