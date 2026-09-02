import {
  InMemoryArtifactService,
  InMemorySessionService,
  LlmAgent,
  Runner,
} from '@google/adk';

// Example: Configuring the Runner with an Artifact Service
const myAgent = new LlmAgent({
  name: 'artifact_user_agent',
  model: 'gemini-flash-latest',
});
const artifactService = new InMemoryArtifactService();
const sessionService = new InMemorySessionService();

const runner = new Runner({
  agent: myAgent,
  appName: 'my_artifact_app',
  sessionService: sessionService,
  artifactService: artifactService,
});
// Now, contexts within runs managed by this runner can use artifact methods.