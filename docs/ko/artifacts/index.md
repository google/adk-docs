# 아티팩트 (Artifacts)

ADK에서 **아티팩트(Artifacts)**는 특정 사용자 상호작용 세션과 연관되거나 여러 세션에 걸쳐 사용자와 영구적으로 연관된, 이름이 지정되고 버전이 관리되는 바이너리 데이터를 관리하기 위한 중요한 메커니즘을 나타냅니다. 이를 통해 에이전트와 도구는 단순한 텍스트 문자열을 넘어 파일, 이미지, 오디오 및 기타 바이너리 형식을 포함하는 더 풍부한 상호작용을 처리할 수 있습니다.

!!! Note
    기본 요소에 대한 특정 매개변수나 메서드 이름은 SDK 언어에 따라 약간 다를 수 있습니다(예: Python의 `save_artifact`, Java의 `saveArtifact`). 자세한 내용은 언어별 API 문서를 참조하세요.

## 아티팩트란 무엇인가요?

*   **정의:** 아티팩트는 본질적으로 특정 범위(세션 또는 사용자) 내에서 고유한 `filename` 문자열로 식별되는 바이너리 데이터 조각(파일 내용 등)입니다. 동일한 파일 이름으로 아티팩트를 저장할 때마다 새 버전이 생성됩니다.

*   **표현:** 아티팩트는 표준 `google.genai.types.Part` 객체를 사용하여 일관되게 표현됩니다. 핵심 데이터는 일반적으로 `Part`의 인라인 데이터 구조 내에 저장되며(`inline_data`를 통해 접근), 여기에는 다음이 포함됩니다:
    *   `data`: 원시 바이너리 콘텐츠 (바이트).
    *   `mime_type`: 데이터 유형을 나타내는 문자열 (예: `"image/png"`, `"application/pdf"`). 이는 나중에 데이터를 올바르게 해석하는 데 필수적입니다.


=== "Python"

    ```py
    # 아티팩트가 types.Part로 표현될 수 있는 방법의 예시
    import google.genai.types as types

    # 'image_bytes'에 PNG 이미지의 바이너리 데이터가 포함되어 있다고 가정
    image_bytes = b'\x89PNG\r\n\x1a\n...' # 실제 이미지 바이트를 위한 플레이스홀더

    image_artifact = types.Part(
        inline_data=types.Blob(
            mime_type="image/png",
            data=image_bytes
        )
    )

    # 편의 생성자를 사용할 수도 있습니다:
    # image_artifact_alt = types.Part.from_bytes(data=image_bytes, mime_type="image/png")

    print(f"아티팩트 MIME 유형: {image_artifact.inline_data.mime_type}")
    print(f"아티팩트 데이터 (처음 10바이트): {image_artifact.inline_data.data[:10]}...")
    ```

=== "Java"

    ```java
    import com.google.genai.types.Part;
    import java.nio.charset.StandardCharsets;

    public class ArtifactExample {
        public static void main(String[] args) {
            // 'imageBytes'에 PNG 이미지의 바이너리 데이터가 포함되어 있다고 가정
            byte[] imageBytes = {(byte) 0x89, (byte) 0x50, (byte) 0x4E, (byte) 0x47, (byte) 0x0D, (byte) 0x0A, (byte) 0x1A, (byte) 0x0A, (byte) 0x01, (byte) 0x02}; // 실제 이미지 바이트를 위한 플레이스홀더

            // Part.fromBytes를 사용하여 이미지 아티팩트 생성
            Part imageArtifact = Part.fromBytes(imageBytes, "image/png");

            System.out.println("아티팩트 MIME 유형: " + imageArtifact.inlineData().get().mimeType().get());
            System.out.println(
                "아티팩트 데이터 (처음 10바이트): "
                    + new String(imageArtifact.inlineData().get().data().get(), 0, 10, StandardCharsets.UTF_8)
                    + "...");
        }
    }
    ```

*   **지속성 및 관리:** 아티팩트는 에이전트나 세션 상태에 직접 저장되지 않습니다. 저장 및 검색은 전용 **아티팩트 서비스(Artifact Service)**에 의해 관리됩니다 (`google.adk.artifacts`에 정의된 `BaseArtifactService`의 구현체). ADK는 다음과 같은 다양한 구현을 제공합니다:
    *   테스트 또는 임시 저장을 위한 인메모리 서비스 (예: Python의 `InMemoryArtifactService`, `google.adk.artifacts.in_memory_artifact_service.py`에 정의됨).
    *   Google Cloud Storage(GCS)를 사용한 영구 저장을 위한 서비스 (예: Python의 `GcsArtifactService`, `google.adk.artifacts.gcs_artifact_service.py`에 정의됨).
    선택된 서비스 구현은 데이터를 저장할 때 자동으로 버전 관리를 처리합니다.

## 왜 아티팩트를 사용해야 하나요?

세션 `state`는 작은 구성 정보나 대화 컨텍스트(문자열, 숫자, 불리언 또는 작은 사전/리스트 등)를 저장하는 데 적합하지만, 아티팩트는 바이너리 또는 대용량 데이터를 포함하는 시나리오를 위해 설계되었습니다:

