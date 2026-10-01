/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

// --8<-- [start:full_example]
import {Agent, Skill, SkillToolset} from '@google/adk';

const greetingSkill: Skill = {
  frontmatter: {
    name: 'greeting-skill',
    description: 'A friendly greeting skill that can say hello to a specific person.',
  },
  instructions:
    "Step 1: Read the 'references/hello_world.txt' file to understand how to greet the user. Step 2: Return a greeting based on the reference.",
  resources: {
    references: {
      'hello_world.txt': 'Hello! So glad to have you here!',
      'example.md': 'This is an example reference.',
    },
  },
};

const mySkillToolset = new SkillToolset([greetingSkill]);

const rootAgent = new Agent({
  model: 'gemini-flash-latest',
  name: 'greeting_agent',
  description: 'An agent that uses an inline greeting skill.',
  instruction: 'You are a helpful assistant that uses skills to greet people.',
  tools: [mySkillToolset],
});

export default rootAgent;
// --8<-- [end:full_example]
