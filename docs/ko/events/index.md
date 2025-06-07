# 이벤트

이벤트는 Agent Development Kit(ADK) 내에서 정보 흐름의 기본 단위입니다. 이는 초기 사용자 입력부터 최종 응답 및 그 사이의 모든 단계에 이르기까지 에이전트의 상호 작용 수명 주기 동안 발생하는 모든 중요한 발생을 나타냅니다. 이벤트는 구성 요소가 통신하고, 상태가 관리되며, 제어 흐름이 지시되는 기본 방식이므로 이벤트를 이해하는 것이 중요합니다.

## 이벤트란 무엇이며 왜 중요한가요?

ADK의 `이벤트`는 에이전트 실행의 특정 지점을 나타내는 불변의 기록입니다. 사용자 메시지, 에이전트 답장, 도구 사용 요청(함수 호출), 도구 결과, 상태 변경, 제어 신호 및 오류를 캡처합니다.

=== "Python"
    기술적으로, 이는 `google.adk.events.Event` 클래스의 인스턴스이며, 필수적인 ADK 관련 메타데이터와 `actions` 페이로드를 추가하여 기본 `LlmResponse` 구조를 기반으로 합니다.

    ```python
    # 이벤트의 개념적 구조 (Python)
    # from google.adk.events import Event, EventActions
    # from google.genai import types

    # class Event(LlmResponse): # 간소화된 보기
    #     # --- LlmResponse 필드 ---
    #     content: Optional[types.Content]
    #     partial: Optional[bool]
    #     # ... 기타 응답 필드 ...

    #     # --- ADK 관련 추가 사항 ---
    #     author: str          # 'user' 또는 에이전트 이름
    #     invocation_id: str   # 전체 상호 작용 실행에 대한 ID
    #     id: str              # 이 특정 이벤트에 대한 고유 ID
    #     timestamp: float     # 생성 시간
    #     actions: EventActions # 부작용 및 제어에 중요
    #     branch: Optional[str] # 계층 경로
    #     # ...
    ```

=== "Java"
    Java에서는 이것이 `com.google.adk.events.Event` 클래스의 인스턴스입니다. 또한 필수적인 ADK 관련 메타데이터와 `actions` 페이로드를 추가하여 기본 응답 구조를 기반으로 합니다.

    ```java
    // 이벤트의 개념적 구조 (Java - com.google.adk.events.Event.java 참조)
    // 제공된 com.google.adk.events.Event.java에 기반한 간소화된 보기
    // public class Event extends JsonBaseModel {
    //     // --- LlmResponse와 유사한 필드 ---
    //     private Optional<Content> content;
    //     private Optional<Boolean> partial;
    //     // ... errorCode, errorMessage와 같은 기타 응답 필드 ...

    //     // --- ADK 관련 추가 사항 ---
    //     private String author;         // 'user' 또는 에이전트 이름
    //     private String invocationId;   // 전체 상호 작용 실행에 대한 ID
    //     private String id;             // 이 특정 이벤트에 대한 고유 ID
    //     private long timestamp;        // 생성 시간 (에포크 밀리초)
    //     private EventActions actions;  // 부작용 및 제어에 중요
    //     private Optional<String> branch; // 계층 경로
    //     // ... turnComplete, longRunningToolIds 등과 같은 기타 필드
    // }
    ```

이벤트는 다음과 같은 몇 가지 주요 이유로 ADK 운영의 중심입니다:

1.  **통신:** 사용자 인터페이스, `Runner`, 에이전트, LLM 및 도구 간의 표준 메시지 형식으로 사용됩니다. 모든 것이 `이벤트`로 흐릅니다.

2.  **상태 및 아티팩트 변경 신호:** 이벤트는 상태 수정에 대한 지침을 전달하고 아티팩트 업데이트를 추적합니다. `SessionService`는 이러한 신호를 사용하여 지속성을 보장합니다. Python에서는 `event.actions.state_delta` 및 `event.actions.artifact_delta`를 통해 변경 사항이 신호됩니다.

3.  **제어 흐름:** `event.actions.transfer_to_agent` 또는 `event.actions.escalate`와 같은 특정 필드는 프레임워크를 지시하는 신호 역할을 하여 다음에 실행할 에이전트나 루프 종료 여부를 결정합니다.