1.  **비텍스트 데이터 처리:** 에이전트의 기능과 관련된 이미지, 오디오 클립, 비디오 스니펫, PDF, 스프레드시트 또는 기타 파일 형식을 쉽게 저장하고 검색합니다.
2.  **대용량 데이터 지속:** 세션 상태는 일반적으로 대량의 데이터를 저장하는 데 최적화되어 있지 않습니다. 아티팩트는 세션 상태를 복잡하게 만들지 않고 더 큰 블롭을 영구적으로 저장하기 위한 전용 메커니즘을 제공합니다.
3.  **사용자 파일 관리:** 사용자가 파일을 업로드(아티팩트로 저장 가능)하고 에이전트가 생성한 파일을 검색하거나 다운로드(아티팩트에서 로드)할 수 있는 기능을 제공합니다.
4.  **출력 공유:** 도구나 에이전트가 `save_artifact`를 통해 저장할 수 있는 바이너리 출력(PDF 보고서나 생성된 이미지 등)을 생성하고, 나중에 애플리케이션의 다른 부분이나 후속 세션에서도 (사용자 네임스페이스를 사용하는 경우) 접근할 수 있도록 합니다.
5.  **바이너리 데이터 캐싱:** 바이너리 데이터를 생성하는 계산 비용이 많이 드는 작업(예: 복잡한 차트 이미지 렌더링)의 결과를 아티팩트로 저장하여 후속 요청 시 다시 생성하는 것을 방지합니다.

본질적으로, 에이전트가 영구적으로 저장되거나, 버전 관리되거나, 공유되어야 하는 파일과 유사한 바이너리 데이터로 작업해야 할 때마다, `ArtifactService`가 관리하는 아티팩트가 ADK 내에서 적절한 메커니즘입니다.


## 일반적인 사용 사례

아티팩트는 ADK 애플리케이션 내에서 바이너리 데이터를 처리하는 유연한 방법을 제공합니다.

다음은 아티팩트가 유용한 일반적인 시나리오입니다:

*   **생성된 보고서/파일:**
    *   도구나 에이전트가 보고서(예: PDF 분석, CSV 데이터 내보내기, 이미지 차트)를 생성합니다.

*   **사용자 업로드 처리:**

    *   사용자가 프론트엔드 인터페이스를 통해 파일(예: 분석용 이미지, 요약용 문서)을 업로드합니다.

*   **중간 바이너리 결과 저장:**

    *   에이전트가 한 단계에서 중간 바이너리 데이터(예: 오디오 합성, 시뮬레이션 결과)를 생성하는 복잡한 다단계 프로세스를 수행합니다.

*   **영구적인 사용자 데이터:**

    *   단순한 키-값 상태가 아닌 사용자별 구성 또는 데이터를 저장합니다.

*   **생성된 바이너리 콘텐츠 캐싱:**

    *   에이전트가 특정 입력에 기반하여 동일한 바이너리 출력(예: 회사 로고 이미지, 표준 오디오 인사말)을 자주 생성합니다.


## 핵심 개념

아티팩트를 이해하려면 몇 가지 핵심 구성 요소, 즉 이를 관리하는 서비스, 이를 담는 데 사용되는 데이터 구조, 그리고 식별 및 버전 관리 방법을 파악해야 합니다.

### 아티팩트 서비스 (`BaseArtifactService`)

*   **역할:** 아티팩트의 실제 저장 및 검색 로직을 담당하는 중앙 구성 요소입니다. 아티팩트가 *어떻게* 그리고 *어디에* 지속되는지를 정의합니다.

*   **인터페이스:** 추상 기본 클래스 `BaseArtifactService`에 의해 정의됩니다. 모든 구체적인 구현은 다음을 위한 메서드를 제공해야 합니다:

    *   `Save Artifact`: 아티팩트 데이터를 저장하고 할당된 버전 번호를 반환합니다.
    *   `Load Artifact`: 아티팩트의 특정 버전(또는 최신 버전)을 검색합니다.
    *   `List Artifact keys`: 주어진 범위 내의 아티팩트 고유 파일 이름을 나열합니다.
    *   `Delete Artifact`: 아티팩트(그리고 잠재적으로 모든 버전, 구현에 따라 다름)를 제거합니다.
    *   `List versions`: 특정 아티팩트 파일 이름에 대해 사용 가능한 모든 버전 번호를 나열합니다.

*   **구성:** `Runner`를 초기화할 때 아티팩트 서비스의 인스턴스(예: `InMemoryArtifactService`, `GcsArtifactService`)를 제공합니다. 그러면 `Runner`는 이 서비스를 `InvocationContext`를 통해 에이전트와 도구에서 사용할 수 있도록 합니다.

=== "Python"

    ```py
    from google.adk.runners import Runner
    from google.adk.artifacts import InMemoryArtifactService # 또는 GcsArtifactService
    from google.adk.agents import LlmAgent # 모든 에이전트
    from google.adk.sessions import InMemorySessionService

    # 예시: Runner를 아티팩트 서비스로 구성하기
    my_agent = LlmAgent(name="artifact_user_agent", model="gemini-2.0-flash")
    artifact_service = InMemoryArtifactService() # 구현체 선택
    session_service = InMemorySessionService()

    runner = Runner(
        agent=my_agent,
        app_name="my_artifact_app",
        session_service=session_service,
        artifact_service=artifact_service # 여기에 서비스 인스턴스 제공
    )
    # 이제 이 러너가 관리하는 실행 내의 컨텍스트에서 아티팩트 메서드를 사용할 수 있습니다.
    ```

