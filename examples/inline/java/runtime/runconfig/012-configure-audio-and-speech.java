import com.google.adk.agents.RunConfig;
import com.google.adk.agents.RunConfig.StreamingMode;
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Modality;
import com.google.genai.types.PrebuiltVoiceConfig;
import com.google.genai.types.SpeechConfig;
import com.google.genai.types.VoiceConfig;

RunConfig runConfig =
    RunConfig.builder()
        .streamingMode(StreamingMode.SSE)
        .maxLlmCalls(1000)
        .responseModalities(ImmutableList.of(new Modality(Modality.Known.AUDIO), new Modality(Modality.Known.TEXT)))
        .speechConfig(
            SpeechConfig.builder()
                .voiceConfig(
                    VoiceConfig.builder()
                        .prebuiltVoiceConfig(
                            PrebuiltVoiceConfig.builder().voiceName("Kore").build())
                        .build())
                .languageCode("en-US")
                .build())
        .build();