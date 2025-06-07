# ストリーミング動作の設定

ライブ（ストリーミング）エージェントには、設定可能な項目がいくつかあります。

これは[RunConfig](https://github.com/google/adk-python/blob/main/src/google/adk/agents/run_config.py)によって設定されます。`RunConfig`は[Runner.run_live(...)](https://github.com/google/adk-python/blob/main/src/google/adk/runners.py)と一緒に使用する必要があります。

例えば、音声設定を行いたい場合は、`speech_config`を利用できます。

```python
voice_config = genai_types.VoiceConfig(
    prebuilt_voice_config=genai_types.PrebuiltVoiceConfigDict(
        voice_name='Aoede'
    )
)
speech_config = genai_types.SpeechConfig(voice_config=voice_config)
run_config = RunConfig(speech_config=speech_config)

runner.run_live(
    ...,
    run_config=run_config,
)
```