=== "Java"
    
    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.runner.Runner;
    import com.google.adk.sessions.InMemorySessionService;
    import com.google.adk.artifacts.InMemoryArtifactService;
    
    // 예시: Runner를 아티팩트 서비스로 구성하기
    LlmAgent myAgent =  LlmAgent.builder()
      .name("artifact_user_agent")
      .model("gemini-2.0-flash")
      .build();
    InMemoryArtifactService artifactService = new InMemoryArtifactService(); // 구현체 선택
    InMemorySessionService sessionService = new InMemorySessionService();

    Runner runner = new Runner(myAgent, "my_artifact_app", artifactService, sessionService); // 여기에 서비스 인스턴스 제공
    // 이제 이 러너가 관리하는 실행 내의 컨텍스트에서 아티팩트 메서드를 사용할 수 있습니다.
    ```

### 아티팩트 데이터

*   **표준 표현:** 아티팩트 콘텐츠는 LLM 메시지의 일부에 사용되는 것과 동일한 구조인 `google.genai.types.Part` 객체를 사용하여 보편적으로 표현됩니다.

*   **핵심 속성 (`inline_data`):** 아티팩트의 경우 가장 관련 있는 속성은 `inline_data`이며, 이는 다음을 포함하는 `google.genai.types.Blob` 객체입니다:

    *   `data` (`bytes`): 아티팩트의 원시 바이너리 콘텐츠.
    *   `mime_type` (`str`): 바이너리 데이터의 특성을 설명하는 표준 MIME 유형 문자열(예: `'application/pdf'`, `'image/png'`, `'audio/mpeg'`). **이는 아티팩트를 로드할 때 올바른 해석을 위해 매우 중요합니다.**

=== "Python"

    ```python
    import google.genai.types as types

    # 예시: 원시 바이트로부터 아티팩트 Part 생성하기
    pdf_bytes = b'%PDF-1.4...' # 원시 PDF 데이터
    pdf_mime_type = "application/pdf"

    # 생성자 사용
    pdf_artifact_py = types.Part(
        inline_data=types.Blob(data=pdf_bytes, mime_type=pdf_mime_type)
    )

    # 편의 클래스 메서드 사용 (동일)
    pdf_artifact_alt_py = types.Part.from_bytes(data=pdf_bytes, mime_type=pdf_mime_type)

    print(f"생성된 Python 아티팩트의 MIME 유형: {pdf_artifact_py.inline_data.mime_type}")
    ```
    
=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/artifacts/ArtifactDataExample.java:full_code"
    ```

### 파일 이름 (Filename)

*   **식별자:** 특정 네임스페이스 내에서 아티팩트의 이름을 지정하고 검색하는 데 사용되는 간단한 문자열입니다.
*   **고유성:** 파일 이름은 해당 범위(세션 또는 사용자 네임스페이스) 내에서 고유해야 합니다.
*   **모범 사례:** 설명적인 이름을 사용하고, 파일 확장자(`"monthly_report.pdf"`, `"user_avatar.jpg"`)를 포함하는 것이 좋습니다. 확장자 자체는 동작을 결정하지 않지만, `mime_type`이 결정합니다.

### 버전 관리 (Versioning)

*   **자동 버전 관리:** 아티팩트 서비스는 자동으로 버전 관리를 처리합니다. `save_artifact`를 호출하면 서비스는 해당 특정 파일 이름과 범위에 대해 다음에 사용 가능한 버전 번호(일반적으로 0부터 시작하여 증가)를 결정합니다.
*   **`save_artifact` 반환 값:** `save_artifact` 메서드는 새로 저장된 아티팩트에 할당된 정수 버전 번호를 반환합니다.
*   **검색:**
  * `load_artifact(..., version=None)` (기본값): 아티팩트의 *최신* 버전을 검색합니다.
  * `load_artifact(..., version=N)`: 특정 버전 `N`을 검색합니다.
*   **버전 목록:** `list_versions` 메서드(컨텍스트가 아닌 서비스에 있음)를 사용하여 아티팩트의 모든 기존 버전 번호를 찾을 수 있습니다.

### 네임스페이스 (세션 vs. 사용자)

*   **개념:** 아티팩트는 특정 세션에만 국한되거나, 애플리케이션 내 모든 세션에 걸쳐 사용자에게 더 광범위하게 적용될 수 있습니다. 이 범위 지정은 `filename` 형식에 의해 결정되며 `ArtifactService`에 의해 내부적으로 처리됩니다.

*   **기본값 (세션 범위):** `"report.pdf"`와 같은 일반 파일 이름을 사용하면 아티팩트는 특정 `app_name`, `user_id` *및* `session_id`와 연결됩니다. 해당 세션 컨텍스트 내에서만 접근할 수 있습니다.


*   **사용자 범위 (`"user:"` 접두사):** 파일 이름에 `"user:"` 접두사를 붙여 `"user:profile.png"`와 같이 사용하면 아티팩트는 `app_name`과 `user_id`에만 연결됩니다. 해당 앱 내에서 해당 사용자에 속한 *모든* 세션에서 접근하거나 업데이트할 수 있습니다.


=== "Python"

    ```python
    # 네임스페이스 차이를 설명하는 예시 (개념적)

    # 세션별 아티팩트 파일 이름
    session_report_filename = "summary.txt"

    # 사용자별 아티팩트 파일 이름
    user_config_filename = "user:settings.json"

    # context.save_artifact를 통해 'summary.txt'를 저장할 때,
    # 현재 app_name, user_id, session_id에 연결됩니다.

    # context.save_artifact를 통해 'user:settings.json'을 저장할 때,
    # ArtifactService 구현은 "user:" 접두사를 인식해야 하며
    # 이를 app_name과 user_id로 범위를 지정하여 해당 사용자의 모든 세션에서 접근할 수 있도록 합니다.
    ```

