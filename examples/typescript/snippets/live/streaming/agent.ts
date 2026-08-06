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
import type {Event} from '@google/adk';

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

/** Joins the answer text in an event, skipping tool calls and reasoning. */
export function textOf(event: Event): string {
  return (event.content?.parts ?? [])
    .filter((part) => part.text && !part.thought)
    .map((part) => part.text)
    .join('');
}

/**
 * Remembers what has already been shown, so nothing is printed twice and
 * nothing is dropped. Create one per `runAsync` loop.
 */
export class TurnText {
  private shown = '';

  /** The text in `event` that has not been shown yet; `''` if there is none. */
  unshown(event: Event): string {
    const text = textOf(event);
    if (!text) return '';
    if (event.partial) {
      this.shown += text;
      return text;
    }
    // A `partial: false` event repeats every chunk since the previous one, and
    // ADK then starts a fresh block — so emit only the tail beyond what was
    // streamed, and reset. Usually the tail is empty. It is not empty when one
    // model chunk carried text *and* a tool call: that text is never sent as a
    // delta, and this is the only event that carries it. If the two ever fail
    // to line up, fall back to the whole thing — better shown twice than lost.
    const tail = text.startsWith(this.shown)
      ? text.slice(this.shown.length)
      : text;
    this.shown = '';
    return tail;
  }
}
// --8<-- [end:full]
