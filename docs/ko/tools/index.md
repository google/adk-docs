# 도구

## 도구란 무엇인가요?

ADK의 맥락에서, 도구는 AI 에이전트에게 제공되는 특정 기능을 나타내며, 에이전트가 핵심적인 텍스트 생성 및 추론 능력을 넘어 행동을 수행하고 세상과 상호 작용할 수 있도록 합니다. 유능한 에이전트를 기본적인 언어 모델과 구별하는 것은 종종 도구의 효과적인 사용입니다.

기술적으로, 도구는 일반적으로 모듈식 코드 구성 요소입니다—**Python/Java 함수**, 클래스 메서드 또는 심지어 다른 전문화된 에이전트와 같이—뚜렷하고 미리 정의된 작업을 실행하도록 설계되었습니다. 이러한 작업은 종종 외부 시스템이나 데이터와의 상호 작용을 포함합니다.

<img src="../assets/agent-tool-call.png" alt="에이전트 도구 호출">

### 주요 특징

**행동 지향적:** 도구는 다음과 같은 특정 작업을 수행합니다:

*   데이터베이스 쿼리
*   API 요청하기 (예: 날씨 데이터 가져오기, 예약 시스템)
*   웹 검색
*   코드 스니펫 실행
*   문서에서 정보 검색 (RAG)
*   다른 소프트웨어 또는 서비스와 상호 작용

**에이전트 기능 확장:** 에이전트가 실시간 정보에 접근하고, 외부 시스템에 영향을 미치며, 훈련 데이터에 내재된 지식 한계를 극복할 수 있도록 합니다.

**미리 정의된 로직 실행:** 결정적으로, 도구는 개발자가 정의한 특정 로직을 실행합니다. 에이전트의 핵심 거대 언어 모델(LLM)과 같은 독립적인 추론 능력은 없습니다. LLM은 어떤 도구를, 언제, 어떤 입력으로 사용할지 추론하지만, 도구 자체는 지정된 함수만 실행합니다.

## 에이전트는 어떻게 도구를 사용하나요?

에이전트는 종종 함수 호출을 포함하는 메커니즘을 통해 동적으로 도구를 활용합니다. 이 과정은 일반적으로 다음과 같은 단계를 따릅니다:

1.  **추론:** 에이전트의 LLM은 시스템 지침, 대화 기록, 사용자 요청을 분석합니다.
2.  **선택:** 분석을 기반으로, LLM은 에이전트에게 사용 가능한 도구와 각 도구를 설명하는 docstring을 기반으로 실행할 도구를 결정합니다.
3.  **호출:** LLM은 선택된 도구에 필요한 인수(입력)를 생성하고 실행을 트리거합니다.
4.  **관찰:** 에이전트는 도구가 반환한 출력(결과)을 받습니다.
5.  **마무리:** 에이전트는 도구의 출력을 진행 중인 추론 프로세스에 통합하여 다음 응답을 공식화하거나, 후속 단계를 결정하거나, 목표가 달성되었는지 여부를 결정합니다.

도구는 에이전트의 지능적인 핵심(LLM)이 복잡한 작업을 달성하기 위해 필요에 따라 접근하고 활용할 수 있는 전문화된 도구 키트로 생각할 수 있습니다.

## ADK의 도구 유형

ADK는 여러 유형의 도구를 지원하여 유연성을 제공합니다:

