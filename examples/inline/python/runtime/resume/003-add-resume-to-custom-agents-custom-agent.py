class WorkflowStep(int, Enum):
 INITIAL_STORY_GENERATION = 1
 CRITIC_REVISER_LOOP = 2
 POST_PROCESSING = 3
 CONDITIONAL_REGENERATION = 4

# Extend BaseAgentState

class StoryFlowAgentState(BaseAgentState):
  step: WorkflowStep

# In the StoryFlowAgent class, replace the existing run implementation with:

@override
async def _run_async_impl(
    self, ctx: InvocationContext
) -> AsyncGenerator[Event, None]:
    """
    Implements the custom orchestration logic for the story workflow.
    Uses the instance attributes assigned by Pydantic (e.g., self.story_generator).
    """
    agent_state = self._load_agent_state(ctx, StoryFlowAgentState)

    if agent_state is None:
      # Record the start of the agent
      agent_state = StoryFlowAgentState(step=WorkflowStep.INITIAL_STORY_GENERATION)
      ctx.set_agent_state(self.name, agent_state=agent_state)
      yield self._create_agent_state_event(ctx)

    next_step = agent_state.step
    logger.info(f"[{self.name}] Starting story generation workflow.")

    # Step 1. Initial Story Generation
    if next_step <= WorkflowStep.INITIAL_STORY_GENERATION:
      logger.info(f"[{self.name}] Running StoryGenerator...")
      async for event in self.story_generator.run_async(ctx):
          yield event

      # Check if story was generated before proceeding
      if "current_story" not in ctx.session.state or not ctx.session.state[
          "current_story"
      ]:
          return  # Stop processing if initial story failed

    agent_state = StoryFlowAgentState(step=WorkflowStep.CRITIC_REVISER_LOOP)
    ctx.set_agent_state(self.name, agent_state=agent_state)
    yield self._create_agent_state_event(ctx)

    # Step 2. Critic-Reviser Loop
    if next_step <= WorkflowStep.CRITIC_REVISER_LOOP:
      logger.info(f"[{self.name}] Running CriticReviserLoop...")
      async for event in self.loop_agent.run_async(ctx):
          logger.info(
              f"[{self.name}] Event from CriticReviserLoop: "
              f"{event.model_dump_json(indent=2, exclude_none=True)}"
          )
          yield event

    agent_state = StoryFlowAgentState(step=WorkflowStep.POST_PROCESSING)
    ctx.set_agent_state(self.name, agent_state=agent_state)
    yield self._create_agent_state_event(ctx)

    # Step 3. Sequential Post-Processing (Grammar and Tone Check)
    if next_step <= WorkflowStep.POST_PROCESSING:
      logger.info(f"[{self.name}] Running PostProcessing...")
      async for event in self.sequential_agent.run_async(ctx):
          logger.info(
              f"[{self.name}] Event from PostProcessing: "
              f"{event.model_dump_json(indent=2, exclude_none=True)}"
          )
          yield event

    agent_state = StoryFlowAgentState(step=WorkflowStep.CONDITIONAL_REGENERATION)
    ctx.set_agent_state(self.name, agent_state=agent_state)
    yield self._create_agent_state_event(ctx)

    # Step 4. Tone-Based Conditional Logic
    if next_step <= WorkflowStep.CONDITIONAL_REGENERATION:
      tone_check_result = ctx.session.state.get("tone_check_result")
      if tone_check_result == "negative":
          logger.info(f"[{self.name}] Tone is negative. Regenerating story...")
          async for event in self.story_generator.run_async(ctx):
              logger.info(
                  f"[{self.name}] Event from StoryGenerator (Regen): "
                  f"{event.model_dump_json(indent=2, exclude_none=True)}"
              )
              yield event
      else:
          logger.info(f"[{self.name}] Tone is not negative. Keeping current story.")

    logger.info(f"[{self.name}] Workflow finished.")
    ctx.set_agent_state(self.name, end_of_agent=True)
    yield self._create_agent_state_event(ctx)