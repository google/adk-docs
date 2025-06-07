# 최초의 지능형 에이전트 팀 구축하기: ADK를 이용한 점진적 날씨 봇

<!-- 전체적인 패딩/간격을 위한 선택적 외부 컨테이너 -->
<div style="padding: 10px 0;">

  <!-- 라인 1: Colab에서 열기 -->
  <!-- 이 div는 링크가 자체 라인을 차지하고 아래에 공간을 추가하도록 합니다 -->
  <div style="margin-bottom: 10px;">
    <a href="https://colab.research.google.com/github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" style="display: inline-flex; align-items: center; gap: 5px; text-decoration: none; color: #4285F4;">
      <img width="32px" src="https://www.gstatic.com/pantheon/images/bigquery/welcome_page/colab-logo.svg" alt="Google Colaboratory 로고">
      <span>Colab에서 열기</span>
    </a>
  </div>

  <!-- 라인 2: 공유 링크 -->
  <!-- 이 div는 "공유하기:" 텍스트와 아이콘을 위한 플렉스 컨테이너 역할을 합니다 -->
  <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
    <!-- 공유 텍스트 -->
    <span style="font-weight: bold;">공유하기:</span>

    <!-- 소셜 미디어 링크 -->
    <a href="https://www.linkedin.com/sharing/share-offsite/?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="LinkedIn에 공유">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg" alt="LinkedIn 로고" style="vertical-align: middle;">
    </a>
    <a href="https://bsky.app/intent/compose?text=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Bluesky에 공유">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/7/7a/Bluesky_Logo.svg" alt="Bluesky 로고" style="vertical-align: middle;">
    </a>
    <a href="https://twitter.com/intent/tweet?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="X (Twitter)에 공유">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/5/5a/X_icon_2.svg" alt="X 로고" style="vertical-align: middle;">
    </a>
    <a href="https://reddit.com/submit?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Reddit에 공유">
      <img width="20px" src="https://redditinc.com/hubfs/Reddit%20Inc/Brand/Reddit_Logo.png" alt="Reddit 로고" style="vertical-align: middle;">
    </a>
    <a href="https://www.facebook.com/sharer/sharer.php?u=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Facebook에 공유">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" alt="Facebook 로고" style="vertical-align: middle;">
    </a>
  </div>

</div>

