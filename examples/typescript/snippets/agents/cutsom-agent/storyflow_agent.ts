/**
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {
  LlmAgent,
  BaseAgent,
  LoopAgent,
  SequentialAgent,
  InMemoryRunner,
  InvocationContext,
  Event,
  isFinalResponse,
} from '@google/adk';
import { createUserContent } from "@google/genai";

// --- Constants ---
const APP_NAME = "story_app_ts";
const USER_ID = "12345";
const SESSION_ID = "123344_ts";
const GEMINI_MODEL = "gemini-2.5-flash";

// --- Custom Orchestrator Agent ---
// --8<-- [start:init]
class StoryFlowAgent extends BaseAgent {
  // --- Property Declarations for TypeScript ---
  private storyGenerator: LlmAgent;
  private critic: LlmAgent;
  private reviser: LlmAgent;
  private grammarCheck: LlmAgent;
  private toneCheck: LlmAgent;

  private loopAgent: LoopAgent;
  private sequentialAgent: SequentialAgent;

  constructor(
    name: string,
    storyGenerator: LlmAgent,
    critic: LlmAgent,
    reviser: LlmAgent,
    grammarCheck: LlmAgent,
    toneCheck: LlmAgent
  ) {
    // Create internal composite agents
    const loopAgent = new LoopAgent({
      name: "CriticReviserLoop",
      subAgents: [critic, reviser],
      maxIterations: 2,
    });

    const sequentialAgent = new SequentialAgent({
      name: "PostProcessing",
      subAgents: [grammarCheck, toneCheck],
    });
    
    // Define the sub-agents for the framework to know about
    const subAgentsList = [
      storyGenerator,
      loopAgent,
      sequentialAgent,
    ];

    // Call the parent constructor
    super({
      name,
      subAgents: subAgentsList,
    });
    
    // Assign agents to class properties for use in the custom run logic
    this.storyGenerator = storyGenerator;
    this.critic = critic;
    this.reviser = reviser;
    this.grammarCheck = grammarCheck;
    this.toneCheck = toneCheck;
    this.loopAgent = loopAgent;
    this.sequentialAgent = sequentialAgent;
  }
// --8<-- [end:init]

  // --8<-- [start:executionlogic]
  // Implements the custom orchestration logic for the story workflow.
  async* runLiveImpl(ctx: InvocationContext): AsyncGenerator<Event, void, undefined> {
    yield* this.runAsyncImpl(ctx);
  }

  // Implements the custom orchestration logic for the story workflow.
  async* runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event, void, undefined> {
    console.log(`[${this.name}] Starting story generation workflow.`);

    // 1. Initial Story Generation
    console.log(`[${this.name}] Running StoryGenerator...`);
    for await (const event of this.storyGenerator.runAsync(ctx)) {
      console.log(`[${this.name}] Event from StoryGenerator: ${JSON.stringify(event, null, 2)}`);
      yield event;
    }

    // Check if the story was generated before proceeding
    if (!ctx.session.state["current_story"]) {
      console.error(`[${this.name}] Failed to generate initial story. Aborting workflow.`);
      return; // Stop processing
    }
    console.log(`[${this.name}] Story state after generator: ${ctx.session.state['current_story']}`);

    // 2. Critic-Reviser Loop
    console.log(`[${this.name}] Running CriticReviserLoop...`);
    for await (const event of this.loopAgent.runAsync(ctx)) {
      console.log(`[${this.name}] Event from CriticReviserLoop: ${JSON.stringify(event, null, 2)}`);
      yield event;
    }
    console.log(`[${this.name}] Story state after loop: ${ctx.session.state['current_story']}`);

    // 3. Sequential Post-Processing (Grammar and Tone Check)
    console.log(`[${this.name}] Running PostProcessing...`);
    for await (const event of this.sequentialAgent.runAsync(ctx)) {
      console.log(`[${this.name}] Event from PostProcessing: ${JSON.stringify(event, null, 2)}`);
      yield event;
    }
    
    // 4. Tone-Based Conditional Logic
    const toneCheckResult = ctx.session.state["tone_check_result"] as string;
    console.log(`[${this.name}] Tone check result: ${toneCheckResult}`);

    if (toneCheckResult === "negative") {
      console.log(`[${this.name}] Tone is negative. Regenerating story...`);
      for await (const event of this.storyGenerator.runAsync(ctx)) {
        console.log(`[${this.name}] Event from StoryGenerator (Regen): ${JSON.stringify(event, null, 2)}`);
        yield event;
      }
    } else {
      console.log(`[${this.name}] Tone is not negative. Keeping current story.`);
    }

    console.log(`[${this.name}] Workflow finished.`);
  }
  // --8<-- [end:executionlogic]
}

// --8<-- [start:llmagents]
// --- Define the individual LLM agents ---
const storyGenerator = new LlmAgent({
    name: "StoryGenerator",
    model: GEMINI_MODEL,
    instruction: `You are a story writer. Write a short story (around 100 words), on the following topic: {topic}`,
    outputKey: "current_story",
});

const critic = new LlmAgent({
    name: "Critic",
    model: GEMINI_MODEL,
    instruction: `You are a story critic. Review the story provided: {{current_story}}. Provide 1-2 sentences of constructive criticism
on how to improve it. Focus on plot or character.`,
    outputKey: "criticism",
});

const reviser = new LlmAgent({
    name: "Reviser",
    model: GEMINI_MODEL,
    instruction: `You are a story reviser. Revise the story provided: {{current_story}}, based on the criticism in
{{criticism}}. Output only the revised story.`,
    outputKey: "current_story", // Overwrites the original story
});

const grammarCheck = new LlmAgent({
    name: "GrammarCheck",
    model: GEMINI_MODEL,
    instruction: `You are a grammar checker. Check the grammar of the story provided: {current_story}. Output only the suggested
corrections as a list, or output 'Grammar is good!' if there are no errors.`,
    outputKey: "grammar_suggestions",
});

const toneCheck = new LlmAgent({
    name: "ToneCheck",
    model: GEMINI_MODEL,
    instruction: `You are a tone analyzer. Analyze the tone of the story provided: {current_story}. Output only one word: 'positive' if
the tone is generally positive, 'negative' if the tone is generally negative, or 'neutral'
otherwise.`,
    outputKey: "tone_check_result",
});
// --8<-- [end:llmagents]

// --8<-- [start:story_flow_agent]
// --- Create the custom agent instance ---
const storyFlowAgent = new StoryFlowAgent(
    "StoryFlowAgent",
    storyGenerator,
    critic,
    reviser,
    grammarCheck,
    toneCheck
);

const INITIAL_STATE = { "topic": "a brave kitten exploring a haunted house" };

// --- Setup Runner and Session ---
async function setupRunnerAndSession() {
  const runner = new InMemoryRunner({
    agent: storyFlowAgent,
    appName: APP_NAME,
  });
  const session = await runner.sessionService.createSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID,
    state: INITIAL_STATE,
  });
  console.log(`Initial session state: ${JSON.stringify(session.state, null, 2)}`);
  return runner;
}

// --- Function to Interact with the Agent ---
async function callAgent(runner: InMemoryRunner, userInputTopic: string) {
  const currentSession = await runner.sessionService.getSession({
      appName: APP_NAME,
      userId: USER_ID,
      sessionId: SESSION_ID
  });

  if (!currentSession) {
      return;
  }
  // Update the state with the new topic for this run
  currentSession.state["topic"] = userInputTopic;
  console.log(`Updated session state topic to: ${userInputTopic}`);

  let finalResponse = "No final response captured.";
  for await (const event of runner.runAsync({
    userId: USER_ID,
    sessionId: SESSION_ID,
    newMessage: createUserContent(`Generate a story about: ${userInputTopic}`)
  })) {
    if (isFinalResponse(event) && event.content?.parts?.length) {
      console.log(`Potential final response from [${event.author}]: ${event.content.parts.map(part => part.text ?? '').join('')}`);
      finalResponse = event.content.parts.map(part => part.text ?? '').join('');
    }
  }

  const finalSession = await runner.sessionService.getSession({
    appName: APP_NAME,
    userId: USER_ID,
    sessionId: SESSION_ID
  });

  console.log("\n--- Agent Interaction Result ---");
  console.log("Agent Final Response: ", finalResponse);
  console.log("Final Session State:");
  console.log(JSON.stringify(finalSession?.state, null, 2));
  console.log("-------------------------------\n");
}

// --- Run the Agent ---
async function main() {
  const runner = await setupRunnerAndSession();
  await callAgent(runner, "a lonely robot finding a friend in a junkyard");
}

main();
// --8<-- [end:story_flow_agent]
