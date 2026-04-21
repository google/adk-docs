/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

// [START full_example]
import {Agent, SkillToolset, loadSkillFromDir} from '@google/adk';
import * as path from 'node:path';
import {fileURLToPath} from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const weatherSkill = await loadSkillFromDir(
  path.join(__dirname, 'skills', 'weather_skill')
);

const mySkillToolset = new SkillToolset([weatherSkill]);

const rootAgent = new Agent({
  model: 'gemini-2.0-flash',
  name: 'skill_user_agent',
  description: 'An agent that can use specialized skills.',
  instruction:
    'You are a helpful assistant that can leverage skills to perform tasks.',
  tools: [mySkillToolset],
});

export default rootAgent;
// [END full_example]
