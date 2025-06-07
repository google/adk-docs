# ADK에서 다양한 모델 사용하기

!!! Note
    Java ADK는 현재 Gemini 및 Anthropic 모델을 지원합니다. 더 많은 모델 지원이 곧 추가될 예정입니다.

에이전트 개발 키트(ADK)는 유연성을 위해 설계되어 다양한 거대 언어 모델(LLM)을 에이전트에 통합할 수 있습니다. Google Gemini 모델의 설정은 [기반 모델 설정](../get-started/installation.md) 가이드에서 다루지만, 이 페이지에서는 Gemini를 효과적으로 활용하고 외부에서 호스팅되거나 로컬에서 실행되는 모델을 포함하여 다른 인기 있는 모델을 통합하는 방법을 자세히 설명합니다.

ADK는 주로 두 가지 메커니즘을 사용하여 모델을 통합합니다:

1. **직접 문자열 / 레지스트리:** Google Cloud와 긴밀하게 통합된 모델(예: Google AI Studio 또는 Vertex AI를 통해 접근하는 Gemini 모델) 또는 Vertex AI 엔드포인트에 호스팅된 모델의 경우. 일반적으로 `LlmAgent`에 모델 이름이나 엔드포인트 리소스 문자열을 직접 제공합니다. ADK의 내부 레지스트리는 이 문자열을 적절한 백엔드 클라이언트로 확인하며, 종종 `google-genai` 라이브러리를 활용합니다.
2. **래퍼 클래스:** 특히 Google 생태계 외부의 모델이나 특정 클라이언트 구성이 필요한 모델(예: LiteLLM을 통해 접근하는 모델)과의 광범위한 호환성을 위해. 특정 래퍼 클래스(예: `LiteLlm`)를 인스턴스화하고 이 객체를 `LlmAgent`의 `model` 매개변수로 전달합니다.

다음 섹션에서는 필요에 따라 이러한 방법을 사용하는 방법을 안내합니다.

## Google Gemini 모델 사용하기

이는 ADK 내에서 Google의 주력 모델을 사용하는 가장 직접적인 방법입니다.

**통합 방법:** 모델의 식별자 문자열을 `LlmAgent`(또는 그 별칭인 `Agent`)의 `model` 매개변수에 직접 전달합니다.

**백엔드 옵션 및 설정:**

ADK가 Gemini를 위해 내부적으로 사용하는 `google-genai` 라이브러리는 Google AI Studio 또는 Vertex AI를 통해 연결할 수 있습니다.

