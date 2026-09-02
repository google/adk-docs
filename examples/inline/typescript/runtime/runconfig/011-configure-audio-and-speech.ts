import { RunConfig, StreamingMode } from '@google/adk';
import { Modality } from '@google/genai';

const config: RunConfig = {
    speechConfig: {
        languageCode: "en-US",
        voiceConfig: {
            prebuiltVoiceConfig: {
                voiceName: "Kore"
            }
        },
    },
    responseModalities: [Modality.AUDIO, Modality.TEXT],
    streamingMode: StreamingMode.SSE,
    maxLlmCalls: 1000,
};