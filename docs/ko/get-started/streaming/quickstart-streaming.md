# 빠른 시작 (스트리밍 / Python) {#adk-streaming-quickstart}

이 빠른 시작을 통해 간단한 에이전트를 만들고 ADK 스트리밍을 사용하여 저지연 양방향 음성 및 영상 통신을 활성화하는 방법을 배웁니다. ADK를 설치하고, 기본적인 "Google 검색" 에이전트를 설정한 다음, `adk web` 도구로 에이전트 스트리밍을 실행해 보고, 마지막으로 ADK 스트리밍과 [FastAPI](https://fastapi.tiangolo.com/)를 사용하여 간단한 비동기 웹 앱을 직접 빌드하는 방법을 설명합니다.

**참고:** 이 가이드는 Windows, Mac, Linux 환경에서 터미널 사용 경험이 있다고 가정합니다.

## 음성/영상 스트리밍 지원 모델 {#supported-models}

ADK에서 음성/영상 스트리밍을 사용하려면 Live API를 지원하는 Gemini 모델을 사용해야 합니다. 문서에서 Gemini Live API를 지원하는 **모델 ID**를 찾을 수 있습니다:

- [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
- [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## 1. 환경 설정 및 ADK 설치 {#1.-setup-installation}

가상 환경 생성 및 활성화 (권장):

```bash
# 생성
python -m venv .venv
# 활성화 (새 터미널마다)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

ADK 설치:

```bash
pip install google-adk
```

## 2. 프로젝트 구조 {#2.-project-structure}

빈 파일로 다음 폴더 구조를 만듭니다:

```console
adk-streaming/  # 프로젝트 폴더
└── app/ # 웹 앱 폴더
    ├── .env # Gemini API 키
    └── google_search_agent/ # 에이전트 폴더
        ├── __init__.py # Python 패키지
        └── agent.py # 에이전트 정의
```

### agent.py

다음 코드 블록을 [`agent.py`](http://agent.py)에 복사하여 붙여넣습니다.

`model`에 대해서는 앞서 [모델 섹션](#supported-models)에서 설명한 대로 모델 ID를 다시 확인해 주세요.

```py
from google.adk.agents import Agent
from google.adk.tools import google_search  # 도구 가져오기

root_agent = Agent(
   # 에이전트의 고유한 이름.
   name="basic_search_agent",
   # 에이전트가 사용할 거대 언어 모델 (LLM).
   model="gemini-2.0-flash-exp",
   # model="gemini-2.0-flash-live-001",  # 2025년 2월 기준 새로운 스트리밍 모델 버전
   # 에이전트의 목적에 대한 간단한 설명.
   description="Google 검색을 사용하여 질문에 답하는 에이전트.",
   # 에이전트의 행동을 설정하기 위한 지침.
   instruction="당신은 전문 연구원입니다. 항상 사실에 입각해야 합니다.",
   # Google 검색으로 그라운딩을 수행하기 위해 google_search 도구 추가.
   tools=[google_search]
)
```

**참고:** 텍스트와 오디오/비디오 입력을 모두 활성화하려면 모델이 generateContent (텍스트용) 및 bidiGenerateContent 메서드를 지원해야 합니다. [모델 목록 문서](https://ai.google.dev/api/models#method:-models.list)를 참조하여 이러한 기능을 확인하세요. 이 빠른 시작에서는 시연 목적으로 gemini-2.0-flash-exp 모델을 활용합니다.

`agent.py`는 모든 에이전트의 로직이 저장될 곳이며, `root_agent`가 정의되어 있어야 합니다.

[Google 검색을 통한 그라운딩](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search) 기능이 얼마나 쉽게 통합되었는지 주목하세요. `Agent` 클래스와 `google_search` 도구는 LLM 및 검색 API와의 복잡한 상호작용을 처리하므로, 여러분은 에이전트의 *목적*과 *행동*에 집중할 수 있습니다.

![intro_components.png](../../assets/quickstart-streaming-tool.png)

다음 코드 블록을 `__init__.py` 파일에 복사하여 붙여넣습니다.

```py title="__init__.py"
from . import agent
```

## 3. 플랫폼 설정 {#3.-set-up-the-platform}

에이전트를 실행하려면 Google AI Studio 또는 Google Cloud Vertex AI 중에서 플랫폼을 선택하세요:

=== "Gemini - Google AI Studio"
    1. [Google AI Studio](https://aistudio.google.com/apikey)에서 API 키를 받으세요.
    2. (`app/` 안에 있는) **`.env`** 파일을 열고 다음 코드를 복사하여 붙여넣습니다.

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3. `PASTE_YOUR_ACTUAL_API_KEY_HERE`를 실제 `API 키`로 교체하세요.

=== "Gemini - Google Cloud Vertex AI"
    1. 기존 [Google Cloud](https://cloud.google.com/?e=48754805&hl=en) 계정과 프로젝트가 필요합니다.
        * [Google Cloud 프로젝트 설정](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
        * [gcloud CLI 설정](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
        * 터미널에서 `gcloud auth login`을 실행하여 Google Cloud에 인증하세요.
        * [Vertex AI API 활성화](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com).
    2. (`app/` 안에 있는) **`.env`** 파일을 엽니다. 다음 코드를 복사하여 붙여넣고 프로젝트 ID와 위치를 업데이트하세요.

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=PASTE_YOUR_ACTUAL_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=us-central1
        ```

## 4. `adk web`으로 에이전트 시험해보기 {#4.-try-it-adk-web}

이제 에이전트를 시험해 볼 준비가 되었습니다. 다음 명령을 실행하여 **개발자 UI**를 시작합니다. 먼저, 현재 디렉토리를 `app`으로 설정해야 합니다:

```shell
cd app
```

또한, 다음 명령으로 `SSL_CERT_FILE` 변수를 설정하세요. 이는 나중에 음성 및 영상 테스트에 필요합니다.

```shell
export SSL_CERT_FILE=$(python -m certifi)
```

그런 다음, 개발자 UI를 실행합니다:

```shell
adk web
```

!!!info "Windows 사용자를 위한 참고 사항"

    `_make_subprocess_transport NotImplementedError`가 발생하면 대신 `adk web --no-reload`를 사용하는 것을 고려해보세요.


제공된 URL(보통 `http://localhost:8000` 또는 `http://127.0.0.1:8000`)을 **브라우저에서 직접** 엽니다. 이 연결은 전적으로 로컬 컴퓨터 내에서 유지됩니다. `google_search_agent`를 선택하세요.

### 텍스트로 시험해보기

UI에 다음 프롬프트를 입력하여 시험해 보세요.

* 뉴욕의 날씨는 어떤가요?
* 뉴욕은 지금 몇 시인가요?
* 파리의 날씨는 어떤가요?
* 파리는 지금 몇 시인가요?

에이전트는 `google_search` 도구를 사용하여 최신 정보를 얻어 해당 질문에 답변할 것입니다.

### 음성 및 영상으로 시험해보기

음성으로 시험하려면 웹 브라우저를 새로고침하고, 마이크 버튼을 클릭하여 음성 입력을 활성화한 후, 같은 질문을 음성으로 해보세요. 실시간으로 음성 답변을 들을 수 있습니다.

영상으로 시험하려면 웹 브라우저를 새로고침하고, 카메라 버튼을 클릭하여 영상 입력을 활성화한 후, "뭐가 보여?"와 같은 질문을 해보세요. 에이전트가 영상 입력에서 보이는 것을 답변할 것입니다.

### 도구 중지하기

콘솔에서 `Ctrl-C`를 눌러 `adk web`을 중지하세요.

### ADK 스트리밍에 대한 참고 사항

ADK 스트리밍의 향후 버전에서는 콜백(Callback), LongRunningTool, ExampleTool, 셸 에이전트(예: SequentialAgent)와 같은 기능이 지원될 예정입니다.

축하합니다! ADK를 사용하여 첫 번째 스트리밍 에이전트를 성공적으로 만들고 상호작용했습니다!

## 다음 단계: 사용자 지정 스트리밍 앱 빌드하기

[사용자 지정 오디오 스트리밍 앱](../../streaming/custom-streaming.md) 튜토리얼에서는 ADK 스트리밍과 [FastAPI](https://fastapi.tiangolo.com/)로 구축된 사용자 지정 비동기 웹 앱의 서버 및 클라이언트 코드를 개괄적으로 설명하여 실시간 양방향 오디오 및 텍스트 통신을 가능하게 합니다.