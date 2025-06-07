# 컨텍스트 (Context)

## 컨텍스트란 무엇인가요?

Agent Development Kit(ADK)에서 "컨텍스트"는 특정 작업 중에 에이전트와 그 도구들이 사용할 수 있는 중요한 정보 묶음을 의미합니다. 현재의 작업이나 대화 차례를 효과적으로 처리하는 데 필요한 배경 지식과 리소스라고 생각하면 됩니다.

에이전트가 잘 작동하려면 종종 최신 사용자 메시지 이상의 것이 필요합니다. 컨텍스트는 다음을 가능하게 하므로 필수적입니다:

1.  **상태 유지:** 대화의 여러 단계에 걸쳐 세부 정보를 기억합니다 (예: 사용자 선호도, 이전 계산, 장바구니 항목). 이는 주로 **세션 상태**를 통해 관리됩니다.
2.  **데이터 전달:** 한 단계(LLM 호출 또는 도구 실행 등)에서 발견되거나 생성된 정보를 후속 단계와 공유합니다. 여기서도 세션 상태가 핵심입니다.
3.  **서비스 접근:** 다음과 같은 프레임워크 기능과 상호작용합니다:
    *   **아티팩트 저장소:** 세션과 관련된 파일이나 데이터 블롭(PDF, 이미지, 구성 파일 등)을 저장하거나 로드합니다.
    *   **메모리:** 사용자와 연결된 과거 상호작용이나 외부 지식 소스에서 관련 정보를 검색합니다.
    *   **인증:** 도구가 외부 API에 안전하게 접근하는 데 필요한 자격 증명을 요청하고 검색합니다.
4.  **신원 및 추적:** 현재 어떤 에이전트가 실행 중인지(`agent.name`) 알고, 로깅 및 디버깅을 위해 현재 요청-응답 주기(`invocation_id`)를 고유하게 식별합니다.
5.  **도구별 작업:** 인증 요청이나 메모리 검색과 같이 현재 상호작용의 세부 정보에 접근해야 하는 도구 내 특수 작업을 활성화합니다.


이 모든 정보를 단일의 완전한 사용자-요청-최종-응답 주기(**호출(invocation)**)를 위해 함께 담고 있는 중심적인 부분은 `InvocationContext`입니다. 그러나 일반적으로 이 객체를 직접 생성하거나 관리하지는 않습니다. ADK 프레임워크는 호출이 시작될 때(예: `runner.run_async`를 통해) 이를 생성하고, 관련 컨텍스트 정보를 에이전트 코드, 콜백, 도구에 암묵적으로 전달합니다.

=== "Python"

    ```python
    # 개념적 의사 코드: 프레임워크가 컨텍스트를 제공하는 방법 (내부 로직)
    
    # runner = Runner(agent=my_root_agent, session_service=..., artifact_service=...)
    # user_message = types.Content(...)
    # session = session_service.get_session(...) # 또는 새로 생성
    
    # --- runner.run_async(...) 내부 ---
    # 1. 프레임워크는 이 특정 실행을 위한 메인 컨텍스트를 생성합니다
    # invocation_context = InvocationContext(
    #     invocation_id="this-run의-고유-id",
    #     session=session,
    #     user_content=user_message,
    #     agent=my_root_agent, # 시작 에이전트
    #     session_service=session_service,
    #     artifact_service=artifact_service,
    #     memory_service=memory_service,
    #     # ... 기타 필요한 필드 ...
    # )
    #
    # 2. 프레임워크는 에이전트의 실행 메서드를 호출하며, 컨텍스트를 암묵적으로 전달합니다
    #    (에이전트의 메서드 시그니처가 이를 받게 됩니다, 예: runAsyncImpl(InvocationContext invocationContext))
    # await my_root_agent.run_async(invocation_context)
    #   --- 내부 로직 끝 ---
    #
    # 개발자로서, 여러분은 메서드 인수로 제공된 컨텍스트 객체로 작업합니다.
    ```

=== "Java"

    ```java
    /* 개념적 의사 코드: 프레임워크가 컨텍스트를 제공하는 방법 (내부 로직) */
    InMemoryRunner runner = new InMemoryRunner(agent);
    Session session = runner
        .sessionService()
        .createSession(runner.appName(), USER_ID, initialState, SESSION_ID )
        .blockingGet();

    try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
      while (true) {
        System.out.print("\nYou > ");
      }
      String userInput = scanner.nextLine();
      if ("quit".equalsIgnoreCase(userInput)) {
        break;
      }
      Content userMsg = Content.fromParts(Part.fromText(userInput));
      Flowable<Event> events = runner.runAsync(session.userId(), session.id(), userMsg);
      System.out.print("\nAgent > ");
      events.blockingForEach(event -> System.out.print(event.stringifyContent()));
    }
    ```

## 다양한 종류의 컨텍스트

`InvocationContext`가 포괄적인 내부 컨테이너 역할을 하는 동안, ADK는 특정 상황에 맞춰진 전문화된 컨텍스트 객체를 제공합니다. 이를 통해 내부 컨텍스트의 모든 복잡성을 다룰 필요 없이 당면한 작업에 적합한 도구와 권한을 가질 수 있습니다. 여러분이 마주하게 될 다양한 "종류"는 다음과 같습니다:

