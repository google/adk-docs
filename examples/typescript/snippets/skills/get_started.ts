/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

// --8<-- [start:full_example]
import {Agent, FunctionTool, SkillToolset, loadSkillFromDir} from '@google/adk';
import * as path from 'node:path';
import {z} from 'zod';

const weatherSkill = await loadSkillFromDir(
  path.join(__dirname, 'skills/weather_skill')
);

const getWeatherTool = new FunctionTool({
  name: 'get_weather',
  description: 'Gets the weather for a given location.',
  parameters: z.object({
    location: z.string().describe('The city and state, e.g. San Francisco, CA'),
  }),
  execute: async ({location}) => {
    return {
      location,
      temperature: '72°F',
      condition: 'Sunny',
    };
  },
});

const mySkillToolset = new SkillToolset([weatherSkill], {
  additionalTools: [getWeatherTool],
});

const rootAgent = new Agent({
  model: 'gemini-flash-latest',
  name: 'skill_user_agent',
  description: 'An agent that can use specialized skills.',
  instruction:
    'You are a helpful assistant that can leverage skills to perform tasks.',
  tools: [mySkillToolset],
});

export default rootAgent;
// --8<-- [end:full_example]