4.  **기록 및 관찰 가능성:** `session.events`에 기록된 이벤트 시퀀스는 상호 작용의 완전하고 시간순으로 된 기록을 제공하여 디버깅, 감사 및 단계별 에이전트 동작 이해에 매우 중요합니다.

본질적으로 사용자의 쿼리에서 에이전트의 최종 답변에 이르기까지 전체 프로세스는 `이벤트` 객체의 생성, 해석 및 처리를 통해 조정됩니다.


## 이벤트 이해 및 사용

개발자로서 여러분은 주로 `Runner`가 생성하는 이벤트 스트림과 상호 작용하게 됩니다. 이를 이해하고 정보를 추출하는 방법은 다음과 같습니다:

!!! Note
    기본 요소에 대한 특정 매개변수나 메서드 이름은 SDK 언어에 따라 약간 다를 수 있습니다(예: Python의 `event.content()`, Java의 `event.content().get().parts()`). 자세한 내용은 언어별 API 문서를 참조하세요.

### 이벤트 출처 및 유형 식별

다음을 확인하여 이벤트가 무엇을 나타내는지 빠르게 파악하세요:

*   **누가 보냈나요? (`event.author`)**
    *   `'user'`: 최종 사용자의 직접적인 입력을 나타냅니다.
    *   `'AgentName'`: 특정 에이전트(예: `'WeatherAgent'`, `'SummarizerAgent'`)의 출력 또는 작업을 나타냅니다.
*   **주요 페이로드는 무엇인가요? (`event.content` 및 `event.content.parts`)**
    *   **텍스트:** 대화 메시지를 나타냅니다. Python의 경우 `event.content.parts.text`가 있는지 확인하세요. Java의 경우 `event.content()`가 있고, `parts()`가 있고 비어 있지 않으며, 첫 번째 파트의 `text()`가 있는지 확인하세요.
    *   **도구 호출 요청:** `event.get_function_calls()`를 확인하세요. 비어 있지 않으면 LLM이 하나 이상의 도구를 실행하도록 요청하는 것입니다. 목록의 각 항목에는 `.name`과 `.args`가 있습니다.
    *   **도구 결과:** `event.get_function_responses()`를 확인하세요. 비어 있지 않으면 이 이벤트는 도구 실행의 결과를 전달합니다. 각 항목에는 `.name`과 `.response`(도구가 반환한 사전)가 있습니다. *참고:* 기록 구조화를 위해 `content` 내부의 `role`은 종종 `'user'`이지만, 이벤트 `author`는 일반적으로 도구 호출을 요청한 에이전트입니다.

*   **스트리밍 출력인가요? (`event.partial`)**
    이것이 LLM의 불완전한 텍스트 덩어리인지 여부를 나타냅니다.
    *   `True`: 더 많은 텍스트가 이어집니다.
    *   `False` 또는 `None`/`Optional.empty()`: 콘텐츠의 이 부분은 완료되었지만 전체 턴은 완료되지 않았을 수 있습니다(`turn_complete`도 false인 경우).

=== "Python"
    ```python
    # 의사 코드: 기본 이벤트 식별 (Python)
    # async for event in runner.run_async(...):
    #     print(f"이벤트 출처: {event.author}")
    #
    #     if event.content and event.content.parts:
    #         if event.get_function_calls():
    #             print("  유형: 도구 호출 요청")
    #         elif event.get_function_responses():
    #             print("  유형: 도구 결과")
    #         elif event.content.parts[0].text:
    #             if event.partial:
    #                 print("  유형: 스트리밍 텍스트 청크")
    #             else:
    #                 print("  유형: 완전한 텍스트 메시지")
    #         else:
    #             print("  유형: 기타 콘텐츠 (예: 코드 결과)")
    #     elif event.actions and (event.actions.state_delta or event.actions.artifact_delta):
    #         print("  유형: 상태/아티팩트 업데이트")
    #     else:
    #         print("  유형: 제어 신호 또는 기타")
    ```

