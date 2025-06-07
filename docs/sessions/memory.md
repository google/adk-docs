# 메모리: `MemoryService`를 이용한 장기 지식

![python_only](https://img.shields.io/badge/현재_지원되는_언어-Python-blue){ title="이 기능은 현재 Python에서만 사용할 수 있습니다. Java 지원은 계획 중이거나 곧 제공될 예정입니다."}

`세션`이 *단일하고 진행 중인 대화*에 대한 기록(`이벤트`)과 임시 데이터(`상태`)를 추적하는 방법을 살펴보았습니다. 하지만 에이전트가 *과거* 대화의 정보를 기억하거나 외부 지식 기반에 접근해야 한다면 어떨까요? 바로 여기서 **장기 지식**과 **`MemoryService`**의 개념이 중요해집니다.

이렇게 생각해 보세요:

* **`세션` / `상태`:** 특정 채팅 중의 단기 기억과 같습니다.
* **장기 지식 (`MemoryService`):** 에이전트가 참고할 수 있는 검색 가능한 아카이브나 지식 라이브러리와 같으며, 여러 과거 채팅이나 다른 소스의 정보를 포함할 수 있습니다.

## `MemoryService`의 역할

`BaseMemoryService`는 이 검색 가능한 장기 지식 저장소를 관리하기 위한 인터페이스를 정의합니다. 주요 책임은 다음과 같습니다:

1. **정보 수집 (`add_session_to_memory`):** (보통 완료된) `세션`의 내용을 가져와 장기 지식 저장소에 관련 정보를 추가합니다.
2. **정보 검색 (`search_memory`):** 에이전트(일반적으로 `도구`를 통해)가 지식 저장소를 쿼리하고 검색 쿼리를 기반으로 관련 스니펫이나 컨텍스트를 검색할 수 있도록 합니다.

## `MemoryService` 구현

ADK는 이 장기 지식 저장소를 구현하는 다양한 방법을 제공합니다:

1. **`InMemoryMemoryService`**

    * **작동 방식:** 세션 정보를 애플리케이션의 메모리에 저장하고 검색을 위해 기본 키워드 일치를 수행합니다.
    * **지속성:** 없음. **애플리케이션이 다시 시작되면 저장된 모든 지식이 손실됩니다.**
    * **요구 사항:** 추가 사항 없음.
    * **최적 사용처:** 프로토타이핑, 간단한 테스트, 기본 키워드 회상만 필요하고 지속성이 필요하지 않은 시나리오.

    ```py
    from google.adk.memory import InMemoryMemoryService
    memory_service = InMemoryMemoryService()
    ```

2. **`VertexAiRagMemoryService`**

    * **작동 방식:** Google Cloud의 Vertex AI RAG(검색 증강 생성) 서비스를 활용합니다. 세션 데이터를 지정된 RAG 코퍼스로 수집하고 검색을 위해 강력한 의미 검색 기능을 사용합니다.
    * **지속성:** 예. 지식은 구성된 Vertex AI RAG 코퍼스 내에 영구적으로 저장됩니다.
    * **요구 사항:** Google Cloud 프로젝트, 적절한 권한, 필요한 SDK(`pip install google-adk[vertexai]`), 미리 구성된 Vertex AI RAG 코퍼스 리소스 이름/ID.
    * **최적 사용처:** 특히 Google Cloud에 배포될 때 확장 가능하고, 지속적이며, 의미적으로 관련된 지식 검색이 필요한 프로덕션 애플리케이션.

    ```py
    # 요구 사항: pip install google-adk[vertexai]
    # 추가로 GCP 설정, RAG 코퍼스 및 인증 필요
    from google.adk.memory import VertexAiRagMemoryService

    # RAG 코퍼스 이름 또는 ID
    RAG_CORPUS_RESOURCE_NAME = "projects/your-gcp-project-id/locations/us-central1/ragCorpora/your-corpus-id"
    # 검색을 위한 선택적 구성
    SIMILARITY_TOP_K = 5
    VECTOR_DISTANCE_THRESHOLD = 0.7

    memory_service = VertexAiRagMemoryService(
        rag_corpus=RAG_CORPUS_RESOURCE_NAME,
        similarity_top_k=SIMILARITY_TOP_K,
        vector_distance_threshold=VECTOR_DISTANCE_THRESHOLD
    )
    ```

## 실제 메모리 작동 방식

일반적인 워크플로는 다음과 같은 단계를 포함합니다:

1. **세션 상호작용:** 사용자가 `SessionService`가 관리하는 `세션`을 통해 에이전트와 상호 작용합니다. 이벤트가 추가되고 상태가 업데이트될 수 있습니다.
2. **메모리에 수집:** 어떤 시점(종종 세션이 완료되었거나 중요한 정보를 생성했을 때)에 애플리케이션이 `memory_service.add_session_to_memory(session)`를 호출합니다. 이는 세션의 이벤트에서 관련 정보를 추출하여 장기 지식 저장소(인메모리 사전 또는 RAG 코퍼스)에 추가합니다.
3. **나중의 쿼리:** *다른* (또는 동일한) 세션에서 사용자가 과거 컨텍스트를 요구하는 질문을 할 수 있습니다(예: "지난주에 X 프로젝트에 대해 무엇을 논의했나요?").
4. **에이전트가 메모리 도구 사용:** 메모리 검색 도구(내장 `load_memory` 도구 등)를 갖춘 에이전트가 과거 컨텍스트의 필요성을 인식합니다. 도구를 호출하여 검색 쿼리("지난주 X 프로젝트 논의" 등)를 제공합니다.
5. **검색 실행:** 도구가 내부적으로 `memory_service.search_memory(app_name, user_id, query)`를 호출합니다.
6. **결과 반환:** `MemoryService`가 저장소(키워드 일치 또는 의미 검색 사용)를 검색하고 관련 스니펫을 `MemoryResult` 객체 목록을 포함하는 `SearchMemoryResponse`로 반환합니다(각각 관련 과거 세션의 이벤트를 포함할 수 있음).
7. **에이전트가 결과 사용:** 도구가 이러한 결과를 에이전트에게 컨텍스트나 함수 응답의 일부로 반환합니다. 그러면 에이전트는 이 검색된 정보를 사용하여 사용자에게 최종 답변을 구성할 수 있습니다.

## 예제: 메모리 추가 및 검색

이 예제는 단순화를 위해 `InMemory` 서비스를 사용하는 기본 흐름을 보여줍니다.

???+ "전체 코드"

    ```py
    import asyncio
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.memory import InMemoryMemoryService # MemoryService 가져오기
    from google.adk.runners import Runner
    from google.adk.tools import load_memory # 메모리 쿼리 도구
    from google.genai.types import Content, Part

    # --- 상수 ---
    APP_NAME = "memory_example_app"
    USER_ID = "mem_user"
    MODEL = "gemini-2.0-flash" # 유효한 모델 사용

    # --- 에이전트 정의 ---
    # 에이전트 1: 정보 수집을 위한 간단한 에이전트
    info_capture_agent = LlmAgent(
        model=MODEL,
        name="InfoCaptureAgent",
        instruction="사용자의 진술을 확인합니다.",
        # output_key="captured_info" # 선택적으로 상태에도 저장 가능
    )

    # 에이전트 2: 메모리를 사용할 수 있는 에이전트
    memory_recall_agent = LlmAgent(
        model=MODEL,
        name="MemoryRecallAgent",
        instruction="사용자의 질문에 답합니다. 답변이 과거 대화에 있을 수 있는 경우 'load_memory' 도구를 사용합니다.",
        tools=[load_memory] # 에이전트에게 도구 제공
    )

    # --- 서비스 및 Runner ---
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService() # 데모를 위해 인메모리 사용

    runner = Runner(
        # 정보 수집 에이전트로 시작
        agent=info_capture_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service # Runner에 메모리 서비스 제공
    )

    # --- 시나리오 ---

    # 1번째 턴: 세션에 일부 정보 수집
    print("--- 1번째 턴: 정보 수집 ---")
    session1_id = "session_info"
    session1 = await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)
    user_input1 = Content(parts=[Part(text="제가 가장 좋아하는 프로젝트는 알파 프로젝트입니다.")], role="user")

    # 에이전트 실행
    final_response_text = "(최종 응답 없음)"
    async for event in runner.run_async(user_id=USER_ID, session_id=session1_id, new_message=user_input1):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_text = event.content.parts[0].text
    print(f"에이전트 1 응답: {final_response_text}")

    # 완료된 세션 가져오기
    completed_session1 = await runner.session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)

    # 이 세션의 내용을 메모리 서비스에 추가
    print("\n--- 세션 1을 메모리에 추가 ---")
    memory_service = await memory_service.add_session_to_memory(completed_session1)
    print("세션이 메모리에 추가되었습니다.")

    # 2번째 턴: *새로운* (또는 동일한) 세션에서 메모리가 필요한 질문하기
    print("\n--- 2번째 턴: 정보 회상 ---")
    session2_id = "session_recall" # 동일하거나 다른 세션 ID 가능
    session2 = await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session2_id)

    # runner를 회상 에이전트로 전환
    runner.agent = memory_recall_agent
    user_input2 = Content(parts=[Part(text="제가 가장 좋아하는 프로젝트는 무엇인가요?")], role="user")

    # 회상 에이전트 실행
    print("MemoryRecallAgent 실행 중...")
    final_response_text_2 = "(최종 응답 없음)"
    async for event in runner.run_async(user_id=USER_ID, session_id=session2_id, new_message=user_input2):
        print(f"  이벤트: {event.author} - 유형: {'Text' if event.content and event.content.parts and event.content.parts[0].text else ''}"
            f"{'FuncCall' if event.get_function_calls() else ''}"
            f"{'FuncResp' if event.get_function_responses() else ''}")
        if event.is_final_response() and event.content and event.content.parts:
            final_response_text_2 = event.content.parts[0].text
            print(f"에이전트 2 최종 응답: {final_response_text_2}")
            break # 최종 응답 후 중지

    # 2번째 턴의 예상 이벤트 시퀀스:
    # 1. 사용자가 "제가 가장 좋아하는 프로젝트는 무엇인가요?"를 보냄
    # 2. 에이전트(LLM)가 "가장 좋아하는 프로젝트"와 같은 쿼리로 `load_memory` 도구를 호출하기로 결정함.
    # 3. Runner가 `load_memory` 도구를 실행하고, 이는 `memory_service.search_memory`를 호출함.
    # 4. `InMemoryMemoryService`가 session1에서 관련 텍스트("제가 가장 좋아하는 프로젝트는 알파 프로젝트입니다.")를 찾음.
    # 5. 도구가 이 텍스트를 FunctionResponse 이벤트로 반환함.
    # 6. 에이전트(LLM)가 함수 응답을 받고 검색된 텍스트를 처리함.
    # 7. 에이전트가 최종 답변("당신이 가장 좋아하는 프로젝트는 알파 프로젝트입니다.")을 생성함.
    ```