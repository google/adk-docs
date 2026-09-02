import {
  InMemoryArtifactService,
  InMemorySessionService,
  LlmAgent,
  Runner,
} from '@google/adk';

// Your agent definition.
const agent = new LlmAgent({
  name: 'my_agent',
  model: 'gemini-flash-latest',
});

// Instantiate the desired artifact service.
const artifactService = new InMemoryArtifactService();

// Provide it to the Runner.
const runner = new Runner({
  agent: agent,
  appName: 'artifact_app',
  sessionService: new InMemorySessionService(),
  artifactService: artifactService,
});
// If no artifactService is configured, calling artifact methods on context objects will throw an error.