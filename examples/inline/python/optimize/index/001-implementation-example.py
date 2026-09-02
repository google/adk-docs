from google.adk.optimization.simple_prompt_optimizer import SimplePromptOptimizer
from google.adk.optimization.simple_prompt_optimizer import SimplePromptOptimizerConfig

# Define your Agent and Sampler first...

# Configure the optimizer
config = SimplePromptOptimizerConfig(
    num_iterations=5,
    batch_size=10
)

# Run optimization
optimizer = SimplePromptOptimizer(config=config)
optimized_result = await optimizer.optimize(agent, sampler)