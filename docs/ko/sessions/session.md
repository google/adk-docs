# 세션: 개별 대화 추적

서론에 이어, `세션`에 대해 자세히 알아보겠습니다. "대화 스레드"라는 아이디어를 다시 생각해 보세요. 모든 문자 메시지를 처음부터 시작하지 않는 것처럼, 에이전트도 진행 중인 상호작용에 대한 컨텍스트가 필요합니다. **`세션`**은 이러한 개별 대화 스레드를 추적하고 관리하기 위해 특별히 설계된 ADK 객체입니다.

## `세션` 객체

사용자가 에이전트와 상호작용을 시작하면, `SessionService`는 `세션` 객체(`google.adk.sessions.Session`)를 생성합니다. 이 객체는 *하나의 특정 채팅 스레드*와 관련된 모든 것을 담는 컨테이너 역할을 합니다. 주요 속성은 다음과 같습니다:

*   **식별 (`id`, `appName`, `userId`):** 대화에 대한 고유한 레이블입니다.
    * `id`: *이 특정* 대화 스레드에 대한 고유 식별자로, 나중에 검색하는 데 필수적입니다. SessionService 객체는 여러 `세션`을 처리할 수 있습니다. 이 필드는 우리가 참조하는 특정 세션 객체를 식별합니다. 예: "test_id_modification".
    * `appName`: 이 대화가 속한 에이전트 애플리케이션을 식별합니다. 예: "id_modifier_workflow".
    *   `userId`: 대화를 특정 사용자와 연결합니다.
*   **기록 (`events`):** 이 특정 스레드 내에서 발생한 모든 상호작용(`이벤트` 객체 – 사용자 메시지, 에이전트 응답, 도구 작업)의 시간순 시퀀스입니다.
*   **세션 상태 (`state`):** 이 특정하고 진행 중인 대화에만 관련된 임시 데이터를 저장하는 장소입니다. 상호작용 중에 에이전트를 위한 스크래치패드 역할을 합니다. `상태`를 사용하고 관리하는 방법은 다음 섹션에서 자세히 다룰 것입니다.
*   **활동 추적 (`lastUpdateTime`):** 이 대화 스레드에서 마지막으로 이벤트가 발생한 시간을 나타내는 타임스탬프입니다.

### 예제: 세션 속성 검사


=== "Python"

       ```py
        from google.adk.sessions import InMemorySessionService, Session
    
        # 속성을 검사하기 위해 간단한 세션 생성
        temp_service = InMemorySessionService()
        example_session = await temp_service.create_session(
            app_name="my_app",
            user_id="example_user",
            state={"initial_key": "initial_value"} # 상태는 초기화될 수 있음
        )

        print(f"--- 세션 속성 검사 ---")
        print(f"ID (`id`):                {example_session.id}")
        print(f"애플리케이션 이름 (`app_name`): {example_session.app_name}")
        print(f"사용자 ID (`user_id`):         {example_session.user_id}")
        print(f"상태 (`state`):           {example_session.state}") # 참고: 여기서는 초기 상태만 표시됨
        print(f"이벤트 (`events`):         {example_session.events}") # 처음에는 비어 있음
        print(f"마지막 업데이트 (`last_update_time`): {example_session.last_update_time:.2f}")
        print(f"---------------------------------")

        # 정리 (이 예제에서는 선택 사항)
        temp_service = await temp_service.delete_session(app_name=example_session.app_name,
                                    user_id=example_session.user_id, session_id=example_session.id)
        print("temp_service의 최종 상태 - ", temp_service)
       ```

=== "Java"

       ```java
        import com.google.adk.sessions.InMemorySessionService;
        import com.google.adk.sessions.Session;
        import java.util.concurrent.ConcurrentMap;
        import java.util.concurrent.ConcurrentHashMap;
        import java.util.Map;
        import java.util.Optional;
    
        String sessionId = "123";
        String appName = "example-app"; // 예제 앱 이름
        String userId = "example-user"; // 예제 사용자 ID
        ConcurrentMap<String, Object> initialState = new ConcurrentHashMap<>(Map.of("newKey", "newValue"));
        InMemorySessionService exampleSessionService = new InMemorySessionService();
    
        // 세션 생성
        Session exampleSession = exampleSessionService.createSession(
            appName, userId, initialState, Optional.of(sessionId)).blockingGet();
        System.out.println("세션이 성공적으로 생성되었습니다.");
    
        System.out.println("--- 세션 속성 검사 ---");
        System.out.printf("ID (`id`): %s%n", exampleSession.id());
        System.out.printf("애플리케이션 이름 (`appName`): %s%n", exampleSession.appName());
        System.out.printf("사용자 ID (`userId`): %s%n", exampleSession.userId());
        System.out.printf("상태 (`state`): %s%n", exampleSession.state());
        System.out.println("------------------------------------");
    
    
        // 정리 (이 예제에서는 선택 사항)
        var unused = exampleSessionService.deleteSession(appName, userId, sessionId);
       ```