=== "Java"
    ```java
    // 의사 코드: 기본 이벤트 식별 (Java)
    // import com.google.genai.types.Content;
    // import com.google.adk.events.Event;
    // import com.google.adk.events.EventActions;

    // runner.runAsync(...).forEach(event -> { // 동기 스트림 또는 반응형 스트림이라고 가정
    //     System.out.println("이벤트 출처: " + event.author());
    //
    //     if (event.content().isPresent()) {
    //         Content content = event.content().get();
    //         if (!event.functionCalls().isEmpty()) {
    //             System.out.println("  유형: 도구 호출 요청");
    //         } else if (!event.functionResponses().isEmpty()) {
    //             System.out.println("  유형: 도구 결과");
    //         } else if (content.parts().isPresent() && !content.parts().get().isEmpty() &&
    //                    content.parts().get().get(0).text().isPresent()) {
    //             if (event.partial().orElse(false)) {
    //                 System.out.println("  유형: 스트리밍 텍스트 청크");
    //             } else {
    //                 System.out.println("  유형: 완전한 텍스트 메시지");
    //             }
    //         } else {
    //             System.out.println("  유형: 기타 콘텐츠 (예: 코드 결과)");
    //         }
    //     } else if (event.actions() != null &&
    //                ((event.actions().stateDelta() != null && !event.actions().stateDelta().isEmpty()) ||
    //                 (event.actions().artifactDelta() != null && !event.actions().artifactDelta().isEmpty()))) {
    //         System.out.println("  유형: 상태/아티팩트 업데이트");
    //     } else {
    //         System.out.println("  유형: 제어 신호 또는 기타");
    //     }
    // });
    ```

### 주요 정보 추출

이벤트 유형을 알게 되면 관련 데이터에 접근합니다:

*   **텍스트 콘텐츠:**
    텍스트에 접근하기 전에 항상 콘텐츠와 파트가 있는지 확인하세요. Python에서는 `text = event.content.parts.text`입니다.

*   **함수 호출 세부 정보:**
    
    === "Python"
        ```python
        calls = event.get_function_calls()
        if calls:
            for call in calls:
                tool_name = call.name
                arguments = call.args # 이것은 보통 딕셔너리입니다
                print(f"  도구: {tool_name}, 인수: {arguments}")
                # 애플리케이션은 이를 기반으로 실행을 디스패치할 수 있습니다
        ```
    === "Java"

        ```java
        import com.google.genai.types.FunctionCall;
        import com.google.common.collect.ImmutableList;
        import java.util.Map;
    
        ImmutableList<FunctionCall> calls = event.functionCalls(); // Event.java에서
        if (!calls.isEmpty()) {
          for (FunctionCall call : calls) {
            String toolName = call.name().get();
            // args는 Optional<Map<String, Object>>입니다
            Map<String, Object> arguments = call.args().get();
                   System.out.println("  도구: " + toolName + ", 인수: " + arguments);
            // 애플리케이션은 이를 기반으로 실행을 디스패치할 수 있습니다
          }
        }
        ```

*   **함수 응답 세부 정보:**
    
    === "Python"
        ```python
        responses = event.get_function_responses()
        if responses:
            for response in responses:
                tool_name = response.name
                result_dict = response.response # 도구가 반환한 딕셔너리
                print(f"  도구 결과: {tool_name} -> {result_dict}")
        ```
    === "Java"

        ```java
        import com.google.genai.types.FunctionResponse;
        import com.google.common.collect.ImmutableList;
        import java.util.Map; 

        ImmutableList<FunctionResponse> responses = event.functionResponses(); // Event.java에서
        if (!responses.isEmpty()) {
            for (FunctionResponse response : responses) {
                String toolName = response.name().get();
                Map<String, String> result= response.response().get(); // 응답을 받기 전에 확인
                System.out.println("  도구 결과: " + toolName + " -> " + result);
            }
        }
        ```

*   **식별자:**
    *   `event.id`: 이 특정 이벤트 인스턴스에 대한 고유 ID입니다.
    *   `event.invocation_id`: 이 이벤트가 속한 전체 사용자-요청-최종-응답 주기에 대한 ID입니다. 로깅 및 추적에 유용합니다.

### 작업 및 부작용 감지

`event.actions` 객체는 발생했거나 발생해야 하는 변경 사항을 알립니다. 접근하기 전에 항상 `event.actions`와 그 필드/메서드가 있는지 확인하세요.

