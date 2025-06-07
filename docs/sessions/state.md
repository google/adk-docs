# 상태: 세션의 스크래치패드

각 `세션`(우리의 대화 스레드) 내에서 **`상태(state)`** 속성은 해당 특정 상호작용을 위한 에이전트의 전용 스크래치패드 역할을 합니다. `session.events`가 전체 기록을 보유하는 반면, `session.state`는 에이전트가 대화 *중에* 필요한 동적 세부 정보를 저장하고 업데이트하는 곳입니다.

## `session.state`란 무엇인가요?

개념적으로, `session.state`는 키-값 쌍을 담고 있는 컬렉션(딕셔너리 또는 맵)입니다. 에이전트가 현재 대화를 효과적으로 만들기 위해 기억하거나 추적해야 하는 정보를 위해 설계되었습니다:

*   **상호작용 개인화:** 이전에 언급된 사용자 선호도 기억하기 (예: `'user_preference_theme': 'dark'`).
*   **작업 진행 상황 추적:** 다중 턴 프로세스의 단계를 추적하기 (예: `'booking_step': 'confirm_payment'`).
*   **정보 축적:** 목록이나 요약 만들기 (예: `'shopping_cart_items': ['book', 'pen']`).
*   **정보에 기반한 결정:** 다음 응답에 영향을 미치는 플래그나 값 저장하기 (예: `'user_is_authenticated': True`).

### `상태`의 주요 특징

1. **구조: 직렬화 가능한 키-값 쌍**

    *   데이터는 `키: 값`으로 저장됩니다.
    *   **키:** 항상 문자열(`str`)입니다. 명확한 이름을 사용하세요 (예: `'departure_city'`, `'user:language_preference'`).
    *   **값:** **직렬화 가능**해야 합니다. 즉, `SessionService`에 의해 쉽게 저장되고 로드될 수 있어야 합니다. 문자열, 숫자, 불리언과 같은 기본 유형과 이러한 기본 유형만 포함하는 간단한 리스트 또는 딕셔너리와 같은 특정 언어(Python/Java)의 기본 유형을 고수하세요. (자세한 내용은 API 문서를 참조하세요).
    *   **⚠️ 복잡한 객체 피하기:** **직렬화 불가능한 객체**(사용자 정의 클래스 인스턴스, 함수, 연결 등)를 상태에 직접 저장하지 마세요. 필요한 경우 간단한 식별자를 저장하고 다른 곳에서 복잡한 객체를 검색하세요.

2. **가변성: 변경됩니다**

    *   `상태`의 내용은 대화가 진행됨에 따라 변경될 것으로 예상됩니다.

3. **지속성: `SessionService`에 따라 다름**

    *   상태가 애플리케이션 재시작 후에도 유지되는지 여부는 선택한 서비스에 따라 다릅니다:
      * `InMemorySessionService`: **지속성 없음.** 재시작 시 상태가 손실됩니다.
      * `DatabaseSessionService` / `VertexAiSessionService`: **지속성 있음.** 상태가 안정적으로 저장됩니다.

!!! Note
    기본 요소의 특정 매개변수나 메서드 이름은 SDK 언어에 따라 약간 다를 수 있습니다(예: Python의 `session.state['current_intent'] = 'book_flight'`, Java의 `session.state().put("current_intent", "book_flight)`). 자세한 내용은 언어별 API 문서를 참조하세요.

### 접두사로 상태 구성하기: 범위가 중요합니다

상태 키의 접두사는 특히 영구 서비스를 사용할 때 범위와 지속성 동작을 정의합니다:

*   **접두사 없음 (세션 상태):**

    *   **범위:** *현재* 세션(`id`)에만 해당됩니다.
    *   **지속성:** `SessionService`가 영구적인 경우에만 지속됩니다(`Database`, `VertexAI`).
    *   **사용 사례:** 현재 작업 내 진행 상황 추적(예: `'current_booking_step'`), 이 상호작용을 위한 임시 플래그(예: `'needs_clarification'`).
    *   **예시:** `session.state['current_intent'] = 'book_flight'`

