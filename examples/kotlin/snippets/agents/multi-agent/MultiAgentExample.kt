package com.google.adk.kt.examples.agents.multiagent

import com.google.adk.kt.agents.BaseAgent
import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.InvocationContext
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.agents.LoopAgent
import com.google.adk.kt.agents.ParallelAgent
import com.google.adk.kt.agents.SequentialAgent
import com.google.adk.kt.events.Event
import com.google.adk.kt.events.EventActions
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.tools.AgentTool
import com.google.adk.kt.tools.BaseTool
import com.google.adk.kt.tools.ToolContext
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.FunctionDeclaration
import com.google.adk.kt.types.Part
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf

// --8<-- [start:custom_agent]
class TaskExecutorAgent : BaseAgent(name = "TaskExecutor") {
    override fun runAsyncImpl(context: InvocationContext): Flow<Event> {
        return flowOf(
            Event(
                author = name,
                content = Content(parts = listOf(Part(text = "Task completed!"))),
            ),
        )
    }
}
// --8<-- [end:custom_agent]

// --8<-- [start:check_condition_agent]
class CheckConditionAgent(name: String) : BaseAgent(name = name) {
    override fun runAsyncImpl(context: InvocationContext): Flow<Event> {
        val status = context.session.state["status"] as? String ?: "pending"
        val isDone = status == "completed"
        return flowOf(
            Event(
                author = name,
                actions = EventActions(escalate = isDone),
            ),
        )
    }
}
// --8<-- [end:check_condition_agent]

// --8<-- [start:human_in_loop_pattern]
class ExternalApprovalTool : BaseTool(
    "external_approval_tool",
    "Sends a request for human approval.",
) {
    override fun declaration(): FunctionDeclaration =
        FunctionDeclaration(
            "external_approval_tool",
            "Sends a request for human approval.",
        )

    override suspend fun run(
        context: ToolContext,
        args: Map<String, Any>,
    ): Any {
        // Simulate calling external system (e.g., UI, ticketing system)
        // In a real app, this might poll for a result or wait for a webhook.
        return mapOf("decision" to "approved")
    }
}
// --8<-- [end:human_in_loop_pattern]

