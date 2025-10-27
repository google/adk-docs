// Copyright 2025 Google LLC
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

import {
  ParallelAgent,
  LlmAgent,
  SequentialAgent,
  InMemoryRunner,
  GOOGLE_SEARCH,
  isFinalResponse,
} from "@google/adk";

import {createUserContent} from '@google/genai';

// --- Configuration ---
const APP_NAME = "parallel_research_app";
const USER_ID = "research_user_01";
const SESSION_ID = "parallel_research_session_with_merge";
const GEMINI_MODEL = "gemini-2.5-flash";


// --8<-- [start:init]
// Part of agent.ts --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup
// --- 1. Define Researcher Sub-Agents (to run in parallel) ---

const researchTools = [GOOGLE_SEARCH];

// Researcher 1: Renewable Energy
const researcherAgent1 = new LlmAgent({
    name: "RenewableEnergyResearcher",
    model: GEMINI_MODEL,
    instruction: `You are an AI Research Assistant specializing in energy.
Research the latest advancements in 'renewable energy sources'.
Use the Google Search tool provided.
Summarize your key findings concisely (1-2 sentences).
Output *only* the summary.
`,
    description: "Researches renewable energy sources.",
    tools: researchTools,
    // Store result in state for the merger agent
    outputKey: "renewable_energy_result"
});

// Researcher 2: Electric Vehicles
const researcherAgent2 = new LlmAgent({
    name: "EVResearcher",
    model: GEMINI_MODEL,
    instruction: `You are an AI Research Assistant specializing in transportation.
Research the latest developments in 'electric vehicle technology'.
Use the Google Search tool provided.
Summarize your key findings concisely (1-2 sentences).
Output *only* the summary.
`,
    description: "Researches electric vehicle technology.",
    tools: researchTools,
    // Store result in state for the merger agent
    outputKey: "ev_technology_result"
});

// Researcher 3: Carbon Capture
const researcherAgent3 = new LlmAgent({
    name: "CarbonCaptureResearcher",
    model: GEMINI_MODEL,
    instruction: `You are an AI Research Assistant specializing in climate solutions.
Research the current state of 'carbon capture methods'.
Use the Google Search tool provided.
Summarize your key findings concisely (1-2 sentences).
Output *only* the summary.
`,
    description: "Researches carbon capture methods.",
    tools: researchTools,
    // Store result in state for the merger agent
    outputKey: "carbon_capture_result"
});

// --- 2. Create the ParallelAgent (Runs researchers concurrently) ---
// This agent orchestrates the concurrent execution of the researchers.
// It finishes once all researchers have completed and stored their results in state.
const parallelResearchAgent = new ParallelAgent({
    name: "ParallelWebResearchAgent",
    subAgents: [researcherAgent1, researcherAgent2, researcherAgent3],
    description: "Runs multiple research agents in parallel to gather information."
});

// --- 3. Define the Merger Agent (Runs *after* the parallel agents) ---
// This agent takes the results stored in the session state by the parallel agents
// and synthesizes them into a single, structured response with attributions.
const mergerAgent = new LlmAgent({
    name: "SynthesisAgent",
    model: GEMINI_MODEL,  // Or potentially a more powerful model if needed for synthesis
    instruction: `You are an AI Assistant responsible for combining research findings into a structured report.

Your primary task is to synthesize the following research summaries, clearly attributing findings to their source areas. Structure your response using headings for each topic. Ensure the report is coherent and integrates the key points smoothly.

**Crucially: Your entire response MUST be grounded *exclusively* on the information provided in the 'Input Summaries' below. Do NOT add any external knowledge, facts, or details not present in these specific summaries.**

**Input Summaries:**

*   **Renewable Energy:**
    {renewable_energy_result}

*   **Electric Vehicles:**
    {ev_technology_result}

*   **Carbon Capture:**
    {carbon_capture_result}

**Output Format:**

## Summary of Recent Sustainable Technology Advancements

### Renewable Energy Findings
(Based on RenewableEnergyResearcher's findings)
[Synthesize and elaborate *only* on the renewable energy input summary provided above.]

### Electric Vehicle Findings
(Based on EVResearcher's findings)
[Synthesize and elaborate *only* on the EV input summary provided above.]

### Carbon Capture Findings
(Based on CarbonCaptureResearcher's findings)
[Synthesize and elaborate *only* on the carbon capture input summary provided above.]

### Overall Conclusion
[Provide a brief (1-2 sentence) concluding statement that connects *only* the findings presented above.]

Output *only* the structured report following this format. Do not include introductory or concluding phrases outside this structure, and strictly adhere to using only the provided input summary content.
`,
    description: "Combines research findings from parallel agents into a structured, cited report, strictly grounded on provided inputs.",
    // No tools needed for merging
    // No output_key needed here, as its direct response is the final output of the sequence
});