1.  **`InvocationContext`**
    *   **사용처:** 에이전트의 핵심 구현 메서드(`_run_async_impl`, `_run_live_impl`) 내에서 `ctx` 인수로 직접 수신됩니다.
    *   **목적:** 현재 호출의 *전체* 상태에 대한 접근을 제공합니다. 이것이 가장 포괄적인 컨텍스트 객체입니다.
    *   **주요 내용:** `session`( `state` 및 `events` 포함), 현재 `agent` 인스턴스, `invocation_id`, 초기 `user_content`, 구성된 서비스(`artifact_service`, `memory_service`, `session_service`)에 대한 참조, 그리고 라이브/스트리밍 모드와 관련된 필드에 직접 접근할 수 있습니다.
    *   **사용 사례:** 주로 에이전트의 핵심 로직이 전체 세션이나 서비스에 직접 접근해야 할 때 사용되지만, 종종 상태 및 아티팩트 상호작용은 자체 컨텍스트를 사용하는 콜백/도구에 위임됩니다. 또한 호출 자체를 제어하는 데 사용됩니다(예: `ctx.end_invocation = True` 설정).

    === "Python"
    
        ```python
        # 의사 코드: InvocationContext를 수신하는 에이전트 구현
        from google.adk.agents import BaseAgent
        from google.adk.agents.invocation_context import InvocationContext
        from google.adk.events import Event
        from typing import AsyncGenerator
    
        class MyAgent(BaseAgent):
            async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
                # 직접 접근 예제
                agent_name = ctx.agent.name
                session_id = ctx.session.id
                print(f"에이전트 {agent_name}가 세션 {session_id}에서 호출 {ctx.invocation_id}에 대해 실행 중")
                # ... ctx를 사용하는 에이전트 로직 ...
                yield # ... 이벤트 ...
        ```
    
    === "Java"
    
        ```java
        // 의사 코드: InvocationContext를 수신하는 에이전트 구현
        import com.google.adk.agents.BaseAgent;
        import com.google.adk.agents.InvocationContext;
        
            LlmAgent root_agent =
                LlmAgent.builder()
                    .model("gemini-***")
                    .name("sample_agent")
                    .description("사용자 질문에 답변합니다.")
                    .instruction(
                        """
                        여기에 에이전트에 대한 지침을 제공하세요.
                        """
                    )
                    .tools(sampleTool)
                    .outputKey("YOUR_KEY")
                    .build();
    
            ConcurrentMap<String, Object> initialState = new ConcurrentHashMap<>();
            initialState.put("YOUR_KEY", "");
          
            InMemoryRunner runner = new InMemoryRunner(agent);
            Session session =
                  runner
                      .sessionService()
                      .createSession(runner.appName(), USER_ID, initialState, SESSION_ID )
                      .blockingGet();
    
           try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
                while (true) {
                  System.out.print("\nYou > ");
                  String userInput = scanner.nextLine();
        
                  if ("quit".equalsIgnoreCase(userInput)) {
                    break;
                  }
                  
                  Content userMsg = Content.fromParts(Part.fromText(userInput));
                  Flowable<Event> events = 
                          runner.runAsync(session.userId(), session.id(), userMsg);
        
                  System.out.print("\nAgent > ");
                  events.blockingForEach(event -> 
                          System.out.print(event.stringifyContent()));
              }
        
            protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
                // 직접 접근 예제
                String agentName = invocationContext.agent.name
                String sessionId = invocationContext.session.id
                String invocationId = invocationContext.invocationId
                System.out.println("에이전트 " + agent_name + "가 세션 " + session_id + "에서 호출 " + invocationId + "에 대해 실행 중")
                // ... ctx를 사용하는 에이전트 로직 ...
            }
        ```

2.  **`ReadonlyContext`**
    *   **사용처:** 기본 정보에 대한 읽기 접근만 필요하고 변경이 허용되지 않는 시나리오에서 제공됩니다 (예: `InstructionProvider` 함수). 또한 다른 컨텍스트의 기본 클래스이기도 합니다.
    *   **목적:** 기본적인 컨텍스트 세부 정보에 대한 안전한 읽기 전용 뷰를 제공합니다.
    *   **주요 내용:** `invocation_id`, `agent_name`, 그리고 현재 `state`의 읽기 전용 *뷰*.

    === "Python"
    
        ```python
        # 의사 코드: ReadonlyContext를 수신하는 지침 제공자
        from google.adk.agents import ReadonlyContext
    
        def my_instruction_provider(context: ReadonlyContext) -> str:
            # 읽기 전용 접근 예제
            user_tier = context.state().get("user_tier", "standard") # 상태를 읽을 수 있음
            # context.state['new_key'] = 'value' # 이것은 일반적으로 오류를 발생시키거나 효과가 없음
            return f"{user_tier} 사용자에 대한 요청을 처리하세요."
        ```
    
    === "Java"
    
        ```java
        // 의사 코드: ReadonlyContext를 수신하는 지침 제공자
        import com.google.adk.agents.ReadonlyContext;
    
        public String myInstructionProvider(ReadonlyContext context){
            // 읽기 전용 접근 예제
            String userTier = context.state().get("user_tier", "standard");
            context.state().put('new_key', 'value'); //이것은 일반적으로 오류를 발생시킴
            return "Process the request for a " + userTier + " user."
        }
        ```
    