=== "Java"

    ```java
    // 네임스페이스 차이를 설명하는 예시 (개념적)
    
    // 세션별 아티팩트 파일 이름
    String sessionReportFilename = "summary.txt";
    
    // 사용자별 아티팩트 파일 이름
    String userConfigFilename = "user:settings.json"; // "user:" 접두사가 핵심
    
    // context.save_artifact를 통해 'summary.txt'를 저장할 때,
    // 현재 app_name, user_id, session_id에 연결됩니다.
    // artifactService.saveArtifact(appName, userId, sessionId1, sessionReportFilename, someData);
    
    // context.save_artifact를 통해 'user:settings.json'을 저장할 때,
    // ArtifactService 구현은 "user:" 접두사를 인식해야 하며
    // 이를 app_name과 user_id로 범위를 지정하여 해당 사용자의 모든 세션에서 접근할 수 있도록 합니다.
    // artifactService.saveArtifact(appName, userId, sessionId1, userConfigFilename, someData);
    ```

이러한 핵심 개념들은 ADK 프레임워크 내에서 바이너리 데이터를 관리하기 위한 유연한 시스템을 제공하기 위해 함께 작동합니다.

## 아티팩트와 상호작용하기 (컨텍스트 객체를 통해)

에이전트 로직(특히 콜백이나 도구 내)에서 아티팩트와 상호작용하는 주요 방법은 `CallbackContext`와 `ToolContext` 객체에서 제공하는 메서드를 통하는 것입니다. 이 메서드들은 `ArtifactService`가 관리하는 기본 스토리지 세부 정보를 추상화합니다.

### 전제 조건: `ArtifactService` 구성하기

