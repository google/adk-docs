# 런타임 구성

`RunConfig`는 ADK에서 에이전트의 런타임 동작과 옵션을 정의합니다. 음성 및 스트리밍 설정, 함수 호출, 아티팩트 저장, LLM 호출 제한 등을 제어합니다.

에이전트 실행을 구성할 때, `RunConfig`를 전달하여 에이전트가 모델과 상호 작용하고, 오디오를 처리하며, 응답을 스트리밍하는 방식을 맞춤 설정할 수 있습니다. 기본적으로 스트리밍은 활성화되지 않으며 입력은 아티팩트로 보존되지 않습니다. `RunConfig`를 사용하여 이러한 기본값을 재정의하세요.

## 클래스 정의

`RunConfig` 클래스는 에이전트의 런타임 동작에 대한 구성 매개변수를 보유합니다.

- Python ADK는 이 유효성 검사를 위해 Pydantic을 사용합니다.

- Java ADK는 일반적으로 불변 데이터 클래스를 사용합니다.

=== "Python"

    ```python
    class RunConfig(BaseModel):
        """에이전트의 런타임 동작에 대한 구성입니다."""
    
        model_config = ConfigDict(
            extra='forbid',
        )
    
        speech_config: Optional[types.SpeechConfig] = None
        response_modalities: Optional[list[str]] = None
        save_input_blobs_as_artifacts: bool = False
        support_cfc: bool = False
        streaming_mode: StreamingMode = StreamingMode.NONE
        output_audio_transcription: Optional[types.AudioTranscriptionConfig] = None
        max_llm_calls: int = 500
    ```

=== "Java"

    ```java
    public abstract class RunConfig {
      
      public enum StreamingMode {
        NONE,
        SSE,
        BIDI
      }
      
      public abstract @Nullable SpeechConfig speechConfig();
    
      public abstract ImmutableList<Modality> responseModalities();
    
      public abstract boolean saveInputBlobsAsArtifacts();
      
      public abstract @Nullable AudioTranscriptionConfig outputAudioTranscription();
    
      public abstract int maxLlmCalls();
      
      // ...
    }
    ```

## 런타임 매개변수

| 매개변수                       | Python 유형                                  | Java 유형                                             | 기본값 (Py / Java)               | 설명                                                                                                                  |
| :------------------------------ | :------------------------------------------- |:------------------------------------------------------|:----------------------------------|:-----------------------------------------------------------------------------------------------------------------------------|
| `speech_config`                 | `Optional[types.SpeechConfig]`               | `SpeechConfig` (@Nullable을 통해 nullable)             | `None` / `null`                   | `SpeechConfig` 유형을 사용하여 음성 합성(음성, 언어)을 구성합니다.                                                 |
| `response_modalities`           | `Optional[list[str]]`                        | `ImmutableList<Modality>`                             | `None` / 빈 `ImmutableList`    | 원하는 출력 양식 목록 (예: Python: `["TEXT", "AUDIO"]`; Java: 구조화된 `Modality` 객체 사용).             |
| `save_input_blobs_as_artifacts` | `bool`                                       | `boolean`                                             | `False` / `false`                 | `true`인 경우, 입력 블롭(예: 업로드된 파일)을 디버깅/감사를 위해 실행 아티팩트로 저장합니다.                                 |
| `streaming_mode`                | `StreamingMode`                              | *현재 지원되지 않음*                             | `StreamingMode.NONE` / N/A        | 스트리밍 동작을 설정합니다: `NONE`(기본값), `SSE`(서버-전송 이벤트), 또는 `BIDI`(양방향).                        |
| `output_audio_transcription`    | `Optional[types.AudioTranscriptionConfig]`   | `AudioTranscriptionConfig` (@Nullable을 통해 nullable) | `None` / `null`                   | `AudioTranscriptionConfig` 유형을 사용하여 생성된 오디오 출력의 전사를 구성합니다.                                |
| `max_llm_calls`                 | `int`                                        | `int`                                                 | `500` / `500`                     | 실행당 총 LLM 호출을 제한합니다. `0` 또는 음수는 무제한(경고); `sys.maxsize`는 `ValueError`를 발생시킵니다.                 |
| `support_cfc`                   | `bool`                                       | *현재 지원되지 않음*                             | `False` / N/A                     | **Python:** 구성적 함수 호출을 활성화합니다. `streaming_mode=SSE`가 필요하며 LIVE API를 사용합니다. **실험적 기능.**   |