*   **`user:` 접두사 (사용자 상태):**

    *   **범위:** `user_id`에 연결되어 해당 사용자의 *모든* 세션에서 공유됩니다(동일한 `app_name` 내에서).
    *   **지속성:** `Database` 또는 `VertexAI`와 함께 사용하면 영구적입니다. (`InMemory`에 의해 저장되지만 재시작 시 손실됩니다).
    *   **사용 사례:** 사용자 선호도(예: `'user:theme'`), 프로필 세부 정보(예: `'user:name'`).
    *   **예시:** `session.state['user:preferred_language'] = 'fr'`

*   **`app:` 접두사 (앱 상태):**

    *   **범위:** `app_name`에 연결되어 해당 애플리케이션의 *모든* 사용자와 세션에서 공유됩니다.
    *   **지속성:** `Database` 또는 `VertexAI`와 함께 사용하면 영구적입니다. (`InMemory`에 의해 저장되지만 재시작 시 손실됩니다).
    *   **사용 사례:** 전역 설정(예: `'app:api_endpoint'`), 공유 템플릿.
    *   **예시:** `session.state['app:global_discount_code'] = 'SAVE10'`

*   **`temp:` 접두사 (임시 세션 상태):**

    *   **범위:** *현재* 세션 처리 턴에만 해당됩니다.
    *   **지속성:** **절대 영구적이지 않음.** 영구 서비스를 사용하더라도 폐기되는 것이 보장됩니다.
    *   **사용 사례:** 즉시 필요한 중간 결과, 명시적으로 저장하고 싶지 않은 데이터.
    *   **예시:** `session.state['temp:raw_api_response'] = {...}`

**에이전트가 보는 방식:** 에이전트 코드는 단일 `session.state` 컬렉션(dict/Map)을 통해 *결합된* 상태와 상호 작용합니다. `SessionService`는 접두사를 기반으로 올바른 기본 스토리지에서 상태를 가져오고 병합하는 것을 처리합니다.

### 상태 업데이트 방법: 권장 방법

상태는 **항상** `session_service.append_event()`를 사용하여 세션 기록에 `이벤트`를 추가하는 과정의 일부로 업데이트되어야 합니다. 이렇게 하면 변경 사항이 추적되고, 지속성이 올바르게 작동하며, 업데이트가 스레드로부터 안전하게 이루어집니다.

**1. 쉬운 방법: `output_key` (에이전트 텍스트 응답용)**

이것은 에이전트의 최종 텍스트 응답을 상태에 직접 저장하는 가장 간단한 방법입니다. `LlmAgent`를 정의할 때 `output_key`를 지정하세요:

=== "Python"

    ```py
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.runners import Runner
    from google.genai.types import Content, Part
    
    # output_key로 에이전트 정의
    greeting_agent = LlmAgent(
        name="Greeter",
        model="gemini-2.0-flash", # 유효한 모델 사용
        instruction="짧고 친근한 인사를 생성하세요.",
        output_key="last_greeting" # 응답을 state['last_greeting']에 저장
    )
    
    # --- Runner 및 세션 설정 ---
    app_name, user_id, session_id = "state_app", "user1", "session1"
    session_service = InMemorySessionService()
    runner = Runner(
        agent=greeting_agent,
        app_name=app_name,
        session_service=session_service
    )
    session = await session_service.create_session(app_name=app_name, 
                                        user_id=user_id, 
                                        session_id=session_id)
    print(f"초기 상태: {session.state}")
    
    # --- 에이전트 실행 ---
    # Runner는 append_event를 호출하며, 이는 output_key를 사용하여
    # 자동으로 state_delta를 생성합니다.
    user_message = Content(parts=[Part(text="Hello")])
    for event in runner.run(user_id=user_id, 
                            session_id=session_id, 
                            new_message=user_message):
        if event.is_final_response():
          print(f"에이전트가 응답했습니다.") # 응답 텍스트도 event.content에 있음
    
    # --- 업데이트된 상태 확인 ---
    updated_session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    print(f"에이전트 실행 후 상태: {updated_session.state}")
    # 예상 출력에는 다음이 포함될 수 있습니다: {'last_greeting': '안녕하세요! 오늘 무엇을 도와드릴까요?'}
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/state/GreetingAgentExample.java:full_code"
    ```

내부적으로 `Runner`는 `output_key`를 사용하여 `state_delta`가 포함된 필요한 `EventActions`를 생성하고 `append_event`를 호출합니다.