3.  **`CallbackContext`**
    *   **사용처:** 에이전트 생명주기 콜백(`before_agent_callback`, `after_agent_callback`) 및 모델 상호작용 콜백(`before_model_callback`, `after_model_callback`)에 `callback_context`로 전달됩니다.
    *   **목적:** *콜백 내에서 구체적으로* 상태를 검사하고 수정하며, 아티팩트와 상호작용하고, 호출 세부 정보에 접근하는 것을 용이하게 합니다.
    *   **주요 기능 (`ReadonlyContext`에 추가됨):**
        *   **변경 가능한 `state` 속성:** 세션 상태를 읽고 *쓸 수* 있습니다. 여기서 이루어진 변경 사항(`callback_context.state['key'] = value`)은 콜백 후 프레임워크가 생성한 이벤트와 연결되어 추적됩니다.
        *   **아티팩트 메서드:** 구성된 `artifact_service`와 상호작용하기 위한 `load_artifact(filename)` 및 `save_artifact(filename, part)` 메서드.
        *   직접적인 `user_content` 접근.

    === "Python"
    
        ```python
        # 의사 코드: CallbackContext를 수신하는 콜백
        from google.adk.agents.callback_context import CallbackContext
        from google.adk.models import LlmRequest
        from google.genai import types
        from typing import Optional
    
        def my_before_model_cb(callback_context: CallbackContext, request: LlmRequest) -> Optional[types.Content]:
            # 상태 읽기/쓰기 예제
            call_count = callback_context.state.get("model_calls", 0)
            callback_context.state["model_calls"] = call_count + 1 # 상태 수정
    
            # 선택적으로 아티팩트 로드
            # config_part = callback_context.load_artifact("model_config.json")
            print(f"호출 {callback_context.invocation_id}에 대한 모델 호출 #{call_count + 1} 준비 중")
            return None # 모델 호출 진행 허용
        ```
    
    === "Java"
    
        ```java
        // 의사 코드: CallbackContext를 수신하는 콜백
        import com.google.adk.agents.CallbackContext;
        import com.google.adk.models.LlmRequest;
        import com.google.genai.types.Content;
        import java.util.Optional;
    
        public Maybe<LlmResponse> myBeforeModelCb(CallbackContext callbackContext, LlmRequest request){
            // 상태 읽기/쓰기 예제
            callCount = callbackContext.state().get("model_calls", 0)
            callbackContext.state().put("model_calls") = callCount + 1 # 상태 수정
    
            // 선택적으로 아티팩트 로드
            // Maybe<Part> configPart = callbackContext.loadArtifact("model_config.json");
            System.out.println("Preparing model call " + callCount + 1);
            return Maybe.empty(); // 모델 호출 진행 허용
        }
        ```

4.  **`ToolContext`**
    *   **사용처:** `FunctionTool`의 백업 함수와 도구 실행 콜백(`before_tool_callback`, `after_tool_callback`)에 `tool_context`로 전달됩니다.
    *   **목적:** `CallbackContext`가 제공하는 모든 것과 더불어, 인증 처리, 메모리 검색, 아티팩트 목록 보기와 같은 도구 실행에 필수적인 특수 메서드를 제공합니다.
    *   **주요 기능 (`CallbackContext`에 추가됨):**
        *   **인증 메서드:** 인증 흐름을 트리거하기 위한 `request_credential(auth_config)` 및 사용자/시스템이 제공한 자격 증명을 검색하기 위한 `get_auth_response(auth_config)`.
        *   **아티팩트 목록 보기:** 세션에서 사용 가능한 아티팩트를 찾기 위한 `list_artifacts()`.
        *   **메모리 검색:** 구성된 `memory_service`를 쿼리하기 위한 `search_memory(query)`.
        *   **`function_call_id` 속성:** 이 도구 실행을 트리거한 LLM의 특정 함수 호출을 식별하여 인증 요청이나 응답을 올바르게 다시 연결하는 데 중요합니다.
        *   **`actions` 속성:** 이 단계의 `EventActions` 객체에 직접 접근하여 도구가 상태 변경, 인증 요청 등을 신호로 보낼 수 있도록 합니다.

    === "Python"
    
        ```python
        # 의사 코드: ToolContext를 수신하는 도구 함수
        from google.adk.tools import ToolContext
        from typing import Dict, Any
    
        # 이 함수가 FunctionTool에 의해 래핑되었다고 가정
        def search_external_api(query: str, tool_context: ToolContext) -> Dict[str, Any]:
            api_key = tool_context.state.get("api_key")
            if not api_key:
                # 필요한 인증 구성 정의
                # auth_config = AuthConfig(...)
                # tool_context.request_credential(auth_config) # 자격 증명 요청
                # 'actions' 속성을 사용하여 인증 요청이 이루어졌음을 신호로 보냄
                # tool_context.actions.requested_auth_configs[tool_context.function_call_id] = auth_config
                return {"status": "인증 필요"}
    
            # API 키 사용...
            print(f"API 키를 사용하여 쿼리 '{query}'에 대한 도구 실행 중. 호출: {tool_context.invocation_id}")
    
            # 선택적으로 메모리 검색 또는 아티팩트 목록 보기
            # relevant_docs = tool_context.search_memory(f"{query} 관련 정보")
            # available_files = tool_context.list_artifacts()
    
            return {"result": f"{query}에 대한 데이터 가져옴."}
        ```
    
    === "Java"
    
        ```java
        // 의사 코드: ToolContext를 수신하는 도구 함수
        import com.google.adk.tools.ToolContext;
        import java.util.HashMap;
        import java.util.Map;
    
        // 이 함수가 FunctionTool에 의해 래핑되었다고 가정
        public Map<String, Object> searchExternalApi(String query, ToolContext toolContext){
            String apiKey = toolContext.state.get("api_key");
            if(apiKey.isEmpty()){
                // 필요한 인증 구성 정의
                // authConfig = AuthConfig(...);
                // toolContext.requestCredential(authConfig); # 자격 증명 요청
                // 'actions' 속성을 사용하여 인증 요청이 이루어졌음을 신호로 보냄
                ...
                return Map.of("status", "인증 필요");
    
            // API 키 사용...
            System.out.println("API 키를 사용하여 쿼리 " + query + "에 대한 도구 실행 중. ");
    
            // 선택적으로 아티팩트 목록 보기
            // Single<List<String>> availableFiles = toolContext.listArtifacts();
    
            return Map.of("result", "Data for " + query + " fetched");
        }
        ```