컨텍스트 객체를 통해 아티팩트 메서드를 사용하기 전에, `Runner`를 초기화할 때 **반드시** [`BaseArtifactService` 구현체](#available-implementations)의 인스턴스([`InMemoryArtifactService`](#inmemoryartifactservice) 또는 [`GcsArtifactService`](#gcsartifactservice) 등)를 제공해야 합니다.

=== "Python"

    Python에서는 `Runner`를 초기화할 때 이 인스턴스를 제공합니다.

    ```python
    from google.adk.runners import Runner
    from google.adk.artifacts import InMemoryArtifactService # 또는 GcsArtifactService
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService

    # 에이전트 정의
    agent = LlmAgent(name="my_agent", model="gemini-2.0-flash")

    # 원하는 아티팩트 서비스 인스턴스화
    artifact_service = InMemoryArtifactService()

    # Runner에 제공
    runner = Runner(
        agent=agent,
        app_name="artifact_app",
        session_service=InMemorySessionService(),
        artifact_service=artifact_service # 서비스는 여기에 제공되어야 함
    )
    ```
    `InvocationContext`에 `artifact_service`가 구성되어 있지 않으면(즉, `Runner`에 전달되지 않은 경우), 컨텍스트 객체에서 `save_artifact`, `load_artifact`, 또는 `list_artifacts`를 호출하면 `ValueError`가 발생합니다.

=== "Java"

    Java에서는 `BaseArtifactService` 구현을 인스턴스화한 다음, 아티팩트를 관리하는 애플리케이션의 부분에서 접근할 수 있도록 해야 합니다. 이는 종종 의존성 주입을 통하거나 서비스 인스턴스를 명시적으로 전달하여 수행됩니다.

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.artifacts.InMemoryArtifactService; // 또는 GcsArtifactService
    import com.google.adk.runner.Runner;
    import com.google.adk.sessions.InMemorySessionService;
    
    public class SampleArtifactAgent {
    
      public static void main(String[] args) {
    
        // 에이전트 정의
        LlmAgent agent = LlmAgent.builder()
            .name("my_agent")
            .model("gemini-2.0-flash")
            .build();
    
        // 원하는 아티팩트 서비스 인스턴스화
        InMemoryArtifactService artifactService = new InMemoryArtifactService();
    
        // Runner에 제공
        Runner runner = new Runner(agent,
            "APP_NAME",
            artifactService, // 서비스는 여기에 제공되어야 함
            new InMemorySessionService());
    
      }
    }
    ```
    Java에서 아티팩트 작업이 시도될 때 `ArtifactService` 인스턴스를 사용할 수 없는 경우(예: `null`), 애플리케이션 구조에 따라 일반적으로 `NullPointerException`이나 사용자 정의 오류가 발생합니다. 견고한 애플리케이션은 종종 의존성 주입 프레임워크를 사용하여 서비스 수명 주기를 관리하고 가용성을 보장합니다.


### 메서드 접근하기

아티팩트 상호작용 메서드는 `CallbackContext`(에이전트 및 모델 콜백에 전달됨)와 `ToolContext`(도구 콜백에 전달됨)의 인스턴스에서 직접 사용할 수 있습니다. `ToolContext`는 `CallbackContext`를 상속한다는 점을 기억하세요.

*   **코드 예제:**

    === "Python"

        ```python
        import google.genai.types as types
        from google.adk.agents.callback_context import CallbackContext # 또는 ToolContext

        async def save_generated_report_py(context: CallbackContext, report_bytes: bytes):
            """생성된 PDF 보고서 바이트를 아티팩트로 저장합니다."""
            report_artifact = types.Part.from_data(
                data=report_bytes,
                mime_type="application/pdf"
            )
            filename = "generated_report.pdf"

            try:
                version = await context.save_artifact(filename=filename, artifact=report_artifact)
                print(f"Python 아티팩트 '{filename}'를 버전 {version}으로 성공적으로 저장했습니다.")
                # 이 콜백 이후에 생성된 이벤트는 다음을 포함합니다:
                # event.actions.artifact_delta == {"generated_report.pdf": version}
            except ValueError as e:
                print(f"Python 아티팩트 저장 오류: {e}. Runner에 ArtifactService가 구성되어 있나요?")
            except Exception as e:
                # 잠재적인 스토리지 오류 처리 (예: GCS 권한)
                print(f"Python 아티팩트 저장 중 예기치 않은 오류 발생: {e}")

        # --- 예제 사용 개념 (Python) ---
        # async def main_py():
        #   callback_context: CallbackContext = ... # 컨텍스트 얻기
        #   report_data = b'...' # PDF 바이트를 담고 있다고 가정
        #   await save_generated_report_py(callback_context, report_data)
        ```

    === "Java"
    
        ```java
        import com.google.adk.agents.CallbackContext;
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.adk.artifacts.InMemoryArtifactService;
        import com.google.genai.types.Part;
        import java.nio.charset.StandardCharsets;

        public class SaveArtifactExample {

        public void saveGeneratedReport(CallbackContext callbackContext, byte[] reportBytes) {
        // 생성된 PDF 보고서 바이트를 아티팩트로 저장합니다.
        Part reportArtifact = Part.fromBytes(reportBytes, "application/pdf");
        String filename = "generatedReport.pdf";

            callbackContext.saveArtifact(filename, reportArtifact);
            System.out.println("Java 아티팩트 '" + filename + "'를 성공적으로 저장했습니다.");
            // 이 콜백 이후에 생성된 이벤트는 다음을 포함합니다:
            // event().actions().artifactDelta == {"generated_report.pdf": version}
        }

        // --- 예제 사용 개념 (Java) ---
        public static void main(String[] args) {
            BaseArtifactService service = new InMemoryArtifactService(); // 또는 GcsArtifactService
            SaveArtifactExample myTool = new SaveArtifactExample();
            byte[] reportData = "...".getBytes(StandardCharsets.UTF_8); // PDF 바이트
            CallbackContext callbackContext; // ... 앱에서 콜백 컨텍스트 얻기
            myTool.saveGeneratedReport(callbackContext, reportData);
            // 비동기 특성으로 인해 실제 앱에서는 프로그램이 완료를 기다리거나 처리하도록 해야 합니다.
          }
        }
        ```

#### 아티팩트 로드하기

*   **코드 예제:**

    === "Python"

        ```python
        import google.genai.types as types
        from google.adk.agents.callback_context import CallbackContext # 또는 ToolContext

        async def process_latest_report_py(context: CallbackContext):
            """최신 보고서 아티팩트를 로드하고 데이터를 처리합니다."""
            filename = "generated_report.pdf"
            try:
                # 최신 버전 로드
                report_artifact = await context.load_artifact(filename=filename)

                if report_artifact and report_artifact.inline_data:
                    print(f"최신 Python 아티팩트 '{filename}'를 성공적으로 로드했습니다.")
                    print(f"MIME 유형: {report_artifact.inline_data.mime_type}")
                    # report_artifact.inline_data.data (바이트) 처리
                    pdf_bytes = report_artifact.inline_data.data
                    print(f"보고서 크기: {len(pdf_bytes)} 바이트.")
                    # ... 추가 처리 ...
                else:
                    print(f"Python 아티팩트 '{filename}'를 찾을 수 없습니다.")

                # 예제: 특정 버전 로드 (버전 0이 존재하는 경우)
                # specific_version_artifact = await context.load_artifact(filename=filename, version=0)
                # if specific_version_artifact:
                #     print(f"'{filename}'의 버전 0을 로드했습니다.")

            except ValueError as e:
                print(f"Python 아티팩트 로드 오류: {e}. ArtifactService가 구성되어 있나요?")
            except Exception as e:
                # 잠재적인 스토리지 오류 처리
                print(f"Python 아티팩트 로드 중 예기치 않은 오류 발생: {e}")

        # --- 예제 사용 개념 (Python) ---
        # async def main_py():
        #   callback_context: CallbackContext = ... # 컨텍스트 얻기
        #   await process_latest_report_py(callback_context)
        ```

    === "Java"

        ```java
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.genai.types.Part;
        import io.reactivex.rxjava3.core.MaybeObserver;
        import io.reactivex.rxjava3.disposables.Disposable;
        import java.util.Optional;

        public class MyArtifactLoaderService {

            private final BaseArtifactService artifactService;
            private final String appName;

            public MyArtifactLoaderService(BaseArtifactService artifactService, String appName) {
                this.artifactService = artifactService;
                this.appName = appName;
            }

            public void processLatestReportJava(String userId, String sessionId, String filename) {
                // 버전에 Optional.empty()를 전달하여 최신 버전 로드
                artifactService
                        .loadArtifact(appName, userId, sessionId, filename, Optional.empty())
                        .subscribe(
                                new MaybeObserver<Part>() {
                                    @Override
                                    public void onSubscribe(Disposable d) {
                                        // 선택 사항: 구독 처리
                                    }

                                    @Override
                                    public void onSuccess(Part reportArtifact) {
                                        System.out.println(
                                                "최신 Java 아티팩트 '" + filename + "'를 성공적으로 로드했습니다.");
                                        reportArtifact
                                                .inlineData()
                                                .ifPresent(
                                                        blob -> {
                                                            System.out.println(
                                                                    "MIME 유형: " + blob.mimeType().orElse("N/A"));
                                                            byte[] pdfBytes = blob.data().orElse(new byte[0]);
                                                            System.out.println("보고서 크기: " + pdfBytes.length + " 바이트.");
                                                            // ... pdfBytes 추가 처리 ...
                                                        });
                                    }

                                    @Override
                                    public void onError(Throwable e) {
                                        // 잠재적인 스토리지 오류 또는 다른 예외 처리
                                        System.err.println(
                                                "Java 아티팩트 '"
                                                        + filename
                                                        + "' 로드 중 오류 발생: "
                                                        + e.getMessage());
                                    }

                                    @Override
                                    public void onComplete() {
                                        // 아티팩트(최신 버전)를 찾을 수 없는 경우 호출됨
                                        System.out.println("Java 아티팩트 '" + filename + "'를 찾을 수 없습니다.");
                                    }
                                });

                // 예제: 특정 버전 로드 (예: 버전 0)
                /*
                artifactService.loadArtifact(appName, userId, sessionId, filename, Optional.of(0))
                    .subscribe(part -> {
                        System.out.println("Java 아티팩트 '" + filename + "'의 버전 0을 로드했습니다.");
                    }, throwable -> {
                        System.err.println("'" + filename + "'의 버전 0 로드 오류: " + throwable.getMessage());
                    }, () -> {
                        System.out.println("Java 아티팩트 '" + filename + "'의 버전 0을 찾을 수 없습니다.");
                    });
                */
            }

            // --- 예제 사용 개념 (Java) ---
            public static void main(String[] args) {
                // BaseArtifactService service = new InMemoryArtifactService(); // 또는 GcsArtifactService
                // MyArtifactLoaderService loader = new MyArtifactLoaderService(service, "myJavaApp");
                // loader.processLatestReportJava("user123", "sessionABC", "java_report.pdf");
                // 비동기 특성으로 인해 실제 앱에서는 프로그램이 완료를 기다리거나 처리하도록 해야 합니다.
            }
        }
        ```

#### 아티팩트 파일 이름 목록 보기

*   **코드 예제:**

    === "Python"

        ```python
        from google.adk.tools.tool_context import ToolContext

        def list_user_files_py(tool_context: ToolContext) -> str:
            """사용 가능한 아티팩트 목록을 사용자에게 제공하는 도구입니다."""
            try:
                available_files = await tool_context.list_artifacts()
                if not available_files:
                    return "저장된 아티팩트가 없습니다."
                else:
                    # 사용자/LLM을 위한 목록 형식 지정
                    file_list_str = "\n".join([f"- {fname}" for fname in available_files])
                    return f"사용 가능한 Python 아티팩트는 다음과 같습니다:\n{file_list_str}"
            except ValueError as e:
                print(f"Python 아티팩트 목록 보기 오류: {e}. ArtifactService가 구성되어 있나요?")
                return "오류: Python 아티팩트 목록을 볼 수 없습니다."
            except Exception as e:
                print(f"Python 아티팩트 목록 보기 중 예기치 않은 오류 발생: {e}")
                return "오류: Python 아티팩트 목록을 보는 동안 예기치 않은 오류가 발생했습니다."

        # 이 함수는 일반적으로 FunctionTool로 래핑됩니다.
        # from google.adk.tools import FunctionTool
        # list_files_tool = FunctionTool(func=list_user_files_py)
        ```

    === "Java"

        ```java
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.adk.artifacts.ListArtifactsResponse;
        import com.google.common.collect.ImmutableList;
        import io.reactivex.rxjava3.core.SingleObserver;
        import io.reactivex.rxjava3.disposables.Disposable;

        public class MyArtifactListerService {

            private final BaseArtifactService artifactService;
            private final String appName;

            public MyArtifactListerService(BaseArtifactService artifactService, String appName) {
                this.artifactService = artifactService;
                this.appName = appName;
            }

            // 도구나 에이전트 로직에 의해 호출될 수 있는 예제 메서드
            public void listUserFilesJava(String userId, String sessionId) {
                artifactService
                        .listArtifactKeys(appName, userId, sessionId)
                        .subscribe(
                                new SingleObserver<ListArtifactsResponse>() {
                                    @Override
                                    public void onSubscribe(Disposable d) {
                                        // 선택 사항: 구독 처리
                                    }

                                    @Override
                                    public void onSuccess(ListArtifactsResponse response) {
                                        ImmutableList<String> availableFiles = response.filenames();
                                        if (availableFiles.isEmpty()) {
                                            System.out.println(
                                                    "사용자 "
                                                            + userId
                                                            + " (세션 "
                                                            + sessionId
                                                            + ") 에는 저장된 Java 아티팩트가 없습니다.");
                                        } else {
                                            StringBuilder fileListStr =
                                                    new StringBuilder(
                                                            "사용자 "
                                                                    + userId
                                                                    + " (세션 "
                                                                    + sessionId
                                                                    + ") 의 사용 가능한 Java 아티팩트는 다음과 같습니다:\n");
                                            for (String fname : availableFiles) {
                                                fileListStr.append("- ").append(fname).append("\n");
                                            }
                                            System.out.println(fileListStr.toString());
                                        }
                                    }

                                    @Override
                                    public void onError(Throwable e) {
                                        System.err.println(
                                                "사용자 "
                                                        + userId
                                                        + " (세션 "
                                                        + sessionId
                                                        + ") 의 Java 아티팩트 목록 보기 오류: "
                                                        + e.getMessage());
                                        // 실제 애플리케이션에서는 사용자/LLM에게 오류 메시지를 반환할 수 있습니다.
                                    }
                                });
            }

            // --- 예제 사용 개념 (Java) ---
            public static void main(String[] args) {
                // BaseArtifactService service = new InMemoryArtifactService(); // 또는 GcsArtifactService
                // MyArtifactListerService lister = new MyArtifactListerService(service, "myJavaApp");
                // lister.listUserFilesJava("user123", "sessionABC");
                // 비동기 특성으로 인해 실제 앱에서는 프로그램이 완료를 기다리거나 처리하도록 해야 합니다.
            }
        }
        ```

저장, 로드, 목록 보기 메서드는 Python의 컨텍스트 객체를 사용하든 Java에서 `BaseArtifactService`와 직접 상호작용하든, 선택한 백엔드 스토리지 구현에 관계없이 바이너리 데이터 지속성을 관리하는 편리하고 일관된 방법을 제공합니다.

## 사용 가능한 구현체

ADK는 `BaseArtifactService` 인터페이스의 구체적인 구현을 제공하여 다양한 개발 단계 및 배포 요구에 적합한 다양한 스토리지 백엔드를 제공합니다. 이러한 구현체는 `app_name`, `user_id`, `session_id` 및 `filename`(`user:` 네임스페이스 접두사 포함)을 기반으로 아티팩트 데이터를 저장, 버전 관리 및 검색하는 세부 사항을 처리합니다.

### InMemoryArtifactService

*   **스토리지 메커니즘:**
    *   Python: 애플리케이션의 메모리에 유지되는 Python 사전(`self.artifacts`)을 사용합니다. 사전 키는 아티팩트 경로를 나타내고 값은 `types.Part`의 리스트이며, 각 리스트 요소는 버전입니다.
    *   Java: 메모리에 유지되는 중첩된 `HashMap` 인스턴스(`private final Map<String, Map<String, Map<String, Map<String, List<Part>>>>> artifacts;`)를 사용합니다. 각 수준의 키는 각각 `appName`, `userId`, `sessionId`, `filename`입니다. 가장 안쪽의 `List<Part>`는 아티팩트의 버전을 저장하며, 리스트 인덱스는 버전 번호에 해당합니다.
*   **주요 특징:**
    *   **단순성:** 핵심 ADK 라이브러리 외에 외부 설정이나 종속성이 필요하지 않습니다.
    *   **속도:** 작업은 일반적으로 인메모리 맵/사전 조회 및 리스트 조작을 포함하므로 매우 빠릅니다.
    *   **휘발성:** 저장된 모든 아티팩트는 애플리케이션 프로세스가 종료될 때 **손실됩니다**. 데이터는 애플리케이션 재시작 사이에 지속되지 않습니다.
*   **사용 사례:**
    *   지속성이 필요하지 않은 로컬 개발 및 테스트에 이상적입니다.
    *   단기적인 데모나 아티팩트 데이터가 애플리케이션의 단일 실행 내에서 순수하게 임시적인 시나리오에 적합합니다.
*   **인스턴스화:**

    === "Python"

        ```python
        from google.adk.artifacts import InMemoryArtifactService

        # 클래스를 간단히 인스턴스화
        in_memory_service_py = InMemoryArtifactService()

        # 그런 다음 Runner에 전달
        # runner = Runner(..., artifact_service=in_memory_service_py)
        ```

    === "Java"

        ```java
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.adk.artifacts.InMemoryArtifactService;

        public class InMemoryServiceSetup {
            public static void main(String[] args) {
                // 클래스를 간단히 인스턴스화
                BaseArtifactService inMemoryServiceJava = new InMemoryArtifactService();

                System.out.println("InMemoryArtifactService (Java) 인스턴스화됨: " + inMemoryServiceJava.getClass().getName());

                // 이 인스턴스는 Runner에 제공됩니다.
                // Runner runner = new Runner(
                //     /* 다른 서비스들 */,
                //     inMemoryServiceJava
                // );
            }
        }
        ```

### GcsArtifactService


*   **스토리지 메커니즘:** 영구적인 아티팩트 저장을 위해 Google Cloud Storage(GCS)를 활용합니다. 아티팩트의 각 버전은 지정된 GCS 버킷 내에 별도의 객체(blob)로 저장됩니다.
*   **객체 명명 규칙:** 계층적 경로 구조를 사용하여 GCS 객체 이름(blob 이름)을 구성합니다.
*   **주요 특징:**
    *   **지속성:** GCS에 저장된 아티팩트는 애플리케이션 재시작 및 배포 전반에 걸쳐 지속됩니다.
    *   **확장성:** Google Cloud Storage의 확장성과 내구성을 활용합니다.
    *   **버전 관리:** 각 버전을 별개의 GCS 객체로 명시적으로 저장합니다. `GcsArtifactService`의 `saveArtifact` 메서드.
    *   **필요한 권한:** 애플리케이션 환경에는 지정된 GCS 버킷에서 읽고 쓸 수 있는 적절한 자격 증명(예: 애플리케이션 기본 자격 증명)과 IAM 권한이 필요합니다.
*   **사용 사례:**
    *   영구적인 아티팩트 저장이 필요한 프로덕션 환경.
    *   아티팩트가 다른 애플리케이션 인스턴스나 서비스 간에 공유되어야 하는 시나리오(동일한 GCS 버킷에 액세스함으로써).
    *   사용자 또는 세션 데이터의 장기 저장 및 검색이 필요한 애플리케이션.
*   **인스턴스화:**

    === "Python"

        ```python
        from google.adk.artifacts import GcsArtifactService

        # GCS 버킷 이름 지정
        gcs_bucket_name_py = "your-gcs-bucket-for-adk-artifacts" # 버킷 이름으로 교체

        try:
            gcs_service_py = GcsArtifactService(bucket_name=gcs_bucket_name_py)
            print(f"Python GcsArtifactService가 버킷에 대해 초기화됨: {gcs_bucket_name_py}")
            # 환경에 이 버킷에 액세스할 자격 증명이 있는지 확인하세요.
            # 예: 애플리케이션 기본 자격 증명(ADC)을 통해

            # 그런 다음 Runner에 전달
            # runner = Runner(..., artifact_service=gcs_service_py)

        except Exception as e:
            # GCS 클라이언트 초기화 중 잠재적인 오류 포착 (예: 인증 문제)
            print(f"Python GcsArtifactService 초기화 오류: {e}")
            # 오류를 적절하게 처리 - InMemory로 대체하거나 예외 발생
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/artifacts/GcsServiceSetup.java:full_code"
        ```

적절한 `ArtifactService` 구현을 선택하는 것은 애플리케이션의 데이터 지속성, 확장성 및 운영 환경 요구 사항에 따라 달라집니다.

## 모범 사례

아티팩트를 효과적이고 유지 관리 가능하게 사용하려면:

*   **올바른 서비스 선택:** 빠른 프로토타이핑, 테스트 및 지속성이 필요하지 않은 시나리오에는 `InMemoryArtifactService`를 사용하세요. 데이터 지속성 및 확장성이 필요한 프로덕션 환경에는 `GcsArtifactService`(또는 다른 백엔드를 위한 자체 `BaseArtifactService` 구현)를 사용하세요.
*   **의미 있는 파일 이름:** 명확하고 설명적인 파일 이름을 사용하세요. 관련 확장자(`.pdf`, `.png`, `.wav`)를 포함하면 `mime_type`이 프로그래밍 방식의 처리를 결정하지만, 사람이 내용을 이해하는 데 도움이 됩니다. 임시 아티팩트 이름과 영구 아티팩트 이름에 대한 규칙을 설정하세요.
*   **올바른 MIME 유형 지정:** `save_artifact`를 위해 `types.Part`를 생성할 때 항상 정확한 `mime_type`을 제공하세요. 이는 나중에 `load_artifact`하는 애플리케이션이나 도구가 `bytes` 데이터를 올바르게 해석하는 데 중요합니다. 가능한 경우 표준 IANA MIME 유형을 사용하세요.
*   **버전 관리 이해:** 특정 `version` 인수 없이 `load_artifact()`를 호출하면 *최신* 버전을 검색한다는 점을 기억하세요. 로직이 아티팩트의 특정 과거 버전에 의존하는 경우, 로드할 때 정수 버전 번호를 제공해야 합니다.
*   **네임스페이스 (`user:`) 신중하게 사용:** 데이터가 진정으로 사용자에게 속하고 모든 세션에서 접근 가능해야 하는 경우에만 파일 이름에 `"user:"` 접두사를 사용하세요. 단일 대화나 세션에 특정한 데이터의 경우 접두사 없이 일반 파일 이름을 사용하세요.
*   **오류 처리:**
    *   컨텍스트 메서드(`save_artifact`, `load_artifact`, `list_artifacts`)를 호출하기 전에 `artifact_service`가 실제로 구성되었는지 항상 확인하세요. 서비스가 `None`이면 `ValueError`가 발생합니다.
    *   `load_artifact`의 반환 값을 확인하세요. 아티팩트나 버전이 존재하지 않으면 `None`이 됩니다. 항상 `Part`를 반환한다고 가정하지 마세요.
    *   특히 `GcsArtifactService`의 경우 기본 스토리지 서비스에서 발생하는 예외(예: 권한 문제에 대한 `google.api_core.exceptions.Forbidden`, 버킷이 없는 경우 `NotFound`, 네트워크 오류)를 처리할 준비를 하세요.
*   **크기 고려 사항:** 아티팩트는 일반적인 파일 크기에 적합하지만, 특히 클라우드 스토리지의 경우 매우 큰 파일로 인한 잠재적인 비용 및 성능 영향을 염두에 두세요. `InMemoryArtifactService`는 많은 대용량 아티팩트를 저장할 경우 상당한 메모리를 소비할 수 있습니다. 매우 큰 데이터가 전체 바이트 배열을 메모리에 전달하는 대신 직접적인 GCS 링크나 다른 전문 스토리지 솔루션을 통해 더 잘 처리될 수 있는지 평가하세요.
*   **정리 전략:** `GcsArtifactService`와 같은 영구 스토리지의 경우, 아티팩트는 명시적으로 삭제될 때까지 남아 있습니다. 아티팩트가 임시 데이터를 나타내거나 수명이 제한된 경우 정리 전략을 구현하세요. 여기에는 다음이 포함될 수 있습니다:
    *   버킷에 GCS 수명 주기 정책 사용.
    *   `artifact_service.delete_artifact` 메서드를 활용하는 특정 도구나 관리 기능 구축(참고: 안전을 위해 delete는 컨텍스트 객체를 통해 노출되지 않음).
    *   필요한 경우 패턴 기반 삭제를 허용하도록 파일 이름을 신중하게 관리.