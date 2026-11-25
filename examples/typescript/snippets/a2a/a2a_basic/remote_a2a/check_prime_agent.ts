/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import {FunctionTool, LlmAgent} from '@google/adk';
import {z} from 'zod';

const checkPrimeTool = new FunctionTool({
  name: 'check_prime',
  description: 'Checks whether each integer in a list is a prime number.',
  parameters: z.object({
    nums: z.array(z.number().int()).describe('The list of integers to check.'),
  }),
  execute: ({nums}) => {
    const primes = new Set<number>();
    for (const num of nums) {
      if (num <= 1) {
        continue;
      }
      let isPrime = true;
      for (let i = 2; i * i <= num; i++) {
        if (num % i === 0) {
          isPrime = false;
          break;
        }
      }
      if (isPrime) {
        primes.add(num);
      }
    }
    if (primes.size === 0) {
      return 'No prime numbers found.';
    }
    return `${Array.from(primes).join(', ')} are prime numbers.`;
  },
});

export const rootAgent = new LlmAgent({
  name: 'check_prime_agent',
  model: 'gemini-flash-latest',
  description: 'Agent that checks whether numbers are prime.',
  instruction:
    'You check whether numbers are prime. When checking prime numbers, call the check_prime tool with a list of integers.',
  tools: [checkPrimeTool],
});
