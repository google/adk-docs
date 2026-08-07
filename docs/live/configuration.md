# Configuring streaming behavior

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.5.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-preview">Experimental</span>
</div>

There are some configurations you can set for live(streaming) agents. 

It's set by [RunConfig](https://github.com/google/adk-python/blob/main/src/google/adk/agents/run_config.py). You should use RunConfig with your [Runner.run_live(...)](https://github.com/google/adk-python/blob/main/src/google/adk/runners.py). 

For example, if you want to set voice config, you can leverage speech_config. 

=== "Python"

    ```python
    voice_config = genai_types.VoiceConfig(
        prebuilt_voice_config=genai_types.PrebuiltVoiceConfigDict(
            voice_name='Aoede'
        )
    )
    speech_config = genai_types.SpeechConfig(voice_config=voice_config)
    run_config = RunConfig(speech_config=speech_config)

    runner.run_live(
        # ...,
        run_config=run_config,
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.genai.types.PrebuiltVoiceConfig;
    import com.google.genai.types.SpeechConfig;
    import com.google.genai.types.VoiceConfig;

    VoiceConfig voiceConfig =
        VoiceConfig.builder()
            .prebuiltVoiceConfig(PrebuiltVoiceConfig.builder().voiceName("Aoede").build())
            .build();
    SpeechConfig speechConfig = SpeechConfig.builder().voiceConfig(voiceConfig).build();
    RunConfig runConfig = RunConfig.builder().setSpeechConfig(speechConfig).build();

    runner.runLive(
        // ...,
        runConfig);
    ```

RunConfig accepts many more settings than `speech_config`. For the full list, see [Part 4: Understanding RunConfig](dev-guide/part4.md).

!!! note "Python: audio transcription is on by default"

    The `input_audio_transcription` and `output_audio_transcription` fields of `RunConfig` default to `AudioTranscriptionConfig()`, not `None`, so ADK asks the Live API to transcribe both the user's audio and the model's audio unless you explicitly set them to `None`. See [Part 5: Audio Transcription](dev-guide/part5.md#audio-transcription).