*   **상태 변경:** 이 이벤트를 생성한 단계 동안 세션 상태에서 수정된 키-값 쌍의 컬렉션을 제공합니다.
    
    === "Python"
        `delta = event.actions.state_delta` (`{key: value}` 쌍의 딕셔너리).
        ```python
        if event.actions and event.actions.state_delta:
            print(f"  상태 변경: {event.actions.state_delta}")
            # 필요한 경우 로컬 UI 또는 애플리케이션 상태 업데이트
        ```
    === "Java"
        `ConcurrentMap<String, Object> delta = event.actions().stateDelta();`

        ```java
        import java.util.concurrent.ConcurrentMap;
        import com.google.adk.events.EventActions;

        EventActions actions = event.actions(); // event.actions()가 null이 아니라고 가정
        if (actions != null && actions.stateDelta() != null && !actions.stateDelta().isEmpty()) {
            ConcurrentMap<String, Object> stateChanges = actions.stateDelta();
            System.out.println("  상태 변경: " + stateChanges);
            // 필요한 경우 로컬 UI 또는 애플리케이션 상태 업데이트
        }
        ```

*   **아티팩트 저장:** 어떤 아티팩트가 저장되었고 그 새 버전 번호(또는 관련 `Part` 정보)를 나타내는 컬렉션을 제공합니다.
    
    === "Python"
        `artifact_changes = event.actions.artifact_delta` (`{filename: version}`의 딕셔너리).
        ```python
        if event.actions and event.actions.artifact_delta:
            print(f"  저장된 아티팩트: {event.actions.artifact_delta}")
            # UI가 아티팩트 목록을 새로 고칠 수 있음
        ```
    === "Java"
        `ConcurrentMap<String, Part> artifactChanges = event.actions().artifactDelta();`
        
        ```java
        import java.util.concurrent.ConcurrentMap;
        import com.google.genai.types.Part;
        import com.google.adk.events.EventActions;

        EventActions actions = event.actions(); // event.actions()가 null이 아니라고 가정
        if (actions != null && actions.artifactDelta() != null && !actions.artifactDelta().isEmpty()) {
            ConcurrentMap<String, Part> artifactChanges = actions.artifactDelta();
            System.out.println("  저장된 아티팩트: " + artifactChanges);
            // UI가 아티팩트 목록을 새로 고칠 수 있음
            // 파일 이름과 Part 세부 정보를 얻기 위해 artifactChanges.entrySet()을 반복
        }
        ```

*   **제어 흐름 신호:** 불리언 플래그 또는 문자열 값을 확인합니다:
    
    === "Python"
        *   `event.actions.transfer_to_agent` (문자열): 제어가 명명된 에이전트로 전달되어야 합니다.
        *   `event.actions.escalate` (불리언): 루프가 종료되어야 합니다.
        *   `event.actions.skip_summarization` (불리언): 도구 결과가 LLM에 의해 요약되어서는 안 됩니다.
        ```python
        if event.actions:
            if event.actions.transfer_to_agent:
                print(f"  신호: {event.actions.transfer_to_agent}로 전송")
            if event.actions.escalate:
                print("  신호: 에스컬레이션 (루프 종료)")
            if event.actions.skip_summarization:
                print("  신호: 도구 결과 요약 건너뛰기")
        ```
    === "Java"
        *   `event.actions().transferToAgent()` (`Optional<String>` 반환): 제어가 명명된 에이전트로 전달되어야 합니다.
        *   `event.actions().escalate()` (`Optional<Boolean>` 반환): 루프가 종료되어야 합니다.
        *   `event.actions().skipSummarization()` (`Optional<Boolean>` 반환): 도구 결과가 LLM에 의해 요약되어서는 안 됩니다.

        ```java
        import com.google.adk.events.EventActions;
        import java.util.Optional;

        EventActions actions = event.actions(); // event.actions()가 null이 아니라고 가정
        if (actions != null) {
            Optional<String> transferAgent = actions.transferToAgent();
            if (transferAgent.isPresent()) {
                System.out.println("  신호: " + transferAgent.get() + "로 전송");
            }

            Optional<Boolean> escalate = actions.escalate();
            if (escalate.orElse(false)) { // 또는 escalate.isPresent() && escalate.get()
                System.out.println("  신호: 에스컬레이션 (루프 종료)");
            }

            Optional<Boolean> skipSummarization = actions.skipSummarization();
            if (skipSummarization.orElse(false)) { // 또는 skipSummarization.isPresent() && skipSummarization.get()
                System.out.println("  신호: 도구 결과 요약 건너뛰기");
            }
        }
        ```

### 이벤트가 "최종" 응답인지 확인하기

