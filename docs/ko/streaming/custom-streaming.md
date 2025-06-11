# 커스텀 오디오 스트리밍 앱 (SSE) {#custom-streaming}

이 문서는 ADK 스트리밍과 [FastAPI](https://fastapi.tiangolo.com/)를 사용하여 구축된 커스텀 비동기 웹 앱의 서버 및 클라이언트 코드를 전체적으로 살펴봅니다. 이 앱은 서버-전송 이벤트(Server-Sent Events, SSE)를 통해 실시간 양방향 오디오 및 텍스트 통신을 구현합니다. 주요 기능은 다음과 같습니다.

**서버 측 (Python/FastAPI)**:
- FastAPI와 ADK 통합
- 실시간 스트리밍을 위한 서버-전송 이벤트(SSE)
- 분리된 사용자 컨텍스트를 통한 세션 관리
- 텍스트 및 오디오 통신 모드 모두 지원
- 근거 기반 응답을 위한 Google Search 도구 통합

**클라이언트 측 (JavaScript/Web Audio API)**:
- SSE와 HTTP POST를 통한 실시간 양방향 통신
- AudioWorklet 프로세서를 사용한 전문적인 오디오 처리
- 텍스트와 오디오 간의 원활한 모드 전환
- 자동 재연결 및 오류 처리
- 오디오 데이터 전송을 위한 Base64 인코딩

해당 샘플은 [WebSocket](custom-streaming-ws.md) 버전으로도 제공됩니다.

## 1. ADK 설치 {#1.-setup-installation}

가상 환경 생성 및 활성화 (권장):

```bash
# 생성
python -m venv .venv
# 활성화 (새 터미널마다 실행)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

ADK 설치:

```bash
pip install --upgrade google-adk==1.2.1
```

다음 명령어로 `SSL_CERT_FILE` 변수를 설정합니다.

```shell
export SSL_CERT_FILE=$(python -m certifi)
```

샘플 코드 다운로드:

```bash
git clone --no-checkout https://github.com/google/adk-docs.git
cd adk-docs
git sparse-checkout init --cone
git sparse-checkout set examples/python/snippets/streaming/adk-streaming
git checkout main
cd examples/python/snippets/streaming/adk-streaming/app
```

이 샘플 코드는 다음과 같은 파일과 폴더 구조를 가집니다:

```console
adk-streaming/
└── app/ # 웹 앱 폴더
    ├── .env # Gemini API 키 / Google Cloud 프로젝트 ID
    ├── main.py # FastAPI 웹 앱
    ├── static/ # 정적 콘텐츠 폴더
    |   ├── js # JavaScript 파일 폴더 (app.js 포함)
    |   └── index.html # 웹 클라이언트 페이지
    └── google_search_agent/ # 에이전트 폴더
        ├── __init__.py # Python 패키지
        └── agent.py # 에이전트 정의
```

## 2. 플랫폼 설정 {#2.-set-up-the-platform}

샘플 앱을 실행하려면 Google AI Studio 또는 Google Cloud Vertex AI 중에서 플랫폼을 선택하세요.

=== "Gemini - Google AI Studio"
    1. [Google AI Studio](https://aistudio.google.com/apikey)에서 API 키를 발급받으세요.
    2. `app/` 폴더에 있는 **`.env`** 파일을 열고 다음 코드를 복사하여 붙여넣으세요.

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3. `PASTE_YOUR_ACTUAL_API_KEY_HERE`를 실제 `API 키`로 교체하세요.

=== "Gemini - Google Cloud Vertex AI"
    1. 기존 [Google Cloud](https://cloud.google.com/?e=48754805&hl=en) 계정과 프로젝트가 필요합니다.
        * [Google Cloud 프로젝트 설정하기](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
        * [gcloud CLI 설정하기](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
        * 터미널에서 `gcloud auth login`을 실행하여 Google Cloud에 인증합니다.
        * [Vertex AI API 활성화하기](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com).
    2. `app/` 폴더에 있는 **`.env`** 파일을 엽니다. 다음 코드를 복사하여 붙여넣고 프로젝트 ID와 위치(location)를 업데이트하세요.

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=PASTE_YOUR_ACTUAL_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=us-central1
        ```

## 3. 스트리밍 앱과 상호작용하기 {#3.-interact-with-your-streaming-app}

1. **올바른 디렉터리로 이동:**

   에이전트를 효과적으로 실행하려면 **app 폴더 (`adk-streaming/app`)** 에 있는지 확인하세요.

2. **FastAPI 서버 시작**: 다음 명령어를 실행하여 CLI 인터페이스를 시작합니다.

```console
uvicorn main:app --reload
```

3. **텍스트 모드로 앱 접속:** 앱이 시작되면 터미널에 로컬 URL(예: [http://localhost:8000](http://localhost:8000))이 표시됩니다. 이 링크를 클릭하여 브라우저에서 UI를 여세요.

이제 다음과 같은 UI가 보일 것입니다:

![ADK Streaming app](../assets/adk-streaming-text.png)

`지금 몇 시야?`와 같은 질문을 해보세요. 에이전트는 Google Search를 사용하여 여러분의 질문에 응답할 것입니다. UI가 에이전트의 응답을 스트리밍 텍스트로 보여주는 것을 볼 수 있습니다. 또한, 에이전트가 응답하는 중에도 언제든지 메시지를 보낼 수 있습니다. 이를 통해 ADK 스트리밍의 양방향 통신 기능을 확인할 수 있습니다.

4. **오디오 모드로 앱 접속:** 이제 `Start Audio` 버튼을 클릭하세요. 앱은 오디오 모드로 서버에 다시 연결되며, 처음에는 UI에 다음과 같은 대화 상자가 표시됩니다.

![ADK Streaming app](../assets/adk-streaming-audio-dialog.png)

`사이트를 방문하는 동안 허용`을 클릭하면 브라우저 상단에 마이크 아이콘이 표시됩니다.

![ADK Streaming app](../assets/adk-streaming-mic.png)

이제 음성으로 에이전트와 대화할 수 있습니다. `지금 몇 시야?`와 같은 질문을 음성으로 하면 에이전트도 음성으로 응답하는 것을 들을 수 있습니다. ADK 스트리밍은 [여러 언어](https://ai.google.dev/gemini-api/docs/live#supported-languages)를 지원하므로, 지원되는 언어로 질문하면 해당 언어로 응답할 수도 있습니다.

5. **콘솔 로그 확인**

Chrome 브라우저를 사용 중이라면, 마우스 오른쪽 버튼을 클릭하고 `검사(Inspect)`를 선택하여 개발자 도구(DevTools)를 여세요. `콘솔(Console)` 탭에서 `[CLIENT TO AGENT]`와 `[AGENT TO CLIENT]`와 같이 들어오고 나가는 오디오 데이터를 볼 수 있으며, 이는 브라우저와 서버 간에 오디오 데이터가 스트리밍되고 있음을 나타냅니다.

동시에 앱 서버 콘솔에서는 다음과 같은 내용을 볼 수 있습니다:

```
Client #90766266 connected via SSE, audio mode: false
INFO:     127.0.0.1:52692 - "GET /events/90766266?is_audio=false HTTP/1.1" 200 OK
[CLIENT TO AGENT]: hi
INFO:     127.0.0.1:52696 - "POST /send/90766266 HTTP/1.1" 200 OK
[AGENT TO CLIENT]: text/plain: {'mime_type': 'text/plain', 'data': 'Hi'}
[AGENT TO CLIENT]: text/plain: {'mime_type': 'text/plain', 'data': ' there! How can I help you today?\n'}
[AGENT TO CLIENT]: {'turn_complete': True, 'interrupted': None}
```

이러한 콘솔 로그는 자체 스트리밍 애플리케이션을 개발할 때 중요합니다. 많은 경우, 브라우저와 서버 간의 통신 실패가 스트리밍 애플리케이션 버그의 주요 원인이 됩니다.

6. **문제 해결 팁**

- **브라우저가 SSH 프록시를 통해 서버에 연결할 수 없는 경우:** 다양한 클라우드 서비스에서 사용되는 SSH 프록시는 SSE와 호환되지 않을 수 있습니다. SSH 프록시 없이 로컬 노트북 등에서 시도하거나, [WebSocket](custom-streaming-ws.md) 버전을 사용해 보세요.
- **`gemini-2.0-flash-exp` 모델이 작동하지 않는 경우:** 앱 서버 콘솔에서 `gemini-2.0-flash-exp` 모델 가용성과 관련된 오류가 표시되면, `app/google_search_agent/agent.py` 파일의 6번째 줄에서 해당 모델을 `gemini-2.0-flash-live-001`로 교체해 보세요.

## 4. 에이전트 정의

`google_search_agent` 폴더의 에이전트 정의 코드 `agent.py` 파일은 에이전트의 로직이 작성되는 곳입니다.

```py
from google.adk.agents import Agent
from google.adk.tools import google_search  # 도구 임포트

root_agent = Agent(
   name="google_search_agent",
   model="gemini-2.0-flash-exp", # 이 모델이 작동하지 않으면 아래 모델을 시도해 보세요
   #model="gemini-2.0-flash-live-001",
   description="Agent to answer questions using Google Search.",
   instruction="Answer the question using the Google Search tool.",
   tools=[google_search],
)
```

[Google Search를 통한 근거 기반(grounding) 기능](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search)을 얼마나 쉽게 통합했는지 주목하세요. `Agent` 클래스와 `google_search` 도구가 LLM과의 복잡한 상호작용과 검색 API를 통한 근거 기반 작업을 처리하므로, 개발자는 에이전트의 *목적*과 *동작*에만 집중할 수 있습니다.

![intro_components.png](../assets/quickstart-streaming-tool.png)

서버와 클라이언트 아키텍처는 적절한 세션 격리 및 리소스 관리를 통해 웹 클라이언트와 AI 에이전트 간의 실시간 양방향 통신을 가능하게 합니다.

## 5. 서버 측 코드 개요 {#5.-server-side-code-overview}

FastAPI 서버는 웹 클라이언트와 AI 에이전트 간의 실시간 통신을 제공합니다.

### 양방향 통신 개요 {#4.-bidi-comm-overview}

#### 클라이언트에서 에이전트로의 흐름:
1.  **연결 수립** - 클라이언트가 `/events/{user_id}`로 SSE 연결을 열면 세션이 생성되고, 요청 큐가 `active_sessions`에 저장됩니다.
2.  **메시지 전송** - 클라이언트는 `mime_type`과 `data`를 포함한 JSON 페이로드를 `/send/{user_id}`로 POST 요청합니다.
3.  **큐 처리** - 서버는 해당 세션의 `live_request_queue`를 가져와 `send_content()` 또는 `send_realtime()`을 통해 에이전트로 메시지를 전달합니다.

#### 에이전트에서 클라이언트로의 흐름:
1.  **이벤트 생성** - 에이전트는 요청을 처리하고 `live_events` 비동기 제너레이터를 통해 이벤트를 생성합니다.
2.  **스트림 처리** - `agent_to_client_sse()`는 이벤트를 필터링하고 SSE와 호환되는 JSON 형식으로 변환합니다.
3.  **실시간 전달** - 이벤트는 적절한 SSE 헤더와 함께 영구적인 HTTP 연결을 통해 클라이언트로 스트리밍됩니다.

#### 세션 관리:
-   **사용자별 격리** - 각 사용자는 `active_sessions` 딕셔너리에 저장되는 고유한 세션을 가집니다.
-   **생명주기 관리** - 연결이 끊어지면 세션이 자동으로 정리되고 관련 리소스가 적절히 폐기됩니다.
-   **동시성 지원** - 여러 사용자가 동시에 활성 세션을 가질 수 있습니다.

#### 오류 처리:
-   **세션 유효성 검사** - POST 요청은 처리 전에 세션 존재 여부를 확인합니다.
-   **스트림 복원력** - SSE 스트림은 예외를 처리하고 자동으로 정리 작업을 수행합니다.
-   **연결 복구** - 클라이언트는 SSE 연결을 다시 설정하여 재연결할 수 있습니다.

### 에이전트 세션 관리

`start_agent_session()` 함수는 격리된 AI 에이전트 세션을 생성합니다.

```py
async def start_agent_session(user_id, is_audio=False):
    """에이전트 세션을 시작합니다."""

    # Runner 생성
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=root_agent,
    )

    # Session 생성
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,  # 실제 사용자 ID로 교체
    )

    # 응답 형태(modality) 설정
    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(response_modalities=[modality])

    # 이 세션을 위한 LiveRequestQueue 생성
    live_request_queue = LiveRequestQueue()

    # 에이전트 세션 시작
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue
```

-   **`InMemoryRunner` 설정** - 앱 이름 "ADK Streaming example"과 Google Search 에이전트를 사용하여, 에이전트 생명주기를 메모리에서 관리하는 러너(runner) 인스턴스를 생성합니다.

-   **세션 생성** - `runner.session_service.create_session()`을 사용하여 사용자 ID별로 고유한 세션을 설정하여 여러 동시 사용자를 지원합니다.

-   **응답 형태(Modality) 설정** - `is_audio` 매개변수에 따라 `RunConfig`를 "AUDIO" 또는 "TEXT" 형태로 설정하여 출력 형식을 결정합니다.

-   **`LiveRequestQueue`** - 들어오는 요청을 큐에 넣고 클라이언트와 에이전트 간의 실시간 메시지 전달을 가능하게 하는 양방향 통신 채널을 생성합니다.

-   **라이브 이벤트 스트림** - `runner.run_live()`는 부분 응답, 턴(turn) 완료, 인터럽트(중단)를 포함하여 에이전트로부터 실시간 이벤트를 생성하는 비동기 제너레이터를 반환합니다.

### 서버-전송 이벤트 (SSE) 스트리밍

`agent_to_client_sse()` 함수는 에이전트에서 클라이언트로의 실시간 스트리밍을 처리합니다.

```py
async def agent_to_client_sse(live_events):
    """SSE를 통한 에이전트-클라이언트 통신"""
    async for event in live_events:
        # 턴이 완료되거나 중단되면 전송
        if event.turn_complete or event.interrupted:
            message = {
                "turn_complete": event.turn_complete,
                "interrupted": event.interrupted,
            }
            yield f"data: {json.dumps(message)}\n\n"
            print(f"[AGENT TO CLIENT]: {message}")
            continue

        # Content와 그 첫 번째 Part를 읽음
        part: Part = (
            event.content and event.content.parts and event.content.parts[0]
        )
        if not part:
            continue

        # 오디오인 경우, Base64로 인코딩된 오디오 데이터 전송
        is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/pcm")
        if is_audio:
            audio_data = part.inline_data and part.inline_data.data
            if audio_data:
                message = {
                    "mime_type": "audio/pcm",
                    "data": base64.b64encode(audio_data).decode("ascii")
                }
                yield f"data: {json.dumps(message)}\n\n"
                print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                continue

        # 텍스트이고 부분 텍스트인 경우 전송
        if part.text and event.partial:
            message = {
                "mime_type": "text/plain",
                "data": part.text
            }
            yield f"data: {json.dumps(message)}\n\n"
            print(f"[AGENT TO CLIENT]: text/plain: {message}")
```

-   **이벤트 처리 루프** - `live_events` 비동기 제너레이터를 순회하며 에이전트로부터 도착하는 각 이벤트를 처리합니다.

-   **턴(Turn) 관리** - 대화 턴 완료 또는 중단 이벤트를 감지하고 `turn_complete` 및 `interrupted` 플래그가 포함된 JSON 메시지를 보내 대화 상태 변경을 알립니다.

-   **콘텐츠 파트(Part) 추출** - 이벤트 콘텐츠에서 텍스트 또는 오디오 데이터를 포함하는 첫 번째 `Part`를 추출합니다.

-   **오디오 스트리밍** - PCM 오디오 데이터를 다음과 같이 처리합니다:
    -   `inline_data`에서 `audio/pcm` MIME 타입을 감지합니다.
    -   JSON 전송을 위해 원시 오디오 바이트를 Base64로 인코딩합니다.
    -   `mime_type`과 `data` 필드와 함께 전송합니다.

-   **텍스트 스트리밍** - 부분 텍스트 응답이 생성될 때마다 점진적인 텍스트 업데이트를 전송하여 실시간 타이핑 효과를 구현합니다.

-   **SSE 형식** - 모든 데이터는 브라우저의 EventSource API 호환성을 위해 SSE 사양에 따라 `data: {json}\n\n` 형식으로 포맷됩니다.

### HTTP 엔드포인트와 라우팅

#### 루트 엔드포인트
**GET /** - FastAPI의 `FileResponse`를 사용하여 `static/index.html`을 메인 애플리케이션 인터페이스로 제공합니다.

#### SSE 이벤트 엔드포인트

```py
@app.get("/events/{user_id}")
async def sse_endpoint(user_id: int, is_audio: str = "false"):
    """에이전트-클라이언트 통신을 위한 SSE 엔드포인트"""

    # 에이전트 세션 시작
    user_id_str = str(user_id)
    live_events, live_request_queue = await start_agent_session(user_id_str, is_audio == "true")

    # 이 사용자를 위한 요청 큐 저장
    active_sessions[user_id_str] = live_request_queue

    print(f"Client #{user_id} connected via SSE, audio mode: {is_audio}")

    def cleanup():
        live_request_queue.close()
        if user_id_str in active_sessions:
            del active_sessions[user_id_str]
        print(f"Client #{user_id} disconnected from SSE")

    async def event_generator():
        try:
            async for data in agent_to_client_sse(live_events):
                yield data
        except Exception as e:
            print(f"Error in SSE stream: {e}")
        finally:
            cleanup()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )
```

**GET /events/{user_id}** - 영구적인 SSE 연결을 수립합니다:

-   **매개변수** - `user_id`(int)와 선택적인 `is_audio` 쿼리 매개변수(기본값 "false")를 받습니다.

-   **세션 초기화** - `start_agent_session()`을 호출하고 `user_id`를 키로 사용하여 `live_request_queue`를 `active_sessions` 딕셔너리에 저장합니다.

-   **`StreamingResponse`** - 다음을 포함하는 `StreamingResponse`를 반환합니다:
    -   `agent_to_client_sse()`를 감싸는 비동기 함수 `event_generator()`
    -   MIME 타입: `text/event-stream`
    -   크로스-오리진 접근을 위한 CORS 헤더
    -   캐싱을 방지하기 위한 Cache-control 헤더

-   **정리 로직** - 스트림 중단에 대한 오류 처리와 함께, 요청 큐를 닫고 활성 세션에서 제거하여 연결 종료를 처리합니다.

#### 메시지 전송 엔드포인트

```py
@app.post("/send/{user_id}")
async def send_message_endpoint(user_id: int, request: Request):
    """클라이언트-에이전트 통신을 위한 HTTP 엔드포인트"""

    user_id_str = str(user_id)

    # 이 사용자의 라이브 요청 큐 가져오기
    live_request_queue = active_sessions.get(user_id_str)
    if not live_request_queue:
        return {"error": "Session not found"}

    # 메시지 파싱
    message = await request.json()
    mime_type = message["mime_type"]
    data = message["data"]

    # 에이전트로 메시지 전송
    if mime_type == "text/plain":
        content = Content(role="user", parts=[Part.from_text(text=data)])
        live_request_queue.send_content(content=content)
        print(f"[CLIENT TO AGENT]: {data}")
    elif mime_type == "audio/pcm":
        decoded_data = base64.b64decode(data)
        live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
        print(f"[CLIENT TO AGENT]: audio/pcm: {len(decoded_data)} bytes")
    else:
        return {"error": f"Mime type not supported: {mime_type}"}

    return {"status": "sent"}
```

**POST /send/{user_id}** - 클라이언트 메시지를 수신합니다:

-   **세션 조회** - `active_sessions`에서 `live_request_queue`를 가져오거나, 세션이 없으면 오류를 반환합니다.

-   **메시지 처리** - `mime_type`과 `data` 필드가 있는 JSON을 파싱합니다:
    -   **텍스트 메시지** - `Part.from_text()`로 `Content`를 생성하고 `send_content()`를 통해 전송합니다.
    -   **오디오 메시지** - PCM 데이터를 Base64로 디코딩하고 `Blob`과 함께 `send_realtime()`을 통해 전송합니다.

-   **오류 처리** - 지원되지 않는 MIME 타입이나 누락된 세션에 대해 적절한 오류 응답을 반환합니다.

## 6. 클라이언트 측 코드 개요 {#6.-client-side-code-overview}

클라이언트 측은 실시간 통신 및 오디오 기능을 갖춘 웹 인터페이스로 구성됩니다.

### HTML 인터페이스 (`static/index.html`)

```html
<!doctype html>
<html>
  <head>
    <title>ADK Streaming Test (Audio)</title>
    <script src="/static/js/app.js" type="module"></script>
  </head>

  <body>
    <h1>ADK Streaming Test</h1>
    <div
      id="messages"
      style="height: 300px; overflow-y: auto; border: 1px solid black"></div>
    <br />

    <form id="messageForm">
      <label for="message">Message:</label>
      <input type="text" id="message" name="message" />
      <button type="submit" id="sendButton" disabled>Send</button>
      <button type="button" id="startAudioButton">Start Audio</button>
    </form>
  </body>

</html>
```

간단한 웹 인터페이스 구성 요소:
-   **메시지 표시** - 대화 기록을 위한 스크롤 가능한 div
-   **텍스트 입력 폼** - 텍스트 메시지를 위한 입력 필드와 전송 버튼
-   **오디오 제어** - 오디오 모드와 마이크 접근을 활성화하는 버튼

### 메인 애플리케이션 로직 (`static/js/app.js`)

#### 세션 관리 (`app.js`)

```js
const sessionId = Math.random().toString().substring(10);
const sse_url =
  "http://" + window.location.host + "/events/" + sessionId;
const send_url =
  "http://" + window.location.host + "/send/" + sessionId;
let is_audio = false;
```

-   **랜덤 세션 ID** - 각 브라우저 인스턴스에 대해 고유한 세션 ID를 생성합니다.
-   **URL 구성** - 세션 ID를 사용하여 SSE 및 전송 엔드포인트 URL을 구성합니다.
-   **오디오 모드 플래그** - 오디오 모드 활성화 여부를 추적합니다.

#### 서버-전송 이벤트 연결 (`app.js`)
`connectSSE()` 함수는 실시간 서버 통신을 처리합니다:

```js
// SSE 핸들러
function connectSSE() {
  // SSE 엔드포인트에 연결
  eventSource = new EventSource(sse_url + "?is_audio=" + is_audio);

  // 연결 성공 시 핸들러
  eventSource.onopen = function () {
    // 연결 성공 메시지
    console.log("SSE connection opened.");
    document.getElementById("messages").textContent = "Connection opened";

    // 전송 버튼 활성화
    document.getElementById("sendButton").disabled = false;
    addSubmitHandler();
  };

  // 메시지 수신 시 핸들러
  eventSource.onmessage = function (event) {
    ...
  };

  // 연결 오류 시 핸들러
  eventSource.onerror = function (event) {
    console.log("SSE connection error or closed.");
    document.getElementById("sendButton").disabled = true;
    document.getElementById("messages").textContent = "Connection closed";
    eventSource.close();
    setTimeout(function () {
      console.log("Reconnecting...");
      connectSSE();
    }, 5000);
  };
}
```

-   **`EventSource` 설정** - 오디오 모드 매개변수를 포함하여 SSE 연결을 생성합니다.
-   **연결 핸들러**:
    -   `onopen` - 연결되면 전송 버튼과 폼 제출을 활성화합니다.
    -   `onmessage` - 에이전트로부터 들어오는 메시지를 처리합니다.
    -   `onerror` - 5초 후 자동 재연결 기능으로 연결 끊김을 처리합니다.

#### 메시지 처리 (`app.js`)
서버로부터 오는 다양한 유형의 메시지를 처리합니다:

```js
  // 메시지 수신 시 핸들러
  eventSource.onmessage = function (event) {
    // 수신 메시지 파싱
    const message_from_server = JSON.parse(event.data);
    console.log("[AGENT TO CLIENT] ", message_from_server);

    // 턴 완료 여부 확인
    // 턴이 완료되면 새 메시지 추가
    if (
      message_from_server.turn_complete &&
      message_from_server.turn_complete == true
    ) {
      currentMessageId = null;
      return;
    }

    // 오디오인 경우 재생
    if (message_from_server.mime_type == "audio/pcm" && audioPlayerNode) {
      audioPlayerNode.port.postMessage(base64ToArray(message_from_server.data));
    }

    // 텍스트인 경우 출력
    if (message_from_server.mime_type == "text/plain") {
      // 새 턴에 대한 새 메시지 추가
      if (currentMessageId == null) {
        currentMessageId = Math.random().toString(36).substring(7);
        const message = document.createElement("p");
        message.id = currentMessageId;
        // messagesDiv에 메시지 요소 추가
        messagesDiv.appendChild(message);
      }

      // 기존 메시지 요소에 텍스트 추가
      const message = document.getElementById(currentMessageId);
      message.textContent += message_from_server.data;

      // messagesDiv의 맨 아래로 스크롤
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
```

-   **턴(Turn) 관리** - `turn_complete`를 감지하여 메시지 상태를 초기화합니다.
-   **오디오 재생** - Base64로 인코딩된 PCM 데이터를 디코딩하여 오디오 워크릿(worklet)으로 보냅니다.
-   **텍스트 표시** - 새 메시지 요소를 생성하고 실시간 타이핑 효과를 위해 부분 텍스트 업데이트를 추가합니다.

#### 메시지 전송 (`app.js`)
`sendMessage()` 함수는 서버로 데이터를 전송합니다:

```js
async function sendMessage(message) {
  try {
    const response = await fetch(send_url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(message)
    });
    
    if (!response.ok) {
      console.error('Failed to send message:', response.statusText);
    }
  } catch (error) {
    console.error('Error sending message:', error);
  }
}
```

-   **HTTP POST** - `/send/{session_id}` 엔드포인트로 JSON 페이로드를 전송합니다.
-   **오류 처리** - 실패한 요청 및 네트워크 오류를 로그에 기록합니다.
-   **메시지 형식** - `{mime_type, data}` 표준화된 구조를 사용합니다.

### 오디오 플레이어 (`static/js/audio-player.js`)

`startAudioPlayerWorklet()` 함수:

-   **`AudioContext` 설정** - 재생을 위해 24kHz 샘플링 레이트로 컨텍스트를 생성합니다.
-   **워크릿(Worklet) 로딩** - 오디오 처리를 위해 PCM 플레이어 프로세서를 로드합니다.
-   **오디오 파이프라인** - 워크릿 노드를 오디오 출력 장치(스피커)에 연결합니다.

### 오디오 레코더 (`static/js/audio-recorder.js`)

`startAudioRecorderWorklet()` 함수:

-   **`AudioContext` 설정** - 녹음을 위해 16kHz 샘플링 레이트로 컨텍스트를 생성합니다.
-   **마이크 접근** - 오디오 입력을 위해 사용자 미디어 권한을 요청합니다.
-   **오디오 처리** - 마이크를 레코더 워크릿에 연결합니다.
-   **데이터 변환** - Float32 샘플을 16비트 PCM 형식으로 변환합니다.

### 오디오 워크릿 프로세서

#### PCM 플레이어 프로세서 (`static/js/pcm-player-processor.js`)
`PCMPlayerProcessor` 클래스는 오디오 재생을 처리합니다:

-   **링 버퍼(Ring Buffer)** - 24kHz 오디오를 180초 동안 저장할 수 있는 순환 버퍼입니다.
-   **데이터 수신(Data Ingestion)** - Int16을 Float32로 변환하여 버퍼에 저장합니다.
-   **재생 루프** - 지속적으로 버퍼에서 데이터를 읽어 출력 채널로 보냅니다.
-   **오버플로우 처리** - 버퍼가 가득 차면 가장 오래된 샘플을 덮어씁니다.

#### PCM 레코더 프로세서 (`static/js/pcm-recorder-processor.js`)
`PCMProcessor` 클래스는 마이크 입력을 캡처합니다:

-   **오디오 입력** - 들어오는 오디오 프레임을 처리합니다.
-   **데이터 전송** - Float32 샘플을 복사하여 메시지 포트를 통해 메인 스레드로 전송합니다.

#### 모드 전환:
-   **오디오 활성화** - "Start Audio" 버튼은 마이크를 활성화하고 오디오 플래그와 함께 SSE를 다시 연결합니다.
-   **원활한 전환** - 기존 연결을 닫고 새로운 오디오 지원 세션을 설정합니다.

클라이언트 아키텍처는 텍스트와 오디오 두 형태 모두에서 원활한 실시간 통신을 가능하게 하며, 전문적인 수준의 오디오 처리를 위해 최신 웹 API를 사용합니다.

## 요약

이 애플리케이션은 다음과 같은 주요 특징을 가진 완전한 실시간 AI 에이전트 시스템을 보여줍니다:

**아키텍처 주요 특징**:
-   **실시간**: 부분 텍스트 업데이트와 연속적인 오디오를 통한 스트리밍 응답
-   **견고함**: 포괄적인 오류 처리 및 자동 복구 메커니즘
-   **최신 기술**: 최신 웹 표준(AudioWorklet, SSE, ES6 모듈) 사용

이 시스템은 실시간 상호작용, 웹 검색 기능, 멀티미디어 통신이 필요한 정교한 AI 애플리케이션을 구축하기 위한 기반을 제공합니다.

### 프로덕션 환경을 위한 다음 단계

이 시스템을 프로덕션 환경에 배포하려면 다음 개선 사항을 구현하는 것을 고려해 보세요:

#### 보안
-   **인증**: 랜덤 세션 ID를 적절한 사용자 인증으로 교체
-   **API 키 보안**: 환경 변수 또는 시크릿 관리 서비스 사용
-   **HTTPS**: 모든 통신에 TLS 암호화 강제
-   **요청량 제한(Rate Limiting)**: 악용을 방지하고 API 비용 제어

#### 확장성
-   **영구 저장소**: 인메모리 세션을 영구 세션 저장소로 교체
-   **로드 밸런싱**: 공유 세션 상태를 가진 다중 서버 인스턴스 지원
-   **오디오 최적화**: 대역폭 사용량을 줄이기 위한 압축 기술 구현

#### 모니터링
-   **오류 추적**: 시스템 장애 모니터링 및 알림
-   **API 비용 모니터링**: 예산 초과를 방지하기 위해 Google Search 및 Gemini 사용량 추적
-   **성능 지표**: 응답 시간 및 오디오 지연 시간 모니터링

#### 인프라
-   **컨테이너화**: Cloud Run 또는 Agent Engine을 사용한 일관된 배포를 위해 Docker로 패키징
-   **헬스 체크(Health Checks)**: 가동 시간 추적을 위한 엔드포인트 모니터링 구현