*(**참고:** 위에 표시된 상태는 초기 상태일 뿐입니다. 상태 업데이트는 상태 섹션에서 논의된 대로 이벤트를 통해 발생합니다.)*

## `SessionService`로 세션 관리하기

위에서 보았듯이, 일반적으로 `세션` 객체를 직접 생성하거나 관리하지 않습니다.
대신 **`SessionService`**를 사용합니다. 이 서비스는 대화 세션의 전체 생명주기를 책임지는 중앙 관리자 역할을 합니다.

핵심 책임은 다음과 같습니다:

*   **새로운 대화 시작:** 사용자가 상호작용을 시작할 때 새로운 `세션` 객체 생성.
*   **기존 대화 재개:** 에이전트가 중단된 지점부터 계속할 수 있도록 특정 `세션`(ID 사용)을 검색.
*   **진행 상황 저장:** 세션의 기록에 새로운 상호작용(`이벤트` 객체)을 추가. 이는 세션 `상태`가 업데이트되는 메커니즘이기도 합니다(`상태` 섹션에서 자세히 설명).
*   **대화 목록 보기:** 특정 사용자와 애플리케이션의 활성 세션 스레드를 찾기.
*   **정리:** 대화가 끝나거나 더 이상 필요하지 않을 때 `세션` 객체와 관련 데이터를 삭제.

## `SessionService` 구현

ADK는 다양한 `SessionService` 구현을 제공하여 사용자의 요구에 가장 적합한 스토리지 백엔드를 선택할 수 있도록 합니다:

1.  **`InMemorySessionService`**

    *   **작동 방식:** 모든 세션 데이터를 애플리케이션의 메모리에 직접 저장합니다.
    *   **지속성:** 없음. **애플리케이션이 다시 시작되면 모든 대화 데이터가 손실됩니다.**
    *   **요구 사항:** 추가 사항 없음.
    *   **최적 사용처:** 빠른 개발, 로컬 테스트, 예제 및 장기적인 지속성이 필요하지 않은 시나리오.

    === "Python"
    
           ```py
            from google.adk.sessions import InMemorySessionService
            session_service = InMemorySessionService()
           ```
    === "Java"
    
           ```java
            import com.google.adk.sessions.InMemorySessionService;
            InMemorySessionService exampleSessionService = new InMemorySessionService();
           ```

