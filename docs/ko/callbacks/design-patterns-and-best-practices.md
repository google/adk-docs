# 콜백을 위한 디자인 패턴 및 모범 사례

콜백은 에이전트 생명주기에 강력한 연결 고리를 제공합니다. 다음은 ADK에서 콜백을 효과적으로 활용하는 방법을 보여주는 일반적인 디자인 패턴과 구현을 위한 모범 사례입니다.

## 디자인 패턴

이러한 패턴들은 콜백을 사용하여 에이전트의 행동을 향상시키거나 제어하는 일반적인 방법을 보여줍니다:

### 1. 가드레일 및 정책 시행

*   **패턴:** LLM이나 도구에 도달하기 전에 요청을 가로채 규칙을 시행합니다.
*   **방법:** `before_model_callback`을 사용하여 `LlmRequest` 프롬프트를 검사하거나 `before_tool_callback`을 사용하여 도구 인수를 검사합니다. 정책 위반(예: 금지된 주제, 비속어)이 감지되면 미리 정의된 응답(`LlmResponse` 또는 `dict`/`Map`)을 반환하여 작업을 차단하고 선택적으로 `context.state`를 업데이트하여 위반을 기록합니다.
*   **예시:** `before_model_callback`은 `llm_request.contents`에서 민감한 키워드를 확인하고, 발견되면 LLM 호출을 방지하기 위해 표준 "이 요청을 처리할 수 없습니다" `LlmResponse`를 반환합니다.

### 2. 동적 상태 관리

*   **패턴:** 콜백 내에서 세션 상태를 읽고 써서 에이전트의 행동을 문맥 인식적으로 만들고 단계 간에 데이터를 전달합니다.
*   **방법:** `callback_context.state` 또는 `tool_context.state`에 접근합니다. 수정 사항(`state['key'] = value`)은 `SessionService`에 의한 지속성을 위해 후속 `Event.actions.state_delta`에서 자동으로 추적됩니다.
*   **예시:** `after_tool_callback`은 도구 결과에서 얻은 `transaction_id`를 `tool_context.state['last_transaction_id']`에 저장합니다. 나중에 `before_agent_callback`은 `state['user_tier']`를 읽어 에이전트의 인사를 맞춤화할 수 있습니다.

### 3. 로깅 및 모니터링

*   **패턴:** 관찰 가능성 및 디버깅을 위해 특정 생명주기 지점에 상세 로깅을 추가합니다.
*   **방법:** `before_agent_callback`, `after_tool_callback`, `after_model_callback`과 같은 콜백을 구현하여 에이전트 이름, 도구 이름, 호출 ID 및 컨텍스트나 인수의 관련 데이터를 포함하는 구조화된 로그를 출력하거나 보냅니다.
*   **예시:** `INFO: [Invocation: e-123] Before Tool: search_api - Args: {'query': 'ADK'}`와 같은 로그 메시지를 기록합니다.

### 4. 캐싱

*   **패턴:** 결과를 캐싱하여 중복된 LLM 호출이나 도구 실행을 방지합니다.
*   **방법:** `before_model_callback` 또는 `before_tool_callback`에서 요청/인수를 기반으로 캐시 키를 생성합니다. `context.state`(또는 외부 캐시)에서 이 키를 확인합니다. 발견되면 캐시된 `LlmResponse` 또는 결과를 직접 반환하여 실제 작업을 건너뜁니다. 찾지 못하면 작업을 진행하도록 허용하고 해당 `after_` 콜백(`after_model_callback`, `after_tool_callback`)을 사용하여 키를 사용하여 새 결과를 캐시에 저장합니다.
*   **예시:** `get_stock_price(symbol)`에 대한 `before_tool_callback`은 `state[f"cache:stock:{symbol}"]`을 확인합니다. 존재하면 캐시된 가격을 반환하고, 그렇지 않으면 API 호출을 허용하고 `after_tool_callback`이 결과를 상태 키에 저장합니다.

### 5. 요청/응답 수정

*   **패턴:** 데이터가 LLM/도구로 전송되기 직전이나 수신된 직후에 데이터를 변경합니다.
*   **방법:**
    *   `before_model_callback`: `llm_request`를 수정합니다 (예: `state`를 기반으로 시스템 지침 추가).
    *   `after_model_callback`: 반환된 `LlmResponse`를 수정합니다 (예: 텍스트 서식 지정, 콘텐츠 필터링).
    *   `before_tool_callback`: 도구 `args` 딕셔너리(또는 Java의 Map)를 수정합니다.
    *   `after_tool_callback`: `tool_response` 딕셔너리(또는 Java의 Map)를 수정합니다.
*   **예시:** `context.state['lang'] == 'es'`인 경우 `before_model_callback`이 `llm_request.config.system_instruction`에 "사용자 언어 선호도: 스페인어"를 추가합니다.

### 6. 조건부 단계 건너뛰기

*   **패턴:** 특정 조건에 따라 표준 작업(에이전트 실행, LLM 호출, 도구 실행)을 방지합니다.
*   **방법:** `before_` 콜백에서 값을 반환합니다(`before_agent_callback`에서 `Content`, `before_model_callback`에서 `LlmResponse`, `before_tool_callback`에서 `dict`). 프레임워크는 이 반환된 값을 해당 단계의 결과로 해석하여 정상적인 실행을 건너뜁니다.
*   **예시:** `before_tool_callback`은 `tool_context.state['api_quota_exceeded']`를 확인합니다. `True`이면 `{'error': 'API 할당량 초과'}`를 반환하여 실제 도구 함수가 실행되는 것을 방지합니다.