### `speech_config`

!!! Note
    `SpeechConfig`의 인터페이스나 정의는 언어에 관계없이 동일합니다.

오디오 기능이 있는 라이브 에이전트를 위한 음성 구성 설정입니다.
`SpeechConfig` 클래스는 다음과 같은 구조를 가집니다:

```python
class SpeechConfig(_common.BaseModel):
    """음성 생성 구성입니다."""

    voice_config: Optional[VoiceConfig] = Field(
        default=None,
        description="""사용할 스피커에 대한 구성입니다.""",
    )
    language_code: Optional[str] = Field(
        default=None,
        description="""음성 합성을 위한 언어 코드(ISO 639. 예: en-US).
        Live API에서만 사용할 수 있습니다.""",
    )
```

`voice_config` 매개변수는 `VoiceConfig` 클래스를 사용합니다:

```python
class VoiceConfig(_common.BaseModel):
    """사용할 음성에 대한 구성입니다."""

    prebuilt_voice_config: Optional[PrebuiltVoiceConfig] = Field(
        default=None,
        description="""사용할 스피커에 대한 구성입니다.""",
    )
```

그리고 `PrebuiltVoiceConfig`는 다음과 같은 구조를 가집니다:

```python
class PrebuiltVoiceConfig(_common.BaseModel):
    """사용할 미리 빌드된 스피커에 대한 구성입니다."""

    voice_name: Optional[str] = Field(
        default=None,
        description="""사용할 미리 빌드된 음성의 이름입니다.""",
    )
```

이러한 중첩된 구성 클래스를 사용하여 다음을 지정할 수 있습니다:

*   `voice_config`: 사용할 미리 빌드된 음성의 이름 (`PrebuiltVoiceConfig`에서)
*   `language_code`: 음성 합성을 위한 ISO 639 언어 코드 (예: "en-US")

음성 지원 에이전트를 구현할 때, 에이전트가 말할 때 어떻게 들리는지 제어하기 위해 이러한 매개변수를 구성하세요.

### `response_modalities`

에이전트의 출력 양식을 정의합니다. 설정하지 않으면 기본적으로 오디오로 설정됩니다.
응답 양식은 에이전트가 다양한 채널(예: 텍스트, 오디오)을 통해 사용자와 통신하는 방법을 결정합니다.

### `save_input_blobs_as_artifacts`

활성화하면 입력 블롭이 에이전트 실행 중에 아티팩트로 저장됩니다.
이는 개발자가 에이전트가 수신한 정확한 데이터를 검토할 수 있도록 하여 디버깅 및 감사 목적에 유용합니다.

### `support_cfc`

구성적 함수 호출(CFC) 지원을 활성화합니다. StreamingMode.SSE를 사용할 때만 적용됩니다. 활성화하면 CFC 기능만 지원하는 LIVE API가 호출됩니다.

!!! warning

    `support_cfc` 기능은 실험적이며 API나 동작이 향후 릴리스에서 변경될 수 있습니다.

### `streaming_mode`

에이전트의 스트리밍 동작을 구성합니다. 가능한 값:

*   `StreamingMode.NONE`: 스트리밍 없음; 응답이 완전한 단위로 전달됨
*   `StreamingMode.SSE`: 서버-전송 이벤트 스트리밍; 서버에서 클라이언트로의 단방향 스트리밍
*   `StreamingMode.BIDI`: 양방향 스트리밍; 양방향 동시 통신

스트리밍 모드는 성능과 사용자 경험 모두에 영향을 미칩니다. SSE 스트리밍은 사용자가 생성되는 대로 부분적인 응답을 볼 수 있게 해주며, BIDI 스트리밍은 실시간 대화형 경험을 가능하게 합니다.

### `output_audio_transcription`

오디오 응답 기능이 있는 라이브 에이전트의 오디오 출력을 전사하기 위한 구성입니다. 이는 접근성, 기록 보관 및 다중 모드 애플리케이션을 위한 오디오 응답의 자동 전사를 가능하게 합니다.

### `max_llm_calls`

주어진 에이전트 실행에 대한 총 LLM 호출 수를 제한합니다.

*   0보다 크고 `sys.maxsize`보다 작은 값: LLM 호출에 대한 제한을 강제합니다.
*   0 이하의 값: 무제한 LLM 호출을 허용합니다 *(프로덕션 환경에서는 권장되지 않음)*

