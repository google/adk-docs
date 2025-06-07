# 스트리밍 동작 구성하기

라이브(스트리밍) 에이전트에 대해 설정할 수 있는 몇 가지 구성이 있습니다.

이 설정은 [RunConfig](https://github.com/google/adk-python/blob/main/src/google/adk/agents/run_config.py)를 통해 이루어지며, [Runner.run_live(...)](https://github.com/google/adk-python/blob/main/src/google/adk/runners.py) 메서드와 함께 사용해야 합니다.

예를 들어, 음성 구성을 설정하고 싶다면 `speech_config`를 활용할 수 있습니다.

```python
# 음성 구성을 설정합니다.
voice_config = genai_types.VoiceConfig(
    prebuilt_voice_config=genai_types.PrebuiltVoiceConfigDict(
        voice_name='Aoede'
    )
)
# 음성 구성을 포함하는 SpeechConfig를 생성합니다.
speech_config = genai_types.SpeechConfig(voice_config=voice_config)
# speech_config를 사용하여 RunConfig를 생성합니다.
run_config = RunConfig(speech_config=speech_config)

# run_live 메서드에 run_config를 전달합니다.
runner.run_live(
    ...,
    run_config=run_config,
)
```