**2. 표준 방법: `EventActions.state_delta` (복잡한 업데이트용)**

더 복잡한 시나리오(여러 키 업데이트, 문자열이 아닌 값, `user:` 또는 `app:`과 같은 특정 범위 또는 에이전트의 최종 텍스트와 직접 관련 없는 업데이트)의 경우, `EventActions` 내에서 `state_delta`를 수동으로 구성합니다.

=== "Python"

    ```py
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.events import Event, EventActions
    from google.genai.types import Part, Content
    import time

    # --- 설정 ---
    session_service = InMemorySessionService()
    app_name, user_id, session_id = "state_app_manual", "user2", "session2"
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state={"user:login_count": 0, "task_status": "idle"}
    )
    print(f"초기 상태: {session.state}")

    # --- 상태 변경 정의 ---
    current_time = time.time()
    state_changes = {
        "task_status": "active",              # 세션 상태 업데이트
        "user:login_count": session.state.get("user:login_count", 0) + 1, # 사용자 상태 업데이트
        "user:last_login_ts": current_time,   # 사용자 상태 추가
        "temp:validation_needed": True        # 임시 상태 추가 (폐기됨)
    }

    # --- 작업과 함께 이벤트 생성 ---
    actions_with_update = EventActions(state_delta=state_changes)
    # 이 이벤트는 에이전트 응답뿐만 아니라 내부 시스템 작업을 나타낼 수 있음
    system_event = Event(
        invocation_id="inv_login_update",
        author="system", # 또는 'agent', 'tool' 등
        actions=actions_with_update,
        timestamp=current_time
        # 내용은 None이거나 수행된 작업을 나타낼 수 있음
    )

    # --- 이벤트 추가 (이것이 상태를 업데이트함) ---
    await session_service.append_event(session, system_event)
    print("명시적인 state_delta와 함께 `append_event` 호출됨.")

    # --- 업데이트된 상태 확인 ---
    updated_session = await session_service.get_session(app_name=app_name,
                                                user_id=user_id, 
                                                session_id=session_id)
    print(f"이벤트 후 상태: {updated_session.state}")
    # 예상: {'user:login_count': 1, 'task_status': 'active', 'user:last_login_ts': <timestamp>}
    # 참고: 'temp:validation_needed'는 존재하지 않음.
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/state/ManualStateUpdateExample.java:full_code"
    ```

**3. `CallbackContext` 또는 `ToolContext`를 통해 (콜백 및 도구에 권장)**

에이전트 콜백(예: `on_before_agent_call`, `on_after_agent_call`) 또는 도구 함수 내에서 상태를 수정하는 것은 함수에 제공된 `CallbackContext` 또는 `ToolContext`의 `state` 속성을 사용하는 것이 가장 좋습니다.

*   `callback_context.state['my_key'] = my_value`
*   `tool_context.state['my_key'] = my_value`

이러한 컨텍스트 객체는 각각의 실행 범위 내에서 상태 변경을 관리하도록 특별히 설계되었습니다. `context.state`를 수정하면 ADK 프레임워크는 이러한 변경 사항이 자동으로 캡처되어 콜백 또는 도구에 의해 생성되는 이벤트의 `EventActions.state_delta`로 올바르게 라우팅되도록 합니다. 이 델타는 이벤트가 추가될 때 `SessionService`에 의해 처리되어 적절한 지속성과 추적을 보장합니다.

이 방법은 콜백 및 도구 내의 대부분의 일반적인 상태 업데이트 시나리오에 대해 `EventActions` 및 `state_delta`의 수동 생성을 추상화하여 코드를 더 깔끔하고 오류 발생 가능성이 적게 만듭니다.

컨텍스트 객체에 대한 포괄적인 세부 정보는 [컨텍스트 문서](docs/context/index.md)를 참조하세요.

=== "Python"

    ```python
    # 에이전트 콜백 또는 도구 함수에서
    from google.adk.agents import CallbackContext # 또는 ToolContext

    def my_callback_or_tool_function(context: CallbackContext, # 또는 ToolContext
                                     # ... 다른 매개변수 ...
                                    ):
        # 기존 상태 업데이트
        count = context.state.get("user_action_count", 0)
        context.state["user_action_count"] = count + 1

        # 새 상태 추가
        context.state["temp:last_operation_status"] = "success"

        # 상태 변경은 자동으로 이벤트의 state_delta의 일부가 됨
        # ... 나머지 콜백/도구 로직 ...
    ```