내장된 헬퍼 메서드 `event.is_final_response()`를 사용하여 턴에 대한 에이전트의 완전한 출력으로 표시에 적합한 이벤트를 식별하세요.

*   **목적:** 중간 단계(도구 호출, 부분 스트리밍 텍스트, 내부 상태 업데이트 등)를 최종 사용자 대면 메시지에서 필터링합니다.
*   **언제 `True`인가요?**
    1.  이벤트에 도구 결과(`function_response`)가 포함되어 있고 `skip_summarization`이 `True`입니다.
    2.  이벤트에 `is_long_running=True`로 표시된 도구에 대한 도구 호출(`function_call`)이 포함되어 있습니다. Java에서는 `longRunningToolIds` 목록이 비어 있는지 확인하세요:
        *   `event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()`가 `true`입니다.
    3.  또는, 다음이 **모두** 충족될 때:
        *   함수 호출이 없음 (`get_function_calls()`가 비어 있음).
        *   함수 응답이 없음 (`get_function_responses()`가 비어 있음).
        *   부분 스트림 청크가 아님 (`partial`이 `True`가 아님).
        *   추가 처리/표시가 필요할 수 있는 코드 실행 결과로 끝나지 않음.
*   **사용법:** 애플리케이션 로직에서 이벤트 스트림을 필터링합니다.

    === "Python"
        ```python
        # 의사 코드: 애플리케이션에서 최종 응답 처리 (Python)
        # full_response_text = ""
        # async for event in runner.run_async(...):
        #     # 필요한 경우 스트리밍 텍스트 누적...
        #     if event.partial and event.content and event.content.parts and event.content.parts[0].text:
        #         full_response_text += event.content.parts[0].text
        #
        #     # 최종, 표시 가능한 이벤트인지 확인
        #     if event.is_final_response():
        #         print("\n--- 최종 출력 감지됨 ---")
        #         if event.content and event.content.parts and event.content.parts[0].text:
        #              # 스트림의 마지막 부분인 경우 누적된 텍스트 사용
        #              final_text = full_response_text + (event.content.parts[0].text if not event.partial else "")
        #              print(f"사용자에게 표시: {final_text.strip()}")
        #              full_response_text = "" # 누적기 재설정
        #         elif event.actions and event.actions.skip_summarization and event.get_function_responses():
        #              # 필요한 경우 원시 도구 결과 표시 처리
        #              response_data = event.get_function_responses()[0].response
        #              print(f"원시 도구 결과 표시: {response_data}")
        #         elif hasattr(event, 'long_running_tool_ids') and event.long_running_tool_ids:
        #              print("메시지 표시: 도구가 백그라운드에서 실행 중입니다...")
        #         else:
        #              # 해당되는 경우 다른 유형의 최종 응답 처리
        #              print("표시: 최종 비텍스트 응답 또는 신호.")
        ```
    === "Java"
        ```java
        // 의사 코드: 애플리케이션에서 최종 응답 처리 (Java)
        import com.google.adk.events.Event;
        import com.google.genai.types.Content;
        import com.google.genai.types.FunctionResponse;
        import java.util.Map;

        StringBuilder fullResponseText = new StringBuilder();
        runner.run(...).forEach(event -> { // 이벤트 스트림이라고 가정
             // 필요한 경우 스트리밍 텍스트 누적...
             if (event.partial().orElse(false) && event.content().isPresent()) {
                 event.content().flatMap(Content::parts).ifPresent(parts -> {
                     if (!parts.isEmpty() && parts.get(0).text().isPresent()) {
                         fullResponseText.append(parts.get(0).text().get());
                    }
                 });
             }
        
             // 최종, 표시 가능한 이벤트인지 확인
             if (event.finalResponse()) { // Event.java의 메서드 사용
                 System.out.println("\n--- 최종 출력 감지됨 ---");
                 if (event.content().isPresent() &&
                     event.content().flatMap(Content::parts).map(parts -> !parts.isEmpty() && parts.get(0).text().isPresent()).orElse(false)) {
                     // 스트림의 마지막 부분인 경우 누적된 텍스트 사용
                     String eventText = event.content().get().parts().get().get(0).text().get();
                     String finalText = fullResponseText.toString() + (event.partial().orElse(false) ? "" : eventText);
                     System.out.println("사용자에게 표시: " + finalText.trim());
                     fullResponseText.setLength(0); // 누적기 재설정
                 } else if (event.actions() != null && event.actions().skipSummarization().orElse(false)
                            && !event.functionResponses().isEmpty()) {
                     // 필요한 경우 원시 도구 결과 표시 처리,
                     // 특히 finalResponse()가 다른 조건으로 인해 true였거나
                     // finalResponse()와 관계없이 건너뛴 요약 결과를 표시하려는 경우
                     Map<String, Object> responseData = event.functionResponses().get(0).response().get();
                     System.out.println("원시 도구 결과 표시: " + responseData);
                 } else if (event.longRunningToolIds().isPresent() && !event.longRunningToolIds().get().isEmpty()) {
                     // 이 경우는 event.finalResponse()에 의해 처리됨
                     System.out.println("메시지 표시: 도구가 백그라운드에서 실행 중입니다...");
                 } else {
                     // 해당되는 경우 다른 유형의 최종 응답 처리
                     System.out.println("표시: 최종 비텍스트 응답 또는 신호.");
                 }
             }
         });
        ```

