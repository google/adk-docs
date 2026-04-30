# Prompt Optimization

The Simple Prompt Optimizer is a feature that helps you iteratively improve your agent's system prompts using a large language model (LLM).

## How it works

The optimizer uses an optimizer LLM (default `gemini-1.5-flash`) to critique and rewrite the prompt based on evaluation scores. It works as follows:

1.  **Evaluates the initial prompt**: The optimizer first evaluates the agent with the initial prompt to get a baseline score.
2.  **Generates a new prompt**: It then uses the optimizer LLM to generate a new, improved prompt.
3.  **Evaluates the new prompt**: The optimizer evaluates the agent with the new prompt.
4.  **Compares and updates**: If the new prompt results in a better score, it replaces the old prompt with the new one.
5.  **Repeats**: The optimizer repeats this process for a set number of iterations.

## Usage

To use the Simple Prompt Optimizer, you need to:

1.  Define an `Agent` and a `Sampler` (for evaluation).
2.  Configure the `SimplePromptOptimizerConfig`.
3.  Run the optimizer's `optimize` method.

```python
from google.adk.agents import Agent
from google.adk.optimization import SimplePromptOptimizer, SimplePromptOptimizerConfig
from google.adk.optimization import Sampler

# 1. Define an Agent and a Sampler
my_agent = Agent(
    instruction="You are a helpful assistant.",
    ...
)

my_sampler = Sampler(...)

# 2. Configure SimplePromptOptimizerConfig
optimizer_config = SimplePromptOptimizerConfig(
    num_iterations=10,
    batch_size=5,
)

# 3. Run the optimizer
optimizer = SimplePromptOptimizer(config=optimizer_config)
optimization_result = await optimizer.optimize(
    initial_agent=my_agent,
    sampler=my_sampler,
)

best_agent = optimization_result.optimized_agents[0].optimized_agent
```

## Key Classes

*   **`SimplePromptOptimizer`**: The main class that runs the optimization process.
*   **`SimplePromptOptimizerConfig`**: A data class for configuring the optimizer, including the number of iterations and the batch size for evaluation.