이러한 다양한 컨텍스트 객체와 언제 사용해야 하는지 이해하는 것은 ADK 애플리케이션의 상태를 효과적으로 관리하고, 서비스에 접근하며, 흐름을 제어하는 데 핵심입니다. 다음 섹션에서는 이러한 컨텍스트를 사용하여 수행할 수 있는 일반적인 작업에 대해 자세히 설명합니다.


## 컨텍스트를 사용한 일반적인 작업

이제 다양한 컨텍스트 객체를 이해했으니, 에이전트와 도구를 만들 때 이를 사용하여 일반적인 작업을 수행하는 방법에 초점을 맞춰 보겠습니다.

### 정보 접근하기

컨텍스트 내에 저장된 정보를 자주 읽어야 합니다.

*   **세션 상태 읽기:** 이전 단계에서 저장된 데이터나 사용자/앱 수준 설정에 접근합니다. `state` 속성에서 사전과 유사한 접근 방식을 사용합니다.

    === "Python"
    
        ```python
        # 의사 코드: 도구 함수 내
        from google.adk.tools import ToolContext
    
        def my_tool(tool_context: ToolContext, **kwargs):
            user_pref = tool_context.state.get("user_display_preference", "default_mode")
            api_endpoint = tool_context.state.get("app:api_endpoint") # 앱 수준 상태 읽기
    
            if user_pref == "dark_mode":
                # ... 다크 모드 로직 적용 ...
                pass
            print(f"API 엔드포인트 사용: {api_endpoint}")
            # ... 나머지 도구 로직 ...
    
        # 의사 코드: 콜백 함수 내
        from google.adk.agents.callback_context import CallbackContext
    
        def my_callback(callback_context: CallbackContext, **kwargs):
            last_tool_result = callback_context.state.get("temp:last_api_result") # 임시 상태 읽기
            if last_tool_result:
                print(f"마지막 도구에서 임시 결과 발견: {last_tool_result}")
            # ... 콜백 로직 ...
        ```
    
    === "Java"
    
        ```java
        // 의사 코드: 도구 함수 내
        import com.google.adk.tools.ToolContext;
    
        public void myTool(ToolContext toolContext){
           String userPref = toolContext.state().get("user_display_preference");
           String apiEndpoint = toolContext.state().get("app:api_endpoint"); // 앱 수준 상태 읽기
           if(userPref.equals("dark_mode")){
                // ... 다크 모드 로직 적용 ...
                pass
            }
           System.out.println("API 엔드포인트 사용: " + api_endpoint);
           // ... 나머지 도구 로직 ...
        }
    
    
        // 의사 코드: 콜백 함수 내
        import com.google.adk.agents.CallbackContext;
    
            public void myCallback(CallbackContext callbackContext){
                String lastToolResult = (String) callbackContext.state().get("temp:last_api_result"); // 임시 상태 읽기
            }
            if(!(lastToolResult.isEmpty())){
                System.out.println("마지막 도구에서 임시 결과 발견: " + lastToolResult);
            }
            // ... 콜백 로직 ...
        ```

*   **현재 식별자 가져오기:** 로깅이나 현재 작업을 기반으로 한 사용자 지정 로직에 유용합니다.

    === "Python"
    
        ```python
        # 의사 코드: 모든 컨텍스트 내 (ToolContext 예시)
        from google.adk.tools import ToolContext
    
        def log_tool_usage(tool_context: ToolContext, **kwargs):
            agent_name = tool_context.agent_name
            inv_id = tool_context.invocation_id
            func_call_id = getattr(tool_context, 'function_call_id', 'N/A') # ToolContext에만 해당
    
            print(f"로그: 호출={inv_id}, 에이전트={agent_name}, 함수호출ID={func_call_id} - 도구 실행됨.")
        ```    
    === "Java"
    
        ```java
        // 의사 코드: 모든 컨텍스트 내 (ToolContext 예시)
         import com.google.adk.tools.ToolContext;
    
         public void logToolUsage(ToolContext toolContext){
                    String agentName = toolContext.agentName;
                    String invId = toolContext.invocationId;
                    String functionCallId = toolContext.functionCallId().get(); // ToolContext에만 해당
                    System.out.println("로그: 호출= " + invId + " 에이전트= " + agentName);
                }
        ```

*   **초기 사용자 입력 접근:** 현재 호출을 시작한 메시지를 다시 참조합니다.

    === "Python"
    
        ```python
        # 의사 코드: 콜백 내
        from google.adk.agents.callback_context import CallbackContext
    
        def check_initial_intent(callback_context: CallbackContext, **kwargs):
            initial_text = "N/A"
            if callback_context.user_content and callback_context.user_content.parts:
                initial_text = callback_context.user_content.parts[0].text or "텍스트 아닌 입력"
    
            print(f"이 호출은 다음 사용자 입력으로 시작되었습니다: '{initial_text}'")
    
        # 의사 코드: 에이전트의 _run_async_impl 내
        # async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        #     if ctx.user_content and ctx.user_content.parts:
        #         initial_text = ctx.user_content.parts[0].text
        #         print(f"초기 쿼리를 기억하는 에이전트 로직: {initial_text}")
        #     ...
        ```
    
    === "Java"
    
        ```java
        // 의사 코드: 콜백 내
        import com.google.adk.agents.CallbackContext;
    
        public void checkInitialIntent(CallbackContext callbackContext){
            String initialText = "N/A";
            if((!(callbackContext.userContent().isEmpty())) && (!(callbackContext.userContent().parts.isEmpty()))){
                initialText = cbx.userContent().get().parts().get().get(0).text().get();
                ...
                System.out.println("이 호출은 다음 사용자 입력으로 시작되었습니다: " + initialText);
            }
        }
        ```
    