!!!note "음성/영상 스트리밍을 위한 모델 지원"

    ADK에서 음성/영상 스트리밍을 사용하려면 Live API를 지원하는 Gemini 모델을 사용해야 합니다. 문서에서 Gemini Live API를 지원하는 **모델 ID**를 찾을 수 있습니다:

    - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
    - [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

### Google AI Studio

* **사용 사례:** Google AI Studio는 Gemini를 시작하는 가장 쉬운 방법입니다. [API 키](https://aistudio.google.com/app/apikey)만 있으면 됩니다. 빠른 프로토타이핑 및 개발에 가장 적합합니다.
* **설정:** 일반적으로 API 키가 필요합니다:
     * 환경 변수로 설정하거나
     * 아래 예제와 같이 `Client`를 통해 모델 초기화 중에 전달합니다.

```shell
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

* **모델:** [Google AI for Developers 사이트](https://ai.google.dev/gemini-api/docs/models)에서 사용 가능한 모든 모델을 찾을 수 있습니다.

### Vertex AI

* **사용 사례:** 프로덕션 애플리케이션에 권장되며, Google Cloud 인프라를 활용합니다. Vertex AI의 Gemini는 엔터프라이즈급 기능, 보안 및 규정 준수 제어를 지원합니다.
* **설정:**
    * 애플리케이션 기본 자격 증명(ADC)을 사용하여 인증합니다:

        ```shell
        gcloud auth application-default login
        ```

    * 이러한 변수를 환경 변수로 설정하거나 모델을 직접 초기화할 때 제공합니다.
            
         Google Cloud 프로젝트 및 위치 설정:
    
         ```shell
         export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
         export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # 예: us-central1
         ```     
    
         라이브러리에 Vertex AI를 사용하도록 명시적으로 지시합니다:
    
         ```shell
         export GOOGLE_GENAI_USE_VERTEXAI=TRUE
         ```

* **모델:** [Vertex AI 문서](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)에서 사용 가능한 모델 ID를 찾을 수 있습니다.

**예제:**

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    
    # --- 안정적인 Gemini Flash 모델을 사용하는 예제 ---
    agent_gemini_flash = LlmAgent(
        # 최신 안정적인 Flash 모델 식별자 사용
        model="gemini-2.0-flash",
        name="gemini_flash_agent",
        instruction="당신은 빠르고 도움이 되는 Gemini 어시스턴트입니다.",
        # ... 기타 에이전트 매개변수
    )
    
    # --- 강력한 Gemini Pro 모델을 사용하는 예제 ---
    # 참고: 필요한 경우 특정 미리보기 버전을 포함하여 최신 모델 이름은 항상 공식 Gemini 문서를 확인하세요.
    # 미리보기 모델은 가용성이나 할당량 제한이 다를 수 있습니다.
    agent_gemini_pro = LlmAgent(
        # 최신 일반 사용 가능한 Pro 모델 식별자 사용
        model="gemini-2.5-pro-preview-03-25",
        name="gemini_pro_agent",
        instruction="당신은 강력하고 지식이 풍부한 Gemini 어시스턴트입니다.",
        # ... 기타 에이전트 매개변수
    )
    ```

=== "Java"

    ```java
    // --- 예제 #1: 환경 변수를 사용하는 안정적인 Gemini Flash 모델 ---
    LlmAgent agentGeminiFlash =
        LlmAgent.builder()
            // 최신 안정적인 Flash 모델 식별자 사용
            .model("gemini-2.0-flash") // 이 모델을 사용하려면 환경 변수 설정
            .name("gemini_flash_agent")
            .instruction("당신은 빠르고 도움이 되는 Gemini 어시스턴트입니다.")
            // ... 기타 에이전트 매개변수
            .build();

    // --- 예제 #2: 모델에 API 키를 사용하는 강력한 Gemini Pro 모델 ---
    LlmAgent agentGeminiPro =
        LlmAgent.builder()
            // 최신 일반 사용 가능한 Pro 모델 식별자 사용
            .model(new Gemini("gemini-2.5-pro-preview-03-25",
                Client.builder()
                    .vertexAI(false)
                    .apiKey("API_KEY") // API 키 설정 (또는) 프로젝트/위치
                    .build()))
            // 또는 API_KEY를 직접 전달할 수도 있습니다
            // .model(new Gemini("gemini-2.5-pro-preview-03-25", "API_KEY"))
            .name("gemini_pro_agent")
            .instruction("당신은 강력하고 지식이 풍부한 Gemini 어시스턴트입니다.")
            // ... 기타 에이전트 매개변수
            .build();

    // 참고: 필요한 경우 특정 미리보기 버전을 포함하여 최신 모델 이름은 항상 공식 Gemini 문서를 확인하세요.
    // 미리보기 모델은 가용성이나 할당량 제한이 다를 수 있습니다.
    ```

## Anthropic 모델 사용하기

![java_only](https://img.shields.io/badge/지원되는_언어-Java-orange){ title="이 기능은 현재 Java에서 사용할 수 있습니다. 직접적인 Anthropic API(Vertex가 아닌)에 대한 Python 지원은 LiteLLM을 통해 이루어집니다."}

API 키를 직접 사용하거나 Vertex AI 백엔드에서 Anthropic의 Claude 모델을 Java ADK 애플리케이션에 직접 통합할 수 있습니다. ADK의 `Claude` 래퍼 클래스를 사용하면 됩니다.

Vertex AI 백엔드의 경우, [Vertex AI의 타사 모델(예: Anthropic Claude)](#third-party-models-on-vertex-ai-eg-anthropic-claude) 섹션을 참조하세요.

**전제 조건:**

1.  **종속성:**
    *   **Anthropic SDK 클래스(전이적):** Java ADK의 `com.google.adk.models.Claude` 래퍼는 Anthropic의 공식 Java SDK 클래스에 의존합니다. 이들은 일반적으로 **전이적 종속성**으로 포함됩니다.

2.  **Anthropic API 키:**
    *   Anthropic에서 API 키를 얻습니다. 이 키를 비밀 관리자를 사용하여 안전하게 관리하세요.

**통합:**

원하는 Claude 모델 이름과 API 키로 구성된 `AnthropicOkHttpClient`를 제공하여 `com.google.adk.models.Claude`를 인스턴스화합니다. 그런 다음 이 `Claude` 인스턴스를 `LlmAgent`에 전달합니다.

**예제:**

```java
import com.anthropic.client.AnthropicClient;
import com.google.adk.agents.LlmAgent;
import com.google.adk.models.Claude;
import com.anthropic.client.okhttp.AnthropicOkHttpClient; // Anthropic의 SDK에서

public class DirectAnthropicAgent {
  
  private static final String CLAUDE_MODEL_ID = "claude-3-7-sonnet-latest"; // 또는 선호하는 Claude 모델

  public static LlmAgent createAgent() {

    // 민감한 키는 보안 구성에서 로드하는 것이 좋습니다.
    AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
        .apiKey("ANTHROPIC_API_KEY")
        .build();

    Claude claudeModel = new Claude(
        CLAUDE_MODEL_ID,
        anthropicClient
    );

    return LlmAgent.builder()
        .name("claude_direct_agent")
        .model(claudeModel)
        .instruction("당신은 Anthropic Claude로 구동되는 도움이 되는 AI 어시스턴트입니다.")
        // ... 기타 LlmAgent 구성
        .build();
  }

  public static void main(String[] args) {
    try {
      LlmAgent agent = createAgent();
      System.out.println("직접적인 Anthropic 에이전트가 성공적으로 생성되었습니다: " + agent.name());
    } catch (IllegalStateException e) {
      System.err.println("에이전트 생성 오류: " + e.getMessage());
    }
  }
}
```



## LiteLLM을 통해 클라우드 및 독점 모델 사용하기

![python_only](https://img.shields.io/badge/지원되는_언어-Python-blue)

OpenAI, Anthropic(Vertex AI가 아닌), Cohere 등 다양한 제공업체의 광범위한 LLM에 접근하기 위해 ADK는 LiteLLM 라이브러리를 통한 통합을 제공합니다.

**통합 방법:** `LiteLlm` 래퍼 클래스를 인스턴스화하고 `LlmAgent`의 `model` 매개변수에 전달합니다.

**LiteLLM 개요:** [LiteLLM](https://docs.litellm.ai/)은 100개 이상의 LLM에 대한 표준화된 OpenAI 호환 인터페이스를 제공하는 변환 계층 역할을 합니다.

**설정:**

1. **LiteLLM 설치:**
        ```shell
        pip install litellm
        ```
2. **제공업체 API 키 설정:** 사용하려는 특정 제공업체에 대해 환경 변수로 API 키를 구성합니다.

    * *OpenAI 예시:*

        ```shell
        export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
        ```

    * *Anthropic(Vertex AI가 아닌) 예시:*

        ```shell
        export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
        ```

    * *다른 제공업체에 대한 올바른 환경 변수 이름은 [LiteLLM 제공업체 문서](https://docs.litellm.ai/docs/providers)를 참조하세요.*

        **예제:**

        ```python
        from google.adk.agents import LlmAgent
        from google.adk.models.lite_llm import LiteLlm

        # --- OpenAI의 GPT-4o를 사용하는 에이전트 예제 ---
        # (OPENAI_API_KEY 필요)
        agent_openai = LlmAgent(
            model=LiteLlm(model="openai/gpt-4o"), # LiteLLM 모델 문자열 형식
            name="openai_agent",
            instruction="당신은 GPT-4o로 구동되는 도움이 되는 어시스턴트입니다.",
            # ... 기타 에이전트 매개변수
        )

        # --- Anthropic의 Claude Haiku(Vertex가 아닌)를 사용하는 에이전트 예제 ---
        # (ANTHROPIC_API_KEY 필요)
        agent_claude_direct = LlmAgent(
            model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
            name="claude_direct_agent",
            instruction="당신은 Claude Haiku로 구동되는 어시스턴트입니다.",
            # ... 기타 에이전트 매개변수
        )
        ```

!!!info "Windows 사용자 참고"

    ### Windows에서 LiteLLM UnicodeDecodeError 피하기
    Windows에서 LiteLlm으로 ADK 에이전트를 사용할 때 사용자는 다음과 같은 오류를 만날 수 있습니다:
    ```
    UnicodeDecodeError: 'charmap' 코덱이 바이트를 디코딩할 수 없음...
    ```
    이 문제는 `litellm`(LiteLlm에서 사용)이 캐시된 파일(예: 모델 가격 정보)을 UTF-8 대신 기본 Windows 인코딩(`cp1252`)을 사용하여 읽기 때문에 발생합니다.
    Windows 사용자는 `PYTHONUTF8` 환경 변수를 `1`로 설정하여 이 문제를 방지할 수 있습니다. 이렇게 하면 Python이 전역적으로 UTF-8을 사용하도록 강제합니다.
    **예제 (PowerShell):**
    ```powershell
    # 현재 세션에 대해 설정
    $env:PYTHONUTF8 = "1"
    # 사용자에 대해 영구적으로 설정
    [System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', [System.EnvironmentVariableTarget]::User)
    이 설정을 적용하면 Python이 UTF-8을 사용하여 캐시된 파일을 읽도록 하여 디코딩 오류를 방지합니다.
    ```


## LiteLLM을 통해 개방형 및 로컬 모델 사용하기

![python_only](https://img.shields.io/badge/지원되는_언어-Python-blue)

최대한의 제어, 비용 절감, 개인 정보 보호 또는 오프라인 사용 사례를 위해 오픈 소스 모델을 로컬에서 실행하거나 자체 호스팅하고 LiteLLM을 사용하여 통합할 수 있습니다.

**통합 방법:** 로컬 모델 서버를 가리키도록 구성된 `LiteLlm` 래퍼 클래스를 인스턴스화합니다.

### Ollama 통합

[Ollama](https://ollama.com/)를 사용하면 오픈 소스 모델을 로컬에서 쉽게 실행할 수 있습니다.

#### 모델 선택

에이전트가 도구에 의존하는 경우, [Ollama 웹사이트](https://ollama.com/search?c=tools)에서 도구 지원이 있는 모델을 선택해야 합니다.

신뢰할 수 있는 결과를 얻으려면 도구 지원이 있는 적당한 크기의 모델을 사용하는 것이 좋습니다.

모델의 도구 지원은 다음 명령으로 확인할 수 있습니다:

```bash
ollama show mistral-small3.1
  Model
    architecture        mistral3
    parameters          24.0B
    context length      131072
    embedding length    5120
    quantization        Q4_K_M

  Capabilities
    completion
    vision
    tools
```

기능 아래에 `tools`가 나열되어야 합니다.

모델이 사용하는 템플릿을 보고 필요에 따라 조정할 수도 있습니다.

```bash
ollama show --modelfile llama3.2 > model_file_to_modify
```

예를 들어, 위 모델의 기본 템플릿은 모델이 항상 함수를 호출해야 함을 본질적으로 제안합니다. 이로 인해 무한 함수 호출 루프가 발생할 수 있습니다.

```
다음 함수가 주어졌을 때, 주어진 프롬프트에 가장 잘 답하는 함수 호출과 적절한 인수를 포함한 JSON으로 응답해 주세요.

{"name": 함수 이름, "parameters": 인수 이름과 값의 딕셔너리} 형식으로 응답하세요. 변수를 사용하지 마세요.
```

무한 도구 호출 루프를 방지하기 위해 이러한 프롬프트를 더 설명적인 것으로 바꿀 수 있습니다.

예를 들어:

```
사용자의 프롬프트와 아래 나열된 사용 가능한 함수를 검토하세요.
먼저, 이러한 함수 중 하나를 호출하는 것이 가장 적절한 응답 방법인지 결정하세요. 프롬프트가 특정 작업을 요청하거나, 외부 데이터 조회가 필요하거나, 함수가 처리하는 계산을 포함하는 경우 함수 호출이 필요할 가능성이 높습니다. 프롬프트가 일반적인 질문이거나 직접 답변할 수 있는 경우 함수 호출이 필요하지 않을 가능성이 높습니다.

함수 호출이 필요하다고 판단되면: {"name": "함수_이름", "parameters": {"인수_이름": "값"}} 형식의 JSON 객체로만 응답하세요. 매개변수 값은 변수가 아닌 구체적인 값이어야 합니다.

함수 호출이 필요하지 않다고 판단되면: 사용자의 프롬프트에 직접 일반 텍스트로 응답하여 요청된 답변이나 정보를 제공하세요. JSON을 출력하지 마세요.
```

그런 다음 다음 명령으로 새 모델을 만들 수 있습니다:

```bash
ollama create llama3.2-modified -f model_file_to_modify
```

#### ollama_chat 제공자 사용

LiteLLM 래퍼를 사용하여 Ollama 모델로 에이전트를 만들 수 있습니다.

```py
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral-small3.1"),
    name="dice_agent",
    description=(
        "8면 주사위를 굴리고 소수를 확인할 수 있는 hello world 에이전트."
    ),
    instruction="""
      주사위를 굴리고 주사위 굴리기 결과에 대한 질문에 답합니다.
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

**`ollama` 대신 제공자로 `ollama_chat`을 설정하는 것이 중요합니다. `ollama`를 사용하면 무한 도구 호출 루프 및 이전 컨텍스트 무시와 같은 예기치 않은 동작이 발생할 수 있습니다.**

생성을 위해 LiteLLM 내에서 `api_base`를 제공할 수 있지만, LiteLLM 라이브러리는 완료 후 v1.65.5 현재 대신 env 변수에 의존하는 다른 API를 호출합니다. 따라서 현재로서는 `OLLAMA_API_BASE` env 변수를 설정하여 ollama 서버를 가리키도록 하는 것이 좋습니다.

```bash
export OLLAMA_API_BASE="http://localhost:11434"
adk web
```

#### openai 제공자 사용

또는 제공자 이름으로 `openai`를 사용할 수 있습니다. 그러나 이 경우 `OLLAMA_API_BASE` 대신 `OPENAI_API_BASE=http://localhost:11434/v1` 및 `OPENAI_API_KEY=anything` 환경 변수를 설정해야 합니다. **api base 끝에 `/v1`이 추가되었음을 유의하세요.**

```py
root_agent = Agent(
    model=LiteLlm(model="openai/mistral-small3.1"),
    name="dice_agent",
    description=(
        "8면 주사위를 굴리고 소수를 확인할 수 있는 hello world 에이전트."
    ),
    instruction="""
      주사위를 굴리고 주사위 굴리기 결과에 대한 질문에 답합니다.
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

```bash
export OPENAI_API_BASE=http://localhost:11434/v1
export OPENAI_API_KEY=anything
adk web
```

#### 디버깅

에이전트 코드에 임포트 직후 다음을 추가하여 Ollama 서버로 전송된 요청을 볼 수 있습니다.

```py
import litellm
litellm._turn_on_debug()
```

다음과 같은 줄을 찾으세요:

```bash
LiteLLM에서 보낸 요청:
curl -X POST \
http://localhost:11434/api/chat \
-d '{'model': 'mistral-small3.1', 'messages': [{'role': 'system', 'content': ...
```

### 자체 호스팅 엔드포인트 (예: vLLM)

![python_only](https://img.shields.io/badge/지원되는_언어-Python-blue)

[vLLM](https://github.com/vllm-project/vllm)과 같은 도구를 사용하면 모델을 효율적으로 호스팅하고 종종 OpenAI 호환 API 엔드포인트를 노출할 수 있습니다.

**설정:**

1. **모델 배포:** vLLM(또는 유사한 도구)을 사용하여 선택한 모델을 배포합니다. API 기본 URL(예: `https://your-vllm-endpoint.run.app/v1`)을 기록해 둡니다.
    * *ADK 도구에 중요:* 배포 시 서빙 도구가 OpenAI 호환 도구/함수 호출을 지원하고 활성화하는지 확인하세요. vLLM의 경우 모델에 따라 `--enable-auto-tool-choice` 및 잠재적으로 특정 `--tool-call-parser`와 같은 플래그가 포함될 수 있습니다. vLLM 문서의 도구 사용을 참조하세요.
2. **인증:** 엔드포인트가 인증을 처리하는 방법(예: API 키, 베어러 토큰)을 결정합니다.

    **통합 예제:**

    ```python
    import subprocess
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm

    # --- vLLM 엔드포인트에 호스팅된 모델을 사용하는 에이전트 예제 ---

    # vLLM 배포에서 제공하는 엔드포인트 URL
    api_base_url = "https://your-vllm-endpoint.run.app/v1"

    # *vLLM* 엔드포인트 구성에서 인식하는 모델 이름
    model_name_at_endpoint = "hosted_vllm/google/gemma-3-4b-it" # vllm_test.py의 예제

    # 인증 (예: Cloud Run 배포에 gcloud ID 토큰 사용)
    # 엔드포인트 보안에 따라 이것을 조정하세요.
    try:
        gcloud_token = subprocess.check_output(
            ["gcloud", "auth", "print-identity-token", "-q"]
        ).decode().strip()
        auth_headers = {"Authorization": f"Bearer {gcloud_token}"}
    except Exception as e:
        print(f"경고: gcloud 토큰을 가져올 수 없음 - {e}. 엔드포인트가 보안되지 않았거나 다른 인증이 필요할 수 있습니다.")
        auth_headers = None # 또는 오류를 적절하게 처리

    agent_vllm = LlmAgent(
        model=LiteLlm(
            model=model_name_at_endpoint,
            api_base=api_base_url,
            # 필요한 경우 인증 헤더 전달
            extra_headers=auth_headers
            # 또는 엔드포인트가 API 키를 사용하는 경우:
            # api_key="YOUR_ENDPOINT_API_KEY"
        ),
        name="vllm_agent",
        instruction="당신은 자체 호스팅 vLLM 엔드포인트에서 실행되는 도움이 되는 어시스턴트입니다.",
        # ... 기타 에이전트 매개변수
    )
    ```

## Vertex AI에서 호스팅 및 미세 조정된 모델 사용하기

엔터프라이즈급 확장성, 안정성 및 Google Cloud의 MLOps 생태계와의 통합을 위해 Vertex AI 엔드포인트에 배포된 모델을 사용할 수 있습니다. 여기에는 Model Garden의 모델 또는 자체 미세 조정된 모델이 포함됩니다.

**통합 방법:** 전체 Vertex AI 엔드포인트 리소스 문자열(`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`)을 `LlmAgent`의 `model` 매개변수에 직접 전달합니다.

**Vertex AI 설정 (통합):**

환경이 Vertex AI에 맞게 구성되었는지 확인하세요:

1. **인증:** 애플리케이션 기본 자격 증명(ADC) 사용:

    ```shell
    gcloud auth application-default login
    ```

2. **환경 변수:** 프로젝트 및 위치 설정:

    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # 예: us-central1
    ```

3. **Vertex 백엔드 활성화:** 결정적으로, `google-genai` 라이브러리가 Vertex AI를 대상으로 하는지 확인하세요:

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

### Model Garden 배포

![python_only](https://img.shields.io/badge/지원되는_언어-Python-blue){ title="이 기능은 현재 Python에서만 사용할 수 있습니다. Java 지원은 계획 중이거나 곧 제공될 예정입니다."}

[Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)에서 다양한 개방형 및 독점 모델을 엔드포인트에 배포할 수 있습니다.

**예제:**

```python
from google.adk.agents import LlmAgent
from google.genai import types # config 객체용

# --- Model Garden에서 배포된 Llama 3 모델을 사용하는 에이전트 예제 ---

# 실제 Vertex AI 엔드포인트 리소스 이름으로 교체
llama3_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID"

agent_llama3_vertex = LlmAgent(
    model=llama3_endpoint,
    name="llama3_vertex_agent",
    instruction="당신은 Vertex AI에서 호스팅되는 Llama 3 기반의 도움이 되는 어시스턴트입니다.",
    generate_content_config=types.GenerateContentConfig(max_output_tokens=2048),
    # ... 기타 에이전트 매개변수
)
```

### 미세 조정된 모델 엔드포인트

![python_only](https://img.shields.io/badge/지원되는_언어-Python-blue){ title="이 기능은 현재 Python에서만 사용할 수 있습니다. Java 지원은 계획 중이거나 곧 제공될 예정입니다."}

미세 조정된 모델(Gemini 또는 Vertex AI에서 지원하는 다른 아키텍처 기반)을 배포하면 직접 사용할 수 있는 엔드포인트가 생성됩니다.

**예제:**

```python
from google.adk.agents import LlmAgent

# --- 미세 조정된 Gemini 모델 엔드포인트를 사용하는 에이전트 예제 ---

# 미세 조정된 모델의 엔드포인트 리소스 이름으로 교체
finetuned_gemini_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID"

agent_finetuned_gemini = LlmAgent(
    model=finetuned_gemini_endpoint,
    name="finetuned_gemini_agent",
    instruction="당신은 특정 데이터로 훈련된 전문화된 어시스턴트입니다.",
    # ... 기타 에이전트 매개변수
)
```

### Vertex AI의 타사 모델 (예: Anthropic Claude)

Anthropic과 같은 일부 제공업체는 Vertex AI를 통해 직접 모델을 제공합니다.

=== "Python"

    **통합 방법:** 직접 모델 문자열(예: `"claude-3-sonnet@20240229"`)을 사용하지만, ADK 내에서 *수동 등록*이 필요합니다.
    
    **등록 이유?** ADK의 레지스트리는 `gemini-*` 문자열과 표준 Vertex AI 엔드포인트 문자열(`projects/.../endpoints/...`)을 자동으로 인식하고 `google-genai` 라이브러리를 통해 라우팅합니다. Vertex AI를 통해 직접 사용되는 다른 모델 유형(예: Claude)의 경우, ADK 레지스트리에 해당 모델 식별자 문자열을 Vertex AI 백엔드와 함께 처리하는 방법을 아는 특정 래퍼 클래스(`Claude` 이 경우)를 명시적으로 알려줘야 합니다.
    
    **설정:**
    
    1. **Vertex AI 환경:** 통합 Vertex AI 설정(ADC, 환경 변수, `GOOGLE_GENAI_USE_VERTEXAI=TRUE`)이 완료되었는지 확인합니다.
    
    2. **제공업체 라이브러리 설치:** Vertex AI용으로 구성된 필요한 클라이언트 라이브러리를 설치합니다.
    
        ```shell
        pip install "anthropic[vertex]"
        ```
    
    3. **모델 클래스 등록:** Claude 모델 문자열을 사용하는 에이전트를 생성하기 *전에* 애플리케이션 시작 부분 근처에 이 코드를 추가합니다:
    
        ```python
        # LlmAgent와 함께 Vertex AI를 통해 직접 Claude 모델 문자열을 사용하기 위해 필요
        from google.adk.models.anthropic_llm import Claude
        from google.adk.models.registry import LLMRegistry
    
        LLMRegistry.register(Claude)
        ```
    
       **예제:**

       ```python
       from google.adk.agents import LlmAgent
       from google.adk.models.anthropic_llm import Claude # 등록에 필요
       from google.adk.models.registry import LLMRegistry # 등록에 필요
       from google.genai import types
        
       # --- Claude 클래스 등록 (시작 시 한 번 수행) ---
       LLMRegistry.register(Claude)
        
       # --- Vertex AI에서 Claude 3 Sonnet을 사용하는 에이전트 예제 ---
        
       # Vertex AI에서 Claude 3 Sonnet의 표준 모델 이름
       claude_model_vertexai = "claude-3-sonnet@20240229"
        
       agent_claude_vertexai = LlmAgent(
           model=claude_model_vertexai, # 등록 후 직접 문자열 전달
           name="claude_vertexai_agent",
           instruction="당신은 Vertex AI에서 Claude 3 Sonnet으로 구동되는 어시스턴트입니다.",
           generate_content_config=types.GenerateContentConfig(max_output_tokens=4096),
           # ... 기타 에이전트 매개변수
       )
       ```

=== "Java"

    **통합 방법:** 제공업체별 모델 클래스(예: `com.google.adk.models.Claude`)를 직접 인스턴스화하고 Vertex AI 백엔드로 구성합니다.
    
    **직접 인스턴스화 이유?** Java ADK의 `LlmRegistry`는 기본적으로 주로 Gemini 모델을 처리합니다. Vertex AI의 Claude와 같은 타사 모델의 경우, ADK의 래퍼 클래스(예: `Claude`) 인스턴스를 `LlmAgent`에 직접 제공합니다. 이 래퍼 클래스는 Vertex AI용으로 구성된 특정 클라이언트 라이브러리를 통해 모델과 상호 작용할 책임이 있습니다.
    
    **설정:**
    
    1.  **Vertex AI 환경:**
        *   Google Cloud 프로젝트 및 리전이 올바르게 설정되었는지 확인합니다.
        *   **애플리케이션 기본 자격 증명(ADC):** 환경에서 ADC가 올바르게 구성되었는지 확인합니다. 일반적으로 `gcloud auth application-default login`을 실행하여 수행됩니다. Java 클라이언트 라이브러리는 이러한 자격 증명을 사용하여 Vertex AI에 인증합니다. 자세한 설정은 [ADC에 대한 Google Cloud Java 문서](https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault__)를 따르세요.
    
    2.  **제공업체 라이브러리 종속성:**
        *   **타사 클라이언트 라이브러리(종종 전이적):** ADK 코어 라이브러리는 종종 Vertex AI의 일반적인 타사 모델(Anthropic의 필수 클래스 등)에 필요한 클라이언트 라이브러리를 **전이적 종속성**으로 포함합니다. 즉, `pom.xml` 또는 `build.gradle`에 Anthropic Vertex SDK에 대한 별도의 종속성을 명시적으로 추가할 필요가 없을 수 있습니다.

    3.  **모델 인스턴스화 및 구성:**
        `LlmAgent`를 생성할 때 `Claude` 클래스(또는 다른 제공업체의 동등한 클래스)를 인스턴스화하고 `VertexBackend`로 구성합니다.
    
    **예제:**

    ```java
    import com.anthropic.client.AnthropicClient;
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.anthropic.vertex.backends.VertexBackend;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Claude; // ADK의 Claude 래퍼
    import com.google.auth.oauth2.GoogleCredentials;
    import java.io.IOException;

    // ... 기타 가져오기

    public class ClaudeVertexAiAgent {

        public static LlmAgent createAgent() throws IOException {
            // Vertex AI의 Claude 3 Sonnet 모델 이름 (또는 다른 버전)
            String claudeModelVertexAi = "claude-3-7-sonnet"; // 또는 다른 Claude 모델

            // AnthropicOkHttpClient를 VertexBackend로 구성
            AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
                .backend(
                    VertexBackend.builder()
                        .region("us-east5") // Vertex AI 리전 지정
                        .project("your-gcp-project-id") // GCP 프로젝트 ID 지정
                        .googleCredentials(GoogleCredentials.getApplicationDefault())
                        .build())
                .build();

            // ADK Claude 래퍼로 LlmAgent 인스턴스화
            LlmAgent agentClaudeVertexAi = LlmAgent.builder()
                .model(new Claude(claudeModelVertexAi, anthropicClient)) // Claude 인스턴스 전달
                .name("claude_vertexai_agent")
                .instruction("당신은 Vertex AI에서 Claude 3 Sonnet으로 구동되는 어시스턴트입니다.")
                // .generateContentConfig(...) // 필요한 경우 생성 구성 추가
                // ... 기타 에이전트 매개변수
                .build();
            
            return agentClaudeVertexAi;
        }

        public static void main(String[] args) {
            try {
                LlmAgent agent = createAgent();
                System.out.println("에이전트가 성공적으로 생성되었습니다: " + agent.name());
                // 여기서는 일반적으로 에이전트와 상호 작용하기 위해 Runner와 Session을 설정합니다.
            } catch (IOException e) {
                System.err.println("에이전트 생성 실패: " + e.getMessage());
                e.printStackTrace();
            }
        }
    }
    ```