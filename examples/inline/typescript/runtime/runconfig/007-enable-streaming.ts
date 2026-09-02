import { RunConfig, StreamingMode } from '@google/adk';

const config: RunConfig = {
    streamingMode: StreamingMode.SSE,
    supportCfc: true,
    maxLlmCalls: 150,
};