### 세션 상태 관리

상태는 메모리와 데이터 흐름에 매우 중요합니다. `CallbackContext` 또는 `ToolContext`를 사용하여 상태를 수정하면 변경 사항이 자동으로 추적되고 프레임워크에 의해 지속됩니다.

*   **작동 방식:** `callback_context.state['my_key'] = my_value` 또는 `tool_context.state['my_key'] = my_value`에 쓰는 것은 현재 단계의 이벤트와 관련된 `EventActions.state_delta`에 이 변경 사항을 추가합니다. 그런 다음 `SessionService`는 이벤트를 지속할 때 이러한 델타를 적용합니다.
*   **도구 간 데이터 전달:**

    === "Python"
    
        ```python
        # 의사 코드: 도구 1 - 사용자 ID 가져오기
        from google.adk.tools import ToolContext
        import uuid
    
        def get_user_profile(tool_context: ToolContext) -> dict:
            user_id = str(uuid.uuid4()) # ID 가져오기 시뮬레이션
            # 다음 도구를 위해 상태에 ID 저장
            tool_context.state["temp:current_user_id"] = user_id
            return {"profile_status": "ID 생성됨"}
    
        # 의사 코드: 도구 2 - 상태에서 사용자 ID 사용
        def get_user_orders(tool_context: ToolContext) -> dict:
            user_id = tool_context.state.get("temp:current_user_id")
            if not user_id:
                return {"error": "상태에서 사용자 ID를 찾을 수 없음"}
    
            print(f"사용자 ID로 주문 가져오기: {user_id}")
            # ... user_id를 사용하여 주문을 가져오는 로직 ...
            return {"orders": ["order123", "order456"]}
        ```
    
    === "Java"
    
        ```java
        // 의사 코드: 도구 1 - 사용자 ID 가져오기
        import com.google.adk.tools.ToolContext;
        import java.util.UUID;
    
        public Map<String, String> getUserProfile(ToolContext toolContext){
            String userId = UUID.randomUUID().toString();
            // 다음 도구를 위해 상태에 ID 저장
            toolContext.state().put("temp:current_user_id", user_id);
            return Map.of("profile_status", "ID 생성됨");
        }
    
        // 의사 코드: 도구 2 - 상태에서 사용자 ID 사용
        public  Map<String, String> getUserOrders(ToolContext toolContext){
            String userId = toolContext.state().get("temp:current_user_id");
            if(userId.isEmpty()){
                return Map.of("error", "상태에서 사용자 ID를 찾을 수 없음");
            }
            System.out.println("사용자 ID로 주문 가져오기: " + userId);
             // ... user_id를 사용하여 주문을 가져오는 로직 ...
            return Map.of("orders", "order123");
        }
        ```

*   **사용자 선호도 업데이트:**

    === "Python"
    
        ```python
        # 의사 코드: 도구 또는 콜백이 선호도를 식별
        from google.adk.tools import ToolContext # 또는 CallbackContext
    
        def set_user_preference(tool_context: ToolContext, preference: str, value: str) -> dict:
            # 사용자 수준 상태를 위해 'user:' 접두사 사용 (영구 SessionService 사용 시)
            state_key = f"user:{preference}"
            tool_context.state[state_key] = value
            print(f"사용자 선호도 '{preference}'를 '{value}'로 설정")
            return {"status": "선호도 업데이트됨"}
        ```
    
    === "Java"
    
        ```java
        // 의사 코드: 도구 또는 콜백이 선호도를 식별
        import com.google.adk.tools.ToolContext; // 또는 CallbackContext
    
        public Map<String, String> setUserPreference(ToolContext toolContext, String preference, String value){
            // 사용자 수준 상태를 위해 'user:' 접두사 사용 (영구 SessionService 사용 시)
            String stateKey = "user:" + preference;
            toolContext.state().put(stateKey, value);
            System.out.println("사용자 선호도 '" + preference + "'를 '" + value + "'로 설정");
            return Map.of("status", "선호도 업데이트됨");
        }
        ```

*   **상태 접두사:** 기본 상태는 세션에만 해당하지만, `app:` 및 `user:`와 같은 접두사는 영구 `SessionService` 구현(`DatabaseSessionService` 또는 `VertexAiSessionService` 등)과 함께 사용하여 더 넓은 범위(앱 전체 또는 세션 간 사용자 전체)를 나타낼 수 있습니다. `temp:`는 현재 호출 내에서만 관련된 데이터를 나타낼 수 있습니다.

### 아티팩트 작업

세션과 관련된 파일이나 대용량 데이터 블롭을 처리하려면 아티팩트를 사용하세요. 일반적인 사용 사례: 업로드된 문서 처리.

