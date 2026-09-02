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