이 매개변수는 과도한 API 사용과 잠재적인 폭주 프로세스를 방지합니다.
LLM 호출은 종종 비용과 리소스를 소모하므로 적절한 제한을 설정하는 것이 중요합니다.

## 유효성 검사 규칙

`RunConfig` 클래스는 적절한 에이전트 작동을 보장하기 위해 매개변수를 검증합니다. Python ADK는 자동 유형 검증을 위해 `Pydantic`을 사용하지만, Java ADK는 정적 타이핑에 의존하며 RunConfig 생성 시 명시적인 검사를 포함할 수 있습니다.
특히 `max_llm_calls` 매개변수의 경우:

1.  매우 큰 값(Python의 `sys.maxsize` 또는 Java의 `Integer.MAX_VALUE` 등)은 문제를 방지하기 위해 일반적으로 허용되지 않습니다.

2.  0 이하의 값은 일반적으로 무제한 LLM 상호 작용에 대한 경고를 트리거합니다.

## 예제

### 기본 런타임 구성

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode
    
    config = RunConfig(
        streaming_mode=StreamingMode.NONE,
        max_llm_calls=100
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    
    RunConfig config = RunConfig.builder()
            .setStreamingMode(StreamingMode.NONE)
            .setMaxLlmCalls(100)
            .build();
    ```

이 구성은 완전한 응답이 바람직한 간단한 작업 지향 에이전트에 적합한 100회 LLM 호출 제한이 있는 비스트리밍 에이전트를 생성합니다.

### 스트리밍 활성화

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode
    
    config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=200
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    
    RunConfig config = RunConfig.builder()
        .setStreamingMode(StreamingMode.SSE)
        .setMaxLlmCalls(200)
        .build();
    ```

SSE 스트리밍을 사용하면 사용자가 생성되는 대로 응답을 볼 수 있어 챗봇과 어시스턴트에 더 반응적인 느낌을 줍니다.

### 음성 지원 활성화

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode
    from google.genai import types
    
    config = RunConfig(
        speech_config=types.SpeechConfig(
            language_code="en-US",
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Kore"
                )
            ),
        ),
        response_modalities=["AUDIO", "TEXT"],
        save_input_blobs_as_artifacts=True,
        support_cfc=True,
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=1000,
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    import com.google.common.collect.ImmutableList;
    import com.google.genai.types.Content;
    import com.google.genai.types.Modality;
    import com.google.genai.types.Part;
    import com.google.genai.types.PrebuiltVoiceConfig;
    import com.google.genai.types.SpeechConfig;
    import com.google.genai.types.VoiceConfig;
    
    RunConfig runConfig =
        RunConfig.builder()
            .setStreamingMode(StreamingMode.SSE)
            .setMaxLlmCalls(1000)
            .setSaveInputBlobsAsArtifacts(true)
            .setResponseModalities(ImmutableList.of(new Modality("AUDIO"), new Modality("TEXT")))
            .setSpeechConfig(
                SpeechConfig.builder()
                    .voiceConfig(
                        VoiceConfig.builder()
                            .prebuiltVoiceConfig(
                                PrebuiltVoiceConfig.builder().voiceName("Kore").build())
                            .build())
                    .languageCode("en-US")
                    .build())
            .build();
    ```

이 포괄적인 예제는 다음과 같은 에이전트를 구성합니다:

*   "Kore" 음성(미국 영어)을 사용한 음성 기능
*   오디오 및 텍스트 출력 양식 모두
*   입력 블롭에 대한 아티팩트 저장 (디버깅에 유용)
*   실험적인 CFC 지원 활성화 **(Python만 해당)**
*   반응형 상호 작용을 위한 SSE 스트리밍
*   1000회 LLM 호출 제한

### 실험적 CFC 지원 활성화

![python_only](https://img.shields.io/badge/현재_지원되는_언어-Python-blue){ title="이 기능은 현재 Python에서만 사용할 수 있습니다. Java 지원은 계획 중이거나 곧 제공될 예정입니다."}

```python
from google.genai.adk import RunConfig, StreamingMode

config = RunConfig(
    streaming_mode=StreamingMode.SSE,
    support_cfc=True,
    max_llm_calls=150
)
```

구성적 함수 호출을 활성화하면 모델 출력에 따라 동적으로 함수를 실행할 수 있는 에이전트가 생성되며, 이는 복잡한 워크플로가 필요한 애플리케이션에 강력합니다.