// --- 4. Create the SequentialAgent (Orchestrates the overall flow) ---
// This is the main agent that will be run. It first executes the ParallelAgent
// to populate the state, and then executes the MergerAgent to produce the final output.
const rootAgent = new SequentialAgent({
    name: "ResearchAndSynthesisPipeline",
    // Run parallel research first, then merge
    subAgents: [parallelResearchAgent, mergerAgent],
    description: "Coordinates parallel research and synthesizes the results."
});
// --8<-- [end:init]

// --- 5. Running the Agent (Using InMemoryRunner for local testing) This works in Notebooks and script file ---

async function callSequentialPipeline(runner: InMemoryRunner, query: string, userId: string, sessionId: string) {
    console.log(`--- Running Research & Synthesis Pipeline for query: "${query}" ---`);
    // The initial query mainly triggers the pipeline; the research topics are fixed in the agents for this example.
    const content = createUserContent(query);
    let finalResponseText: string | undefined = undefined;
    // Keep track of which researchers have reported
    const researcherOutputs: {[key: string]: string} = {};
    const researcherNames = new Set(["RenewableEnergyResearcher", "EVResearcher", "CarbonCaptureResearcher"]);
    const mergerAgentName = "SynthesisAgent"; // Name of the final agent in sequence

    console.log("Starting pipeline...");
    try {
        for await (const event of runner.runAsync({
            userId,
            sessionId,
            newMessage: content,
        })) {
            const authorName = event.author || "System";
            const isFinal = isFinalResponse(event);
            console.log(`  [Event] From: ${authorName}, Final: ${isFinal}`); // Basic event logging

            // Check if it's a final response from one of the researcher agents
            if (isFinal && researcherNames.has(authorName) && event.content?.parts?.length) {
                const researcherOutput = event.content.parts[0].text?.trim();
                if (researcherOutput && !(authorName in researcherOutputs)) { // Print only once per researcher
                    console.log(`    -> Intermediate Result from ${authorName}: ${researcherOutput}`);
                    researcherOutputs[authorName] = researcherOutput;
                }
            }
            // Check if it's the final response from the merger agent (the last agent in the sequence)
            else if (isFinal && authorName === mergerAgentName && event.content?.parts?.length) {
                    finalResponseText = event.content.parts[0].text?.trim();
                    console.log(`<<< Final Synthesized Response (from ${authorName}): ${finalResponseText}`);
                    // Since this is the last agent in the sequence, we can break after its final response
                    break;
            } else if (event.errorMessage) {
                    console.log(`  -> Error from ${authorName}: ${event.errorMessage}`);
            }
        }
    if (!finalResponseText) {
            console.log("<<< Pipeline finished but did not produce the expected final text response from the SynthesisAgent.");
    }
    } catch (e) {
        console.log(`\n❌ An error occurred during agent execution: ${e}`);
    }
}

async function main() {
  // Use InMemoryRunner: Ideal for quick prototyping and local testing
  const runner = new InMemoryRunner({agent: rootAgent, appName: APP_NAME});
  console.log(`InMemoryRunner created for agent "${rootAgent.name}".`);

  // We still need access to the session service (bundled in InMemoryRunner)
  // to create the session instance for the run.
  const sessionService = runner.sessionService;
  await sessionService.createSession({appName: APP_NAME, userId: USER_ID, sessionId: SESSION_ID});
  console.log(`Session "${SESSION_ID}" created for direct run.`);

  const initialTriggerQuery = "Summarize recent sustainable tech advancements.";

  await callSequentialPipeline(runner, initialTriggerQuery, USER_ID, SESSION_ID);
}

main();