1.  **[함수 도구](../tools/function-tools.md):** 사용자가 특정 애플리케이션의 요구에 맞게 만든 도구입니다.
    *   **[함수/메서드](../tools/function-tools.md#1-function-tool):** 코드에서 표준 동기 함수 또는 메서드를 정의합니다(예: Python def).
    *   **[도구로서의 에이전트](../tools/function-tools.md#3-agent-as-a-tool):** 다른, 잠재적으로 전문화된 에이전트를 부모 에이전트의 도구로 사용합니다.
    *   **[장기 실행 함수 도구](../tools/function-tools.md#2-long-running-function-tool):** 비동기 작업을 수행하거나 완료하는 데 상당한 시간이 걸리는 도구를 지원합니다.
2.  **[내장 도구](../tools/built-in-tools.md):** 일반적인 작업을 위해 프레임워크에서 제공하는 바로 사용할 수 있는 도구입니다.
        예: Google 검색, 코드 실행, 검색 증강 생성(RAG).
3.  **[타사 도구](../tools/third-party-tools.md):** 인기 있는 외부 라이브러리의 도구를 원활하게 통합합니다.
        예: LangChain 도구, CrewAI 도구.

각 도구 유형에 대한 자세한 정보와 예제는 위에 링크된 해당 문서 페이지로 이동하세요.

## 에이전트 지침에서 도구 참조하기

에이전트의 지침 내에서 **함수 이름**을 사용하여 도구를 직접 참조할 수 있습니다. 도구의 **함수 이름**과 **docstring**이 충분히 설명적이라면, 지침은 주로 **거대 언어 모델(LLM)이 언제 도구를 활용해야 하는지**에 초점을 맞출 수 있습니다. 이는 명확성을 촉진하고 모델이 각 도구의 의도된 사용을 이해하는 데 도움이 됩니다.

도구가 생성할 수 있는 **다양한 반환 값을 에이전트가 어떻게 처리해야 하는지 명확하게 지시하는 것이 매우 중요합니다**. 예를 들어, 도구가 오류 메시지를 반환하는 경우, 지침은 에이전트가 작업을 재시도해야 하는지, 작업을 포기해야 하는지, 또는 사용자에게 추가 정보를 요청해야 하는지를 지정해야 합니다.

또한, ADK는 한 도구의 출력이 다른 도구의 입력으로 사용될 수 있는 순차적인 도구 사용을 지원합니다. 이러한 워크플로를 구현할 때, 모델이 필요한 단계를 통해 안내받도록 에이전트의 지침 내에서 **의도된 도구 사용 순서를 설명**하는 것이 중요합니다.

### 예제

다음 예제는 에이전트가 **지침에서 함수 이름을 참조**하여 도구를 사용하는 방법을 보여줍니다. 또한 성공 또는 오류 메시지와 같은 **도구의 다양한 반환 값을 처리**하도록 에이전트를 안내하는 방법과 작업을 완료하기 위해 **여러 도구의 순차적인 사용**을 조율하는 방법을 보여줍니다.

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/weather_sentiment.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/WeatherSentimentAgentApp.java:full_code"
    ```

## 도구 컨텍스트

더 고급 시나리오의 경우, ADK는 특수 매개변수 `tool_context: ToolContext`를 포함하여 도구 함수 내에서 추가적인 컨텍스트 정보에 접근할 수 있도록 합니다. 함수 서명에 이를 포함하면, ADK는 에이전트 실행 중에 도구가 호출될 때 **자동으로 ToolContext 클래스의 인스턴스를 제공**합니다.

**ToolContext**는 다음과 같은 몇 가지 주요 정보 및 제어 수단에 대한 접근을 제공합니다:

*   `state: State`: 현재 세션의 상태를 읽고 수정합니다. 여기서 이루어진 변경 사항은 추적되고 지속됩니다.

*   `actions: EventActions`: 도구 실행 후 에이전트의 후속 작업에 영향을 줍니다(예: 요약 건너뛰기, 다른 에이전트로 전송).

*   `function_call_id: str`: 프레임워크가 이 특정 도구 호출에 할당한 고유 식별자입니다. 인증 응답과 추적 및 상호 연관에 유용합니다. 이는 단일 모델 응답 내에서 여러 도구가 호출될 때도 유용할 수 있습니다.

*   `function_call_event_id: str`: 이 속성은 현재 도구 호출을 트리거한 **이벤트**의 고유 식별자를 제공합니다. 이는 추적 및 로깅 목적에 유용할 수 있습니다.

*   `auth_response: Any`: 이 도구 호출 전에 인증 흐름이 완료된 경우 인증 응답/자격 증명을 포함합니다.

*   서비스 접근: 아티팩트 및 메모리와 같은 구성된 서비스와 상호 작용하는 메서드.

도구 함수 docstring에 `tool_context` 매개변수를 포함해서는 안 됩니다. `ToolContext`는 LLM이 도구 함수를 호출하기로 결정한 *후에* ADK 프레임워크에 의해 자동으로 주입되므로, LLM의 의사 결정과 관련이 없으며 이를 포함하면 LLM을 혼동시킬 수 있습니다.

### **상태 관리**

`tool_context.state` 속성은 현재 세션과 관련된 상태에 대한 직접적인 읽기 및 쓰기 접근을 제공합니다. 이는 딕셔너리처럼 작동하지만 모든 수정 사항이 델타로 추적되고 세션 서비스에 의해 지속되도록 보장합니다. 이를 통해 도구는 다양한 상호 작용과 에이전트 단계 전반에 걸쳐 정보를 유지하고 공유할 수 있습니다.

*   **상태 읽기**: 표준 딕셔너리 접근(`tool_context.state['my_key']`) 또는 `.get()` 메서드(`tool_context.state.get('my_key', default_value)`)를 사용합니다.

*   **상태 쓰기**: 직접 값을 할당합니다(`tool_context.state['new_key'] = 'new_value'`). 이러한 변경 사항은 결과 이벤트의 state_delta에 기록됩니다.

*   **상태 접두사**: 표준 상태 접두사를 기억하세요:

    *   `app:*`: 애플리케이션의 모든 사용자 간에 공유됩니다.

    *   `user:*`: 모든 세션에 걸쳐 현재 사용자에게만 해당됩니다.

    *   (접두사 없음): 현재 세션에만 해당됩니다.

    *   `temp:*`: 임시적이며, 호출 간에 지속되지 않습니다(단일 실행 호출 내에서 데이터를 전달하는 데 유용하지만, 일반적으로 LLM 호출 사이에 작동하는 도구 컨텍스트 내에서는 덜 유용함).

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/user_preference.py"
    ```

=== "Java"

    ```java
    import com.google.adk.tools.FunctionTool;
    import com.google.adk.tools.ToolContext;

    // 사용자별 기본 설정을 업데이트합니다.
    public Map<String, String> updateUserThemePreference(String value, ToolContext toolContext) {
      String userPrefsKey = "user:preferences:theme";
  
      // 현재 기본 설정을 가져오거나 없는 경우 초기화합니다.
      String preference = toolContext.state().getOrDefault(userPrefsKey, "").toString();
      if (preference.isEmpty()) {
        preference = value;
      }
  
      // 업데이트된 딕셔너리를 상태에 다시 씁니다.
      toolContext.state().put("user:preferences", preference);
      System.out.printf("도구: 사용자 기본 설정 %s를 %s로 업데이트했습니다.", userPrefsKey, preference);
  
      return Map.of("status", "success", "updated_preference", toolContext.state().get(userPrefsKey).toString());
      // LLM이 updateUserThemePreference("dark")를 호출하면:
      // toolContext.state가 업데이트되고 변경 사항은
      // 결과 도구 응답 이벤트의 actions.stateDelta의 일부가 됩니다.
    }
    ```

### **에이전트 흐름 제어**

`tool_context.actions` 속성(Java에서는 `ToolContext.actions()`)은 **EventActions** 객체를 보유합니다. 이 객체의 속성을 수정하면 도구가 실행을 마친 후 에이전트나 프레임워크가 수행할 작업에 영향을 줄 수 있습니다.

*   **`skip_summarization: bool`**: (기본값: False) True로 설정하면 ADK에게 도구의 출력을 요약하는 LLM 호출을 건너뛰도록 지시합니다. 이는 도구의 반환 값이 이미 사용자에게 바로 사용할 수 있는 메시지일 때 유용합니다.

*   **`transfer_to_agent: str`**: 다른 에이전트의 이름으로 설정합니다. 프레임워크는 현재 에이전트의 실행을 중단하고 **대화의 제어권을 지정된 에이전트에게 이전**합니다. 이를 통해 도구는 동적으로 작업을 더 전문화된 에이전트에게 넘겨줄 수 있습니다.

*   **`escalate: bool`**: (기본값: False) True로 설정하면 현재 에이전트가 요청을 처리할 수 없으며 제어권을 부모 에이전트에게 넘겨야 함을 알립니다(계층 구조에 있는 경우). LoopAgent에서 하위 에이전트의 도구에서 **escalate=True**를 설정하면 루프가 종료됩니다.

#### 예제

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/customer_support_agent.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CustomerSupportAgentApp.java:full_code"
    ```

##### 설명

*   `main_agent`와 `support_agent`라는 두 에이전트를 정의합니다. `main_agent`는 초기 접점 역할을 하도록 설계되었습니다.
*   `check_and_transfer` 도구는 `main_agent`에 의해 호출될 때 사용자의 쿼리를 검사합니다.
*   쿼리에 "urgent"라는 단어가 포함되어 있으면 도구는 `tool_context`에 접근하여, 특히 **`tool_context.actions`**에 접근하여 transfer\_to\_agent 속성을 `support_agent`로 설정합니다.
*   이 작업은 프레임워크에 **대화의 제어권을 `support_agent`라는 이름의 에이전트에게 이전**하도록 신호를 보냅니다.
*   `main_agent`가 긴급 쿼리를 처리하면 `check_and_transfer` 도구가 이전을 트리거합니다. 후속 응답은 이상적으로 `support_agent`에서 나옵니다.
*   긴급성이 없는 일반 쿼리의 경우 도구는 이전을 트리거하지 않고 단순히 처리합니다.

이 예는 도구가 ToolContext의 EventActions를 통해 대화의 흐름을 다른 전문 에이전트에게 제어권을 이전함으로써 동적으로 영향을 미칠 수 있는 방법을 보여줍니다.

### **인증**

![python_only](https://img.shields.io/badge/현재_지원되는_언어-Python-blue){ title="이 기능은 현재 Python에서만 사용할 수 있습니다. Java 지원은 계획 중이거나 곧 제공될 예정입니다."}

ToolContext는 인증된 API와 상호 작용하는 도구를 위한 메커니즘을 제공합니다. 도구가 인증을 처리해야 하는 경우 다음을 사용할 수 있습니다:

*   **`auth_response`**: 도구가 호출되기 전에 프레임워크에서 인증이 이미 처리된 경우 자격 증명(예: 토큰)을 포함합니다(RestApiTool 및 OpenAPI 보안 스키마에서 일반적).

*   **`request_credential(auth_config: dict)`**: 도구가 인증이 필요하다고 판단했지만 자격 증명을 사용할 수 없는 경우 이 메서드를 호출합니다. 이는 제공된 auth_config를 기반으로 프레임워크에 인증 흐름을 시작하도록 신호를 보냅니다.

*   **`get_auth_response()`**: 후속 호출에서(request_credential이 성공적으로 처리된 후) 사용자가 제공한 자격 증명을 검색하기 위해 이 메서드를 호출합니다.

인증 흐름, 구성 및 예제에 대한 자세한 설명은 전용 도구 인증 문서 페이지를 참조하세요.

### **컨텍스트 인식 데이터 접근 방법**

이러한 메서드는 도구가 구성된 서비스에서 관리하는 세션 또는 사용자와 관련된 영구 데이터와 상호 작용할 수 있는 편리한 방법을 제공합니다.

*   **`list_artifacts()`** (또는 Java의 **`listArtifacts()`**): artifact_service를 통해 현재 세션에 저장된 모든 아티팩트의 파일 이름(또는 키) 목록을 반환합니다. 아티팩트는 일반적으로 사용자가 업로드하거나 도구/에이전트가 생성한 파일(이미지, 문서 등)입니다.

*   **`load_artifact(filename: str)`**: **artifact_service**에서 파일 이름으로 특정 아티팩트를 검색합니다. 선택적으로 버전을 지정할 수 있으며, 생략하면 최신 버전이 반환됩니다. 아티팩트 데이터와 mime 유형이 포함된 `google.genai.types.Part` 객체를 반환하거나, 찾을 수 없는 경우 None을 반환합니다.

*   **`save_artifact(filename: str, artifact: types.Part)`**: artifact_service에 새 버전의 아티팩트를 저장합니다. 새 버전 번호(0부터 시작)를 반환합니다.

*   **`search_memory(query: str)`** ![python_only](https://img.shields.io/badge/현재_지원되는_언어-Python-blue){ title="이 기능은 현재 Python에서만 사용할 수 있습니다. Java 지원은 계획 중이거나 곧 제공될 예정입니다."}

       구성된 `memory_service`를 사용하여 사용자의 장기 메모리를 쿼리합니다. 이는 과거 상호 작용이나 저장된 지식에서 관련 정보를 검색하는 데 유용합니다. **SearchMemoryResponse**의 구조는 특정 메모리 서비스 구현에 따라 다르지만 일반적으로 관련 텍스트 스니펫이나 대화 발췌문을 포함합니다.

#### 예제

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/overview/doc_analysis.py"
    ```

=== "Java"

    ```java
    // 메모리의 컨텍스트를 사용하여 문서를 분석합니다.
    // 콜백 컨텍스트 또는 LoadArtifacts 도구를 사용하여 아티팩트를 나열, 로드 및 저장할 수도 있습니다.
    public static @NonNull Maybe<ImmutableMap<String, Object>> processDocument(
        @Annotations.Schema(description = "분석할 문서의 이름입니다.") String documentName,
        @Annotations.Schema(description = "분석을 위한 쿼리입니다.") String analysisQuery,
        ToolContext toolContext) {
  
      // 1. 사용 가능한 모든 아티팩트 나열
      System.out.printf(
          "사용 가능한 모든 아티팩트 나열 %s:", toolContext.listArtifacts().blockingGet());
  
      // 2. 아티팩트를 메모리에 로드
      System.out.println("도구: 아티팩트 로드 시도 중: " + documentName);
      Part documentPart = toolContext.loadArtifact(documentName, Optional.empty()).blockingGet();
      if (documentPart == null) {
        System.out.println("도구: 문서 '" + documentName + "'를 찾을 수 없습니다.");
        return Maybe.just(
            ImmutableMap.<String, Object>of(
                "status", "error", "message", "문서 '" + documentName + "'를 찾을 수 없습니다."));
      }
      String documentText = documentPart.text().orElse("");
      System.out.println(
          "도구: 문서 '" + documentName + "' 로드됨 (" + documentText.length() + "자).");
  
      // 3. 분석 수행 (자리 표시자)
      String analysisResult =
          "'"
              + documentName
              + "'에 대한 분석 '"
              + analysisQuery
              + " [자리 표시자 분석 결과]";
      System.out.println("도구: 분석 수행됨.");
  
      // 4. 분석 결과를 새 아티팩트로 저장
      Part analysisPart = Part.fromText(analysisResult);
      String newArtifactName = "analysis_" + documentName;
  
      toolContext.saveArtifact(newArtifactName, analysisPart);
  
      return Maybe.just(
          ImmutableMap.<String, Object>builder()
              .put("status", "success")
              .put("analysis_artifact", newArtifactName)
              .build());
    }
    // FunctionTool processDocumentTool =
    //      FunctionTool.create(ToolContextArtifactExample.class, "processDocument");
    // 에이전트에서 이 함수 도구를 포함합니다.
    // LlmAgent agent = LlmAgent().builder().tools(processDocumentTool).build();
    ```

**ToolContext**를 활용하여 개발자는 ADK의 아키텍처와 원활하게 통합되고 에이전트의 전반적인 기능을 향상시키는 더 정교하고 컨텍스트를 인식하는 사용자 정의 도구를 만들 수 있습니다.

## 효과적인 도구 함수 정의하기

메서드나 함수를 ADK 도구로 사용할 때, 어떻게 정의하느냐가 에이전트가 이를 올바르게 사용하는 능력에 큰 영향을 미칩니다. 에이전트의 거대 언어 모델(LLM)은 함수의 **이름**, **매개변수(인수)**, **타입 힌트**, **독스트링** / **소스 코드 주석**에 크게 의존하여 그 목적을 이해하고 올바른 호출을 생성합니다.

다음은 효과적인 도구 함수를 정의하기 위한 주요 지침입니다:

*   **함수 이름:**
    *   행동을 명확하게 나타내는 동사-명사 기반의 설명적인 이름을 사용하세요(예: `get_weather`, `searchDocuments`, `schedule_meeting`).
    *   `run`, `process`, `handle_data`와 같은 일반적인 이름이나 `doStuff`와 같이 지나치게 모호한 이름은 피하세요. 좋은 설명이 있더라도 `doStuff`와 같은 이름은 모델이 언제 이 도구를 사용해야 할지, 예를 들어 `cancelFlight`와 비교하여 혼동을 줄 수 있습니다.
    *   LLM은 도구 선택 시 함수 이름을 주요 식별자로 사용합니다.

*   **매개변수(인수):**
    *   함수는 임의의 수의 매개변수를 가질 수 있습니다.
    *   명확하고 설명적인 이름을 사용하세요(예: `c` 대신 `city`, `q` 대신 `search_query`).
    *   **Python에서는 모든 매개변수에 대해 타입 힌트를 제공하세요**(예: `city: str`, `user_id: int`, `items: list[str]`). 이는 ADK가 LLM을 위한 올바른 스키마를 생성하는 데 필수적입니다.
    *   모든 매개변수 유형이 **JSON 직렬화 가능**한지 확인하세요. `str`, `int`, `float`, `bool`, `list`, `dict`와 같은 모든 표준 Python 유형과 그 조합은 일반적으로 안전합니다. 명확한 JSON 표현이 없는 한 복잡한 사용자 정의 클래스 인스턴스를 직접적인 매개변수로 사용하지 마세요.
    *   매개변수에 **기본값을 설정하지 마세요**. 예: `def my_func(param1: str = "default")`. 기본값은 함수 호출 생성 시 기본 모델에서 안정적으로 지원되거나 사용되지 않습니다. 모든 필요한 정보는 LLM이 컨텍스트에서 도출하거나 누락된 경우 명시적으로 요청해야 합니다.
    *   **`self` / `cls`는 자동으로 처리됩니다:** `self`(인스턴스 메서드용) 또는 `cls`(클래스 메서드용)와 같은 암시적 매개변수는 ADK에 의해 자동으로 처리되며 LLM에 표시되는 스키마에서 제외됩니다. 도구에 필요한 논리적 매개변수에 대해서만 타입 힌트와 설명을 정의하면 됩니다.

*   **반환 유형:**
    *   함수의 반환 값은 Python에서는 **딕셔너리(`dict`)**여야 하고, Java에서는 **맵(Map)**이어야 합니다.
    *   함수가 딕셔너리가 아닌 유형(예: 문자열, 숫자, 리스트)을 반환하는 경우, ADK 프레임워크는 결과를 모델에 다시 전달하기 전에 자동으로 `{'result': your_original_return_value}`와 같은 딕셔너리/맵으로 래핑합니다.
    *   딕셔너리/맵 키와 값을 **LLM이 쉽게 이해할 수 있도록 설명적으로** 설계하세요. 모델이 이 출력을 읽고 다음 단계를 결정한다는 것을 기억하세요.
    *   의미 있는 키를 포함하세요. 예를 들어, `500`과 같은 오류 코드만 반환하는 대신 `{'status': 'error', 'error_message': '데이터베이스 연결 실패'}`를 반환하세요.
    *   `status` 키(예: `'success'`, `'error'`, `'pending'`, `'ambiguous'`)를 포함하여 모델에 대한 도구 실행의 결과를 명확하게 나타내는 것이 **강력히 권장되는 관행**입니다.

*   **독스트링 / 소스 코드 주석:**
    *   **이것은 매우 중요합니다.** 독스트링은 LLM을 위한 설명 정보의 주요 소스입니다.
    *   **도구가 *무엇을* 하는지 명확하게 기술하세요.** 목적과 한계에 대해 구체적으로 설명하세요.
    *   **도구를 *언제* 사용해야 하는지 설명하세요.** LLM의 의사 결정을 안내하기 위해 컨텍스트나 예제 시나리오를 제공하세요.
    *   **각 매개변수를 명확하게 설명하세요.** LLM이 해당 인수에 대해 제공해야 하는 정보를 설명하세요.
    *   예상되는 `dict` 반환 값의 **구조와 의미**를 설명하세요. 특히 다른 `status` 값과 관련 데이터 키에 대해 설명하세요.
    *   **주입된 ToolContext 매개변수는 설명하지 마세요**. 선택적 `tool_context: ToolContext` 매개변수는 LLM이 알아야 할 매개변수가 아니므로 독스트링 설명 내에서 언급하지 마세요. ToolContext는 LLM이 호출하기로 결정한 *후에* ADK에 의해 주입됩니다.

    **좋은 정의의 예:**

=== "Python"
    
    ```python
    def lookup_order_status(order_id: str) -> dict:
      """고객의 주문 ID를 사용하여 현재 주문 상태를 가져옵니다.

      사용자가 특정 주문의 상태를 명시적으로 묻고 주문 ID를 제공할 때만 이 도구를 사용하세요.
      일반적인 문의에는 사용하지 마세요.

      Args:
          order_id: 조회할 주문의 고유 식별자입니다.

      Returns:
          주문 상태를 포함하는 딕셔너리입니다.
          가능한 상태: 'shipped', 'processing', 'pending', 'error'.
          성공 예시: {'status': 'shipped', 'tracking_number': '1Z9...'}
          오류 예시: {'status': 'error', 'error_message': '주문 ID를 찾을 수 없습니다.'}
      """
      # ... 상태를 가져오는 함수 구현 ...
      if status := fetch_status_from_backend(order_id):
           return {"status": status.state, "tracking_number": status.tracking} # 예제 구조
      else:
           return {"status": "error", "error_message": f"주문 ID {order_id}를 찾을 수 없습니다."}

    ```

=== "Java"

    ```java
    /**
     * 지정된 도시의 현재 날씨 보고서를 검색합니다.
     *
     * @param city 날씨 보고서를 검색할 도시입니다.
     * @param toolContext 도구의 컨텍스트입니다.
     * @return 날씨 정보를 포함하는 딕셔너리입니다.
     */
    public static Map<String, Object> getWeatherReport(String city, ToolContext toolContext) {
        Map<String, Object> response = new HashMap<>();
        if (city.toLowerCase(Locale.ROOT).equals("london")) {
            response.put("status", "success");
            response.put(
                    "report",
                    "런던의 현재 날씨는 흐리고 기온은 섭씨 18도이며 비가 올 가능성이 있습니다.");
        } else if (city.toLowerCase(Locale.ROOT).equals("paris")) {
            response.put("status", "success");
            response.put("report", "파리의 날씨는 맑고 기온은 섭씨 25도입니다.");
        } else {
            response.put("status", "error");
            response.put("error_message", String.format("'%s'에 대한 날씨 정보를 사용할 수 없습니다.", city));
        }
        return response;
    }
    ```

*   **단순성과 집중:**
    *   **도구를 집중적으로 유지:** 각 도구는 이상적으로 하나의 잘 정의된 작업을 수행해야 합니다.
    *   **더 적은 매개변수가 더 좋습니다:** 모델은 일반적으로 많거나 복잡한 매개변수가 있는 도구보다 적고 명확하게 정의된 매개변수가 있는 도구를 더 안정적으로 처리합니다.
    *   **간단한 데이터 유형 사용:** 가능한 경우 복잡한 사용자 정의 클래스나 깊게 중첩된 구조보다 기본 유형(`str`, `int`, `bool`, `float`, `List[str]`, **Python**에서 또는 `int`, `byte`, `short`, `long`, `float`, `double`, `boolean`, `char`, **Java**에서)을 선호하세요.
    *   **복잡한 작업 분해:** 여러 개의 뚜렷한 논리적 단계를 수행하는 함수를 더 작고 집중된 도구로 분해하세요. 예를 들어, 단일 `update_user_profile(profile: ProfileObject)` 도구 대신 `update_user_name(name: str)`, `update_user_address(address: str)`, `update_user_preferences(preferences: list[str])` 등과 같은 별도의 도구를 고려하세요. 이렇게 하면 LLM이 올바른 기능을 더 쉽게 선택하고 사용할 수 있습니다.

이러한 지침을 준수함으로써, LLM이 사용자 정의 함수 도구를 효과적으로 활용하는 데 필요한 명확성과 구조를 제공하여 더 유능하고 신뢰할 수 있는 에이전트 동작을 유도할 수 있습니다.

## 도구 세트: 도구 그룹화 및 동적 제공 ![python_only](https://img.shields.io/badge/현재_지원되는_언어-Python-blue){ title="이 기능은 현재 Python에서만 사용할 수 있습니다. Java 지원은 계획 중이거나 곧 제공될 예정입니다."}

개별 도구를 넘어, ADK는 `google.adk.tools.base_toolset`에 정의된 `BaseToolset` 인터페이스를 통해 **도구 세트**라는 개념을 도입합니다. 도구 세트를 사용하면 종종 동적으로 에이전트에게 `BaseTool` 인스턴스 모음을 관리하고 제공할 수 있습니다.

이 접근 방식은 다음에 유용합니다:

*   **관련 도구 구성:** 공통된 목적을 가진 도구를 그룹화합니다(예: 수학 연산을 위한 모든 도구 또는 특정 API와 상호 작용하는 모든 도구).
*   **동적 도구 가용성:** 에이전트가 현재 컨텍스트(예: 사용자 권한, 세션 상태 또는 기타 런타임 조건)에 따라 다른 도구를 사용할 수 있도록 합니다. 도구 세트의 `get_tools` 메서드는 어떤 도구를 노출할지 결정할 수 있습니다.
*   **외부 도구 제공자 통합:** 도구 세트는 OpenAPI 사양이나 MCP 서버와 같은 외부 시스템에서 오는 도구에 대한 어댑터 역할을 하여 ADK 호환 `BaseTool` 객체로 변환할 수 있습니다.

### `BaseToolset` 인터페이스

ADK에서 도구 세트로 작동하는 모든 클래스는 `BaseToolset` 추상 기본 클래스를 구현해야 합니다. 이 인터페이스는 주로 두 가지 메서드를 정의합니다:

*   **`async def get_tools(...) -> list[BaseTool]:`**
    이것은 도구 세트의 핵심 메서드입니다. ADK 에이전트가 사용 가능한 도구를 알아야 할 때, `tools` 목록에 제공된 각 `BaseToolset` 인스턴스에서 `get_tools()`를 호출합니다.
    *   선택적 `readonly_context`(`ReadonlyContext`의 인스턴스)를 받습니다. 이 컨텍스트는 현재 세션 상태(`readonly_context.state`), 에이전트 이름 및 호출 ID와 같은 정보에 대한 읽기 전용 접근을 제공합니다. 도구 세트는 이 컨텍스트를 사용하여 어떤 도구를 반환할지 동적으로 결정할 수 있습니다.
    *   **반드시** `BaseTool` 인스턴스(예: `FunctionTool`, `RestApiTool`)의 `list`를 반환해야 합니다.

*   **`async def close(self) -> None:`**
    이 비동기 메서드는 도구 세트가 더 이상 필요하지 않을 때, 예를 들어 에이전트 서버가 종료되거나 `Runner`가 닫힐 때 ADK 프레임워크에 의해 호출됩니다. 네트워크 연결 닫기, 파일 핸들 해제 또는 도구 세트에서 관리하는 기타 리소스 정리와 같은 필요한 정리 작업을 수행하기 위해 이 메서드를 구현하세요.

### 에이전트와 함께 도구 세트 사용하기

`LlmAgent`의 `tools` 목록에 `BaseToolset` 구현 인스턴스를 개별 `BaseTool` 인스턴스와 함께 직접 포함할 수 있습니다.

에이전트가 초기화되거나 사용 가능한 기능을 결정해야 할 때, ADK 프레임워크는 `tools` 목록을 반복합니다:

*   항목이 `BaseTool` 인스턴스이면 직접 사용됩니다.
*   항목이 `BaseToolset` 인스턴스이면 `get_tools()` 메서드가 호출되고(현재 `ReadonlyContext`와 함께), 반환된 `BaseTool` 목록이 에이전트의 사용 가능한 도구에 추가됩니다.

### 예제: 간단한 수학 도구 세트

간단한 산술 연산을 제공하는 도구 세트의 기본 예제를 만들어 보겠습니다.

```py
--8<-- "examples/python/snippets/tools/overview/toolset_example.py:init"
```

이 예제에서:

*   `SimpleMathToolset`은 `BaseToolset`을 구현하고 `get_tools()` 메서드는 `add_numbers`와 `subtract_numbers`에 대한 `FunctionTool` 인스턴스를 반환합니다. 또한 접두사를 사용하여 이름을 사용자 정의합니다.
*   `calculator_agent`는 개별 `greet_tool`과 `SimpleMathToolset`의 인스턴스로 구성됩니다.
*   `calculator_agent`가 실행되면 ADK는 `math_toolset_instance.get_tools()`를 호출합니다. 그러면 에이전트의 LLM은 사용자 요청을 처리하기 위해 `greet_user`, `calculator_add_numbers`, `calculator_subtract_numbers`에 접근할 수 있습니다.
*   `add_numbers` 도구는 `tool_context.state`에 쓰는 것을 보여주고, 에이전트의 지침은 이 상태를 읽는 것을 언급합니다.
*   `close()` 메서드는 도구 세트가 보유한 모든 리소스가 해제되도록 호출됩니다.

도구 세트는 ADK 에이전트에 도구 모음을 구성, 관리 및 동적으로 제공하는 강력한 방법을 제공하여 더 모듈식이고 유지 관리 가능하며 적응력이 뛰어난 에이전트 애플리케이션을 만들 수 있도록 합니다.