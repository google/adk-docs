# Agent Optimization

The ADK includes tools to optimize your agent's instructions automatically using the Generative Prompt Optimization (GEPA) technique.

## CLI Command

You can run the optimizer using the `adk optimize` command:

```bash
adk optimize AGENT_MODULE_FILE_PATH --sampler_config_file_path=SAMPLER_CONFIG [options]
```

### Arguments

*   `AGENT_MODULE_FILE_PATH`: Path to the agent's module file (e.g., `my_agent/__init__.py`). The module must expose a `root_agent`.
*   `--sampler_config_file_path`: Path to the configuration file for `LocalEvalSampler`. This config defines the evaluation sets used for training and validation.
*   `--optimizer_config_file_path`: (Optional) Path to the configuration file for `GEPARootAgentPromptOptimizer`.
*   `--print_detailed_results`: (Optional) Flag to print detailed optimization metrics.

## Configuration

### Sampler Config (`LocalEvalSamplerConfig`)

Defined in a JSON file, typically containing:
*   `app_name`: Name of the application.
*   `eval_set_ids`: List of evaluation set IDs to use.

### Optimizer Config (`GEPARootAgentPromptOptimizerConfig`)

Defined in a JSON file, controls parameters like:
*   Number of optimization rounds.
*   Batch size.
*   LLM to use for optimization.
