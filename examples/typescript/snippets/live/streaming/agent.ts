// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// --8<-- [start:full]
import {InMemoryRunner, LlmAgent} from '@google/adk';

export const APP_NAME = 'streaming_quickstart';

export const explainerAgent = new LlmAgent({
  name: 'explainer',
  model: 'gemini-2.5-flash',
  description: 'Explains things clearly and at length.',
  instruction:
    'You are a patient explainer. Answer in three short paragraphs so the ' +
    'reader can watch the text arrive.',
});

export const runner = new InMemoryRunner({
  appName: APP_NAME,
  agent: explainerAgent,
});
// --8<-- [end:full]