=== "Java"

    ```java
    // 에이전트 콜백 또는 도구 메서드에서
    import com.google.adk.agents.CallbackContext; // 또는 ToolContext
    // ... 다른 가져오기 ...

    public class MyAgentCallbacks {
        public void onAfterAgent(CallbackContext callbackContext) {
            // 기존 상태 업데이트
            Integer count = (Integer) callbackContext.state().getOrDefault("user_action_count", 0);
            callbackContext.state().put("user_action_count", count + 1);

            // 새 상태 추가
            callbackContext.state().put("temp:last_operation_status", "success");

            // 상태 변경은 자동으로 이벤트의 state_delta의 일부가 됨
            // ... 나머지 콜백 로직 ...
        }
    }
    ```

**`append_event`의 역할:**

* `이벤트`를 `session.events`에 추가합니다.
* 이벤트의 `actions`에서 `state_delta`를 읽습니다.
* 서비스 유형에 따라 접두사와 지속성을 올바르게 처리하면서 `SessionService`가 관리하는 상태에 이러한 변경 사항을 적용합니다.
* 세션의 `last_update_time`을 업데이트합니다.
* 동시 업데이트에 대한 스레드 안전성을 보장합니다.

### ⚠️ 직접적인 상태 수정에 대한 경고

`SessionService`에서 직접 얻은 `세션` 객체(예: `session_service.get_session()` 또는 `session_service.create_session()`을 통해)의 `session.state` 컬렉션(딕셔너리/맵)을 에이전트 호출의 관리된 수명 주기 외부에서(즉, `CallbackContext` 또는 `ToolContext`를 통하지 않고) 직접 수정하는 것을 피하세요. 예를 들어, `retrieved_session = await session_service.get_session(...); retrieved_session.state['key'] = value`와 같은 코드는 문제가 있습니다.

`CallbackContext.state` 또는 `ToolContext.state`를 사용하는 콜백 또는 도구 내의 상태 수정은 이러한 컨텍스트 객체가 이벤트 시스템과의 필요한 통합을 처리하므로 변경 사항이 추적되도록 보장하는 올바른 방법입니다.

**직접적인 수정(컨텍스트 외부)이 강력히 권장되지 않는 이유:**

1. **이벤트 기록 우회:** 변경 사항이 `이벤트`로 기록되지 않아 감사 가능성이 손실됩니다.
2. **지속성 파괴:** 이러한 방식으로 이루어진 변경 사항은 `DatabaseSessionService` 또는 `VertexAiSessionService`에 의해 **저장되지 않을 가능성이 높습니다**. 이들은 저장을 트리거하기 위해 `append_event`에 의존합니다.
3. **스레드로부터 안전하지 않음:** 경쟁 조건 및 업데이트 손실로 이어질 수 있습니다.
4. **타임스탬프/로직 무시:** `last_update_time`을 업데이트하거나 관련 이벤트 로직을 트리거하지 않습니다.

**권장 사항:** `output_key`, `EventActions.state_delta`(이벤트를 수동으로 생성할 때)를 통해 상태를 업데이트하거나, 각각의 범위 내에 있을 때 `CallbackContext` 또는 `ToolContext` 객체의 `state` 속성을 수정하는 방법을 고수하세요. 이러한 방법은 안정적이고, 추적 가능하며, 영구적인 상태 관리를 보장합니다. `session.state`(`SessionService`에서 검색한 세션에서)에 대한 직접적인 접근은 상태를 *읽기* 위해서만 사용하세요.

### 상태 설계 모범 사례 요약

*   **최소주의:** 필수적이고 동적인 데이터만 저장하세요.
*   **직렬화:** 기본적이고 직렬화 가능한 유형을 사용하세요.
*   **설명적인 키 및 접두사:** 명확한 이름과 적절한 접두사(`user:`, `app:`, `temp:` 또는 없음)를 사용하세요.
*   **얕은 구조:** 가능한 경우 깊은 중첩을 피하세요.
*   **표준 업데이트 흐름:** `append_event`에 의존하세요.