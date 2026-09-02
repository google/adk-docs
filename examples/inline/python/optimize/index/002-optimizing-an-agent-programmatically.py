import asyncio
import logging
import os

import agent  # the hello_world agent
from google.adk.cli.utils import envs
from google.adk.cli.utils import logs
from google.adk.evaluation.eval_config import EvalConfig
from google.adk.evaluation.local_eval_sets_manager import LocalEvalSetsManager
from google.adk.optimization.gepa_root_agent_prompt_optimizer import GEPARootAgentPromptOptimizer
from google.adk.optimization.gepa_root_agent_prompt_optimizer import GEPARootAgentPromptOptimizerConfig
from google.adk.optimization.local_eval_sampler import LocalEvalSampler
from google.adk.optimization.local_eval_sampler import LocalEvalSamplerConfig

# setup environment variables (API keys, etc.) and logging
envs.load_dotenv_for_agent(".", ".")
logs.setup_adk_logger(logging.INFO)

# create the sampler
sampler_config = LocalEvalSamplerConfig(
    eval_config=EvalConfig(criteria={"response_match_score": 0.75}),
    app_name="hello_world",  # typically the name of the directory containing the agent
    train_eval_set="train_eval_set",  # from the example
)
eval_sets_manager = LocalEvalSetsManager(
    agents_dir=os.path.dirname(os.getcwd()),
)
sampler = LocalEvalSampler(sampler_config, eval_sets_manager)

# create the optimizer
opt_config = GEPARootAgentPromptOptimizerConfig()
optimizer = GEPARootAgentPromptOptimizer(config=opt_config)

# optimize the root agent
initial_agent = agent.root_agent
result = asyncio.run(
    optimizer.optimize(initial_agent, sampler)
)

# show the results
best_idx = result.gepa_result["best_idx"]
print(
    "Validation score:",
    result.optimized_agents[best_idx].overall_score,
    "Optimized prompt:",
    result.optimized_agents[best_idx].optimized_agent.instruction,
    "GEPA metrics:",
    result.gepa_result,
    sep="\n",
)