*   **문서 요약기 예제 흐름:**

    1.  **참조 수집 (예: 설정 도구 또는 콜백에서):** 전체 내용이 아닌 문서의 *경로나 URI*를 아티팩트로 저장합니다.

        === "Python"
    
               ```python
               # 의사 코드: 콜백 또는 초기 도구 내
               from google.adk.agents import CallbackContext # 또는 ToolContext
               from google.genai import types
                
               def save_document_reference(context: CallbackContext, file_path: str) -> None:
                   # file_path가 "gs://my-bucket/docs/report.pdf" 또는 "/local/path/to/report.pdf"와 같다고 가정
                   try:
                       # 경로/URI 텍스트를 포함하는 Part 생성
                       artifact_part = types.Part(text=file_path)
                       version = context.save_artifact("document_to_summarize.txt", artifact_part)
                       print(f"문서 참조 '{file_path}'를 아티팩트 버전 {version}으로 저장함")
                       # 다른 도구에서 필요할 경우 상태에 파일 이름 저장
                       context.state["temp:doc_artifact_name"] = "document_to_summarize.txt"
                   except ValueError as e:
                       print(f"아티팩트 저장 오류: {e}") # 예: 아티팩트 서비스가 구성되지 않음
                   except Exception as e:
                       print(f"아티팩트 참조 저장 중 예기치 않은 오류 발생: {e}")
                
               # 예제 사용법:
               # save_document_reference(callback_context, "gs://my-bucket/docs/report.pdf")
               ```
    
        === "Java"
    
               ```java
               // 의사 코드: 콜백 또는 초기 도구 내
               import com.google.adk.agents.CallbackContext;
               import com.google.genai.types.Content;
               import com.google.genai.types.Part;
                
                
               pubic void saveDocumentReference(CallbackContext context, String filePath){
                   // file_path가 "gs://my-bucket/docs/report.pdf" 또는 "/local/path/to/report.pdf"와 같다고 가정
                   try{
                       // 경로/URI 텍스트를 포함하는 Part 생성
                       Part artifactPart = types.Part(filePath)
                       Optional<Integer> version = context.saveArtifact("document_to_summarize.txt", artifactPart)
                       System.out.println("문서 참조 " + filePath + "를 아티팩트 버전 " + version + "으로 저장함");
                       // 다른 도구에서 필요할 경우 상태에 파일 이름 저장
                       context.state().put("temp:doc_artifact_name", "document_to_summarize.txt");
                   } catch(Exception e){
                       System.out.println("아티팩트 참조 저장 중 예기치 않은 오류 발생: " + e);
                   }
               }
                    
               // 예제 사용법:
               // saveDocumentReference(context, "gs://my-bucket/docs/report.pdf")
               ```

    2.  **요약기 도구:** 아티팩트를 로드하여 경로/URI를 가져오고, 적절한 라이브러리를 사용하여 실제 문서 내용을 읽고, 요약한 후 결과를 반환합니다.

        === "Python"

            ```python
            # 의사 코드: 요약기 도구 함수 내
            from google.adk.tools import ToolContext
            from google.genai import types
            # google.cloud.storage나 내장 open과 같은 라이브러리가 사용 가능하다고 가정
            # 'summarize_text' 함수가 존재한다고 가정
            # from my_summarizer_lib import summarize_text

            def summarize_document_tool(tool_context: ToolContext) -> dict:
                artifact_name = tool_context.state.get("temp:doc_artifact_name")
                if not artifact_name:
                    return {"error": "상태에서 문서 아티팩트 이름을 찾을 수 없습니다."}

                try:
                    # 1. 경로/URI를 포함하는 아티팩트 파트 로드
                    artifact_part = tool_context.load_artifact(artifact_name)
                    if not artifact_part or not artifact_part.text:
                        return {"error": f"아티팩트를 로드할 수 없거나 아티팩트에 텍스트 경로가 없습니다: {artifact_name}"}

                    file_path = artifact_part.text
                    print(f"문서 참조 로드됨: {file_path}")

                    # 2. 실제 문서 내용 읽기 (ADK 컨텍스트 외부)
                    document_content = ""
                    if file_path.startswith("gs://"):
                        # 예제: GCS 클라이언트 라이브러리를 사용하여 다운로드/읽기
                        # from google.cloud import storage
                        # client = storage.Client()
                        # blob = storage.Blob.from_string(file_path, client=client)
                        # document_content = blob.download_as_text() # 또는 형식에 따라 바이트
                        pass # 실제 GCS 읽기 로직으로 교체
                    elif file_path.startswith("/"):
                         # 예제: 로컬 파일 시스템 사용
                         with open(file_path, 'r', encoding='utf-8') as f:
                             document_content = f.read()
                    else:
                        return {"error": f"지원되지 않는 파일 경로 체계: {file_path}"}

                    # 3. 내용 요약
                    if not document_content:
                         return {"error": "문서 내용을 읽지 못했습니다."}

                    # summary = summarize_text(document_content) # 요약 로직 호출
                    summary = f"{file_path}의 내용 요약" # 플레이스홀더

                    return {"summary": summary}

                except ValueError as e:
                     return {"error": f"아티팩트 서비스 오류: {e}"}
                except FileNotFoundError:
                     return {"error": f"로컬 파일을 찾을 수 없음: {file_path}"}
                # except Exception as e: # GCS 등에 대한 특정 예외 포착
                #      return {"error": f"문서 {file_path} 읽기 오류: {e}"}
            ```

        === "Java"

            ```java
            // 의사 코드: 요약기 도구 함수 내
            import com.google.adk.tools.ToolContext;
            import com.google.genai.types.Content;
            import com.google.genai.types.Part;

            public Map<String, String> summarizeDocumentTool(ToolContext toolContext){
                String artifactName = toolContext.state().get("temp:doc_artifact_name");
                if(artifactName.isEmpty()){
                    return Map.of("error", "상태에서 문서 아티팩트 이름을 찾을 수 없습니다.");
                }
                try{
                    // 1. 경로/URI를 포함하는 아티팩트 파트 로드
                    Maybe<Part> artifactPart = toolContext.loadArtifact(artifactName);
                    if((artifactPart == null) || (artifactPart.text().isEmpty())){
                        return Map.of("error", "아티팩트를 로드할 수 없거나 아티팩트에 텍스트 경로가 없습니다: " + artifactName);
                    }
                    filePath = artifactPart.text();
                    System.out.println("문서 참조 로드됨: " + filePath);

                    // 2. 실제 문서 내용 읽기 (ADK 컨텍스트 외부)
                    String documentContent = "";
                    if(filePath.startsWith("gs://")){
                        // 예제: GCS 클라이언트 라이브러리를 사용하여 documentContent로 다운로드/읽기
                        pass; // 실제 GCS 읽기 로직으로 교체
                    } else if(){
                        // 예제: 로컬 파일 시스템을 사용하여 documentContent로 다운로드/읽기
                    } else{
                        return Map.of("error", "지원되지 않는 파일 경로 체계: " + filePath); 
                    }

                    // 3. 내용 요약
                    if(documentContent.isEmpty()){
                        return Map.of("error", "문서 내용을 읽지 못했습니다."); 
                    }

                    // summary = summarizeText(documentContent) // 요약 로직 호출
                    summary = "" + filePath + "의 내용 요약"; // 플레이스홀더

                    return Map.of("summary", summary);
                } catch(IllegalArgumentException e){
                    return Map.of("error", "아티팩트 서비스 오류 " + filePath + e);
                } catch(FileNotFoundException e){
                    return Map.of("error", "로컬 파일을 찾을 수 없음 " + filePath + e);
                } catch(Exception e){
                    return Map.of("error", "문서 " + filePath + " 읽기 오류: " + e);
                }
            }
            ```
    
