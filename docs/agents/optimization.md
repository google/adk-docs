---
title: Agent Optimization
---

The `google.adk.optimization` module provides a framework for optimizing your agents. This allows you to iteratively improve your agent's performance based on defined metrics.

## AgentOptimizer

The `AgentOptimizer` is an abstract base class that serves as the foundation for all optimizers. To create your own optimizer, you need to subclass `AgentOptimizer` and implement the `optimize` method.

```python
class AgentOptimizer(ABC, Generic[SamplingResult, AgentWithScores]):
  """Base class for agent optimizers."""

  @abstractmethod
  async def optimize(
      self,
      initial_agent: Agent,
      sampler: Sampler[SamplingResult],
  ) -> OptimizerResult[AgentWithScores]:
    """Runs the optimizer.

    Args:
      initial_agent: The initial agent to be optimized.
      sampler: The interface used to get training and validation example UIDs,
        request agent evaluations, and get useful data for optimizing the agent.

    Returns:
      The final result of the optimization process, containing the optimized
      agent instances along with their corresponding scores on the validation
      examples and any optimization metadata.
    """
```

The `optimize` method takes an initial agent and a sampler as input and returns an `OptimizerResult` containing the optimized agents and their scores.

## Sampler

The `Sampler` is an interface that defines how to sample training and validation data and how to score candidate agents. You must implement this interface for your evaluation service to work with the optimizer.

```python
class Sampler(ABC, Generic[SamplingResult]):
  """Base class for agent optimizers to sample and score candidate agents.

  The developer must implement this interface for their evaluation service to
  work with the optimizer. The optimizer will call the sample_and_score method
  to get evaluation results for the candidate agent on the batch of examples.
  """

  @abstractmethod
  def get_train_example_ids(self) -> list[str]:
    """Returns the UIDs of examples to use for training the agent."""
    ...

  @abstractmethod
  def get_validation_example_ids(self) -> list[str]:
    """Returns the UIDs of examples to use for validating the optimized agent."""
    ...

  @abstractmethod
  async def sample_and_score(
      self,
      candidate: Agent,
      example_set: Literal["train", "validation"] = "validation",
      batch: Optional[list[str]] = None,
      capture_full_eval_data: bool = False,
  ) -> SamplingResult:
    """Evaluates the candidate agent on the batch of examples.

    Args:
      candidate: The candidate agent to be evaluated.
      example_set: The set of examples to evaluate the candidate agent on.
        Possible values are "train" and "validation".
      batch: List of UIDs of examples to evaluate the candidate agent on. If not
        provided, all examples from the chosen set will be used.
      capture_full_eval_data: If false, it is enough to only calculate the
        scores for each example. If true, this method should also capture all
        other data required for optimizing the agent (e.g., outputs,
        trajectories, and tool calls).

    Returns:
      The evaluation results, containing the scores for each example and (if
      requested) other data required for optimization.
    """
```

## Data Types

The `google.adk.optimization.data_types` module defines the following data types:

*   **`AgentWithScores`**: Represents an optimized agent and its scores.
*   **`OptimizerResult`**: Represents the final result of the optimization process. It contains a list of `AgentWithScores` that are on the Pareto front, meaning they cannot be considered strictly better than one another.
*   **`SamplingResult`**: Represents the evaluation results for a batch of examples. It includes per-example scores and may also contain other data required for optimizing the agent, such as outputs, trajectories, and metrics.

## How to Implement a Custom Optimizer and Sampler

1.  **Implement the `Sampler` interface**:
    *   Create a class that inherits from `google.adk.optimization.Sampler`.
    *   Implement the `get_train_example_ids`, `get_validation_example_ids`, and `sample_and_score` methods.
2.  **Implement the `AgentOptimizer` class**:
    *   Create a class that inherits from `google.adk.optimization.AgentOptimizer`.
    *   Implement the `optimize` method. This method should use the provided `Sampler` to evaluate and improve the agent.
3.  **Run the optimization**:
    *   Instantiate your custom optimizer and sampler.
    *   Create an initial agent.
    *   Call the `optimize` method of your optimizer with the initial agent and sampler.