이벤트의 이러한 측면을 신중하게 검토함으로써 ADK 시스템을 통해 흐르는 풍부한 정보에 적절하게 반응하는 견고한 애플리케이션을 구축할 수 있습니다.

## 이벤트 흐름: 생성 및 처리

이벤트는 다른 지점에서 생성되고 프레임워크에 의해 체계적으로 처리됩니다. 이 흐름을 이해하면 작업과 기록이 어떻게 관리되는지 명확해집니다.

*   **생성 소스:**
    *   **사용자 입력:** `Runner`는 일반적으로 초기 사용자 메시지나 대화 중 입력을 `author='user'`인 `이벤트`로 래핑합니다.
    *   **에이전트 로직:** 에이전트(`BaseAgent`, `LlmAgent`)는 응답을 전달하거나 작업을 신호하기 위해 명시적으로 `yield Event(...)` 객체(`author=self.name` 설정)를 생성합니다.
    *   **LLM 응답:** ADK 모델 통합 계층은 원시 LLM 출력(텍스트, 함수 호출, 오류)을 호출 에이전트가 작성한 `이벤트` 객체로 변환합니다.
    *   **도구 결과:** 도구가 실행된 후 프레임워크는 `function_response`를 포함하는 `이벤트`를 생성합니다. `author`는 일반적으로 도구를 요청한 에이전트이며, `content` 내부의 `role`은 LLM 기록을 위해 `'user'`로 설정됩니다.


*   **처리 흐름:**
    1.  **생성/반환:** 이벤트가 생성되고 소스에 의해 생성(Python) 또는 반환/방출(Java)됩니다.
    2.  **Runner 수신:** 에이전트를 실행하는 메인 `Runner`가 이벤트를 받습니다.
    3.  **SessionService 처리:** `Runner`는 이벤트를 구성된 `SessionService`로 보냅니다. 이것은 중요한 단계입니다:
        *   **델타 적용:** 서비스는 `event.actions.state_delta`를 `session.state`에 병합하고 `event.actions.artifact_delta`를 기반으로 내부 기록을 업데이트합니다. (참고: 실제 아티팩트 *저장*은 일반적으로 `context.save_artifact`가 호출되었을 때 더 일찍 발생했습니다).
        *   **메타데이터 확정:** 없는 경우 고유한 `event.id`를 할당하고, `event.timestamp`를 업데이트할 수 있습니다.
        *   **기록에 지속:** 처리된 이벤트를 `session.events` 목록에 추가합니다.
    4.  **외부 생성:** `Runner`는 처리된 이벤트를 호출 애플리케이션(예: `runner.run_async`를 호출한 코드)으로 외부로 생성(Python) 또는 반환/방출(Java)합니다.

이 흐름은 상태 변경과 기록이 각 이벤트의 통신 내용과 함께 일관되게 기록되도록 보장합니다.


## 일반적인 이벤트 예시 (설명 패턴)

스트림에서 볼 수 있는 일반적인 이벤트의 간결한 예시는 다음과 같습니다:

*   **사용자 입력:**
    ```json
    {
      "author": "user",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"text": "다음 화요일 런던행 항공편을 예약하세요"}]}
      // actions는 보통 비어 있음
    }
    ```
