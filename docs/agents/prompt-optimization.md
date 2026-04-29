---
title: Simple Prompt Optimizer
---

The Simple Prompt Optimizer is a tool that helps you iteratively improve the system prompt of an agent.

## How it works

The optimizer uses a large language model (LLM), by default `gemini-1.5-flash`, to critique and rewrite the agent's prompt. This process is guided by evaluation scores from a `Sampler` that you provide. The optimizer runs for a specified number of iterations, and in each iteration, it generates a new prompt, evaluates it, and retains the version that performs the best.

## Usage

To use the `SimplePromptOptimizer`, you need to:

1.  Define an `Agent` and a `Sampler`. The `Sampler` is used for evaluation and should contain your evaluation dataset.
2.  Configure the `SimplePromptOptimizerConfig` with the desired number of iterations (`num_iterations`) and batch size (`batch_size`).
3.  Instantiate the `SimplePromptOptimizer` with the configuration.
4.  Call the `optimize()` method with your agent and sampler.

Here is an example of how to use the `SimplePromptOptimizer`:

```python
from google.adk.agents import Agent
from google.adk.optimization import SimplePromptOptimizer, SimplePromptOptimizerConfig
from google.adk.optimization import Sampler

# 1. Define an Agent and a Sampler
my_agent = Agent(
    instruction="You are a helpful assistant.",
    # ... other agent configuration
)

my_sampler = Sampler(
    # ... sampler configuration
)

# 2. Configure the SimplePromptOptimizer
optimizer_config = SimplePromptOptimizerConfig(
    num_iterations=10,
    batch_size=5,
)

# 3. Instantiate the optimizer
optimizer = SimplePromptOptimizer(config=optimizer_config)

# 4. Run the optimization
optimizer_result = await optimizer.optimize(
    initial_agent=my_agent,
    sampler=my_sampler,
)

# The best performing agent is available in the result
best_agent = optimizer_result.optimized_agents[0].optimized_agent
```

## Key Classes

*   `SimplePromptOptimizer`: The main class that runs the optimization loop.
*   `SimplePromptOptimizerConfig`: The configuration class for the `SimplePromptOptimizer`, allowing you to set the number of iterations, batch size, and the optimizer model.