*   **아티팩트 목록 보기:** 어떤 파일이 사용 가능한지 확인합니다.
    
    === "Python"
        
        ```python
        # 의사 코드: 도구 함수 내
        from google.adk.tools import ToolContext
        
        def check_available_docs(tool_context: ToolContext) -> dict:
            try:
                artifact_keys = tool_context.list_artifacts()
                print(f"사용 가능한 아티팩트: {artifact_keys}")
                return {"available_docs": artifact_keys}
            except ValueError as e:
                return {"error": f"아티팩트 서비스 오류: {e}"}
        ```
        
    === "Java"
        
        ```java
        // 의사 코드: 도구 함수 내
        import com.google.adk.tools.ToolContext;
        
        public Map<String, String> checkAvailableDocs(ToolContext toolContext){
            try{
                Single<List<String>> artifactKeys = toolContext.listArtifacts();
                System.out.println("사용 가능한 아티팩트" + artifactKeys.tostring());
                return Map.of("availableDocs", "artifactKeys");
            } catch(IllegalArgumentException e){
                return Map.of("error", "아티팩트 서비스 오류: " + e);
            }
        }
        ```

### 도구 인증 처리

![python_only](https://img.shields.io/badge/현재_지원되는_언어-Python-blue){ title="이 기능은 현재 Python에서만 사용할 수 있습니다. Java 지원은 계획 중이거나 곧 제공될 예정입니다."}

도구에 필요한 API 키나 기타 자격 증명을 안전하게 관리합니다.

```python
# 의사 코드: 인증이 필요한 도구
from google.adk.tools import ToolContext
from google.adk.auth import AuthConfig # 적절한 AuthConfig가 정의되었다고 가정

# 필요한 인증 구성 정의 (예: OAuth, API 키)
MY_API_AUTH_CONFIG = AuthConfig(...)
AUTH_STATE_KEY = "user:my_api_credential" # 검색된 자격 증명을 저장할 키

def call_secure_api(tool_context: ToolContext, request_data: str) -> dict:
    # 1. 상태에 자격 증명이 이미 있는지 확인
    credential = tool_context.state.get(AUTH_STATE_KEY)

    if not credential:
        # 2. 없으면 요청
        print("자격 증명을 찾을 수 없어 요청합니다...")
        try:
            tool_context.request_credential(MY_API_AUTH_CONFIG)
            # 프레임워크가 이벤트 생성을 처리합니다. 이 턴 동안 도구 실행은 여기서 중지됩니다.
            return {"status": "인증이 필요합니다. 자격 증명을 제공해 주세요."}
        except ValueError as e:
            return {"error": f"인증 오류: {e}"} # 예: function_call_id 누락
        except Exception as e:
            return {"error": f"자격 증명 요청 실패: {e}"}

    # 3. 자격 증명이 있는 경우 (요청 후 이전 턴에서 왔을 수 있음)
    #    또는 외부 인증 흐름이 완료된 후 후속 호출인 경우
    try:
        # 선택적으로 필요한 경우 재검증/검색하거나 직접 사용
        # 외부 흐름이 방금 완료된 경우 자격 증명을 검색할 수 있음
        auth_credential_obj = tool_context.get_auth_response(MY_API_AUTH_CONFIG)
        api_key = auth_credential_obj.api_key # 또는 access_token 등

        # 세션 내 미래 호출을 위해 상태에 다시 저장
        tool_context.state[AUTH_STATE_KEY] = auth_credential_obj.model_dump() # 검색된 자격 증명 지속

        print(f"검색된 자격 증명을 사용하여 데이터로 API 호출: {request_data}")
        # ... api_key를 사용하여 실제 API 호출 ...
        api_result = f"{request_data}에 대한 API 결과"

        return {"result": api_result}
    except Exception as e:
        # 자격 증명 검색/사용 오류 처리
        print(f"자격 증명 사용 오류: {e}")
        # 자격 증명이 유효하지 않은 경우 상태 키를 지울 수도 있음
        # tool_context.state[AUTH_STATE_KEY] = None
        return {"error": "자격 증명 사용 실패"}

```
*기억하세요: `request_credential`은 도구를 일시 중지하고 인증 필요성을 알립니다. 사용자/시스템이 자격 증명을 제공하면, 후속 호출에서 `get_auth_response`(또는 상태를 다시 확인)를 통해 도구가 계속 진행할 수 있습니다.* `tool_context.function_call_id`는 프레임워크에 의해 요청과 응답을 연결하는 데 암묵적으로 사용됩니다.

### 메모리 활용

![python_only](https://img.shields.io/badge/현재_지원되는_언어-Python-blue){ title="이 기능은 현재 Python에서만 사용할 수 있습니다. Java 지원은 계획 중이거나 곧 제공될 예정입니다."}

과거 또는 외부 소스에서 관련 정보에 접근합니다.

```python
# 의사 코드: 메모리 검색을 사용하는 도구
from google.adk.tools import ToolContext

def find_related_info(tool_context: ToolContext, topic: str) -> dict:
    try:
        search_results = tool_context.search_memory(f"{topic}에 대한 정보")
        if search_results.results:
            print(f"'{topic}'에 대한 메모리 결과 {len(search_results.results)}개 발견")
            # search_results.results 처리 (SearchMemoryResponseEntry)
            top_result_text = search_results.results[0].text
            return {"memory_snippet": top_result_text}
        else:
            return {"message": "관련 메모리를 찾을 수 없습니다."}
    except ValueError as e:
        return {"error": f"메모리 서비스 오류: {e}"} # 예: 서비스가 구성되지 않음
    except Exception as e:
        return {"error": f"메모리 검색 중 예기치 않은 오류 발생: {e}"}
```

### 고급: 직접적인 `InvocationContext` 사용

![python_only](https://img.shields.io/badge/현재_지원되는_언어-Python-blue){ title="이 기능은 현재 Python에서만 사용할 수 있습니다. Java 지원은 계획 중이거나 곧 제공될 예정입니다."}

대부분의 상호작용은 `CallbackContext` 또는 `ToolContext`를 통해 이루어지지만, 때로는 에이전트의 핵심 로직(`_run_async_impl`/`_run_live_impl`)이 직접적인 접근을 필요로 합니다.

```python
# 의사 코드: 에이전트의 _run_async_impl 내부
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator

class MyControllingAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 예제: 특정 서비스가 사용 가능한지 확인
        if not ctx.memory_service:
            print("이 호출에 메모리 서비스를 사용할 수 없습니다.")
            # 잠재적으로 에이전트 동작 변경

        # 예제: 특정 조건에 따른 조기 종료
        if ctx.session.state.get("critical_error_flag"):
            print("치명적인 오류 감지, 호출 종료.")
            ctx.end_invocation = True # 프레임워크에 처리 중지 신호
            yield Event(author=self.name, invocation_id=ctx.invocation_id, content="치명적인 오류로 인해 중지합니다.")
            return # 이 에이전트의 실행 중지

        # ... 일반 에이전트 처리 ...
        yield # ... 이벤트 ...
```

`ctx.end_invocation = True`를 설정하는 것은 에이전트나 콜백/도구 내(각각의 컨텍스트 객체를 통해 기본 `InvocationContext`의 플래그를 수정할 수 있음)에서 전체 요청-응답 주기를 정상적으로 중지하는 방법입니다.

## 주요 요점 및 모범 사례

*   **올바른 컨텍스트 사용:** 항상 제공되는 가장 구체적인 컨텍스트 객체를 사용하세요 (`ToolContext`는 도구/도구-콜백에서, `CallbackContext`는 에이전트/모델-콜백에서, 해당하는 경우 `ReadonlyContext`). 전체 `InvocationContext`(`ctx`)는 필요한 경우에만 `_run_async_impl` / `_run_live_impl`에서 직접 사용하세요.
*   **데이터 흐름을 위한 상태:** `context.state`는 호출 *내에서* 데이터를 공유하고, 선호도를 기억하며, 대화 메모리를 관리하는 주요 방법입니다. 영구 스토리지를 사용할 때는 접두사(`app:`, `user:`, `temp:`)를 신중하게 사용하세요.
*   **파일을 위한 아티팩트:** 파일 참조(경로나 URI 등)나 대용량 데이터 블롭을 관리하려면 `context.save_artifact` 및 `context.load_artifact`를 사용하세요. 참조를 저장하고, 필요할 때 내용을 로드하세요.
*   **추적된 변경 사항:** 컨텍스트 메서드를 통해 상태나 아티팩트를 수정하면 현재 단계의 `EventActions`와 자동으로 연결되고 `SessionService`에 의해 처리됩니다.
*   **단순하게 시작:** 먼저 `state`와 기본 아티팩트 사용에 집중하세요. 필요가 더 복잡해지면 인증, 메모리 및 고급 `InvocationContext` 필드(라이브 스트리밍용 등)를 탐색하세요.

이러한 컨텍스트 객체를 이해하고 효과적으로 사용함으로써 ADK로 더 정교하고, 상태를 유지하며, 유능한 에이전트를 구축할 수 있습니다.