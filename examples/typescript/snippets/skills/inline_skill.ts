/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

// [START full_example]
import {Skill} from '@google/adk';

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
// [END full_example]