*   **에이전트 최종 텍스트 응답:** (`is_final_response() == True`)
    ```json
    {
      "author": "TravelAgent",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"text": "네, 도와드릴 수 있습니다. 출발 도시를 확인해 주시겠어요?"}]},
      "partial": false,
      "turn_complete": true
      // actions에는 상태 델타 등이 포함될 수 있음
    }
    ```
*   **에이전트 스트리밍 텍스트 응답:** (`is_final_response() == False`)
    ```json
    {
      "author": "SummaryAgent",
      "invocation_id": "e-abc...",
      "content": {"parts": [{"text": "이 문서는 세 가지 주요 사항을 논의합니다:"}]},
      "partial": true,
      "turn_complete": false
    }
    // ... 더 많은 partial=True 이벤트가 이어짐 ...
    ```
*   **도구 호출 요청 (LLM에 의해):** (`is_final_response() == False`)
    ```json
    {
      "author": "TravelAgent",
      "invocation_id": "e-xyz...",
      "content": {"parts": [{"function_call": {"name": "find_airports", "args": {"city": "London"}}}]}
      // actions는 보통 비어 있음
    }
    ```
*   **도구 결과 제공됨 (LLM에게):** (`is_final_response()`는 `skip_summarization`에 따라 다름)
    ```json
    {
      "author": "TravelAgent", // 작성자는 호출을 요청한 에이전트
      "invocation_id": "e-xyz...",
      "content": {
        "role": "user", // LLM 기록을 위한 역할
        "parts": [{"function_response": {"name": "find_airports", "response": {"result": ["LHR", "LGW", "STN"]}}}]
      }
      // actions에는 skip_summarization=True가 포함될 수 있음
    }
    ```
*   **상태/아티팩트 업데이트만:** (`is_final_response() == False`)
    ```json
    {
      "author": "InternalUpdater",
      "invocation_id": "e-def...",
      "content": null,
      "actions": {
        "state_delta": {"user_status": "verified"},
        "artifact_delta": {"verification_doc.pdf": 2}
      }
    }
    ```
*   **에이전트 전송 신호:** (`is_final_response() == False`)
    ```json
    {
      "author": "OrchestratorAgent",
      "invocation_id": "e-789...",
      "content": {"parts": [{"function_call": {"name": "transfer_to_agent", "args": {"agent_name": "BillingAgent"}}}]},
      "actions": {"transfer_to_agent": "BillingAgent"} // 프레임워크에 의해 추가됨
    }
    ```
*   **루프 에스컬레이션 신호:** (`is_final_response() == False`)
    ```json
    {
      "author": "CheckerAgent",
      "invocation_id": "e-loop...",
      "content": {"parts": [{"text": "최대 재시도 횟수에 도달했습니다."}]}, // 선택적 콘텐츠
      "actions": {"escalate": true}
    }
    ```

## 추가 컨텍스트 및 이벤트 세부 정보

핵심 개념 외에도 특정 사용 사례에 중요한 컨텍스트 및 이벤트에 대한 몇 가지 구체적인 세부 정보는 다음과 같습니다:

1.  **`ToolContext.function_call_id` (도구 작업 연결):**
    *   LLM이 도구(FunctionCall)를 요청하면 해당 요청에 ID가 있습니다. 도구 함수에 제공된 `ToolContext`에는 이 `function_call_id`가 포함됩니다.
    *   **중요성:** 이 ID는 인증과 같은 작업을 시작한 특정 도구 요청과 다시 연결하는 데 중요하며, 특히 한 턴에 여러 도구가 호출되는 경우 더욱 그렇습니다. 프레임워크는 이 ID를 내부적으로 사용합니다.

2.  **상태/아티팩트 변경 기록 방식:**
    *   `CallbackContext` 또는 `ToolContext`를 사용하여 상태를 수정하거나 아티팩트를 저장하면 이러한 변경 사항이 즉시 영구 저장소에 기록되지 않습니다.
    *   대신 `EventActions` 객체 내의 `state_delta` 및 `artifact_delta` 필드를 채웁니다.
    *   이 `EventActions` 객체는 변경 후 생성된 *다음 이벤트*(예: 에이전트의 응답 또는 도구 결과 이벤트)에 연결됩니다.
    *   `SessionService.append_event` 메서드는 들어오는 이벤트에서 이러한 델타를 읽어 세션의 영구 상태 및 아티팩트 기록에 적용합니다. 이렇게 하면 변경 사항이 이벤트 스트림에 시간순으로 연결되도록 보장합니다.

