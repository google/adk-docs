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

// A graph workflow whose first node calls an unreliable service. The node
// retries transient failures with exponential backoff, and each attempt is
// limited by a timeout.

// --8<-- [start:get-started]
import {
  createEvent,
  node,
  NodeContext,
  NodeTimeoutError,
  Workflow,
} from '@google/adk';

/** Stands in for a transient failure from a remote service. */
class ServiceUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ServiceUnavailableError';
  }
}

/** Simulates an unreliable call to a forecast service. */
async function* fetchForecast(ctx: NodeContext) {
  yield createEvent({
    content: {
      role: 'model',
      parts: [{ text: `Fetching forecast, attempt ${ctx.attemptCount}` }],
    },
  });
  if (Math.random() < 0.5) {
    throw new ServiceUnavailableError('Forecast service unavailable');
  }
  yield 'sunny';
}

function reportForecast(_ctx: NodeContext, forecast: string) {
  return `The forecast is ${forecast}.`;
}

export const rootAgent = new Workflow({
  name: 'forecast_workflow',
  edges: [
    [
      'START',
      node(fetchForecast, {
        name: 'fetch_forecast',
        retryConfig: {
          maxAttempts: 3, // 1 original attempt + 2 retries
          initialDelay: 1, // seconds before the first retry
          exceptions: [ServiceUnavailableError, NodeTimeoutError],
        },
        timeout: 10, // seconds allowed for each attempt
      }),
      node(reportForecast, { name: 'report_forecast' }),
    ],
  ],
});
// --8<-- [end:get-started]