2.  **`VertexAiSessionService`**

    *   **작동 방식:** 세션 관리를 위해 API 호출을 통해 Google Cloud의 Vertex AI 인프라를 사용합니다.
    *   **지속성:** 예. 데이터는 [Vertex AI Agent Engine](https://google.github.io/adk-docs/deploy/agent-engine/)을 통해 안정적이고 확장 가능하게 관리됩니다.
    *   **요구 사항:**
        *   Google Cloud 프로젝트 (`pip install vertexai`)
        *   이 [단계](https://cloud.google.com/vertex-ai/docs/pipelines/configure-project#storage)에 따라 구성할 수 있는 Google Cloud 스토리지 버킷.
        *   이 [튜토리얼](https://google.github.io/adk-docs/deploy/agent-engine/)에 따라 설정할 수 있는 Reasoning Engine 리소스 이름/ID.
    *   **최적 사용처:** Google Cloud에 배포된 확장 가능한 프로덕션 애플리케이션, 특히 다른 Vertex AI 기능과 통합할 때.

    === "Python"
    
           ```py
           # 요구 사항: pip install google-adk[vertexai]
           # 추가로 GCP 설정 및 인증 필요
           from google.adk.sessions import VertexAiSessionService

           PROJECT_ID = "your-gcp-project-id"
           LOCATION = "us-central1"
           # 이 서비스와 함께 사용되는 app_name은 Reasoning Engine ID 또는 이름이어야 함
           REASONING_ENGINE_APP_NAME = "projects/your-gcp-project-id/locations/us-central1/reasoningEngines/your-engine-id"

           session_service = VertexAiSessionService(project=PROJECT_ID, location=LOCATION)
           # 서비스 메서드를 호출할 때 REASONING_ENGINE_APP_NAME 사용, 예:
           # session_service = await session_service.create_session(app_name=REASONING_ENGINE_APP_NAME, ...)
           ```
       
    === "Java"
    
           ```java
           // 위의 요구 사항을 확인한 후, bashrc 파일에 다음을 내보내세요:
           // export GOOGLE_CLOUD_PROJECT=my_gcp_project
           // export GOOGLE_CLOUD_LOCATION=us-central1
           // export GOOGLE_API_KEY=my_api_key

           import com.google.adk.sessions.VertexAiSessionService;
           import java.util.UUID;
           import java.util.concurrent.ConcurrentMap;
           import java.util.concurrent.ConcurrentHashMap;
           import java.util.Optional;

           String sessionId = UUID.randomUUID().toString();
           String reasoningEngineAppName = "123456789";
           String userId = "u_123"; // 예제 사용자 ID
           ConcurrentMap<String, Object> initialState = new
               ConcurrentHashMap<>(); // 이 예제에는 초기 상태가 필요 없음

           VertexAiSessionService sessionService = new VertexAiSessionService();
           Session mySession =
               sessionService
                   .createSession(reasoningEngineAppName, userId, initialState, Optional.of(sessionId))
                   .blockingGet();
           ```

3.  **`DatabaseSessionService`**

    ![python_only](https://img.shields.io/badge/현재_지원되는_언어-Python-blue){ title="이 기능은 현재 Python에서만 사용할 수 있습니다. Java 지원은 계획 중이거나 곧 제공될 예정입니다."}

    *   **작동 방식:** 관계형 데이터베이스(예: PostgreSQL, MySQL, SQLite)에 연결하여 세션 데이터를 테이블에 영구적으로 저장합니다.
    *   **지속성:** 예. 데이터는 애플리케이션 재시작 후에도 유지됩니다.
    *   **요구 사항:** 구성된 데이터베이스.
    *   **최적 사용처:** 직접 관리하는 안정적이고 영구적인 저장이 필요한 애플리케이션.

    ```py
    from google.adk.sessions import DatabaseSessionService
    # 로컬 SQLite 파일을 사용하는 예제:
    db_url = "sqlite:///./my_agent_data.db"
    session_service = DatabaseSessionService(db_url=db_url)
    ```

올바른 `SessionService`를 선택하는 것은 에이전트의 대화 기록과 임시 데이터가 어떻게 저장되고 지속되는지를 정의하는 핵심입니다.

## 세션 생명주기

<img src="../../assets/session_lifecycle.png" alt="세션 생명주기">

대화 턴 동안 `세션`과 `SessionService`가 함께 작동하는 간소화된 흐름은 다음과 같습니다:

1.  **시작 또는 재개:** 애플리케이션의 `Runner`는 `SessionService`를 사용하여 `create_session`(새로운 채팅용) 또는 `get_session`(기존 채팅 검색용)을 호출합니다.
2.  **컨텍스트 제공:** `Runner`는 적절한 서비스 메서드에서 적절한 `세션` 객체를 가져와 에이전트가 해당 세션의 `상태`와 `이벤트`에 접근할 수 있도록 합니다.
3.  **에이전트 처리:** 사용자가 쿼리로 에이전트를 프롬프트합니다. 에이전트는 쿼리와 잠재적으로 세션 `상태` 및 `이벤트` 기록을 분석하여 응답을 결정합니다.
4.  **응답 및 상태 업데이트:** 에이전트는 응답을 생성하고(잠재적으로 `상태`에서 업데이트할 데이터를 플래그 지정) `Runner`는 이를 `이벤트`로 패키징합니다.
5.  **상호작용 저장:** `Runner`는 `sessionService.append_event(session, event)`를 `세션`과 새로운 `이벤트`를 인수로 호출합니다. 서비스는 `이벤트`를 기록에 추가하고 이벤트 내의 정보를 기반으로 세션의 `상태`를 스토리지에서 업데이트합니다. 세션의 `last_update_time`도 업데이트됩니다.
6.  **다음 준비:** 에이전트의 응답이 사용자에게 전달됩니다. 업데이트된 `세션`은 이제 `SessionService`에 의해 저장되어 다음 턴을 준비합니다(일반적으로 현재 세션에서 대화를 계속하는 것으로 1단계에서 주기를 다시 시작).
7.  **대화 종료:** 대화가 끝나면 애플리케이션은 더 이상 필요하지 않은 경우 저장된 세션 데이터를 정리하기 위해 `sessionService.delete_session(...)`을 호출합니다.

이 주기는 `SessionService`가 각 `세션` 객체와 관련된 기록과 상태를 관리하여 대화의 연속성을 보장하는 방법을 보여줍니다.