이 튜토리얼은 [Agent Development Kit](https://google.github.io/adk-docs/get-started/)의 [빠른 시작 예제](https://google.github.io/adk-docs/get-started/quickstart/)를 확장한 것입니다. 이제 더 깊이 파고들어 더 정교한 **멀티 에이전트 시스템**을 구축할 준비가 되었습니다.

우리는 간단한 기반 위에 점진적으로 고급 기능을 추가하며 **날씨 봇 에이전트 팀**을 구축할 것입니다. 날씨를 조회할 수 있는 단일 에이전트부터 시작하여 다음과 같은 기능을 점진적으로 추가할 것입니다:

*   다양한 AI 모델(Gemini, GPT, Claude) 활용하기.
*   독립적인 작업(인사, 작별 등)을 위한 전문 하위 에이전트 설계하기.
*   에이전트 간의 지능적인 위임 활성화하기.
*   영구적인 세션 상태를 사용하여 에이전트에게 메모리 부여하기.
*   콜백을 사용하여 중요한 안전 가드레일 구현하기.

**왜 날씨 봇 팀인가요?**

이 사용 사례는 간단해 보이지만, 복잡한 실제 에이전트 애플리케이션을 구축하는 데 필수적인 핵심 ADK 개념을 탐색하기 위한 실용적이고 공감하기 쉬운 캔버스를 제공합니다. 상호 작용을 구조화하고, 상태를 관리하고, 안전을 보장하고, 함께 작동하는 여러 AI "두뇌"를 조율하는 방법을 배우게 됩니다.

**ADK란 무엇인가요?**

다시 한번 상기시켜 드리자면, ADK는 거대 언어 모델(LLM) 기반 애플리케이션 개발을 간소화하기 위해 설계된 Python 프레임워크입니다. 추론하고, 계획하고, 도구를 사용하고, 사용자와 동적으로 상호 작용하며, 팀 내에서 효과적으로 협력할 수 있는 에이전트를 만들기 위한 강력한 구성 요소를 제공합니다.

**이 고급 튜토리얼에서 마스터할 내용:**

*   ✅ **도구 정의 및 사용:** 에이전트에게 특정 능력(데이터 가져오기 등)을 부여하는 Python 함수(`tools`)를 만들고 에이전트에게 이를 효과적으로 사용하는 방법을 지시합니다.
*   ✅ **멀티 LLM 유연성:** LiteLLM 통합을 통해 다양한 주요 LLM(Gemini, GPT-4o, Claude Sonnet)을 사용하도록 에이전트를 구성하여 각 작업에 가장 적합한 모델을 선택할 수 있습니다.
*   ✅ **에이전트 위임 및 협업:** 전문 하위 에이전트를 설계하고 사용자 요청을 팀 내에서 가장 적절한 에이전트에게 자동으로 라우팅(`auto flow`)할 수 있도록 합니다.
*   ✅ **메모리를 위한 세션 상태:** `Session State` 및 `ToolContext`를 활용하여 에이전트가 대화 턴 간에 정보를 기억하게 하여 더 문맥적인 상호 작용을 유도합니다.
*   ✅ **콜백을 이용한 안전 가드레일:** `before_model_callback` 및 `before_tool_callback`을 구현하여 미리 정의된 규칙에 따라 요청/도구 사용을 검사, 수정 또는 차단하여 애플리케이션 안전성과 제어력을 향상시킵니다.

**최종 결과물 예상:**

이 튜토리얼을 완료하면 작동하는 멀티 에이전트 날씨 봇 시스템을 구축하게 될 것입니다. 이 시스템은 날씨 정보를 제공할 뿐만 아니라, 대화상의 예의를 처리하고, 마지막으로 확인한 도시를 기억하며, ADK를 사용하여 조율된 정의된 안전 경계 내에서 작동합니다.

**전제 조건:**

*   ✅ **Python 프로그래밍에 대한 확실한 이해.**
*   ✅ **거대 언어 모델(LLM), API, 에이전트 개념에 대한 친숙함.**
*   ❗ **중요: ADK 빠른 시작 튜토리얼 완료 또는 ADK 기본 사항(Agent, Runner, SessionService, 기본 도구 사용)에 대한 동등한 기초 지식.** 이 튜토리얼은 이러한 개념을 직접 기반으로 합니다.
*   ✅ 사용하려는 LLM에 대한 **API 키** (예: Gemini용 Google AI Studio, OpenAI Platform, Anthropic Console).


---

**실행 환경에 대한 참고 사항:**

이 튜토리얼은 Google Colab, Colab Enterprise 또는 Jupyter 노트북과 같은 대화형 노트북 환경을 위해 구성되었습니다. 다음 사항을 유념해 주십시오:

*   **비동기 코드 실행:** 노트북 환경은 비동기 코드를 다르게 처리합니다. `await` (이벤트 루프가 이미 실행 중일 때 적합, 노트북에서 일반적) 또는 `asyncio.run()` (독립적인 `.py` 스크립트로 실행하거나 특정 노트북 설정에서 필요)을 사용하는 예제를 보게 될 것입니다. 코드 블록은 두 시나리오 모두에 대한 지침을 제공합니다.
*   **수동 Runner/세션 설정:** 단계에는 `Runner` 및 `SessionService` 인스턴스를 명시적으로 생성하는 과정이 포함됩니다. 이 접근 방식은 에이전트의 실행 수명 주기, 세션 관리 및 상태 지속성에 대한 세분화된 제어를 제공하기 때문에 보여줍니다.

**대안: ADK의 내장 도구 사용 (웹 UI / CLI / API 서버)**

ADK의 표준 도구를 사용하여 러너 및 세션 관리를 자동으로 처리하는 설정을 선호하는 경우, 해당 목적에 맞게 구성된 코드를 [여기](https://github.com/google/adk-docs/tree/main/examples/python/tutorial/agent_team/adk-tutorial)에서 찾을 수 있습니다. 해당 버전은 `adk web` (웹 UI용), `adk run` (CLI 상호작용용) 또는 `adk api_server` (API 노출용)와 같은 명령으로 직접 실행되도록 설계되었습니다. 해당 대체 리소스에 제공된 `README.md` 지침을 따르십시오.

---

**에이전트 팀을 만들 준비가 되셨나요? 시작해 봅시다!**

> **참고:** 이 튜토리얼은 adk 버전 1.0.0 이상에서 작동합니다.

```python
# @title 0단계: 설정 및 설치
# 멀티 모델 지원을 위해 ADK와 LiteLLM 설치

!pip install google-adk -q
!pip install litellm -q

print("설치가 완료되었습니다.")
```


```python
# @title 필요한 라이브러리 가져오기
import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # 멀티 모델 지원용
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # 메시지 Content/Parts 생성용

import warnings
# 모든 경고 무시
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

print("라이브러리를 가져왔습니다.")
```


```python
# @title API 키 구성 (실제 키로 교체하세요!)

# --- 중요: 플레이스홀더를 실제 API 키로 교체하세요 ---

# Gemini API 키 (Google AI Studio에서 받기: https://aistudio.google.com/app/apikey)
os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY" # <--- 교체

# [선택 사항]
# OpenAI API 키 (OpenAI Platform에서 받기: https://platform.openai.com/api-keys)
os.environ['OPENAI_API_KEY'] = 'YOUR_OPENAI_API_KEY' # <--- 교체

# [선택 사항]
# Anthropic API 키 (Anthropic Console에서 받기: https://console.anthropic.com/settings/keys)
os.environ['ANTHROPIC_API_KEY'] = 'YOUR_ANTHROPIC_API_KEY' # <--- 교체

# --- 키 확인 (선택적 검사) ---
print("API 키 설정됨:")
print(f"Google API 키 설정됨: {'예' if os.environ.get('GOOGLE_API_KEY') and os.environ['GOOGLE_API_KEY'] != 'YOUR_GOOGLE_API_KEY' else '아니오 (플레이스홀더 교체 필요!)'}")
print(f"OpenAI API 키 설정됨: {'예' if os.environ.get('OPENAI_API_KEY') and os.environ['OPENAI_API_KEY'] != 'YOUR_OPENAI_API_KEY' else '아니오 (플레이스홀더 교체 필요!)'}")
print(f"Anthropic API 키 설정됨: {'예' if os.environ.get('ANTHROPIC_API_KEY') and os.environ['ANTHROPIC_API_KEY'] != 'YOUR_ANTHROPIC_API_KEY' else '아니오 (플레이스홀더 교체 필요!)'}")

# 이 멀티 모델 설정을 위해 API 키를 직접 사용하도록 ADK 구성 (Vertex AI 사용 안 함)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


# @markdown **보안 참고:** API 키를 노트북에 직접 하드코딩하는 것보다 Colab Secrets나 환경 변수 등을 사용하여 안전하게 관리하는 것이 가장 좋습니다. 위의 플레이스홀더 문자열을 교체하세요.
```


```python
# --- 쉬운 사용을 위해 모델 상수 정의 ---

# 더 많은 지원 모델은 여기에서 참조할 수 있습니다: https://ai.google.dev/gemini-api/docs/models#model-variations
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

# 더 많은 지원 모델은 여기에서 참조할 수 있습니다: https://docs.litellm.ai/docs/providers/openai#openai-chat-completion-models
MODEL_GPT_4O = "openai/gpt-4.1" # gpt-4.1-mini, gpt-4o 등도 시도해 볼 수 있습니다.

# 더 많은 지원 모델은 여기에서 참조할 수 있습니다: https://docs.litellm.ai/docs/providers/anthropic
MODEL_CLAUDE_SONNET = "anthropic/claude-sonnet-4-20250514" # claude-opus-4-20250514 , claude-3-7-sonnet-20250219 등도 시도해 볼 수 있습니다.

print("\n환경이 구성되었습니다.")
```

---

## 1단계: 첫 번째 에이전트 - 기본 날씨 조회

날씨 봇의 기본 구성 요소인 특정 작업(날씨 정보 조회)을 수행할 수 있는 단일 에이전트를 구축하는 것부터 시작하겠습니다. 여기에는 두 가지 핵심 부분을 만드는 것이 포함됩니다.

1. **도구:** 에이전트에게 날씨 데이터를 가져올 *능력*을 부여하는 Python 함수입니다.
2. **에이전트:** 사용자의 요청을 이해하고, 날씨 도구가 있다는 것을 알며, 언제 어떻게 사용할지 결정하는 AI "두뇌"입니다.

---

**1. `get_weather` 도구 정의**

ADK에서 **도구**는 에이전트에게 단순한 텍스트 생성을 넘어서는 구체적인 능력을 부여하는 구성 요소입니다. 일반적으로 API 호출, 데이터베이스 쿼리, 계산 수행과 같은 특정 작업을 수행하는 일반 Python 함수입니다.

우리의 첫 번째 도구는 *모의* 날씨 보고서를 제공할 것입니다. 이를 통해 아직 외부 API 키 없이 에이전트 구조에 집중할 수 있습니다. 나중에 이 모의 함수를 실제 날씨 서비스를 호출하는 함수로 쉽게 교체할 수 있습니다.

**핵심 개념: Docstring은 매우 중요합니다!** 에이전트의 LLM은 함수의 **docstring**에 크게 의존하여 다음을 이해합니다.

*   도구가 *무엇을* 하는지.
*   *언제* 사용해야 하는지.
*   *어떤 인수*가 필요한지 (`city: str`).
*   *어떤 정보*를 반환하는지.

**모범 사례:** 도구에 대해 명확하고, 설명적이며, 정확한 docstring을 작성하세요. 이는 LLM이 도구를 올바르게 사용하는 데 필수적입니다.


```python
# @title get_weather 도구 정의
def get_weather(city: str) -> dict:
    """지정된 도시의 현재 날씨 보고서를 검색합니다.

    Args:
        city (str): 도시 이름 (예: "New York", "London", "Tokyo").

    Returns:
        dict: 날씨 정보를 포함하는 사전.
              'status' 키('success' 또는 'error')를 포함합니다.
              'success'인 경우 날씨 세부 정보가 포함된 'report' 키를 포함합니다.
              'error'인 경우 'error_message' 키를 포함합니다.
    """
    print(f"--- 도구: {city}에 대해 get_weather 호출됨 ---") # 도구 실행 기록
    city_normalized = city.lower().replace(" ", "") # 기본 정규화

    # 모의 날씨 데이터
    mock_weather_db = {
        "newyork": {"status": "success", "report": "뉴욕의 날씨는 맑고 기온은 25°C입니다."},
        "london": {"status": "success", "report": "런던은 흐리고 기온은 15°C입니다."},
        "tokyo": {"status": "success", "report": "도쿄는 약한 비가 내리고 기온은 18°C입니다."},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"죄송합니다. '{city}'에 대한 날씨 정보가 없습니다."}

# 예제 도구 사용 (선택적 테스트)
print(get_weather("New York"))
print(get_weather("Paris"))
```

---

**2. `weather_agent` 에이전트 정의**

이제 **에이전트** 자체를 만들어 봅시다. ADK의 `Agent`는 사용자와 LLM, 그리고 사용 가능한 도구 간의 상호작용을 조율합니다.

몇 가지 주요 매개변수로 구성합니다:

* `name`: 이 에이전트의 고유 식별자 (예: "weather\_agent\_v1").
* `model`: 사용할 LLM을 지정합니다 (예: `MODEL_GEMINI_2_0_FLASH`). 특정 Gemini 모델로 시작하겠습니다.
* `description`: 에이전트의 전반적인 목적에 대한 간결한 요약입니다. 나중에 다른 에이전트가 이 에이전트에게 작업을 위임할지 결정할 때 중요해집니다.
* `instruction`: LLM에게 어떻게 행동해야 하는지, 그 페르소나, 목표, 그리고 특히 할당된 `tools`를 *어떻게 그리고 언제* 활용해야 하는지에 대한 상세한 지침입니다.
* `tools`: 에이전트가 사용할 수 있도록 허용된 실제 Python 도구 함수 목록입니다 (예: `[get_weather]`).

**모범 사례:** 명확하고 구체적인 `instruction` 프롬프트를 제공하세요. 지침이 상세할수록 LLM은 자신의 역할을 더 잘 이해하고 도구를 효과적으로 사용할 수 있습니다. 필요한 경우 오류 처리에 대해 명시적으로 언급하세요.

**모범 사례:** 설명적인 `name`과 `description` 값을 선택하세요. 이들은 ADK 내부에서 사용되며 나중에 다룰 자동 위임과 같은 기능에 필수적입니다.


```python
# @title 날씨 에이전트 정의
# 이전에 정의된 모델 상수 중 하나를 사용
AGENT_MODEL = MODEL_GEMINI_2_0_FLASH # Gemini로 시작

weather_agent = Agent(
    name="weather_agent_v1",
    model=AGENT_MODEL, # Gemini용 문자열 또는 LiteLlm 객체가 될 수 있음
    description="특정 도시의 날씨 정보를 제공합니다.",
    instruction="당신은 유용한 날씨 비서입니다. "
                "사용자가 특정 도시의 날씨를 물으면, "
                "'get_weather' 도구를 사용하여 정보를 찾으세요. "
                "도구가 오류를 반환하면 사용자에게 정중하게 알리세요. "
                "도구가 성공하면 날씨 보고서를 명확하게 제시하세요.",
    tools=[get_weather], # 함수를 직접 전달
)

print(f"에이전트 '{weather_agent.name}'가 모델 '{AGENT_MODEL}'을 사용하여 생성되었습니다.")
```

---

**3. Runner 및 세션 서비스 설정**

대화를 관리하고 에이전트를 실행하려면 두 가지 구성 요소가 더 필요합니다.

* `SessionService`: 다른 사용자와 세션에 대한 대화 기록 및 상태를 관리합니다. `InMemorySessionService`는 모든 것을 메모리에 저장하는 간단한 구현으로, 테스트 및 간단한 애플리케이션에 적합합니다. 교환된 메시지를 추적합니다. 4단계에서 상태 지속성에 대해 더 자세히 알아볼 것입니다.
* `Runner`: 상호작용 흐름을 조율하는 엔진입니다. 사용자 입력을 받아 적절한 에이전트로 라우팅하고, 에이전트의 로직에 따라 LLM 및 도구 호출을 관리하며, `SessionService`를 통해 세션 업데이트를 처리하고, 상호작용의 진행 상황을 나타내는 이벤트를 생성합니다.


```python
# @title 세션 서비스 및 Runner 설정

# --- 세션 관리 ---
# 핵심 개념: SessionService는 대화 기록 및 상태를 저장합니다.
# InMemorySessionService는 이 튜토리얼을 위한 간단하고 비영구적인 저장소입니다.
session_service = InMemorySessionService()

# 상호작용 컨텍스트를 식별하기 위한 상수 정의
APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001" # 단순화를 위해 고정 ID 사용

# 대화가 이루어질 특정 세션 생성
session = await session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)
print(f"세션 생성됨: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

# --- Runner ---
# 핵심 개념: Runner는 에이전트 실행 루프를 조율합니다.
runner = Runner(
    agent=weather_agent, # 실행하려는 에이전트
    app_name=APP_NAME,   # 실행을 우리 앱과 연결
    session_service=session_service # 세션 관리자 사용
)
print(f"Runner가 에이전트 '{runner.agent.name}'에 대해 생성되었습니다.")
```

---

**4. 에이전트와 상호작용하기**

에이전트에게 메시지를 보내고 응답을 받을 방법이 필요합니다. LLM 호출과 도구 실행은 시간이 걸릴 수 있으므로 ADK의 `Runner`는 비동기적으로 작동합니다.

우리는 다음을 수행하는 `async` 헬퍼 함수 (`call_agent_async`)를 정의할 것입니다:

1. 사용자 쿼리 문자열을 받습니다.
2. ADK `Content` 형식으로 패키징합니다.
3. 사용자/세션 컨텍스트와 새 메시지를 제공하여 `runner.run_async`를 호출합니다.
4. 러너가 생성한 **이벤트**를 반복합니다. 이벤트는 에이전트 실행의 단계를 나타냅니다 (예: 도구 호출 요청, 도구 결과 수신, 중간 LLM 생각, 최종 응답).
5. `event.is_final_response()`를 사용하여 **최종 응답** 이벤트를 식별하고 출력합니다.

**왜 `async`인가?** LLM 및 잠재적 도구(외부 API 등)와의 상호작용은 I/O 바운드 작업입니다. `asyncio`를 사용하면 프로그램이 실행을 차단하지 않고 이러한 작업을 효율적으로 처리할 수 있습니다.


```python
# @title 에이전트 상호작용 함수 정의

from google.genai import types # 메시지 Content/Parts 생성용

async def call_agent_async(query: str, runner, user_id, session_id):
  """에이전트에게 쿼리를 보내고 최종 응답을 출력합니다."""
  print(f"\n>>> 사용자 쿼리: {query}")

  # 사용자 메시지를 ADK 형식으로 준비
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "에이전트가 최종 응답을 생성하지 않았습니다." # 기본값

  # 핵심 개념: run_async는 에이전트 로직을 실행하고 이벤트를 생성합니다.
  # 최종 답변을 찾기 위해 이벤트를 반복합니다.
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
      # 아래 줄의 주석을 해제하여 실행 중 *모든* 이벤트를 볼 수 있습니다.
      # print(f"  [이벤트] 작성자: {event.author}, 유형: {type(event).__name__}, 최종: {event.is_final_response()}, 내용: {event.content}")

      # 핵심 개념: is_final_response()는 해당 턴의 마무리 메시지를 표시합니다.
      if event.is_final_response():
          if event.content and event.content.parts:
             # 첫 번째 부분에 텍스트 응답이 있다고 가정
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # 잠재적 오류/에스컬레이션 처리
             final_response_text = f"에이전트가 에스컬레이션함: {event.error_message or '특정 메시지 없음.'}"
          # 필요한 경우 여기에 더 많은 확인 추가 (예: 특정 오류 코드)
          break # 최종 응답을 찾으면 이벤트 처리 중지

  print(f"<<< 에이전트 응답: {final_response_text}")
```

---

**5. 대화 실행하기**

마지막으로, 에이전트에게 몇 가지 쿼리를 보내 설정을 테스트해 보겠습니다. `async` 호출을 메인 `async` 함수로 감싸고 `await`를 사용하여 실행합니다.

출력을 보세요:

* 사용자 쿼리를 확인하세요.
* 에이전트가 도구를 사용할 때 `--- 도구: get_weather 호출됨... ---` 로그를 확인하세요.
* 파리에 대한 날씨 데이터를 사용할 수 없는 경우를 포함하여 에이전트의 최종 응답을 관찰하세요.


```python
# @title 초기 대화 실행

# 상호작용 헬퍼를 await하기 위해 async 함수가 필요합니다
async def run_conversation():
    await call_agent_async("런던 날씨는 어때?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

    await call_agent_async("파리는 어때?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID) # 도구의 오류 메시지를 예상

    await call_agent_async("뉴욕 날씨를 알려줘",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

# 비동기 컨텍스트(Colab/Jupyter 등)에서 await를 사용하여 대화 실행
await run_conversation()

# --- 또는 ---

# 표준 Python 스크립트(.py 파일)로 실행하는 경우 다음 줄의 주석을 해제하세요:
# import asyncio
# if __name__ == "__main__":
#     try:
#         asyncio.run(run_conversation())
#     except Exception as e:
#         print(f"오류가 발생했습니다: {e}")
```

---

축하합니다! 첫 번째 ADK 에이전트를 성공적으로 만들고 상호작용했습니다. 이 에이전트는 사용자의 요청을 이해하고, 정보를 찾기 위해 도구를 사용하며, 도구의 결과에 따라 적절하게 응답합니다.

다음 단계에서는 이 에이전트를 구동하는 기본 언어 모델을 쉽게 전환하는 방법을 알아볼 것입니다.

## 2단계: LiteLLM으로 멀티 모델 활용하기 [선택 사항]

1단계에서는 특정 Gemini 모델로 구동되는 기능적인 날씨 에이전트를 구축했습니다. 효과적이긴 하지만, 실제 애플리케이션은 종종 *다른* 거대 언어 모델(LLM)을 사용할 수 있는 유연성의 이점을 얻습니다. 왜 그럴까요?

*   **성능:** 일부 모델은 특정 작업(예: 코딩, 추론, 창의적 글쓰기)에 탁월합니다.
*   **비용:** 다른 모델은 다양한 가격대를 가집니다.
*   **기능:** 모델은 다양한 기능, 컨텍스트 창 크기, 미세 조정 옵션을 제공합니다.
*   **가용성/중복성:** 대안을 가지면 한 제공업체에 문제가 발생하더라도 애플리케이션이 계속 작동하도록 보장합니다.

ADK는 [**LiteLLM**](https://github.com/BerriAI/litellm) 라이브러리와의 통합을 통해 모델 간 전환을 원활하게 만듭니다. LiteLLM은 100개 이상의 다양한 LLM에 대한 일관된 인터페이스 역할을 합니다.

**이 단계에서는 다음을 수행합니다:**

1.  `LiteLlm` 래퍼를 사용하여 OpenAI(GPT) 및 Anthropic(Claude)과 같은 제공업체의 모델을 사용하도록 ADK `Agent`를 구성하는 방법을 배웁니다.
2.  각각 다른 LLM으로 백업된 날씨 에이전트의 인스턴스를 정의, 구성(자체 세션 및 러너 포함)하고 즉시 테스트합니다.
3.  동일한 기본 도구를 사용할 때도 응답의 잠재적 변화를 관찰하기 위해 이러한 다른 에이전트와 상호 작용합니다.

---

**1. `LiteLlm` 가져오기**

초기 설정(0단계) 중에 이것을 가져왔지만, 멀티 모델 지원을 위한 핵심 구성 요소입니다.


```python
# @title 1. LiteLlm 가져오기
from google.adk.models.lite_llm import LiteLlm
```

**2. 멀티 모델 에이전트 정의 및 테스트**

모델 이름 문자열만 전달하는 대신(기본적으로 Google의 Gemini 모델로 설정됨), 원하는 모델 식별자 문자열을 `LiteLlm` 클래스 내에 래핑합니다.

*   **핵심 개념: `LiteLlm` 래퍼:** `LiteLlm(model="provider/model_name")` 구문은 ADK에게 이 에이전트에 대한 요청을 LiteLLM 라이브러리를 통해 지정된 모델 제공업체로 라우팅하도록 지시합니다.

0단계에서 OpenAI 및 Anthropic에 필요한 API 키를 구성했는지 확인하십시오. 이전에 정의한 `call_agent_async` 함수(이제 `runner`, `user_id`, `session_id`를 허용)를 사용하여 각 에이전트를 설정한 직후 상호 작용할 것입니다.

아래 각 블록은 다음을 수행합니다:

*   특정 LiteLLM 모델(`MODEL_GPT_4O` 또는 `MODEL_CLAUDE_SONNET`)을 사용하여 에이전트를 정의합니다.
*   해당 에이전트의 테스트 실행을 위해 *새롭고 별도의* `InMemorySessionService` 및 세션을 특별히 생성합니다. 이는 이 시연을 위해 대화 기록을 격리합니다.
*   특정 에이전트와 해당 세션 서비스에 맞게 구성된 `Runner`를 생성합니다.
*   즉시 `call_agent_async`를 호출하여 쿼리를 보내고 에이전트를 테스트합니다.

**모범 사례:** 오타를 피하고 코드 관리를 쉽게 하기 위해 모델 이름에 상수(0단계에서 정의된 `MODEL_GPT_4O`, `MODEL_CLAUDE_SONNET` 등)를 사용하세요.

**오류 처리:** 에이전트 정의를 `try...except` 블록으로 감쌉니다. 이렇게 하면 특정 제공업체에 대한 API 키가 없거나 유효하지 않은 경우 전체 코드 셀이 실패하는 것을 방지하여 *구성된* 모델로 튜토리얼을 계속 진행할 수 있습니다.

먼저 OpenAI의 GPT-4o를 사용하여 에이전트를 만들고 테스트해 보겠습니다.


```python
# @title GPT 에이전트 정의 및 테스트

# 1단계의 'get_weather' 함수가 환경에 정의되어 있는지 확인하세요.
# 이전에 'call_agent_async'가 정의되어 있는지 확인하세요.

# --- GPT-4o를 사용하는 에이전트 ---
weather_agent_gpt = None # None으로 초기화
runner_gpt = None      # runner를 None으로 초기화

try:
    weather_agent_gpt = Agent(
        name="weather_agent_gpt",
        # 핵심 변경: LiteLLM 모델 식별자를 래핑
        model=LiteLlm(model=MODEL_GPT_4O),
        description="날씨 정보를 제공합니다 (GPT-4o 사용).",
        instruction="당신은 GPT-4o로 구동되는 유용한 날씨 비서입니다. "
                    "도시 날씨 요청에는 'get_weather' 도구를 사용하세요. "
                    "도구의 출력 상태에 따라 성공적인 보고서나 정중한 오류 메시지를 명확하게 제시하세요.",
        tools=[get_weather], # 동일한 도구 재사용
    )
    print(f"에이전트 '{weather_agent_gpt.name}'가 모델 '{MODEL_GPT_4O}'을 사용하여 생성되었습니다.")

    # InMemorySessionService는 이 튜토리얼을 위한 간단하고 비영구적인 저장소입니다.
    session_service_gpt = InMemorySessionService() # 전용 서비스 생성

    # 상호작용 컨텍스트를 식별하기 위한 상수 정의
    APP_NAME_GPT = "weather_tutorial_app_gpt" # 이 테스트를 위한 고유한 앱 이름
    USER_ID_GPT = "user_1_gpt"
    SESSION_ID_GPT = "session_001_gpt" # 단순화를 위해 고정 ID 사용

    # 대화가 이루어질 특정 세션 생성
    session_gpt = await session_service_gpt.create_session(
        app_name=APP_NAME_GPT,
        user_id=USER_ID_GPT,
        session_id=SESSION_ID_GPT
    )
    print(f"세션 생성됨: App='{APP_NAME_GPT}', User='{USER_ID_GPT}', Session='{SESSION_ID_GPT}'")

    # 이 에이전트와 해당 세션 서비스에 특화된 러너 생성
    runner_gpt = Runner(
        agent=weather_agent_gpt,
        app_name=APP_NAME_GPT,       # 특정 앱 이름 사용
        session_service=session_service_gpt # 특정 세션 서비스 사용
        )
    print(f"Runner가 에이전트 '{runner_gpt.agent.name}'에 대해 생성되었습니다.")

    # --- GPT 에이전트 테스트 ---
    print("\n--- GPT 에이전트 테스트 중 ---")
    # call_agent_async가 올바른 runner, user_id, session_id를 사용하는지 확인
    await call_agent_async(query = "도쿄 날씨는 어때?",
                           runner=runner_gpt,
                           user_id=USER_ID_GPT,
                           session_id=SESSION_ID_GPT)
    # --- 또는 ---

    # 표준 Python 스크립트(.py 파일)로 실행하는 경우 다음 줄의 주석을 해제하세요:
    # import asyncio
    # if __name__ == "__main__":
    #     try:
    #         asyncio.run(call_agent_async(query = "도쿄 날씨는 어때?",
    #                      runner=runner_gpt,
    #                       user_id=USER_ID_GPT,
    #                       session_id=SESSION_ID_GPT)
    #     except Exception as e:
    #         print(f"오류가 발생했습니다: {e}")

except Exception as e:
    print(f"❌ GPT 에이전트 '{MODEL_GPT_4O}'를 생성하거나 실행할 수 없습니다. API 키와 모델 이름을 확인하세요. 오류: {e}")
```

다음으로, Anthropic의 Claude Sonnet에 대해서도 동일한 작업을 수행합니다.


```python
# @title Claude 에이전트 정의 및 테스트

# 1단계의 'get_weather' 함수가 환경에 정의되어 있는지 확인하세요.
# 이전에 'call_agent_async'가 정의되어 있는지 확인하세요.

# --- Claude Sonnet을 사용하는 에이전트 ---
weather_agent_claude = None # None으로 초기화
runner_claude = None      # runner를 None으로 초기화

try:
    weather_agent_claude = Agent(
        name="weather_agent_claude",
        # 핵심 변경: LiteLLM 모델 식별자를 래핑
        model=LiteLlm(model=MODEL_CLAUDE_SONNET),
        description="날씨 정보를 제공합니다 (Claude Sonnet 사용).",
        instruction="당신은 Claude Sonnet으로 구동되는 유용한 날씨 비서입니다. "
                    "도시 날씨 요청에는 'get_weather' 도구를 사용하세요. "
                    "도구의 사전 출력('status', 'report'/'error_message')을 분석하세요. "
                    "성공적인 보고서나 정중한 오류 메시지를 명확하게 제시하세요.",
        tools=[get_weather], # 동일한 도구 재사용
    )
    print(f"에이전트 '{weather_agent_claude.name}'가 모델 '{MODEL_CLAUDE_SONNET}'을 사용하여 생성되었습니다.")

    # InMemorySessionService는 이 튜토리얼을 위한 간단하고 비영구적인 저장소입니다.
    session_service_claude = InMemorySessionService() # 전용 서비스 생성

    # 상호작용 컨텍스트를 식별하기 위한 상수 정의
    APP_NAME_CLAUDE = "weather_tutorial_app_claude" # 고유한 앱 이름
    USER_ID_CLAUDE = "user_1_claude"
    SESSION_ID_CLAUDE = "session_001_claude" # 단순화를 위해 고정 ID 사용

    # 대화가 이루어질 특정 세션 생성
    session_claude = await session_service_claude.create_session(
        app_name=APP_NAME_CLAUDE,
        user_id=USER_ID_CLAUDE,
        session_id=SESSION_ID_CLAUDE
    )
    print(f"세션 생성됨: App='{APP_NAME_CLAUDE}', User='{USER_ID_CLAUDE}', Session='{SESSION_ID_CLAUDE}'")

    # 이 에이전트와 해당 세션 서비스에 특화된 러너 생성
    runner_claude = Runner(
        agent=weather_agent_claude,
        app_name=APP_NAME_CLAUDE,       # 특정 앱 이름 사용
        session_service=session_service_claude # 특정 세션 서비스 사용
        )
    print(f"Runner가 에이전트 '{runner_claude.agent.name}'에 대해 생성되었습니다.")

    # --- Claude 에이전트 테스트 ---
    print("\n--- Claude 에이전트 테스트 중 ---")
    # call_agent_async가 올바른 runner, user_id, session_id를 사용하는지 확인
    await call_agent_async(query = "런던 날씨 좀 알려줘.",
                           runner=runner_claude,
                           user_id=USER_ID_CLAUDE,
                           session_id=SESSION_ID_CLAUDE)

    # --- 또는 ---

    # 표준 Python 스크립트(.py 파일)로 실행하는 경우 다음 줄의 주석을 해제하세요:
    # import asyncio
    # if __name__ == "__main__":
    #     try:
    #         asyncio.run(call_agent_async(query = "런던 날씨 좀 알려줘.",
    #                      runner=runner_claude,
    #                       user_id=USER_ID_CLAUDE,
    #                       session_id=SESSION_ID_CLAUDE)
    #     except Exception as e:
    #         print(f"오류가 발생했습니다: {e}")


except Exception as e:
    print(f"❌ Claude 에이전트 '{MODEL_CLAUDE_SONNET}'를 생성하거나 실행할 수 없습니다. API 키와 모델 이름을 확인하세요. 오류: {e}")
```

두 코드 블록의 출력을 주의 깊게 관찰하세요. 다음을 볼 수 있습니다:

1.  각 에이전트(`weather_agent_gpt`, `weather_agent_claude`)가 성공적으로 생성됩니다 (API 키가 유효한 경우).
2.  각각에 대해 전용 세션과 러너가 설정됩니다.
3.  각 에이전트는 쿼리를 처리할 때 `get_weather` 도구를 사용할 필요성을 올바르게 식별합니다 (`--- 도구: get_weather 호출됨... ---` 로그를 볼 수 있습니다).
4.  *기본 도구 로직*은 동일하게 유지되며 항상 모의 데이터를 반환합니다.
5.  그러나 각 에이전트가 생성하는 **최종 텍스트 응답**은 표현, 어조 또는 형식 면에서 약간 다를 수 있습니다. 이는 지시 프롬프트가 다른 LLM(GPT-4o 대 Claude Sonnet)에 의해 해석되고 실행되기 때문입니다.

이 단계는 ADK + LiteLLM이 제공하는 강력함과 유연성을 보여줍니다. 핵심 애플리케이션 로직(도구, 기본 에이전트 구조)을 일관되게 유지하면서 다양한 LLM을 사용하여 에이전트를 쉽게 실험하고 배포할 수 있습니다.

다음 단계에서는 단일 에이전트를 넘어 에이전트들이 서로 작업을 위임할 수 있는 작은 팀을 구축할 것입니다!

---

## 3단계: 에이전트 팀 구축 - 인사 및 작별 위임

1, 2단계에서는 날씨 조회에만 집중하는 단일 에이전트를 구축하고 실험했습니다. 특정 작업에는 효과적이지만, 실제 애플리케이션은 종종 더 다양한 사용자 상호작용을 처리해야 합니다. 단일 날씨 에이전트에 더 많은 도구와 복잡한 지침을 계속 추가할 수도 있지만, 이는 금방 관리하기 어려워지고 효율성이 떨어질 수 있습니다.

더 견고한 접근 방식은 **에이전트 팀**을 구축하는 것입니다. 여기에는 다음이 포함됩니다:

1. 각각 특정 기능을 위해 설계된 여러 **전문 에이전트**를 만듭니다 (예: 날씨용, 인사용, 계산용).
2. 초기 사용자 요청을 받는 **루트 에이전트**(또는 오케스트레이터)를 지정합니다.
3. 루트 에이전트가 사용자의 의도에 따라 가장 적절한 전문 하위 에이전트에게 요청을 **위임**할 수 있도록 합니다.

**왜 에이전트 팀을 구축해야 할까요?**

* **모듈성:** 개별 에이전트를 개발, 테스트 및 유지 관리하기가 더 쉽습니다.
* **전문화:** 각 에이전트는 특정 작업에 맞게 미세 조정(지침, 모델 선택)될 수 있습니다.
* **확장성:** 새 에이전트를 추가하여 새로운 기능을 더 간단하게 추가할 수 있습니다.
* **효율성:** 간단한 작업(인사 등)에 잠재적으로 더 간단하고 저렴한 모델을 사용할 수 있습니다.

**이 단계에서는 다음을 수행합니다:**

1. 인사(`say_hello`) 및 작별(`say_goodbye`)을 처리하기 위한 간단한 도구를 정의합니다.
2. 두 개의 새로운 전문 하위 에이전트인 `greeting_agent`와 `farewell_agent`를 만듭니다.
3. 메인 날씨 에이전트(`weather_agent_v2`)를 **루트 에이전트**로 작동하도록 업데이트합니다.
4. 루트 에이전트를 하위 에이전트로 구성하여 **자동 위임**을 활성화합니다.
5. 루트 에이전트에게 다른 유형의 요청을 보내 위임 흐름을 테스트합니다.

---

**1. 하위 에이전트를 위한 도구 정의**

먼저, 새로운 전문가 에이전트를 위한 도구 역할을 할 간단한 Python 함수를 만듭니다. 명확한 docstring은 이를 사용할 에이전트에게 매우 중요합니다.


```python
# @title 인사 및 작별 에이전트를 위한 도구 정의
from typing import Optional # Optional을 반드시 가져오세요.

# 이 단계를 독립적으로 실행하는 경우 1단계의 'get_weather'가 사용 가능한지 확인하세요.
# def get_weather(city: str) -> dict: ... (1단계에서)

def say_hello(name: Optional[str] = None) -> str:
    """간단한 인사를 제공합니다. 이름이 제공되면 사용됩니다.

    Args:
        name (str, optional): 인사할 사람의 이름. 제공되지 않으면 일반적인 인사말로 기본 설정됩니다.

    Returns:
        str: 친근한 인사 메시지.
    """
    if name:
        greeting = f"안녕하세요, {name}님!"
        print(f"--- 도구: 이름({name})으로 say_hello 호출됨 ---")
    else:
        greeting = "안녕하세요!" # 이름이 None이거나 명시적으로 전달되지 않은 경우 기본 인사말
        print(f"--- 도구: 특정 이름 없이 say_hello 호출됨 (name_arg_value: {name}) ---")
    return greeting

def say_goodbye() -> str:
    """대화를 마무리하기 위한 간단한 작별 메시지를 제공합니다."""
    print(f"--- 도구: say_goodbye 호출됨 ---")
    return "안녕히 가세요! 좋은 하루 되세요."

print("인사 및 작별 도구가 정의되었습니다.")

# 선택적 자체 테스트
print(say_hello("앨리스"))
print(say_hello()) # 인수 없이 테스트 (기본 "안녕하세요!" 사용해야 함)
print(say_hello(name=None)) # 이름을 명시적으로 None으로 테스트 (기본 "안녕하세요!" 사용해야 함)
```

---

**2. 하위 에이전트 정의 (인사 및 작별)**

이제 전문가들을 위한 `Agent` 인스턴스를 만듭니다. 매우 집중된 `instruction`과 결정적으로 명확한 `description`을 주목하세요. `description`은 *루트 에이전트*가 이 하위 에이전트에게 *언제* 위임할지 결정하는 데 사용하는 주요 정보입니다.

**모범 사례:** 하위 에이전트의 `description` 필드는 특정 기능을 정확하고 간결하게 요약해야 합니다. 이는 효과적인 자동 위임에 매우 중요합니다.

**모범 사례:** 하위 에이전트의 `instruction` 필드는 제한된 범위에 맞게 조정되어야 하며, 정확히 무엇을 해야 하고 *무엇을 하지 말아야 하는지* 알려줘야 합니다 (예: "당신의 *유일한* 작업은...").


```python
# @title 인사 및 작별 하위 에이전트 정의

# Gemini 이외의 모델을 사용하려면 LiteLlm이 가져와졌고 API 키가 설정되었는지 확인하세요 (0/2단계에서)
# from google.adk.models.lite_llm import LiteLlm
# MODEL_GPT_4O, MODEL_CLAUDE_SONNET 등이 정의되어야 합니다.
# 그렇지 않으면 계속해서 model = MODEL_GEMINI_2_0_FLASH를 사용합니다.

# --- 인사 에이전트 ---
greeting_agent = None
try:
    greeting_agent = Agent(
        # 간단한 작업을 위해 잠재적으로 다른/저렴한 모델 사용
        model = MODEL_GEMINI_2_0_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # 다른 모델로 실험하고 싶다면
        name="greeting_agent",
        instruction="당신은 인사 에이전트입니다. 당신의 유일한 임무는 사용자에게 친절한 인사를 제공하는 것입니다. "
                    "'say_hello' 도구를 사용하여 인사를 생성하세요. "
                    "사용자가 이름을 제공하면 반드시 도구에 전달하세요. "
                    "다른 대화나 작업에 참여하지 마세요.",
        description="'say_hello' 도구를 사용하여 간단한 인사와 안부를 처리합니다.", # 위임에 중요
        tools=[say_hello],
    )
    print(f"✅ 에이전트 '{greeting_agent.name}'가 모델 '{greeting_agent.model}'을 사용하여 생성되었습니다.")
except Exception as e:
    print(f"❌ 인사 에이전트를 생성할 수 없습니다. API 키({greeting_agent.model})를 확인하세요. 오류: {e}")

# --- 작별 에이전트 ---
farewell_agent = None
try:
    farewell_agent = Agent(
        # 동일하거나 다른 모델 사용 가능
        model = MODEL_GEMINI_2_0_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # 다른 모델로 실험하고 싶다면
        name="farewell_agent",
        instruction="당신은 작별 에이전트입니다. 당신의 유일한 임무는 정중한 작별 메시지를 제공하는 것입니다. "
                    "사용자가 떠나거나 대화를 끝내려 할 때(예: '안녕', '잘가', '고마워 안녕', '나중에 봐' 등) 'say_goodbye' 도구를 사용하세요. "
                    "다른 어떤 작업도 수행하지 마세요.",
        description="'say_goodbye' 도구를 사용하여 간단한 작별과 인사를 처리합니다.", # 위임에 중요
        tools=[say_goodbye],
    )
    print(f"✅ 에이전트 '{farewell_agent.name}'가 모델 '{farewell_agent.model}'을 사용하여 생성되었습니다.")
except Exception as e:
    print(f"❌ 작별 에이전트를 생성할 수 없습니다. API 키({farewell_agent.model})를 확인하세요. 오류: {e}")
```

---

**3. 루트 에이전트 정의 (날씨 에이전트 v2) 및 하위 에이전트 추가**

이제 `weather_agent`를 업그레이드합니다. 주요 변경 사항은 다음과 같습니다.

* `sub_agents` 매개변수 추가: 방금 만든 `greeting_agent`와 `farewell_agent` 인스턴스가 포함된 리스트를 전달합니다.
* `instruction` 업데이트: 루트 에이전트에게 하위 에이전트에 대해 *명시적으로* 알리고 *언제* 작업을 위임해야 하는지 알려줍니다.

**핵심 개념: 자동 위임 (Auto Flow)** `sub_agents` 목록을 제공함으로써 ADK는 자동 위임을 활성화합니다. 루트 에이전트가 사용자 쿼리를 받으면 LLM은 자신의 지침과 도구뿐만 아니라 각 하위 에이전트의 `description`도 고려합니다. LLM이 쿼리가 하위 에이전트의 설명된 기능(예: "간단한 인사를 처리함")과 더 잘 맞는다고 판단하면, 해당 턴에 대해 제어권을 해당 하위 에이전트에게 *넘기는* 특별한 내부 작업을 자동으로 생성합니다. 그러면 하위 에이전트는 자신의 모델, 지침, 도구를 사용하여 쿼리를 처리합니다.

**모범 사례:** 루트 에이전트의 지침이 위임 결정을 명확하게 안내하도록 하세요. 하위 에이전트의 이름을 언급하고 위임이 발생해야 하는 조건을 설명하세요.


```python
# @title 하위 에이전트를 포함한 루트 에이전트 정의

# 루트 에이전트를 정의하기 전에 하위 에이전트가 성공적으로 생성되었는지 확인하세요.
# 또한 원래 'get_weather' 도구가 정의되어 있는지 확인하세요.
root_agent = None
runner_root = None # runner 초기화

if greeting_agent and farewell_agent and 'get_weather' in globals():
    # 오케스트레이션을 처리하기 위해 유능한 Gemini 모델을 루트 에이전트에 사용합시다.
    root_agent_model = MODEL_GEMINI_2_0_FLASH

    weather_agent_team = Agent(
        name="weather_agent_v2", # 새 버전 이름 부여
        model=root_agent_model,
        description="메인 코디네이터 에이전트. 날씨 요청을 처리하고 인사/작별을 전문가에게 위임합니다.",
        instruction="당신은 팀을 조정하는 메인 날씨 에이전트입니다. 주요 책임은 날씨 정보를 제공하는 것입니다. "
                    "'get_weather' 도구는 특정 날씨 요청(예: '런던 날씨')에만 사용하세요. "
                    "당신에게는 전문화된 하위 에이전트가 있습니다: "
                    "1. 'greeting_agent': '안녕', '안녕하세요'와 같은 간단한 인사를 처리합니다. 이들에게 위임하세요. "
                    "2. 'farewell_agent': '안녕히 가세요', '나중에 봐요'와 같은 간단한 작별 인사를 처리합니다. 이들에게 위임하세요. "
                    "사용자의 쿼리를 분석하세요. 인사이면 'greeting_agent'에게 위임하세요. 작별 인사이면 'farewell_agent'에게 위임하세요. "
                    "날씨 요청이면 직접 'get_weather'를 사용하여 처리하세요. "
                    "그 외의 경우에는 적절히 응답하거나 처리할 수 없다고 말하세요.",
        tools=[get_weather], # 루트 에이전트는 여전히 핵심 작업을 위해 날씨 도구가 필요합니다.
        # 핵심 변경: 여기에 하위 에이전트를 연결하세요!
        sub_agents=[greeting_agent, farewell_agent]
    )
    print(f"✅ 루트 에이전트 '{weather_agent_team.name}'가 모델 '{root_agent_model}'과 하위 에이전트: {[sa.name for sa in weather_agent_team.sub_agents]}를 사용하여 생성되었습니다.")

else:
    print("❌ 하나 이상의 하위 에이전트 초기화에 실패했거나 'get_weather' 도구가 없어서 루트 에이전트를 생성할 수 없습니다.")
    if not greeting_agent: print(" - 인사 에이전트가 없습니다.")
    if not farewell_agent: print(" - 작별 에이전트가 없습니다.")
    if 'get_weather' not in globals(): print(" - get_weather 함수가 없습니다.")
```

---

**4. 에이전트 팀과 상호작용하기**

이제 전문화된 하위 에이전트를 갖춘 루트 에이전트(`weather_agent_team` - *참고: 이 변수 이름이 이전 코드 블록, 아마도 `# @title 루트 에이전트 정의`에서 정의된 이름과 일치하는지 확인하세요. 해당 블록에서는 `root_agent`라고 명명했을 수 있습니다*)를 정의했으므로, 위임 메커니즘을 테스트해 보겠습니다.

다음 코드 블록은 다음을 수행합니다:

1.  `async` 함수 `run_team_conversation`을 정의합니다.
2.  이 함수 내에서 이 테스트 실행을 위해 *새롭고 전용인* `InMemorySessionService`와 특정 세션(`session_001_agent_team`)을 생성합니다. 이는 팀 역학 테스트를 위해 대화 기록을 격리합니다.
3.  `weather_agent_team`(루트 에이전트)과 전용 세션 서비스를 사용하도록 구성된 `Runner`(`runner_agent_team`)를 생성합니다.
4.  업데이트된 `call_agent_async` 함수를 사용하여 `runner_agent_team`에 다른 유형의 쿼리(인사, 날씨 요청, 작별)를 보냅니다. 이 특정 테스트를 위해 러너, 사용자 ID, 세션 ID를 명시적으로 전달합니다.
5.  `run_team_conversation` 함수를 즉시 실행합니다.

다음과 같은 흐름을 기대합니다:

1.  "안녕하세요!" 쿼리가 `runner_agent_team`으로 갑니다.
2.  루트 에이전트(`weather_agent_team`)가 이를 수신하고, 지침과 `greeting_agent`의 설명을 기반으로 작업을 위임합니다.
3.  `greeting_agent`가 쿼리를 처리하고, `say_hello` 도구를 호출하며, 응답을 생성합니다.
4.  "뉴욕 날씨는 어떤가요?" 쿼리는 위임되지 않고 루트 에이전트가 직접 `get_weather` 도구를 사용하여 처리합니다.
5.  "고마워요, 안녕히 가세요!" 쿼리는 `farewell_agent`에게 위임되고, `say_goodbye` 도구를 사용합니다.




```python
# @title 에이전트 팀과 상호작용하기
import asyncio # asyncio가 import되었는지 확인

# 루트 에이전트(예: 이전 셀의 'weather_agent_team' 또는 'root_agent')가 정의되었는지 확인합니다.
# call_agent_async 함수가 정의되었는지 확인합니다.

# 루트 에이전트 변수가 있는지 확인한 후 대화 함수를 정의합니다.
root_agent_var_name = 'root_agent' # 3단계 가이드의 기본 이름
if 'weather_agent_team' in globals(): # 사용자가 이 이름을 대신 사용했는지 확인
    root_agent_var_name = 'weather_agent_team'
elif 'root_agent' not in globals():
    print("⚠️ 루트 에이전트('root_agent' 또는 'weather_agent_team')를 찾을 수 없습니다. run_team_conversation을 정의할 수 없습니다.")
    # 코드 블록이 어쨌든 실행될 경우 나중에 NameError를 방지하기 위해 더미 값을 할당합니다.
    root_agent = None # 또는 실행을 방지하기 위해 플래그 설정

# 루트 에이전트가 있을 경우에만 정의하고 실행합니다.
if root_agent_var_name in globals() and globals()[root_agent_var_name]:
    # 대화 로직을 위한 메인 async 함수를 정의합니다.
    # 이 함수 내부의 'await' 키워드는 비동기 작업에 필수적입니다.
    async def run_team_conversation():
        print("\n--- 에이전트 팀 위임 테스트 중 ---")
        session_service = InMemorySessionService()
        APP_NAME = "weather_tutorial_agent_team"
        USER_ID = "user_1_agent_team"
        SESSION_ID = "session_001_agent_team"
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        print(f"세션 생성됨: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

        actual_root_agent = globals()[root_agent_var_name]
        runner_agent_team = Runner( # 또는 InMemoryRunner 사용
            agent=actual_root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"Runner가 에이전트 '{actual_root_agent.name}'에 대해 생성되었습니다.")

        # --- await를 사용한 상호작용 (async def 내에서 올바름) ---
        await call_agent_async(query = "안녕하세요!",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
        await call_agent_async(query = "뉴욕 날씨는 어떤가요?",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
        await call_agent_async(query = "고마워요, 안녕히 가세요!",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)

    # --- `run_team_conversation` 비동기 함수 실행 ---
    # 환경에 따라 아래 방법 중 하나를 선택하세요.
    # 참고: 사용된 모델에 대한 API 키가 필요할 수 있습니다!

    # 방법 1: 직접 await (노트북/비동기 REPL 기본)
    # 환경이 최상위 await를 지원하는 경우(Colab/Jupyter 노트북 등),
    # 이벤트 루프가 이미 실행 중이므로 함수를 직접 await 할 수 있습니다.
    print("'await'를 사용하여 실행 시도 중 (노트북 기본)...")
    await run_team_conversation()

    # 방법 2: asyncio.run (표준 Python 스크립트 [.py]용)
    # 터미널에서 이 코드를 표준 Python 스크립트로 실행하는 경우,
    # 스크립트 컨텍스트는 동기식입니다. 비동기 함수를 실행하려면
    # 이벤트 루프를 생성하고 관리하기 위해 `asyncio.run()`이 필요합니다.
    # 이 방법을 사용하려면:
    # 1. 위의 `await run_team_conversation()` 줄을 주석 처리합니다.
    # 2. 다음 블록의 주석을 해제합니다:
    """
    import asyncio
    if __name__ == "__main__": # 스크립트가 직접 실행될 때만 실행되도록 보장
        print("'asyncio.run()'을 사용하여 실행 중 (표준 Python 스크립트용)...")
        try:
            # 이것은 이벤트 루프를 생성하고, 비동기 함수를 실행하며, 루프를 닫습니다.
            asyncio.run(run_team_conversation())
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
    """

else:
    # 이 메시지는 이전에 루트 에이전트 변수를 찾지 못했을 때 출력됩니다.
    print("\n⚠️ 이전 단계에서 루트 에이전트가 성공적으로 정의되지 않았으므로 에이전트 팀 대화 실행을 건너뜁니다.")
```

---

출력 로그, 특히 `--- 도구: ... 호출됨 ---` 메시지를 자세히 살펴보세요. 다음을 관찰해야 합니다:

*   "안녕하세요!"에 대해서는 `say_hello` 도구가 호출되었습니다 (`greeting_agent`가 처리했음을 나타냄).
*   "뉴욕 날씨는 어떤가요?"에 대해서는 `get_weather` 도구가 호출되었습니다 (루트 에이전트가 처리했음을 나타냄).
*   "고마워요, 안녕히 가세요!"에 대해서는 `say_goodbye` 도구가 호출되었습니다 (`farewell_agent`가 처리했음을 나타냄).

이는 성공적인 **자동 위임**을 확인시켜 줍니다! 루트 에이전트는 지침과 `sub_agents`의 `description`에 따라 사용자 요청을 팀 내 적절한 전문가 에이전트에게 올바르게 라우팅했습니다.

이제 여러 협력 에이전트로 애플리케이션을 구조화했습니다. 이 모듈식 설계는 더 복잡하고 유능한 에이전트 시스템을 구축하는 데 기본이 됩니다. 다음 단계에서는 세션 상태를 사용하여 에이전트가 턴 간에 정보를 기억할 수 있는 능력을 부여할 것입니다.

## 4단계: 세션 상태를 이용한 메모리 및 개인화 추가

지금까지 우리 에이전트 팀은 위임을 통해 다양한 작업을 처리할 수 있었지만, 각 상호작용은 처음부터 다시 시작됩니다. 즉, 에이전트는 세션 내에서 과거 대화나 사용자 선호도에 대한 기억이 없습니다. 더 정교하고 문맥을 인식하는 경험을 만들려면 에이전트에게 **메모리**가 필요합니다. ADK는 **세션 상태(Session State)**를 통해 이를 제공합니다.

**세션 상태란 무엇인가요?**

*   특정 사용자 세션(`APP_NAME`, `USER_ID`, `SESSION_ID`로 식별)에 연결된 Python 사전(`session.state`)입니다.
*   해당 세션 내에서 *여러 대화 턴에 걸쳐* 정보를 유지합니다.
*   에이전트와 도구는 이 상태를 읽고 쓸 수 있어 세부 정보를 기억하고, 행동을 조정하며, 응답을 개인화할 수 있습니다.

**에이전트가 상태와 상호작용하는 방법:**

1.  **`ToolContext` (주요 방법):** 도구는 `ToolContext` 객체를 받을 수 있습니다 (ADK가 마지막 인수로 선언된 경우 자동으로 제공). 이 객체는 `tool_context.state`를 통해 세션 상태에 직접 접근할 수 있게 하여, 도구가 실행 *중에* 선호도를 읽거나 결과를 저장할 수 있도록 합니다.
2.  **`output_key` (에이전트 응답 자동 저장):** `Agent`는 `output_key="your_key"`로 구성될 수 있습니다. 그러면 ADK는 해당 턴에 대한 에이전트의 최종 텍스트 응답을 `session.state["your_key"]`에 자동으로 저장합니다.

**이 단계에서는 날씨 봇 팀을 다음과 같이 향상시킬 것입니다:**

1.  상태를 독립적으로 보여주기 위해 **새로운** `InMemorySessionService`를 사용합니다.
2.  사용자의 `temperature_unit` 선호도로 세션 상태를 초기화합니다.
3.  `ToolContext`를 통해 이 선호도를 읽고 출력 형식(섭씨/화씨)을 조정하는 상태 인식 버전의 날씨 도구(`get_weather_stateful`)를 만듭니다.
4.  이 상태 인식 도구를 사용하도록 루트 에이전트를 업데이트하고, 최종 날씨 보고서를 세션 상태에 자동으로 저장하도록 `output_key`로 구성합니다.
5.  초기 상태가 도구에 어떤 영향을 미치는지, 수동 상태 변경이 후속 행동을 어떻게 바꾸는지, 그리고 `output_key`가 에이전트의 응답을 어떻게 유지하는지 관찰하기 위해 대화를 실행합니다.

---

**1. 새로운 세션 서비스 및 상태 초기화**

이전 단계의 간섭 없이 상태 관리를 명확하게 보여주기 위해 새로운 `InMemorySessionService`를 인스턴스화합니다. 또한 사용자가 선호하는 온도 단위를 정의하는 초기 상태로 세션을 생성합니다.


```python
# @title 1. 새로운 세션 서비스 및 상태 초기화

# 필요한 세션 구성 요소 가져오기
from google.adk.sessions import InMemorySessionService

# 이 상태 시연을 위해 새로운 세션 서비스 인스턴스 생성
session_service_stateful = InMemorySessionService()
print("✅ 상태 시연을 위한 새로운 InMemorySessionService가 생성되었습니다.")

# 이 튜토리얼의 이 부분을 위한 새로운 세션 ID 정의
SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"

# 초기 상태 데이터 정의 - 사용자는 처음에 섭씨를 선호
initial_state = {
    "user_preference_temperature_unit": "Celsius"
}

# 초기 상태를 제공하여 세션 생성
session_stateful = await session_service_stateful.create_session(
    app_name=APP_NAME, # 일관된 앱 이름 사용
    user_id=USER_ID_STATEFUL,
    session_id=SESSION_ID_STATEFUL,
    state=initial_state # <<< 생성 중 상태 초기화
)
print(f"✅ 사용자 '{USER_ID_STATEFUL}'에 대한 세션 '{SESSION_ID_STATEFUL}'이 생성되었습니다.")

# 초기 상태가 올바르게 설정되었는지 확인
retrieved_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id = SESSION_ID_STATEFUL)
print("\n--- 초기 세션 상태 ---")
if retrieved_session:
    print(retrieved_session.state)
else:
    print("오류: 세션을 검색할 수 없습니다.")
```

---

**2. 상태 인식 날씨 도구 생성 (`get_weather_stateful`)**

이제 날씨 도구의 새 버전을 만듭니다. 주요 특징은 `tool_context: ToolContext`를 받아 `tool_context.state`에 접근할 수 있다는 것입니다. `user_preference_temperature_unit`를 읽고 그에 따라 온도를 형식화합니다.


*   **핵심 개념: `ToolContext`** 이 객체는 도구 로직이 상태 변수 읽기 및 쓰기를 포함한 세션의 컨텍스트와 상호 작용할 수 있도록 하는 다리입니다. 도구 함수의 마지막 매개변수로 정의하면 ADK가 자동으로 주입합니다.


*   **모범 사례:** 상태에서 읽을 때 `dictionary.get('key', default_value)`를 사용하여 키가 아직 존재하지 않을 수 있는 경우를 처리하여 도구가 충돌하지 않도록 하세요.


```python
from google.adk.tools.tool_context import ToolContext

def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """세션 상태에 따라 날씨를 검색하고 온도 단위를 변환합니다."""
    print(f"--- 도구: {city}에 대해 get_weather_stateful 호출됨 ---")

    # --- 상태에서 선호도 읽기 ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius") # 기본값은 섭씨
    print(f"--- 도구: 상태 'user_preference_temperature_unit' 읽기: {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # 모의 날씨 데이터 (내부적으로 항상 섭씨로 저장됨)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # 상태 선호도에 따라 온도 형식 지정
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32 # 화씨 계산
            temp_unit = "°F"
        else: # 기본값은 섭씨
            temp_value = temp_c
            temp_unit = "°C"

        report = f"{city.capitalize()}의 날씨는 {condition}이며 온도는 {temp_value:.0f}{temp_unit}입니다."
        result = {"status": "success", "report": report}
        print(f"--- 도구: {preferred_unit}로 보고서 생성됨. 결과: {result} ---")

        # 상태에 다시 쓰기 예제 (이 도구에서는 선택 사항)
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- 도구: 상태 'last_city_checked_stateful' 업데이트됨: {city} ---")

        return result
    else:
        # 도시를 찾을 수 없는 경우 처리
        error_msg = f"죄송합니다. '{city}'에 대한 날씨 정보가 없습니다."
        print(f"--- 도구: 도시 '{city}'를 찾을 수 없음. ---")
        return {"status": "error", "error_message": error_msg}

print("✅ 상태 인식 'get_weather_stateful' 도구가 정의되었습니다.")
```

---

**3. 하위 에이전트 재정의 및 루트 에이전트 업데이트**

이 단계가 독립적으로 올바르게 빌드되도록 하려면 먼저 3단계에서와 똑같이 `greeting_agent`와 `farewell_agent`를 재정의합니다. 그런 다음 새로운 루트 에이전트(`weather_agent_v4_stateful`)를 정의합니다:

*   새로운 `get_weather_stateful` 도구를 사용합니다.
*   위임을 위해 인사 및 작별 하위 에이전트를 포함합니다.
*   **결정적으로**, `output_key="last_weather_report"`를 설정하여 최종 날씨 응답을 세션 상태에 자동으로 저장합니다.


```python
# @title 3. 하위 에이전트 재정의 및 output_key로 루트 에이전트 업데이트

# 필요한 가져오기 확인: Agent, LiteLlm, Runner
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
# 'say_hello', 'say_goodbye' 도구가 정의되었는지 확인 (3단계에서)
# MODEL_GPT_4O, MODEL_GEMINI_2_0_FLASH 등 모델 상수가 정의되었는지 확인

# --- 인사 에이전트 재정의 (3단계에서) ---
greeting_agent = None
try:
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent",
        instruction="당신은 인사 에이전트입니다. 당신의 유일한 임무는 'say_hello' 도구를 사용하여 친절한 인사를 제공하는 것입니다. 다른 작업은 하지 마세요.",
        description="'say_hello' 도구를 사용하여 간단한 인사와 안부를 처리합니다.",
        tools=[say_hello],
    )
    print(f"✅ 에이전트 '{greeting_agent.name}'가 재정의되었습니다.")
except Exception as e:
    print(f"❌ 인사 에이전트를 재정의할 수 없습니다. 오류: {e}")

# --- 작별 에이전트 재정의 (3단계에서) ---
farewell_agent = None
try:
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent",
        instruction="당신은 작별 에이전트입니다. 당신의 유일한 임무는 'say_goodbye' 도구를 사용하여 정중한 작별 메시지를 제공하는 것입니다. 다른 작업은 수행하지 마세요.",
        description="'say_goodbye' 도구를 사용하여 간단한 작별 인사를 처리합니다.",
        tools=[say_goodbye],
    )
    print(f"✅ 에이전트 '{farewell_agent.name}'가 재정의되었습니다.")
except Exception as e:
    print(f"❌ 작별 에이전트를 재정의할 수 없습니다. 오류: {e}")

# --- 업데이트된 루트 에이전트 정의 ---
root_agent_stateful = None
runner_root_stateful = None # runner 초기화

# 루트 에이전트를 생성하기 전에 전제 조건 확인
if greeting_agent and farewell_agent and 'get_weather_stateful' in globals():

    root_agent_model = MODEL_GEMINI_2_0_FLASH # 오케스트레이션 모델 선택

    root_agent_stateful = Agent(
        name="weather_agent_v4_stateful", # 새 버전 이름
        model=root_agent_model,
        description="메인 에이전트: 날씨 제공(상태 인식 단위), 인사/작별 위임, 보고서를 상태에 저장.",
        instruction="당신은 메인 날씨 에이전트입니다. 'get_weather_stateful'을 사용하여 날씨를 제공하는 것이 당신의 임무입니다. "
                    "도구는 상태에 저장된 사용자 선호도에 따라 온도를 형식화합니다. "
                    "간단한 인사는 'greeting_agent'에게, 작별 인사는 'farewell_agent'에게 위임하세요. "
                    "날씨 요청, 인사, 작별 인사만 처리하세요.",
        tools=[get_weather_stateful], # 상태 인식 도구 사용
        sub_agents=[greeting_agent, farewell_agent], # 하위 에이전트 포함
        output_key="last_weather_report" # <<< 에이전트의 최종 날씨 응답 자동 저장
    )
    print(f"✅ 루트 에이전트 '{root_agent_stateful.name}'가 상태 인식 도구와 output_key를 사용하여 생성되었습니다.")

    # --- 이 루트 에이전트 및 새로운 세션 서비스를 위한 Runner 생성 ---
    runner_root_stateful = Runner(
        agent=root_agent_stateful,
        app_name=APP_NAME,
        session_service=session_service_stateful # 새로운 상태 인식 세션 서비스 사용
    )
    print(f"✅ 상태 인식 루트 에이전트 '{runner_root_stateful.agent.name}'를 위한 Runner가 상태 인식 세션 서비스를 사용하여 생성되었습니다.")

else:
    print("❌ 상태 인식 루트 에이전트를 생성할 수 없습니다. 전제 조건이 누락되었습니다.")
    if not greeting_agent: print(" - greeting_agent 정의 누락.")
    if not farewell_agent: print(" - farewell_agent 정의 누락.")
    if 'get_weather_stateful' not in globals(): print(" - get_weather_stateful 도구 누락.")
```

---

**4. 상태 흐름 상호작용 및 테스트**

이제 상태 상호작용을 테스트하기 위해 설계된 대화를 실행해 보겠습니다. 이를 위해 `runner_root_stateful`(우리의 상태 인식 에이전트 및 `session_service_stateful`과 연결됨)을 사용합니다. 이전에 정의한 `call_agent_async` 함수를 사용하며, 올바른 러너, 사용자 ID(`USER_ID_STATEFUL`), 세션 ID(`SESSION_ID_STATEFUL`)를 전달해야 합니다.

대화 흐름은 다음과 같습니다:

1.  **날씨 확인 (런던):** `get_weather_stateful` 도구는 1절에서 초기화된 세션 상태에서 초기 "섭씨" 선호도를 읽어야 합니다. 루트 에이전트의 최종 응답(섭씨로 된 날씨 보고서)은 `output_key` 구성을 통해 `state['last_weather_report']`에 저장되어야 합니다.
2.  **수동으로 상태 업데이트:** `InMemorySessionService` 인스턴스(`session_service_stateful`) 내에 저장된 상태를 *직접 수정*합니다.
    *   **왜 직접 수정하는가?** `session_service.get_session()` 메서드는 세션의 *사본*을 반환합니다. 해당 사본을 수정해도 후속 에이전트 실행에서 사용되는 상태에는 영향을 미치지 않습니다. `InMemorySessionService`를 사용한 이 테스트 시나리오에서는 내부 `sessions` 사전에 접근하여 `user_preference_temperature_unit`에 대해 *실제로* 저장된 상태 값을 "화씨"로 변경합니다. *참고: 실제 애플리케이션에서는 상태 변경이 일반적으로 도구나 에이전트 로직이 `EventActions(state_delta=...)`를 반환하여 트리거되며, 직접적인 수동 업데이트는 아닙니다.*
3.  **다시 날씨 확인 (뉴욕):** `get_weather_stateful` 도구는 이제 상태에서 업데이트된 "화씨" 선호도를 읽고 그에 따라 온도를 변환해야 합니다. 루트 에이전트의 *새로운* 응답(화씨로 된 날씨)은 `output_key`로 인해 `state['last_weather_report']`의 이전 값을 덮어씁니다.
4.  **에이전트에게 인사하기:** 상태 인식 작업과 함께 `greeting_agent`에 대한 위임이 여전히 올바르게 작동하는지 확인합니다. 이 상호작용은 이 특정 시퀀스에서 `output_key`에 의해 저장되는 *마지막* 응답이 됩니다.
5.  **최종 상태 검사:** 대화 후, 세션을 마지막으로 한 번 더 검색(사본 얻기)하고 상태를 출력하여 `user_preference_temperature_unit`가 실제로 "화씨"인지 확인하고, `output_key`에 의해 저장된 최종 값(이 실행에서는 인사가 될 것임)을 관찰하고, 도구에 의해 작성된 `last_city_checked_stateful` 값을 확인합니다.


```python
# @title 4. 상태 흐름 및 output_key 테스트를 위한 상호작용
import asyncio # asyncio가 import되었는지 확인

# 상태 인식 러너(runner_root_stateful)가 이전 셀에서 사용 가능한지 확인
# call_agent_async, USER_ID_STATEFUL, SESSION_ID_STATEFUL, APP_NAME이 정의되었는지 확인

if 'runner_root_stateful' in globals() and runner_root_stateful:
    # 상태 인식 대화 로직을 위한 메인 async 함수 정의
    # 이 함수 내부의 'await' 키워드는 비동기 작업에 필수적
    async def run_stateful_conversation():
        print("\n--- 상태 테스트: 온도 단위 변환 및 output_key ---")

        # 1. 날씨 확인 (초기 상태 사용: 섭씨)
        print("--- 1번째 턴: 런던 날씨 요청 (섭씨 예상) ---")
        await call_agent_async(query= "런던 날씨는 어때?",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 2. 수동으로 상태 선호도를 화씨로 업데이트 - 저장소 직접 수정
        print("\n--- 상태 수동 업데이트: 단위를 화씨로 설정 ---")
        try:
            # 내부 저장소에 직접 접근 - 이는 테스트를 위한 InMemorySessionService에만 해당
            # 참고: 영구 서비스(데이터베이스, VertexAI)를 사용하는 프로덕션에서는
            # 일반적으로 에이전트 작업이나 사용 가능한 특정 서비스 API를 통해 상태를 업데이트하며,
            # 내부 저장소를 직접 조작하지 않습니다.
            stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]
            stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
            # 선택 사항: 로직이 타임스탬프에 의존하는 경우 타임스탬프도 업데이트할 수 있습니다.
            # import time
            # stored_session.last_update_time = time.time()
            print(f"--- 저장된 세션 상태 업데이트됨. 현재 'user_preference_temperature_unit': {stored_session.state.get('user_preference_temperature_unit', '설정되지 않음')} ---") # 안전을 위해 .get 추가
        except KeyError:
            print(f"--- 오류: 상태를 업데이트하기 위해 앱 '{APP_NAME}'의 사용자 '{USER_ID_STATEFUL}'에 대한 내부 저장소에서 세션 '{SESSION_ID_STATEFUL}'을 검색할 수 없습니다. ID와 세션 생성 여부를 확인하세요. ---")
        except Exception as e:
             print(f"--- 내부 세션 상태 업데이트 오류: {e} ---")

        # 3. 다시 날씨 확인 (도구는 이제 화씨를 사용해야 함)
        # 이것은 또한 output_key를 통해 'last_weather_report'를 업데이트함
        print("\n--- 2번째 턴: 뉴욕 날씨 요청 (화씨 예상) ---")
        await call_agent_async(query= "뉴욕 날씨를 알려줘.",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 4. 기본 위임 테스트 (여전히 작동해야 함)
        # 이것은 'last_weather_report'를 다시 업데이트하여 뉴욕 날씨 보고서를 덮어씀
        print("\n--- 3번째 턴: 인사 보내기 ---")
        await call_agent_async(query= "안녕!",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

    # --- `run_stateful_conversation` 비동기 함수 실행 ---
    # 환경에 따라 아래 방법 중 하나를 선택

    # 방법 1: 직접 await (노트북/비동기 REPL 기본)
    # 환경이 최상위 await를 지원하는 경우(Colab/Jupyter 노트북 등),
    # 이벤트 루프가 이미 실행 중이므로 함수를 직접 await 할 수 있습니다.
    print("'await'를 사용하여 실행 시도 중 (노트북 기본)...")
    await run_stateful_conversation()

    # 방법 2: asyncio.run (표준 Python 스크립트 [.py]용)
    # 터미널에서 이 코드를 표준 Python 스크립트로 실행하는 경우,
    # 스크립트 컨텍스트는 동기식입니다. 비동기 함수를 실행하려면
    # 이벤트 루프를 생성하고 관리하기 위해 `asyncio.run()`이 필요합니다.
    # 이 방법을 사용하려면:
    # 1. 위의 `await run_stateful_conversation()` 줄을 주석 처리합니다.
    # 2. 다음 블록의 주석을 해제합니다:
    """
    import asyncio
    if __name__ == "__main__": # 스크립트가 직접 실행될 때만 실행되도록 보장
        print("'asyncio.run()'을 사용하여 실행 중 (표준 Python 스크립트용)...")
        try:
            # 이것은 이벤트 루프를 생성하고, 비동기 함수를 실행하며, 루프를 닫습니다.
            asyncio.run(run_stateful_conversation())
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
    """

    # --- 대화 후 최종 세션 상태 검사 ---
    # 이 블록은 어느 실행 방법이 완료된 후에 실행됩니다.
    print("\n--- 최종 세션 상태 검사 ---")
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id= USER_ID_STATEFUL,
                                                         session_id=SESSION_ID_STATEFUL)
    if final_session:
        # 잠재적으로 누락된 키에 대한 안전한 접근을 위해 .get() 사용
        print(f"최종 선호도: {final_session.state.get('user_preference_temperature_unit', '설정되지 않음')}")
        print(f"최종 마지막 날씨 보고서 (output_key에서): {final_session.state.get('last_weather_report', '설정되지 않음')}")
        print(f"최종 마지막 확인 도시 (도구에 의해): {final_session.state.get('last_city_checked_stateful', '설정되지 않음')}")
        # 상세 보기를 위한 전체 상태 사전 출력
        # print(f"전체 상태 사전: {final_session.state}") # 상세 보기용
    else:
        print("\n❌ 오류: 최종 세션 상태를 검색할 수 없습니다.")

else:
    print("\n⚠️ 상태 테스트 대화를 건너뜁니다. 상태 인식 루트 에이전트 러너('runner_root_stateful')를 사용할 수 없습니다.")
```

---

대화 흐름과 최종 세션 상태 출력을 검토하여 다음을 확인할 수 있습니다:

*   **상태 읽기:** 날씨 도구(`get_weather_stateful`)는 상태에서 `user_preference_temperature_unit`를 올바르게 읽어 처음에는 런던에 대해 "섭씨"를 사용했습니다.
*   **상태 업데이트:** 직접 수정으로 저장된 선호도가 "화씨"로 성공적으로 변경되었습니다.
*   **상태 읽기 (업데이트됨):** 도구는 이후 뉴욕 날씨를 물었을 때 "화씨"를 읽고 변환을 수행했습니다.
*   **도구 상태 쓰기:** 도구는 `tool_context.state`를 통해 상태에 `last_city_checked_stateful`("뉴욕"을 두 번째 날씨 확인 후)을 성공적으로 썼습니다.
*   **위임:** 상태 수정 후에도 "안녕!"에 대한 `greeting_agent`로의 위임이 올바르게 작동했습니다.
*   **`output_key`:** `output_key="last_weather_report"`는 루트 에이전트가 궁극적으로 응답하는 *각 턴*에 대한 루트 에이전트의 *최종* 응답을 성공적으로 저장했습니다. 이 시퀀스에서 마지막 응답은 인사("안녕하세요!")였으므로 상태 키의 날씨 보고서를 덮어썼습니다.
*   **최종 상태:** 최종 확인 결과 선호도가 "화씨"로 유지되었음을 확인합니다.

이제 `ToolContext`를 사용하여 에이전트 동작을 개인화하기 위해 세션 상태를 성공적으로 통합했고, `InMemorySessionService` 테스트를 위해 상태를 수동으로 조작했으며, `output_key`가 에이전트의 마지막 응답을 상태에 저장하는 간단한 메커니즘을 제공하는 방법을 관찰했습니다. 상태 관리에 대한 이 기초적인 이해는 다음 단계에서 콜백을 사용하여 안전 가드레일을 구현하는 데 핵심입니다.

---

## 5단계: 안전 기능 추가 - `before_model_callback`을 이용한 입력 가드레일

우리 에이전트 팀은 선호도를 기억하고 도구를 효과적으로 사용하면서 점점 더 유능해지고 있습니다. 그러나 실제 시나리오에서는 잠재적으로 문제가 있는 요청이 핵심 거대 언어 모델(LLM)에 도달하기 전에 에이전트의 행동을 제어하는 안전 메커니즘이 종종 필요합니다.

ADK는 **콜백(Callbacks)**을 제공합니다. 이는 에이전트의 실행 수명 주기의 특정 지점에 연결할 수 있는 함수입니다. `before_model_callback`은 입력 안전에 특히 유용합니다.

**`before_model_callback`이란 무엇인가요?**

*   에이전트가 컴파일된 요청(대화 기록, 지침, 최신 사용자 메시지 포함)을 기본 LLM으로 보내기 *직전에* ADK가 실행하는 여러분이 정의한 Python 함수입니다.
*   **목적:** 요청을 검사하고, 필요한 경우 수정하거나, 미리 정의된 규칙에 따라 완전히 차단합니다.

**일반적인 사용 사례:**

*   **입력 유효성 검사/필터링:** 사용자 입력이 기준을 충족하는지 또는 허용되지 않는 콘텐츠(예: 개인 식별 정보 또는 키워드)를 포함하는지 확인합니다.
*   **가드레일:** 유해하거나, 주제를 벗어나거나, 정책을 위반하는 요청이 LLM에 의해 처리되는 것을 방지합니다.
*   **동적 프롬프트 수정:** 보내기 직전에 시기적절한 정보(예: 세션 상태에서)를 LLM 요청 컨텍스트에 추가합니다.

**작동 방식:**

1.  `callback_context: CallbackContext`와 `llm_request: LlmRequest`를 받는 함수를 정의합니다.
    *   `callback_context`: 에이전트 정보, 세션 상태(`callback_context.state`) 등에 접근할 수 있습니다.
    *   `llm_request`: LLM을 위한 전체 페이로드(`contents`, `config`)를 포함합니다.
2.  함수 내부:
    *   **검사:** `llm_request.contents`(특히 마지막 사용자 메시지)를 검사합니다.
    *   **수정 (주의해서 사용):** `llm_request`의 일부를 변경할 *수 있습니다*.
    *   **차단 (가드레일):** `LlmResponse` 객체를 반환합니다. ADK는 이 응답을 즉시 다시 보내고 해당 턴에 대한 LLM 호출을 *건너뜁니다*.
    *   **허용:** `None`을 반환합니다. ADK는 (잠재적으로 수정된) 요청으로 LLM을 호출합니다.

**이 단계에서는 다음을 수행합니다:**

1.  사용자 입력에서 특정 키워드("BLOCK")를 확인하는 `before_model_callback` 함수(`block_keyword_guardrail`)를 정의합니다.
2.  이 콜백을 사용하도록 상태 인식 루트 에이전트(4단계의 `weather_agent_v4_stateful`)를 업데이트합니다.
3.  상태 연속성을 유지하기 위해 이 업데이트된 에이전트와 연결되지만 *동일한 상태 인식 세션 서비스*를 사용하는 새로운 러너를 생성합니다.
4.  일반 요청과 키워드가 포함된 요청을 모두 보내 가드레일을 테스트합니다.

---

**1. 가드레일 콜백 함수 정의**

이 함수는 `llm_request` 콘텐츠 내의 마지막 사용자 메시지를 검사합니다. "BLOCK"(대소문자 구분 없음)을 찾으면 `LlmResponse`를 구성하고 반환하여 흐름을 차단합니다. 그렇지 않으면 `None`을 반환합니다.


```python
# @title 1. before_model_callback 가드레일 정의

# 필요한 import가 사용 가능한지 확인
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types # 응답 콘텐츠 생성을 위해
from typing import Optional

def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    최신 사용자 메시지에서 'BLOCK'을 검사합니다. 발견되면 LLM 호출을 차단하고
    미리 정의된 LlmResponse를 반환합니다. 그렇지 않으면 None을 반환하여 계속 진행합니다.
    """
    agent_name = callback_context.agent_name # 모델 호출이 가로채진 에이전트의 이름을 가져옴
    print(f"--- 콜백: block_keyword_guardrail이 에이전트 {agent_name}에 대해 실행 중 ---")

    # 요청 기록에서 최신 사용자 메시지의 텍스트 추출
    last_user_message_text = ""
    if llm_request.contents:
        # 역할이 'user'인 가장 최근 메시지 찾기
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                # 단순화를 위해 텍스트가 첫 번째 부분에 있다고 가정
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break # 마지막 사용자 메시지 텍스트를 찾았음

    print(f"--- 콜백: 마지막 사용자 메시지 검사 중: '{last_user_message_text[:100]}...' ---") # 첫 100자 기록

    # --- 가드레일 로직 ---
    keyword_to_block = "BLOCK"
    if keyword_to_block in last_user_message_text.upper(): # 대소문자 무시 검사
        print(f"--- 콜백: '{keyword_to_block}' 발견. LLM 호출 차단! ---")
        # 선택적으로 상태에 플래그를 설정하여 차단 이벤트 기록
        callback_context.state["guardrail_block_keyword_triggered"] = True
        print(f"--- 콜백: 상태 'guardrail_block_keyword_triggered'를 True로 설정 ---")

        # 흐름을 중지하고 대신 이 응답을 보내기 위해 LlmResponse 구성 및 반환
        return LlmResponse(
            content=types.Content(
                role="model", # 에이전트 관점에서의 응답 모방
                parts=[types.Part(text=f"차단된 키워드 '{keyword_to_block}'가 포함되어 있어 이 요청을 처리할 수 없습니다.")],
            )
            # 참고: 필요한 경우 여기에 error_message 필드를 설정할 수도 있습니다.
        )
    else:
        # 키워드를 찾지 못했으므로 요청을 LLM으로 계속 진행 허용
        print(f"--- 콜백: 키워드를 찾지 못했습니다. {agent_name}에 대한 LLM 호출 허용. ---")
        return None # None을 반환하면 ADK가 정상적으로 계속 진행하라는 신호

print("✅ block_keyword_guardrail 함수가 정의되었습니다.")
```

---

**2. 콜백을 사용하도록 루트 에이전트 업데이트**

루트 에이전트를 재정의하고, `before_model_callback` 매개변수를 추가하고 새로운 가드레일 함수를 가리키도록 합니다. 명확성을 위해 새 버전 이름을 부여합니다.

*중요:* 이 루트 에이전트를 정의하기 전에 하위 에이전트(`greeting_agent`, `farewell_agent`)와 상태 인식 도구(`get_weather_stateful`)가 이 컨텍스트에서 사용 가능하거나 이전 단계에서 이미 사용 가능한지 확인해야 합니다.


```python
# @title 2. before_model_callback으로 루트 에이전트 업데이트


# --- 하위 에이전트 재정의 (이 컨텍스트에 존재하는지 확인) ---
greeting_agent = None
try:
    # 정의된 모델 상수 사용
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent", # 일관성을 위해 원래 이름 유지
        instruction="당신은 인사 에이전트입니다. 당신의 유일한 임무는 'say_hello' 도구를 사용하여 친절한 인사를 제공하는 것입니다. 다른 작업은 하지 마세요.",
        description="'say_hello' 도구를 사용하여 간단한 인사와 안부를 처리합니다.",
        tools=[say_hello],
    )
    print(f"✅ 하위 에이전트 '{greeting_agent.name}'가 재정의되었습니다.")
except Exception as e:
    print(f"❌ 인사 에이전트를 재정의할 수 없습니다. 모델/API 키({greeting_agent.model})를 확인하세요. 오류: {e}")

farewell_agent = None
try:
    # 정의된 모델 상수 사용
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent", # 원래 이름 유지
        instruction="당신은 작별 에이전트입니다. 당신의 유일한 임무는 'say_goodbye' 도구를 사용하여 정중한 작별 메시지를 제공하는 것입니다. 다른 작업은 수행하지 마세요.",
        description="'say_goodbye' 도구를 사용하여 간단한 작별 인사를 처리합니다.",
        tools=[say_goodbye],
    )
    print(f"✅ 하위 에이전트 '{farewell_agent.name}'가 재정의되었습니다.")
except Exception as e:
    print(f"❌ 작별 에이전트를 재정의할 수 없습니다. 모델/API 키({farewell_agent.model})를 확인하세요. 오류: {e}")


# --- 콜백을 포함한 루트 에이전트 정의 ---
root_agent_model_guardrail = None
runner_root_model_guardrail = None

# 진행하기 전에 모든 구성 요소 확인
if greeting_agent and farewell_agent and 'get_weather_stateful' in globals() and 'block_keyword_guardrail' in globals():

    # 정의된 모델 상수 사용
    root_agent_model = MODEL_GEMINI_2_0_FLASH

    root_agent_model_guardrail = Agent(
        name="weather_agent_v5_model_guardrail", # 명확성을 위한 새 버전 이름
        model=root_agent_model,
        description="메인 에이전트: 날씨 처리, 인사/작별 위임, 입력 키워드 가드레일 포함.",
        instruction="당신은 메인 날씨 에이전트입니다. 'get_weather_stateful'을 사용하여 날씨를 제공하세요. "
                    "간단한 인사는 'greeting_agent'에게, 작별 인사는 'farewell_agent'에게 위임하세요. "
                    "날씨 요청, 인사, 작별 인사만 처리하세요.",
        tools=[get_weather],
        sub_agents=[greeting_agent, farewell_agent], # 재정의된 하위 에이전트 참조
        output_key="last_weather_report", # 4단계의 output_key 유지
        before_model_callback=block_keyword_guardrail # <<< 가드레일 콜백 할당
    )
    print(f"✅ 루트 에이전트 '{root_agent_model_guardrail.name}'가 before_model_callback으로 생성되었습니다.")

    # --- 이 에이전트를 위한 Runner 생성, 동일한 상태 인식 세션 서비스 사용 ---
    # 4단계의 session_service_stateful이 존재하는지 확인
    if 'session_service_stateful' in globals():
        runner_root_model_guardrail = Runner(
            agent=root_agent_model_guardrail,
            app_name=APP_NAME, # 일관된 APP_NAME 사용
            session_service=session_service_stateful # <<< 4단계의 서비스 사용
        )
        print(f"✅ 가드레일 에이전트 '{runner_root_model_guardrail.agent.name}'를 위한 Runner가 상태 인식 세션 서비스를 사용하여 생성되었습니다.")
    else:
        print("❌ Runner를 생성할 수 없습니다. 4단계의 'session_service_stateful'이 없습니다.")

else:
    print("❌ 모델 가드레일로 루트 에이전트를 생성할 수 없습니다. 하나 이상의 전제 조건이 없거나 초기화에 실패했습니다:")
    if not greeting_agent: print("   - 인사 에이전트")
    if not farewell_agent: print("   - 작별 에이전트")
    if 'get_weather_stateful' not in globals(): print("   - 'get_weather_stateful' 도구")
    if 'block_keyword_guardrail' not in globals(): print("   - 'block_keyword_guardrail' 콜백")
```

---

**3. 가드레일 테스트를 위한 상호작용**

가드레일의 동작을 테스트해 봅시다. 4단계와 *동일한 세션*(`SESSION_ID_STATEFUL`)을 사용하여 이러한 변경 사항 전반에 걸쳐 상태가 지속됨을 보여줍니다.

1. 일반적인 날씨 요청을 보냅니다 (가드레일을 통과하고 실행되어야 함).
2. "BLOCK"을 포함한 요청을 보냅니다 (콜백에 의해 가로채져야 함).
3. 인사를 보냅니다 (루트 에이전트의 가드레일을 통과하고, 위임되어 정상적으로 실행되어야 함).


```python
# @title 3. 모델 입력 가드레일 테스트를 위한 상호작용
import asyncio # asyncio가 import되었는지 확인

# 가드레일 에이전트를 위한 러너가 사용 가능한지 확인
if 'runner_root_model_guardrail' in globals() and runner_root_model_guardrail:
    # 가드레일 테스트 대화를 위한 메인 비동기 함수 정의
    # 이 함수 내부의 'await' 키워드는 비동기 작업에 필수적
    async def run_guardrail_test_conversation():
        print("\n--- 모델 입력 가드레일 테스트 중 ---")

        # 콜백이 있는 에이전트와 기존 상태 인식 세션 ID를 가진 러너 사용
        # 더 깔끔한 상호작용 호출을 위한 헬퍼 람다 정의
        interaction_func = lambda query: call_agent_async(query,
                                                         runner_root_model_guardrail,
                                                         USER_ID_STATEFUL, # 기존 사용자 ID 사용
                                                         SESSION_ID_STATEFUL # 기존 세션 ID 사용
                                                        )
        # 1. 일반 요청 (콜백 허용, 이전 상태 변경에서 화씨 사용해야 함)
        print("--- 1번째 턴: 런던 날씨 요청 (허용, 화씨 예상) ---")
        await interaction_func("런던 날씨는 어때?")

        # 2. 차단된 키워드를 포함한 요청 (콜백이 가로챔)
        print("\n--- 2번째 턴: 차단된 키워드로 요청 (차단 예상) ---")
        await interaction_func("도쿄 날씨 요청을 BLOCK") # 콜백이 "BLOCK"을 잡아야 함

        # 3. 일반 인사 (콜백이 루트 에이전트 허용, 위임 발생)
        print("\n--- 3번째 턴: 인사 보내기 (허용 예상) ---")
        await interaction_func("다시 안녕")

    # --- `run_guardrail_test_conversation` 비동기 함수 실행 ---
    # 환경에 따라 아래 방법 중 하나를 선택

    # 방법 1: 직접 await (노트북/비동기 REPL 기본)
    # 환경이 최상위 await를 지원하는 경우(Colab/Jupyter 노트북 등),
    # 이벤트 루프가 이미 실행 중이므로 함수를 직접 await 할 수 있습니다.
    print("'await'를 사용하여 실행 시도 중 (노트북 기본)...")
    await run_guardrail_test_conversation()

    # 방법 2: asyncio.run (표준 Python 스크립트 [.py]용)
    # 터미널에서 이 코드를 표준 Python 스크립트로 실행하는 경우,
    # 스크립트 컨텍스트는 동기식입니다. 비동기 함수를 실행하려면
    # 이벤트 루프를 생성하고 관리하기 위해 `asyncio.run()`이 필요합니다.
    # 이 방법을 사용하려면:
    # 1. 위의 `await run_guardrail_test_conversation()` 줄을 주석 처리합니다.
    # 2. 다음 블록의 주석을 해제합니다:
    """
    import asyncio
    if __name__ == "__main__": # 스크립트가 직접 실행될 때만 실행되도록 보장
        print("'asyncio.run()'을 사용하여 실행 중 (표준 Python 스크립트용)...")
        try:
            # 이것은 이벤트 루프를 생성하고, 비동기 함수를 실행하며, 루프를 닫습니다.
            asyncio.run(run_guardrail_test_conversation())
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
    """

    # --- 대화 후 최종 세션 상태 검사 ---
    # 이 블록은 어느 실행 방법이 완료된 후에 실행됩니다.
    # 선택 사항: 콜백에 의해 설정된 트리거 플래그에 대한 상태 확인
    print("\n--- 최종 세션 상태 검사 (가드레일 테스트 후) ---")
    # 이 상태 인식 세션과 관련된 세션 서비스 인스턴스 사용
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id=SESSION_ID_STATEFUL)
    if final_session:
        # 안전한 접근을 위해 .get() 사용
        print(f"가드레일 트리거 플래그: {final_session.state.get('guardrail_block_keyword_triggered', '설정되지 않음 (또는 False)')}")
        print(f"마지막 날씨 보고서: {final_session.state.get('last_weather_report', '설정되지 않음')}") # 성공 시 런던 날씨여야 함
        print(f"온도 단위: {final_session.state.get('user_preference_temperature_unit', '설정되지 않음')}") # 화씨여야 함
        # print(f"전체 상태 사전: {final_session.state}") # 상세 보기용
    else:
        print("\n❌ 오류: 최종 세션 상태를 검색할 수 없습니다.")

else:
    print("\n⚠️ 모델 가드레일 테스트를 건너뜁니다. 러너('runner_root_model_guardrail')를 사용할 수 없습니다.")
```

---

실행 흐름을 관찰하세요:

1.  **런던 날씨:** `weather_agent_v5_model_guardrail`에 대한 콜백이 실행되고, 메시지를 검사한 후 "키워드를 찾을 수 없습니다. LLM 호출 허용."을 출력하고 `None`을 반환합니다. 에이전트는 계속 진행하여 `get_weather_stateful` 도구를 호출하고(4단계의 상태 변경에서 "화씨" 선호도를 사용), 날씨를 반환합니다. 이 응답은 `output_key`를 통해 `last_weather_report`를 업데이트합니다.
2.  **BLOCK 요청:** `weather_agent_v5_model_guardrail`에 대한 콜백이 다시 실행되고, 메시지를 검사하여 "BLOCK"을 찾은 후 "LLM 호출 차단!"을 출력하고, 상태 플래그를 설정하며, 미리 정의된 `LlmResponse`를 반환합니다. 에이전트의 기본 LLM은 이 턴에 대해 *전혀 호출되지 않습니다*. 사용자는 콜백의 차단 메시지를 보게 됩니다.
3.  **다시 안녕:** `weather_agent_v5_model_guardrail`에 대한 콜백이 실행되어 요청을 허용합니다. 루트 에이전트는 `greeting_agent`에게 위임합니다. *참고: 루트 에이전트에 정의된 `before_model_callback`은 하위 에이전트에게 자동으로 적용되지 않습니다.* `greeting_agent`는 정상적으로 진행되어 `say_hello` 도구를 호출하고 인사를 반환합니다.

입력 안전 계층을 성공적으로 구현했습니다! `before_model_callback`은 비용이 많이 들거나 잠재적으로 위험한 LLM 호출이 이루어지기 *전에* 규칙을 적용하고 에이전트 동작을 제어하는 강력한 메커니즘을 제공합니다. 다음으로, 도구 사용 자체에 가드레일을 추가하기 위해 비슷한 개념을 적용할 것입니다.

## 6단계: 안전 기능 추가 - `before_tool_callback`을 이용한 도구 인수 가드레일

5단계에서는 사용자 입력이 LLM에 도달하기 *전에* 검사하고 잠재적으로 차단하는 가드레일을 추가했습니다. 이제 LLM이 도구를 사용하기로 결정한 *후* 하지만 해당 도구가 실제로 실행되기 *전에* 또 다른 제어 계층을 추가할 것입니다. 이는 LLM이 도구에 전달하려는 *인수*를 검증하는 데 유용합니다.

ADK는 바로 이 목적을 위해 `before_tool_callback`을 제공합니다.

**`before_tool_callback`이란 무엇인가요?**

*   LLM이 사용을 요청하고 인수를 결정한 후, 특정 도구 함수가 실행되기 바로 *전에* 실행되는 Python 함수입니다.
*   **목적:** 도구 인수를 검증하고, 특정 입력에 기반한 도구 실행을 방지하고, 인수를 동적으로 수정하거나, 리소스 사용 정책을 시행합니다.

**일반적인 사용 사례:**

*   **인수 유효성 검사:** LLM이 제공한 인수가 유효한지, 허용된 범위 내에 있는지, 또는 예상 형식에 부합하는지 확인합니다.
*   **리소스 보호:** 비용이 많이 들거나, 제한된 데이터에 접근하거나, 원치 않는 부작용을 일으킬 수 있는 입력으로 도구가 호출되는 것을 방지합니다 (예: 특정 매개변수에 대한 API 호출 차단).
*   **동적 인수 수정:** 도구가 실행되기 전에 세션 상태나 다른 문맥 정보를 기반으로 인수를 조정합니다.

**작동 방식:**

1.  `tool: BaseTool`, `args: Dict[str, Any]`, `tool_context: ToolContext`를 받는 함수를 정의합니다.
    *   `tool`: 호출될 도구 객체 (`tool.name` 검사).
    *   `args`: LLM이 도구를 위해 생성한 인수 사전.
    *   `tool_context`: 세션 상태(`tool_context.state`), 에이전트 정보 등에 접근할 수 있습니다.
2.  함수 내부:
    *   **검사:** `tool.name`과 `args` 사전을 검사합니다.
    *   **수정:** `args` 사전 내의 값을 *직접* 변경합니다. `None`을 반환하면 도구는 이러한 수정된 인수로 실행됩니다.
    *   **차단/재정의 (가드레일):** **사전**을 반환합니다. ADK는 이 사전을 도구 호출의 *결과*로 처리하여 원래 도구 함수의 실행을 완전히 *건너뜁니다*. 사전은 이상적으로 차단하는 도구의 예상 반환 형식과 일치해야 합니다.
    *   **허용:** `None`을 반환합니다. ADK는 실제 도구 함수를 (잠재적으로 수정된) 인수로 실행합니다.

**이 단계에서는 다음을 수행합니다:**

1.  `get_weather_stateful` 도구가 "Paris"라는 도시로 호출되는지 구체적으로 확인하는 `before_tool_callback` 함수(`block_paris_tool_guardrail`)를 정의합니다.
2.  "Paris"가 감지되면 콜백은 도구를 차단하고 사용자 지정 오류 사전을 반환합니다.
3.  `before_model_callback`과 이 새로운 `before_tool_callback`을 모두 포함하도록 루트 에이전트(`weather_agent_v6_tool_guardrail`)를 업데이트합니다.
4.  동일한 상태 인식 세션 서비스를 사용하여 이 에이전트를 위한 새로운 러너를 생성합니다.
5.  허용된 도시와 차단된 도시("Paris")에 대한 날씨를 요청하여 흐름을 테스트합니다.

---

**1. 도구 가드레일 콜백 함수 정의**

이 함수는 `get_weather_stateful` 도구를 대상으로 합니다. `city` 인수를 확인합니다. "Paris"이면 도구 자체의 오류 응답처럼 보이는 오류 사전을 반환합니다. 그렇지 않으면 `None`을 반환하여 도구가 실행되도록 허용합니다.


```python
# @title 1. before_tool_callback 가드레일 정의

# 필요한 import가 사용 가능한지 확인
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from typing import Optional, Dict, Any # 타입 힌트를 위해

def block_paris_tool_guardrail(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    'get_weather_stateful'이 'Paris'에 대해 호출되는지 확인합니다.
    만약 그렇다면, 도구 실행을 차단하고 특정 오류 사전을 반환합니다.
    그렇지 않으면 None을 반환하여 도구 호출을 계속 진행하도록 허용합니다.
    """
    tool_name = tool.name
    agent_name = tool_context.agent_name # 도구 호출을 시도하는 에이전트
    print(f"--- 콜백: block_paris_tool_guardrail이 에이전트 '{agent_name}'의 도구 '{tool_name}'에 대해 실행 중 ---")
    print(f"--- 콜백: 인수 검사 중: {args} ---")

    # --- 가드레일 로직 ---
    target_tool_name = "get_weather_stateful" # FunctionTool에서 사용하는 함수 이름과 일치
    blocked_city = "paris"

    # 올바른 도구인지 그리고 도시 인수가 차단된 도시와 일치하는지 확인
    if tool_name == target_tool_name:
        city_argument = args.get("city", "") # 'city' 인수를 안전하게 가져옴
        if city_argument and city_argument.lower() == blocked_city:
            print(f"--- 콜백: 차단된 도시 '{city_argument}' 감지. 도구 실행 차단! ---")
            # 선택적으로 상태 업데이트
            tool_context.state["guardrail_tool_block_triggered"] = True
            print(f"--- 콜백: 상태 'guardrail_tool_block_triggered'를 True로 설정 ---")

            # 도구의 예상 출력 형식과 일치하는 사전을 오류용으로 반환
            # 이 사전은 도구의 결과가 되어 실제 도구 실행을 건너뜁니다.
            return {
                "status": "error",
                "error_message": f"정책 제한: '{city_argument.capitalize()}'에 대한 날씨 확인은 현재 도구 가드레일에 의해 비활성화되었습니다."
            }
        else:
             print(f"--- 콜백: 도시 '{city_argument}'는 도구 '{tool_name}'에 대해 허용됩니다. ---")
    else:
        print(f"--- 콜백: 도구 '{tool_name}'는 대상 도구가 아닙니다. 허용합니다. ---")


    # 위 확인에서 사전을 반환하지 않았다면 도구를 실행하도록 허용
    print(f"--- 콜백: 도구 '{tool_name}' 진행을 허용합니다. ---")
    return None # None을 반환하면 실제 도구 함수가 실행되도록 허용

print("✅ block_paris_tool_guardrail 함수가 정의되었습니다.")
```

---

**2. 두 콜백을 모두 사용하도록 루트 에이전트 업데이트**

루트 에이전트를 다시 정의하고(`weather_agent_v6_tool_guardrail`), 이번에는 5단계의 `before_model_callback`과 함께 `before_tool_callback` 매개변수를 추가합니다.

*독립 실행 참고:* 5단계와 유사하게, 이 에이전트를 정의하기 전에 모든 전제 조건(하위 에이전트, 도구, `before_model_callback`)이 실행 컨텍스트에서 정의되었거나 사용 가능한지 확인하십시오.


```python
# @title 2. 두 콜백을 모두 사용하여 루트 에이전트 업데이트 (독립형)

# --- 전제 조건이 정의되었는지 확인 ---
# (Agent, LiteLlm, Runner, ToolContext,
#  MODEL 상수, say_hello, say_goodbye, greeting_agent, farewell_agent,
#  get_weather_stateful, block_keyword_guardrail, block_paris_tool_guardrail에 대한 정의를 포함하거나 실행 확인)

# --- 하위 에이전트 재정의 (이 컨텍스트에 존재하는지 확인) ---
greeting_agent = None
try:
    # 정의된 모델 상수 사용
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent", # 일관성을 위해 원래 이름 유지
        instruction="당신은 인사 에이전트입니다. 당신의 유일한 임무는 'say_hello' 도구를 사용하여 친절한 인사를 제공하는 것입니다. 다른 작업은 하지 마세요.",
        description="'say_hello' 도구를 사용하여 간단한 인사와 안부를 처리합니다.",
        tools=[say_hello],
    )
    print(f"✅ 하위 에이전트 '{greeting_agent.name}'가 재정의되었습니다.")
except Exception as e:
    print(f"❌ 인사 에이전트를 재정의할 수 없습니다. 모델/API 키({greeting_agent.model})를 확인하세요. 오류: {e}")

farewell_agent = None
try:
    # 정의된 모델 상수 사용
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent", # 원래 이름 유지
        instruction="당신은 작별 에이전트입니다. 당신의 유일한 임무는 'say_goodbye' 도구를 사용하여 정중한 작별 메시지를 제공하는 것입니다. 다른 작업은 수행하지 마세요.",
        description="'say_goodbye' 도구를 사용하여 간단한 작별 인사를 처리합니다.",
        tools=[say_goodbye],
    )
    print(f"✅ 하위 에이전트 '{farewell_agent.name}'가 재정의되었습니다.")
except Exception as e:
    print(f"❌ 작별 에이전트를 재정의할 수 없습니다. 모델/API 키({farewell_agent.model})를 확인하세요. 오류: {e}")

# --- 두 콜백을 모두 포함한 루트 에이전트 정의 ---
root_agent_tool_guardrail = None
runner_root_tool_guardrail = None

if ('greeting_agent' in globals() and greeting_agent and
    'farewell_agent' in globals() and farewell_agent and
    'get_weather_stateful' in globals() and
    'block_keyword_guardrail' in globals() and
    'block_paris_tool_guardrail' in globals()):

    root_agent_model = MODEL_GEMINI_2_0_FLASH

    root_agent_tool_guardrail = Agent(
        name="weather_agent_v6_tool_guardrail", # 새 버전 이름
        model=root_agent_model,
        description="메인 에이전트: 날씨 처리, 위임, 입력 및 도구 가드레일 포함.",
        instruction="당신은 메인 날씨 에이전트입니다. 'get_weather_stateful'을 사용하여 날씨를 제공하세요. "
                    "인사는 'greeting_agent'에게, 작별은 'farewell_agent'에게 위임하세요. "
                    "날씨, 인사, 작별만 처리하세요.",
        tools=[get_weather_stateful],
        sub_agents=[greeting_agent, farewell_agent],
        output_key="last_weather_report",
        before_model_callback=block_keyword_guardrail, # 모델 가드레일 유지
        before_tool_callback=block_paris_tool_guardrail # <<< 도구 가드레일 추가
    )
    print(f"✅ 루트 에이전트 '{root_agent_tool_guardrail.name}'가 두 콜백 모두와 함께 생성되었습니다.")

    # --- Runner 생성, 동일한 상태 인식 세션 서비스 사용 ---
    if 'session_service_stateful' in globals():
        runner_root_tool_guardrail = Runner(
            agent=root_agent_tool_guardrail,
            app_name=APP_NAME,
            session_service=session_service_stateful # <<< 4/5단계의 서비스 사용
        )
        print(f"✅ 도구 가드레일 에이전트 '{runner_root_tool_guardrail.agent.name}'를 위한 Runner가 상태 인식 세션 서비스를 사용하여 생성되었습니다.")
    else:
        print("❌ Runner를 생성할 수 없습니다. 4/5단계의 'session_service_stateful'이 없습니다.")

else:
    print("❌ 도구 가드레일로 루트 에이전트를 생성할 수 없습니다. 전제 조건이 없습니다.")
```

---

**3. 도구 가드레일 테스트를 위한 상호작용**

이전 단계와 동일한 상태 인식 세션(`SESSION_ID_STATEFUL`)을 다시 사용하여 상호작용 흐름을 테스트해 봅시다.

1. "뉴욕" 날씨 요청: 두 콜백을 모두 통과하고 도구가 실행됩니다(상태에서 화씨 선호도 사용).
2. "파리" 날씨 요청: `before_model_callback`을 통과합니다. LLM이 `get_weather_stateful(city='Paris')`를 호출하기로 결정합니다. `before_tool_callback`이 가로채서 도구를 차단하고 오류 사전을 반환합니다. 에이전트가 이 오류를 전달합니다.
3. "런던" 날씨 요청: 두 콜백을 모두 통과하고 도구가 정상적으로 실행됩니다.


```python
# @title 3. 도구 인수 가드레일 테스트를 위한 상호작용
import asyncio # asyncio가 import되었는지 확인

# 도구 가드레일 에이전트를 위한 러너가 사용 가능한지 확인
if 'runner_root_tool_guardrail' in globals() and runner_root_tool_guardrail:
    # 도구 가드레일 테스트 대화를 위한 메인 비동기 함수 정의
    # 이 함수 내부의 'await' 키워드는 비동기 작업에 필수적
    async def run_tool_guardrail_test():
        print("\n--- 도구 인수 가드레일 테스트 중 ('파리' 차단됨) ---")

        # 두 콜백 모두와 기존 상태 인식 세션을 가진 에이전트의 러너 사용
        # 더 깔끔한 상호작용 호출을 위한 헬퍼 람다 정의
        interaction_func = lambda query: call_agent_async(query,
                                                         runner_root_tool_guardrail,
                                                         USER_ID_STATEFUL, # 기존 사용자 ID 사용
                                                         SESSION_ID_STATEFUL # 기존 세션 ID 사용
                                                        )
        # 1. 허용된 도시 (두 콜백 모두 통과, 화씨 상태 사용해야 함)
        print("--- 1번째 턴: 뉴욕 날씨 요청 (허용 예상) ---")
        await interaction_func("뉴욕 날씨는 어때?")

        # 2. 차단된 도시 (모델 콜백 통과, 하지만 도구 콜백에 의해 차단됨)
        print("\n--- 2번째 턴: 파리 날씨 요청 (도구 가드레일에 의해 차단 예상) ---")
        await interaction_func("파리는 어때?") # 도구 콜백이 이것을 가로채야 함

        # 3. 다른 허용된 도시 (다시 정상적으로 작동해야 함)
        print("\n--- 3번째 턴: 런던 날씨 요청 (허용 예상) ---")
        await interaction_func("런던 날씨를 알려줘.")

    # --- `run_tool_guardrail_test` 비동기 함수 실행 ---
    # 환경에 따라 아래 방법 중 하나를 선택

    # 방법 1: 직접 await (노트북/비동기 REPL 기본)
    # 환경이 최상위 await를 지원하는 경우(Colab/Jupyter 노트북 등),
    # 이벤트 루프가 이미 실행 중이므로 함수를 직접 await 할 수 있습니다.
    print("'await'를 사용하여 실행 시도 중 (노트북 기본)...")
    await run_tool_guardrail_test()

    # 방법 2: asyncio.run (표준 Python 스크립트 [.py]용)
    # 터미널에서 이 코드를 표준 Python 스크립트로 실행하는 경우,
    # 스크립트 컨텍스트는 동기식입니다. 비동기 함수를 실행하려면
    # 이벤트 루프를 생성하고 관리하기 위해 `asyncio.run()`이 필요합니다.
    # 이 방법을 사용하려면:
    # 1. 위의 `await run_tool_guardrail_test()` 줄을 주석 처리합니다.
    # 2. 다음 블록의 주석을 해제합니다:
    """
    import asyncio
    if __name__ == "__main__": # 스크립트가 직접 실행될 때만 실행되도록 보장
        print("'asyncio.run()'을 사용하여 실행 중 (표준 Python 스크립트용)...")
        try:
            # 이것은 이벤트 루프를 생성하고, 비동기 함수를 실행하며, 루프를 닫습니다.
            asyncio.run(run_tool_guardrail_test())
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
    """

    # --- 대화 후 최종 세션 상태 검사 ---
    # 이 블록은 어느 실행 방법이 완료된 후에 실행됩니다.
    # 선택 사항: 도구 차단 트리거 플래그에 대한 상태 확인
    print("\n--- 최종 세션 상태 검사 (도구 가드레일 테스트 후) ---")
    # 이 상태 인식 세션과 관련된 세션 서비스 인스턴스 사용
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id= SESSION_ID_STATEFUL)
    if final_session:
        # 안전한 접근을 위해 .get() 사용
        print(f"도구 가드레일 트리거 플래그: {final_session.state.get('guardrail_tool_block_triggered', '설정되지 않음 (또는 False)')}")
        print(f"마지막 날씨 보고서: {final_session.state.get('last_weather_report', '설정되지 않음')}") # 성공 시 런던 날씨여야 함
        print(f"온도 단위: {final_session.state.get('user_preference_temperature_unit', '설정되지 않음')}") # 화씨여야 함
        # print(f"전체 상태 사전: {final_session.state}") # 상세 보기용
    else:
        print("\n❌ 오류: 최종 세션 상태를 검색할 수 없습니다.")

else:
    print("\n⚠️ 도구 가드레일 테스트를 건너뜁니다. 러너('runner_root_tool_guardrail')를 사용할 수 없습니다.")
```

---

출력을 분석해 보세요:

1.  **뉴욕:** `before_model_callback`이 요청을 허용합니다. LLM이 `get_weather_stateful`을 요청합니다. `before_tool_callback`이 실행되어 인수(`{'city': 'New York'}`)를 검사하고, "파리"가 아니므로 "도구 허용 중..."을 출력하고 `None`을 반환합니다. 실제 `get_weather_stateful` 함수가 실행되어 상태에서 "화씨"를 읽고 날씨 보고서를 반환합니다. 에이전트가 이를 전달하고 `output_key`를 통해 저장됩니다.
2.  **파리:** `before_model_callback`이 요청을 허용합니다. LLM이 `get_weather_stateful(city='Paris')`를 요청합니다. `before_tool_callback`이 실행되어 인수를 검사하고 "파리"를 감지한 후 "도구 실행 차단!"을 출력하고, 상태 플래그를 설정하며, 오류 사전 `{'status': 'error', 'error_message': '정책 제한...'}`을 반환합니다. 실제 `get_weather_stateful` 함수는 **전혀 실행되지 않습니다**. 에이전트는 오류 사전을 *마치 도구의 출력인 것처럼* 수신하고 해당 오류 메시지를 기반으로 응답을 구성합니다.
3.  **런던:** 뉴욕처럼 작동하여 두 콜백을 모두 통과하고 도구를 성공적으로 실행합니다. 새로운 런던 날씨 보고서가 상태의 `last_weather_report`를 덮어씁니다.

이제 LLM에 도달하는 *내용*뿐만 아니라 LLM이 생성한 특정 인수에 따라 에이전트의 도구가 *어떻게* 사용될 수 있는지를 제어하는 중요한 안전 계층을 추가했습니다. `before_model_callback` 및 `before_tool_callback`과 같은 콜백은 견고하고 안전하며 정책을 준수하는 에이전트 애플리케이션을 구축하는 데 필수적입니다.


---


## 결론: 여러분의 에이전트 팀이 준비되었습니다!

축하합니다! Agent Development Kit(ADK)를 사용하여 기본적인 단일 날씨 에이전트 구축에서 정교한 멀티 에이전트 팀 구성까지 성공적으로 여정을 마쳤습니다.

**달성한 내용을 요약해 보겠습니다:**

*   단일 도구(`get_weather`)를 갖춘 **기본적인 에이전트**로 시작했습니다.
*   LiteLLM을 사용하여 ADK의 **멀티 모델 유연성**을 탐색하고, Gemini, GPT-4o, Claude와 같은 다양한 LLM으로 동일한 핵심 로직을 실행했습니다.
*   전문화된 하위 에이전트(`greeting_agent`, `farewell_agent`)를 만들고 루트 에이전트로부터의 **자동 위임**을 활성화하여 **모듈성**을 수용했습니다.
*   **세션 상태**를 사용하여 에이전트에게 **메모리**를 부여하여 사용자 선호도(`temperature_unit`)와 과거 상호작용(`output_key`)을 기억할 수 있도록 했습니다.
*   `before_model_callback`(특정 입력 키워드 차단)과 `before_tool_callback`("파리"와 같은 인수에 기반한 도구 실행 차단)을 모두 사용하여 중요한 **안전 가드레일**을 구현했습니다.

이 점진적인 날씨 봇 팀을 구축하면서, 복잡하고 지능적인 애플리케이션을 개발하는 데 필수적인 핵심 ADK 개념에 대한 실무 경험을 얻었습니다.

**핵심 요약:**

*   **에이전트 및 도구:** 기능과 추론을 정의하기 위한 기본적인 구성 요소. 명확한 지침과 docstring이 가장 중요합니다.
*   **러너 및 세션 서비스:** 에이전트 실행을 조율하고 대화 컨텍스트를 유지하는 엔진 및 메모리 관리 시스템입니다.
*   **위임:** 멀티 에이전트 팀을 설계하면 전문화, 모듈성 및 복잡한 작업의 더 나은 관리가 가능합니다. 에이전트 `description`은 자동 흐름의 핵심입니다.
*   **세션 상태 (`ToolContext`, `output_key`):** 문맥을 인식하고, 개인화되며, 다중 턴 대화형 에이전트를 만드는 데 필수적입니다.
*   **콜백 (`before_model`, `before_tool`):** 중요한 작업(LLM 호출 또는 도구 실행) *전에* 안전, 유효성 검사, 정책 시행 및 동적 수정을 구현하기 위한 강력한 후크입니다.
*   **유연성 (`LiteLlm`):** ADK는 성능, 비용 및 기능의 균형을 맞추어 작업에 가장 적합한 LLM을 선택할 수 있는 권한을 부여합니다.

**다음 단계는?**

여러분의 날씨 봇 팀은 훌륭한 출발점입니다. ADK를 더 탐색하고 애플리케이션을 향상시키기 위한 몇 가지 아이디어는 다음과 같습니다:

1.  **실제 날씨 API:** `get_weather` 도구의 `mock_weather_db`를 실제 날씨 API(OpenWeatherMap, WeatherAPI 등) 호출로 교체하세요.
2.  **더 복잡한 상태:** 더 많은 사용자 선호도(예: 선호 위치, 알림 설정) 또는 대화 요약을 세션 상태에 저장하세요.
3.  **위임 구체화:** 다른 루트 에이전트 지침이나 하위 에이전트 설명을 실험하여 위임 로직을 미세 조정하세요. "예보" 에이전트를 추가할 수 있을까요?
4.  **고급 콜백:**
    *   `after_model_callback`을 사용하여 LLM의 응답이 생성된 *후에* 잠재적으로 형식을 변경하거나 삭제하세요.
    *   `after_tool_callback`을 사용하여 도구에서 반환된 결과를 처리하거나 기록하세요.
    *   에이전트 수준의 진입/종료 로직을 위해 `before_agent_callback` 또는 `after_agent_callback`을 구현하세요.
5.  **오류 처리:** 에이전트가 도구 오류나 예상치 못한 API 응답을 처리하는 방법을 개선하세요. 도구 내에 재시도 로직을 추가할 수도 있습니다.
6.  **영구 세션 저장소:** 세션 상태를 영구적으로 저장하기 위해 `InMemorySessionService`의 대안을 탐색하세요 (예: Firestore 또는 Cloud SQL과 같은 데이터베이스 사용 – 사용자 지정 구현 또는 향후 ADK 통합 필요).
7.  **스트리밍 UI:** 에이전트 팀을 웹 프레임워크(ADK 스트리밍 빠른 시작에서 보여준 FastAPI 등)와 통합하여 실시간 채팅 인터페이스를 만드세요.

Agent Development Kit는 정교한 LLM 기반 애플리케이션을 구축하기 위한 견고한 기반을 제공합니다. 이 튜토리얼에서 다룬 개념(도구, 상태, 위임, 콜백)을 마스터함으로써 점점 더 복잡해지는 에이전트 시스템에 대처할 수 있는 충분한 준비가 되었습니다.

즐거운 빌딩 되세요