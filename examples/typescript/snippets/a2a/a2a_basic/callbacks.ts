/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

// --8<-- [start:callbacks]
import {RemoteA2AAgent} from '@google/adk/a2a';
import type {
  AfterA2ARequestCallback,
  BeforeA2ARequestCallback,
} from '@google/adk/a2a';

const addRequestMetadata: BeforeA2ARequestCallback = (ctx, params) => {
  params.metadata = {
    ...params.metadata,
    invocation_id: ctx.invocationId,
  };
};

const logRemoteEvent: AfterA2ARequestCallback = (_ctx, event) => {
  console.log('Received A2A event kind:', event.kind);
};

export const configuredPrimeAgent = new RemoteA2AAgent({
  name: 'prime_agent',
  description: 'Agent that handles checking if numbers are prime.',
  agentCard: 'http://localhost:8001/a2a/check_prime_agent/',
  beforeRequestCallbacks: [addRequestMetadata],
  afterRequestCallbacks: [logRemoteEvent],
  metadata: {
    environment: 'local',
  },
});
// --8<-- [end:callbacks]
