package main

import (
	"context"
	"iter"

	"google.golang.org/adk/agent/workflowagents/loopagent"
	"google.golang.org/adk/agent/workflowagents/parallelagent"
	"google.golang.org/adk/agent/workflowagents/sequentialagent"

	"google.golang.org/adk/agent"
	"google.golang.org/adk/agent/llmagent"
	"google.golang.org/adk/llm/gemini"
	"google.golang.org/adk/session"
	"google.golang.org/genai"
)

func conceptualSnippets() {
	ctx := context.Background()
	model, _ := gemini.NewModel(ctx, "gemini-1.5-flash", &genai.ClientConfig{})

	// --8<-- [start:hierarchy]
	// Conceptual Example: Defining Hierarchy
	// Define individual agents
	greeter, _ := llmagent.New(llmagent.Config{Name: "Greeter", Model: model})
	taskDoer, _ := agent.New(agent.Config{Name: "TaskExecutor"}) // Custom non-LLM agent

	// Create parent agent and assign children via sub_agents
	coordinator, _ := llmagent.New(llmagent.Config{
		Name:        "Coordinator",
		Model:       model,
		Description: "I coordinate greetings and tasks.",
		SubAgents:   []agent.Agent{greeter, taskDoer}, // Assign sub_agents here
	})
	// --8<-- [end:hierarchy]
	_ = coordinator // Avoid unused variable error

	// --8<-- [start:sequential-pipeline]
	// Conceptual Example: Sequential Pipeline
	step1, _ := llmagent.New(llmagent.Config{Name: "Step1_Fetch", OutputKey: "data", Model: model}) // Saves output to state["data"]
	step2, _ := llmagent.New(llmagent.Config{Name: "Step2_Process", Instruction: "Process data from {data}.", Model: model})

	pipeline, _ := sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{Name: "MyPipeline", SubAgents: []agent.Agent{step1, step2}},
	})
	// When pipeline runs, Step2 can access the state["data"] set by Step1.
	// --8<-- [end:sequential-pipeline]
	_ = pipeline // Avoid unused variable error

	// --8<-- [start:parallel-execution]
	// Conceptual Example: Parallel Execution
	fetchWeather, _ := llmagent.New(llmagent.Config{Name: "WeatherFetcher", OutputKey: "weather", Model: model})
	fetchNews, _ := llmagent.New(llmagent.Config{Name: "NewsFetcher", OutputKey: "news", Model: model})

	gatherer, _ := parallelagent.New(parallelagent.Config{
		AgentConfig: agent.Config{Name: "InfoGatherer", SubAgents: []agent.Agent{fetchWeather, fetchNews}},
	})
	// When gatherer runs, WeatherFetcher and NewsFetcher run concurrently.
	// A subsequent agent could read state["weather"] and state["news"].
	// --8<-- [end:parallel-execution]
	_ = gatherer // Avoid unused variable error

	// --8<-- [start:loop-with-condition]
	// Conceptual Example: Loop with Condition
	// Custom agent to check state
	checkCondition, _ := agent.New(agent.Config{
		Name: "Checker",
		Run: func(ctx agent.Context) iter.Seq2[*session.Event, error] {
			return func(yield func(*session.Event, error) bool) {
				status, _ := ctx.Session().State().Get("status")
				isDone := status == "completed"
				yield(&session.Event{Author: "Checker", Actions: &session.EventActions{Escalate: isDone}}, nil)
			}
		},
	})

	processStep, _ := llmagent.New(llmagent.Config{Name: "ProcessingStep", Model: model}) // Agent that might update state["status"]

	poller, _ := loopagent.New(loopagent.Config{
		MaxIterations: 10,
		AgentConfig:   agent.Config{Name: "StatusPoller", SubAgents: []agent.Agent{processStep, checkCondition}},
	})
	// When poller runs, it executes processStep then Checker repeatedly
	// until Checker escalates (state["status"] == "completed") or 10 iterations pass.
	// --8<-- [end:loop-with-condition]
	_ = poller // Avoid unused variable error

	// --8<-- [start:output-key-state]
	// Conceptual Example: Using output_key and reading state
	agentA, _ := llmagent.New(llmagent.Config{Name: "AgentA", Instruction: "Find the capital of France.", OutputKey: "capital_city", Model: model})
	agentB, _ := llmagent.New(llmagent.Config{Name: "AgentB", Instruction: "Tell me about the city stored in {capital_city}.", Model: model})

	pipeline2, _ := sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{Name: "CityInfo", SubAgents: []agent.Agent{agentA, agentB}},
	})
	// AgentA runs, saves "Paris" to state["capital_city"].
	// AgentB runs, its instruction processor reads state["capital_city"] to get "Paris".
	// --8<-- [end:output-key-state]
	_ = pipeline2 // Avoid unused variable error

	// --8<-- [start:llm-transfer]
	// Conceptual Setup: LLM Transfer
	bookingAgent, _ := llmagent.New(llmagent.Config{Name: "Booker", Description: "Handles flight and hotel bookings.", Model: model})
	infoAgent, _ := llmagent.New(llmagent.Config{Name: "Info", Description: "Provides general information and answers questions.", Model: model})

	coordinator2, _ := llmagent.New(llmagent.Config{
		Name:        "Coordinator",
		Model:       model,
		Instruction: "You are an assistant. Delegate booking tasks to Booker and info requests to Info.",
		Description: "Main coordinator.",
		SubAgents:   []agent.Agent{bookingAgent, infoAgent},
	})
	// If coordinator receives "Book a flight", its LLM should generate:
	// FunctionCall{Name: "transfer_to_agent", Args: map[string]any{"agent_name": "Booker"}}
	// ADK framework then routes execution to bookingAgent.
	// --8<-- [end:llm-transfer]
	_ = coordinator2 // Avoid unused variable error

	// --8<-- [start:agent-as-tool]
	// Conceptual Setup: Agent as a Tool
	// Define a target agent (could be LlmAgent or custom BaseAgent)
	imageAgent, _ := agent.New(agent.Config{
		Name:        "ImageGen",
		Description: "Generates an image based on a prompt.",
		// ... internal logic ...
	})

	imageTool, _ := tool.NewAgentTool(imageAgent) // Wrap the agent

	// Parent agent uses the AgentTool
	artistAgent, _ := llmagent.New(llmagent.Config{
		Name:        "Artist",
		Model:       model,
		Instruction: "Create a prompt and use the ImageGen tool to generate the image.",
		Tools:       []tool.Tool{imageTool}, // Include the AgentTool
	})
	// Artist LLM generates a prompt, then calls:
	// FunctionCall{Name: "ImageGen", Args: map[string]any{"image_prompt": "a cat wearing a hat"}}
	// Framework calls imageTool.Run(...), which runs ImageGeneratorAgent.
	// The resulting image Part is returned to the Artist agent as the tool result.
	// --8<-- [end:agent-as-tool]
	_ = artistAgent // Avoid unused variable error

	// --8<-- [start:coordinator-pattern]
	// Conceptual Code: Coordinator using LLM Transfer
	billingAgent2, _ := llmagent.New(llmagent.Config{Name: "Billing", Description: "Handles billing inquiries.", Model: model})
	supportAgent2, _ := llmagent.New(llmagent.Config{Name: "Support", Description: "Handles technical support requests.", Model: model})

	coordinator3, _ := llmagent.New(llmagent.Config{
		Name:        "HelpDeskCoordinator",
		Model:       model,
		Instruction: "Route user requests: Use Billing agent for payment issues, Support agent for technical problems.",
		Description: "Main help desk router.",
		SubAgents:   []agent.Agent{billingAgent2, supportAgent2},
	})
	// User asks "My payment failed" -> Coordinator's LLM should call transfer_to_agent(agent_name='Billing')
	// User asks "I can't log in" -> Coordinator's LLM should call transfer_to_agent(agent_name='Support')
	// --8<-- [end:coordinator-pattern]
	_ = coordinator3 // Avoid unused variable error

	// --8<-- [start:sequential-pipeline-pattern]
	// Conceptual Code: Sequential Data Pipeline
	validator, _ := llmagent.New(llmagent.Config{Name: "ValidateInput", Instruction: "Validate the input.", OutputKey: "validation_status", Model: model})
	processor, _ := llmagent.New(llmagent.Config{Name: "ProcessData", Instruction: "Process data if {validation_status} is 'valid'.", OutputKey: "result", Model: model})
	reporter, _ := llmagent.New(llmagent.Config{Name: "ReportResult", Instruction: "Report the result from {result}.", Model: model})

	dataPipeline, _ := sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{Name: "DataPipeline", SubAgents: []agent.Agent{validator, processor, reporter}},
	})
	// validator runs -> saves to state["validation_status"]
	// processor runs -> reads state["validation_status"], saves to state["result"]
	// reporter runs -> reads state["result"]
	// --8<-- [end:sequential-pipeline-pattern]
	_ = dataPipeline // Avoid unused variable error

	// --8<-- [start:parallel-gather-pattern]
	// Conceptual Code: Parallel Information Gathering
	fetchAPI1, _ := llmagent.New(llmagent.Config{Name: "API1Fetcher", Instruction: "Fetch data from API 1.", OutputKey: "api1_data", Model: model})
	fetchAPI2, _ := llmagent.New(llmagent.Config{Name: "API2Fetcher", Instruction: "Fetch data from API 2.", OutputKey: "api2_data", Model: model})

	gatherConcurrently, _ := parallelagent.New(parallelagent.Config{
		AgentConfig: agent.Config{Name: "ConcurrentFetch", SubAgents: []agent.Agent{fetchAPI1, fetchAPI2}},
	})

	synthesizer, _ := llmagent.New(llmagent.Config{Name: "Synthesizer", Instruction: "Combine results from {api1_data} and {api2_data}.", Model: model})

	overallWorkflow, _ := sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{Name: "FetchAndSynthesize", SubAgents: []agent.Agent{gatherConcurrently, synthesizer}},
	})
	// fetch_api1 and fetch_api2 run concurrently, saving to state.
	// synthesizer runs afterwards, reading state["api1_data"] and state["api2_data"].
	// --8<-- [end:parallel-gather-pattern]
	_ = overallWorkflow // Avoid unused variable error

	// --8<-- [start:hierarchical-pattern]
	// Conceptual Code: Hierarchical Research Task
	// Low-level tool-like agents
	webSearcher, _ := llmagent.New(llmagent.Config{Name: "WebSearch", Description: "Performs web searches for facts.", Model: model})
	summarizer, _ := llmagent.New(llmagent.Config{Name: "Summarizer", Description: "Summarizes text.", Model: model})

	// Mid-level agent combining tools
	webSearcherTool, _ := tool.NewAgentTool(webSearcher)
	summarizerTool, _ := tool.NewAgentTool(summarizer)
	researchAssistant, _ := llmagent.New(llmagent.Config{
		Name:        "ResearchAssistant",
		Model:       model,
		Description: "Finds and summarizes information on a topic.",
		Tools:       []tool.Tool{webSearcherTool, summarizerTool},
	})

	// High-level agent delegating research
	researchAssistantTool, _ := tool.NewAgentTool(researchAssistant)
	reportWriter, _ := llmagent.New(llmagent.Config{
		Name:        "ReportWriter",
		Model:       model,
		Instruction: "Write a report on topic X. Use the ResearchAssistant to gather information.",
		Tools:       []tool.Tool{researchAssistantTool},
	})
	// User interacts with ReportWriter.
	// ReportWriter calls ResearchAssistant tool.
	// ResearchAssistant calls WebSearch and Summarizer tools.
	// Results flow back up.
	// --8<-- [end:hierarchical-pattern]
	_ = reportWriter // Avoid unused variable error

	// --8<-- [start:generator-critic-pattern]
	// Conceptual Code: Generator-Critic
	generator, _ := llmagent.New(llmagent.Config{
		Name:        "DraftWriter",
		Instruction: "Write a short paragraph about subject X.",
		OutputKey:   "draft_text",
		Model:       model,
	})

	reviewer, _ := llmagent.New(llmagent.Config{
		Name:        "FactChecker",
		Instruction: "Review the text in {draft_text} for factual accuracy. Output 'valid' or 'invalid' with reasons.",
		OutputKey:   "review_status",
		Model:       model,
	})

	reviewPipeline, _ := sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{Name: "WriteAndReview", SubAgents: []agent.Agent{generator, reviewer}},
	})
	// generator runs -> saves draft to state["draft_text"]
	// reviewer runs -> reads state["draft_text"], saves status to state["review_status"]
	// --8<-- [end:generator-critic-pattern]
	_ = reviewPipeline // Avoid unused variable error

	// --8<-- [start:iterative-refinement-pattern]
	// Conceptual Code: Iterative Code Refinement
	codeRefiner, _ := llmagent.New(llmagent.Config{
		Name:        "CodeRefiner",
		Instruction: "Read state['current_code'] (if exists) and state['requirements']. Generate/refine Python code to meet requirements. Save to state['current_code'].",
		OutputKey:   "current_code",
		Model:       model,
	})

	qualityChecker, _ := llmagent.New(llmagent.Config{
		Name:        "QualityChecker",
		Instruction: "Evaluate the code in state['current_code'] against state['requirements']. Output 'pass' or 'fail'.",
		OutputKey:   "quality_status",
		Model:       model,
	})

	checkStatusAndEscalate, _ := agent.New(agent.Config{
		Name: "StopChecker",
		Run: func(ctx agent.Context) iter.Seq2[*session.Event, error] {
			return func(yield func(*session.Event, error) bool) {
				status, _ := ctx.Session().State().Get("quality_status")
				shouldStop := status == "pass"
				yield(&session.Event{Author: "StopChecker", Actions: &session.EventActions{Escalate: shouldStop}}, nil)
			}
		},
	})

	refinementLoop, _ := loopagent.New(loopagent.Config{
		MaxIterations: 5,
		AgentConfig:   agent.Config{Name: "CodeRefinementLoop", SubAgents: []agent.Agent{codeRefiner, qualityChecker, checkStatusAndEscalate}},
	})
	// Loop runs: Refiner -> Checker -> StopChecker
	// State["current_code"] is updated each iteration.
	// Loop stops if QualityChecker outputs 'pass' (leading to StopChecker escalating) or after 5 iterations.
	// --8<-- [end:iterative-refinement-pattern]
	_ = refinementLoop // Avoid unused variable error

	// --8<-- [start:human-in-loop-pattern]
	// Conceptual Code: Using a Tool for Human Approval
	// --- Assume externalApprovalTool exists ---
	// func externalApprovalTool(amount float64, reason string) string { ... }
	var externalApprovalTool func(amount float64, reason string) string
	approvalTool, _ := tool.NewFunctionTool(
		tool.FunctionToolConfig{
			Name:        "external_approval_tool",
			Description: "Sends a request for human approval.",
		},
		externalApprovalTool,
	)

	prepareRequest, _ := llmagent.New(llmagent.Config{
		Name:        "PrepareApproval",
		Instruction: "Prepare the approval request details based on user input. Store amount and reason in state.",
		Model:       model,
	})

	requestApproval, _ := llmagent.New(llmagent.Config{
		Name:        "RequestHumanApproval",
		Instruction: "Use the external_approval_tool with amount from state['approval_amount'] and reason from state['approval_reason'].",
		Tools:       []tool.Tool{approvalTool},
		OutputKey:   "human_decision",
		Model:       model,
	})

	processDecision, _ := llmagent.New(llmagent.Config{
		Name:        "ProcessDecision",
		Instruction: "Check {human_decision}. If 'approved', proceed. If 'rejected', inform user.",
		Model:       model,
	})

	approvalWorkflow, _ := sequentialagent.New(sequentialagent.Config{
		AgentConfig: agent.Config{Name: "HumanApprovalWorkflow", SubAgents: []agent.Agent{prepareRequest, requestApproval, processDecision}},
	})
	// --8<-- [end:human-in-loop-pattern]
	_ = approvalWorkflow // Avoid unused variable error
}