fun main() {
    val model = Gemini(name = "gemini-flash-latest")

    // --8<-- [start:hierarchy]
    val greeter = LlmAgent(name = "Greeter", model = model)
    val taskDoer = TaskExecutorAgent()

    val coordinator =
        LlmAgent(
            name = "Coordinator",
            model = model,
            description = "I coordinate greetings and tasks.",
            subAgents = listOf(greeter, taskDoer),
        )
    // --8<-- [end:hierarchy]

    // --8<-- [start:sequential_pipeline]
    val step1 = LlmAgent(name = "Step1_Fetch", model = model)
    val step2 =
        LlmAgent(
            name = "Step2_Process",
            model = model,
            instruction = Instruction("Process data from state."),
        )

    val pipeline = SequentialAgent(name = "MyPipeline", subAgents = listOf(step1, step2))
    // --8<-- [end:sequential_pipeline]

    // --8<-- [start:parallel_execution]
    val fetchWeather = LlmAgent(name = "WeatherFetcher", model = model)
    val fetchNews = LlmAgent(name = "NewsFetcher", model = model)

    val gatherer = ParallelAgent(name = "InfoGatherer", subAgents = listOf(fetchWeather, fetchNews))
    // --8<-- [end:parallel_execution]

    // --8<-- [start:loop_with_condition]
    val processStep = LlmAgent(name = "ProcessingStep", model = model)
    val checker = CheckConditionAgent(name = "Checker")

    val poller =
        LoopAgent(
            name = "StatusPoller",
            maxIterations = 10,
            subAgents = listOf(processStep, checker),
        )
    // --8<-- [end:loop_with_condition]

    // --8<-- [start:output_key_state]
    val agentA =
        LlmAgent(
            name = "AgentA",
            model = model,
            instruction = Instruction("Find the capital of France."),
        )
    val agentB =
        LlmAgent(
            name = "AgentB",
            model = model,
            instruction = Instruction("Tell me about the city stored in state."),
        )

    val cityPipeline = SequentialAgent(name = "CityInfo", subAgents = listOf(agentA, agentB))
    // --8<-- [end:output_key_state]

    // --8<-- [start:llm_transfer]
    val bookingAgent =
        LlmAgent(
            name = "Booker",
            model = model,
            description = "Handles flight and hotel bookings.",
        )
    val infoAgent =
        LlmAgent(
            name = "Info",
            model = model,
            description = "Provides general information and answers questions.",
        )

    val transferCoordinator =
        LlmAgent(
            name = "Coordinator",
            model = model,
            instruction =
                Instruction(
                    "You are an assistant. Delegate booking tasks to Booker and info requests to Info.",
                ),
            description = "Main coordinator.",
            subAgents = listOf(bookingAgent, infoAgent),
        )
    // --8<-- [end:llm_transfer]

    // --8<-- [start:agent_as_tool]
    val imageAgent =
        LlmAgent(
            name = "ImageGen",
            model = model,
            description = "Generates an image based on a prompt.",
        )
    val imageTool = AgentTool(agent = imageAgent)

    val artistAgent =
        LlmAgent(
            name = "Artist",
            model = model,
            instruction =
                Instruction(
                    "Create a prompt and use the ImageGen tool to generate the image.",
                ),
            tools = listOf(imageTool),
        )
    // --8<-- [end:agent_as_tool]

    // --8<-- [start:coordinator_pattern]
    val billingAgent =
        LlmAgent(name = "Billing", model = model, description = "Handles billing inquiries.")
    val supportAgent =
        LlmAgent(
            name = "Support",
            model = model,
            description = "Handles technical support requests.",
        )

    val helpDesk =
        LlmAgent(
            name = "HelpDeskCoordinator",
            model = model,
            instruction =
                Instruction(
                    "Route user requests: Use Billing agent for payment issues, Support agent for technical problems.",
                ),
            description = "Main help desk router.",
            subAgents = listOf(billingAgent, supportAgent),
        )
    // --8<-- [end:coordinator_pattern]

    // --8<-- [start:sequential_pipeline_pattern]
    val validator =
        LlmAgent(
            name = "ValidateInput",
            model = model,
            instruction = Instruction("Validate the input."),
        )
    val processor =
        LlmAgent(
            name = "ProcessData",
            model = model,
            instruction = Instruction("Process data if validation is successful."),
        )
    val reporter =
        LlmAgent(
            name = "ReportResult",
            model = model,
            instruction = Instruction("Report the result."),
        )

    val dataPipeline =
        SequentialAgent(
            name = "DataPipeline",
            subAgents = listOf(validator, processor, reporter),
        )
    // --8<-- [end:sequential_pipeline_pattern]

    // --8<-- [start:parallel_gather_pattern]
    val fetchApi1 =
        LlmAgent(
            name = "API1Fetcher",
            model = model,
            instruction = Instruction("Fetch data from API 1."),
        )
    val fetchApi2 =
        LlmAgent(
            name = "API2Fetcher",
            model = model,
            instruction = Instruction("Fetch data from API 2."),
        )

    val gatherConcurrently =
        ParallelAgent(
            name = "ConcurrentFetch",
            subAgents = listOf(fetchApi1, fetchApi2),
        )

    val synthesizer =
        LlmAgent(
            name = "Synthesizer",
            model = model,
            instruction = Instruction("Combine results from state."),
        )

    val overallWorkflow =
        SequentialAgent(
            name = "FetchAndSynthesize",
            subAgents = listOf(gatherConcurrently, synthesizer),
        )
    // --8<-- [end:parallel_gather_pattern]

    // --8<-- [start:hierarchical_pattern]
    val webSearcher =
        LlmAgent(
            name = "WebSearch",
            model = model,
            description = "Performs web searches for facts.",
        )
    val summarizer = LlmAgent(name = "Summarizer", model = model, description = "Summarizes text.")

    val researchAssistant =
        LlmAgent(
            name = "ResearchAssistant",
            model = model,
            description = "Finds and summarizes information on a topic.",
            subAgents = listOf(webSearcher, summarizer),
        )

    val reportWriter =
        LlmAgent(
            name = "ReportWriter",
            model = model,
            instruction =
                Instruction(
                    "Write a report on topic X. Use the ResearchAssistant to gather information.",
                ),
            subAgents = listOf(researchAssistant),
        )
    // --8<-- [end:hierarchical_pattern]

    // --8<-- [start:generator_critic_pattern]
    val generator =
        LlmAgent(
            name = "DraftWriter",
            model = model,
            instruction = Instruction("Write a short paragraph about subject X."),
        )

    val reviewer =
        LlmAgent(
            name = "FactChecker",
            model = model,
            instruction =
                Instruction(
                    "Review the generated text for factual accuracy. Output 'valid' or 'invalid' with reasons.",
                ),
        )

    val reviewPipeline =
        SequentialAgent(
            name = "WriteAndReview",
            subAgents = listOf(generator, reviewer),
        )
    // --8<-- [end:generator_critic_pattern]

    // --8<-- [start:iterative_refinement_pattern]
    val codeRefiner =
        LlmAgent(
            name = "CodeRefiner",
            model = model,
            instruction =
                Instruction(
                    "Read current code (if exists) and requirements from state. Generate/refine Kotlin code to meet requirements.",
                ),
        )

    val qualityChecker =
        LlmAgent(
            name = "QualityChecker",
            model = model,
            instruction =
                Instruction(
                    "Evaluate the code in state against requirements. Output 'pass' or 'fail'.",
                ),
        )

    val stopChecker = CheckConditionAgent(name = "StopChecker") // Checks quality_status

    val refinementLoop =
        LoopAgent(
            name = "CodeRefinementLoop",
            maxIterations = 5,
            subAgents = listOf(codeRefiner, qualityChecker, stopChecker),
        )
    // --8<-- [end:iterative_refinement_pattern]

    // --8<-- [start:human_in_loop_pattern]
    val approvalTool = ExternalApprovalTool()

    val prepareRequest =
        LlmAgent(
            name = "PrepareApproval",
            model = model,
            instruction =
                Instruction(
                    "Prepare the approval request details based on user input. Store amount and reason in state.",
                ),
        )

    val requestApproval =
        LlmAgent(
            name = "RequestHumanApproval",
            model = model,
            instruction =
                Instruction(
                    "Use the external_approval_tool to get approval for the request in state.",
                ),
            tools = listOf(approvalTool),
        )

    val processDecision =
        LlmAgent(
            name = "ProcessDecision",
            model = model,
            instruction =
                Instruction(
                    "Check the human decision in state. If 'approved', proceed. If 'rejected', inform user.",
                ),
        )

    val approvalWorkflow =
        SequentialAgent(
            name = "HumanApprovalWorkflow",
            subAgents = listOf(prepareRequest, requestApproval, processDecision),
        )
    // --8<-- [end:human_in_loop_pattern]
}