3.  **상태 범위 접두사 (`app:`, `user:`, `temp:`):**
    *   `context.state`를 통해 상태를 관리할 때 선택적으로 접두사를 사용할 수 있습니다:
        *   `app:my_setting`: 전체 애플리케이션과 관련된 상태를 제안합니다 (영구 `SessionService` 필요).
        *   `user:user_preference`: 세션 간 특정 사용자와 관련된 상태를 제안합니다 (영구 `SessionService` 필요).
        *   `temp:intermediate_result` 또는 접두사 없음: 일반적으로 현재 호출에 대한 세션별 또는 임시 상태입니다.
    *   기본 `SessionService`는 지속성을 위해 이러한 접두사가 처리되는 방식을 결정합니다.

4.  **오류 이벤트:**
    *   `이벤트`는 오류를 나타낼 수 있습니다. `event.error_code` 및 `event.error_message` 필드를 확인하세요(`LlmResponse`에서 상속됨).
    *   오류는 LLM에서 발생할 수 있습니다(예: 안전 필터, 리소스 제한). 또는 도구가 치명적으로 실패할 경우 프레임워크에 의해 패키징될 수 있습니다. 일반적인 도구별 오류는 도구 `FunctionResponse` 콘텐츠를 확인하세요.
    ```json
    // 오류 이벤트 예시 (개념적)
    {
      "author": "LLMAgent",
      "invocation_id": "e-err...",
      "content": null,
      "error_code": "SAFETY_FILTER_TRIGGERED",
      "error_message": "안전 설정으로 인해 응답이 차단되었습니다.",
      "actions": {}
    }
    ```

이러한 세부 정보는 도구 인증, 상태 지속성 범위 및 이벤트 스트림 내 오류 처리를 포함하는 고급 사용 사례에 대한 더 완전한 그림을 제공합니다.

## 이벤트 작업 모범 사례

ADK 애플리케이션에서 이벤트를 효과적으로 사용하려면:

*   **명확한 저자:** 사용자 지정 에이전트를 구축할 때 기록에서 에이전트 작업에 대한 올바른 귀속을 보장하세요. 프레임워크는 일반적으로 LLM/도구 이벤트에 대한 저자를 올바르게 처리합니다.
    
    === "Python"
        `BaseAgent` 서브클래스에서 `yield Event(author=self.name, ...)`를 사용하세요.
    === "Java"
        사용자 지정 에이전트 로직에서 `이벤트`를 구성할 때 작성자를 설정하세요. 예: `Event.builder().author(this.getAgentName()) // ... .build();`

*   **의미 있는 내용 및 작업:** 핵심 메시지/데이터(텍스트, 함수 호출/응답)에는 `event.content`를 사용하세요. 부작용(상태/아티팩트 델타) 또는 제어 흐름(`transfer`, `escalate`, `skip_summarization`)을 알리는 데에는 `event.actions`를 구체적으로 사용하세요.
*   **멱등성 인식:** `SessionService`가 `event.actions`에서 신호된 상태/아티팩트 변경을 적용할 책임이 있음을 이해하세요. ADK 서비스는 일관성을 목표로 하지만, 애플리케이션 로직이 이벤트를 다시 처리할 경우 잠재적인 다운스트림 효과를 고려하세요.
*   **`is_final_response()` 사용:** 애플리케이션/UI 계층에서 이 헬퍼 메서드에 의존하여 완전하고 사용자 대면 텍스트 응답을 식별하세요. 수동으로 로직을 복제하지 마세요.
*   **기록 활용:** 세션의 이벤트 목록은 주요 디버깅 도구입니다. 실행을 추적하고 문제를 진단하기 위해 작성자, 내용 및 작업의 순서를 검토하세요.
*   **메타데이터 사용:** 단일 사용자 상호 작용 내의 모든 이벤트를 상호 연관시키려면 `invocation_id`를 사용하세요. 특정하고 고유한 발생을 참조하려면 `event.id`를 사용하세요.

이벤트를 내용과 작업에 대한 명확한 목적을 가진 구조화된 메시지로 취급하는 것이 ADK에서 복잡한 에이전트 동작을 구축, 디버깅 및 관리하는 핵심입니다.