### 7. 도구별 작업 (인증 및 요약 제어)

*   **패턴:** 주로 인증 및 도구 결과의 LLM 요약 제어와 같은 도구 수명주기에 특정한 작업을 처리합니다.
*   **방법:** 도구 콜백(`before_tool_callback`, `after_tool_callback`) 내에서 `ToolContext`를 사용합니다.
    *   **인증:** `before_tool_callback`에서 자격 증명이 필요하지만 찾을 수 없는 경우(예: `tool_context.get_auth_response` 또는 상태 확인을 통해) `tool_context.request_credential(auth_config)`를 호출합니다. 이는 인증 흐름을 시작합니다.
    *   **요약:** 도구의 원시 사전 출력이 LLM으로 다시 전달되거나 잠재적으로 직접 표시되어야 하는 경우, 기본 LLM 요약 단계를 건너뛰려면 `tool_context.actions.skip_summarization = True`를 설정합니다.
*   **예시:** 보안 API에 대한 `before_tool_callback`은 상태에서 인증 토큰을 확인하고, 없으면 `request_credential`을 호출합니다. 구조화된 JSON을 반환하는 도구에 대한 `after_tool_callback`은 `skip_summarization = True`를 설정할 수 있습니다.

### 8. 아티팩트 처리

*   **패턴:** 에이전트 수명주기 동안 세션 관련 파일이나 대용량 데이터 블롭을 저장하거나 로드합니다.
*   **방법:** `callback_context.save_artifact` / `await tool_context.save_artifact`를 사용하여 데이터(예: 생성된 보고서, 로그, 중간 데이터)를 저장합니다. `load_artifact`를 사용하여 이전에 저장된 아티팩트를 검색합니다. 변경 사항은 `Event.actions.artifact_delta`를 통해 추적됩니다.
*   **예시:** "generate_report" 도구에 대한 `after_tool_callback`은 `await tool_context.save_artifact("report.pdf", report_part)`를 사용하여 출력 파일을 저장합니다. `before_agent_callback`은 `callback_context.load_artifact("agent_config.json")`을 사용하여 구성 아티팩트를 로드할 수 있습니다.

## 콜백 모범 사례

*   **집중 유지:** 각 콜백을 단일하고 잘 정의된 목적(예: 로깅만, 유효성 검사만)으로 설계하세요. 단일 책임 원칙을 따릅니다.
*   **성능 고려:** 콜백은 에이전트의 처리 루프 내에서 동기적으로 실행됩니다. 장기 실행 또는 차단 작업(네트워크 호출, 과도한 계산)을 피하세요. 필요한 경우 오프로드하되, 이로 인해 복잡성이 추가될 수 있음을 인지하세요.
*   **안정적인 오류 처리:** 콜백 함수 내에서 `try...except/catch` 블록을 사용하세요. 오류를 적절하게 로깅하고 에이전트 호출을 중지할지 또는 복구를 시도할지 결정하세요. 콜백 오류로 인해 전체 프로세스가 중단되지 않도록 하세요.
*   **상태를 신중하게 관리:**
    *   `context.state`에서 읽고 쓰는 것을 신중하게 하세요. 변경 사항은 *현재* 호출 내에서 즉시 표시되며 이벤트 처리 마지막에 지속됩니다.
    *   의도하지 않은 부작용을 피하기 위해 광범위한 구조를 수정하는 대신 특정 상태 키를 사용하세요.
    *   특히 영구 `SessionService` 구현에서는 명확성을 위해 상태 접두사(`State.APP_PREFIX`, `State.USER_PREFIX`, `State.TEMP_PREFIX`) 사용을 고려하세요.
*   **멱등성 고려:** 콜백이 외부 부작용이 있는 작업(예: 외부 카운터 증가)을 수행하는 경우, 프레임워크나 애플리케이션의 잠재적인 재시도를 처리하기 위해 가능하면 멱등성(동일한 입력으로 여러 번 실행해도 안전)을 갖도록 설계하세요.
*   **철저한 테스트:** 모의 컨텍스트 객체를 사용하여 콜백 함수를 단위 테스트하세요. 전체 에이전트 흐름 내에서 콜백이 올바르게 작동하는지 확인하기 위해 통합 테스트를 수행하세요.
*   **명확성 확보:** 콜백 함수에 설명적인 이름을 사용하세요. 목적, 실행 시점 및 부작용(특히 상태 수정)을 설명하는 명확한 docstring을 추가하세요.
*   **올바른 컨텍스트 유형 사용:** 항상 제공된 특정 컨텍스트 유형(`CallbackContext`는 에이전트/모델용, `ToolContext`는 도구용)을 사용하여 적절한 메서드와 속성에 접근할 수 있도록 하세요.

이러한 패턴과 모범 사례를 적용함으로써, ADK에서 콜백을 효과적으로 사용하여 더 견고하고, 관찰 가능하며, 맞춤화된 에이전트 행동을 만들 수 있습니다.