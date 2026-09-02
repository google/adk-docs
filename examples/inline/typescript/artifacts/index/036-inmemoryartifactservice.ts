import {InMemoryArtifactService} from '@google/adk';

// Simply instantiate the class
const inMemoryService = new InMemoryArtifactService();

// This instance would then be provided to your Runner.
// const runner = new Runner({
//   /* other services */,
//   artifactService: inMemoryService
// });