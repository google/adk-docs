# Agent Optimization

The `google.adk.optimization` module provides a framework for optimizing your agents. This allows you to iteratively improve your agent's performance based on a set of training and validation examples.

## Key Concepts

The agent optimization framework consists of three main components:

-   **Agent Optimizer**: A class that implements the optimization logic.
-   **Sampler**: A class that provides the data for training and validation.
-   **Data Types**: A set of data structures for passing information between the optimizer and the sampler.

## AgentOptimizer

The `AgentOptimizer` is an abstract base class that defines the interface for all agent optimizers. It has a single abstract method, `optimize`, which takes an initial agent and a sampler as input and returns an `OptimizerResult`.

To create your own optimizer, you need to subclass `AgentOptimizer` and implement the `optimize` method.

## Sampler

The `Sampler` interface is responsible for the following:

-   Providing training and validation example UIDs.
-   Requesting agent evaluations.
-   Providing data for optimizing the agent.

You need to implement a `Sampler` to define your training and validation data and how to score your agent's performance.

## Data Types

The `google.adk.optimization.data_types` module defines the following data types:

-   `AgentWithScores`: An optimized agent with its scores. Optimizers can use the `overall_score` field and can return custom metrics by subclassing this class.
-   `OptimizerResult`: The final result of the optimization process. It contains a list of optimized agents with their scores.
-   `SamplingResult`: Represents the evaluation results of a candidate agent on a batch of examples. It includes per-example scores and can contain other data required for optimizing the agent.

## How to Implement a Custom Optimizer and Sampler

Here's a high-level guide on how to implement your own optimization process:

1.  **Create a `Sampler` class**:
    -   Implement the logic to access your training and validation data.
    -   Implement the `score` method to evaluate your agent's performance on a given example.

2.  **Create an `AgentOptimizer` class**:
    -   Implement the `optimize` method.
    -   In the `optimize` method, use the provided `sampler` to get training data and evaluate your agent's performance.
    -   Implement your optimization logic to generate new and improved agents.
    -   Return an `OptimizerResult` containing the best agent(s) you found.

By implementing these components, you can leverage the ADK's optimization framework to systematically improve your agents.
