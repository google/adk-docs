# ADK Visual Agent Builder

The ADK Visual Agent Builder is a powerful web-based tool that provides a visual workflow designer for creating and managing agents. It simplifies the agent development process by allowing you to design, build, and test your agents in a user-friendly graphical interface.

## Core Features

### Visual Workflow Designer

The heart of the Visual Agent Builder is its intuitive drag-and-drop workflow designer. You can visually construct complex agent behaviors by connecting different types of agent nodes, defining their properties, and establishing the flow of control.

### Support for Multiple Agent Types

The Visual Agent Builder supports a variety of agent types, enabling you to build sophisticated multi-agent systems:

*   **LLM Agent:** An agent powered by a Large Language Model.
*   **Sequential Agent:** An agent that executes a series of sub-agents in a sequence.
*   **Parallel Agent:** An agent that executes multiple sub-agents concurrently.
*   **Loop Agent:** An agent that repeatedly executes a sub-agent until a certain condition is met.
*   **Workflow Agent:** A flexible agent that allows you to define custom, complex workflows.

### Agent Tool Support

Integrate tools into your agents to extend their capabilities. The Visual Agent Builder supports:

*   **Nested Agent Tools:** Use other agents as tools within your agent, allowing for modular and reusable designs.
*   **Built-in and Custom Tools:** Leverage a rich set of built-in tools or create your own custom tools to connect to external services and APIs.

### Callback Management

Define and manage callbacks to instrument your agent's behavior. You can set up callbacks to trigger at different points in the agent's lifecycle, such as before or after an agent runs, a model is called, or a tool is executed.

### Assistant for Building Agents

The Visual Agent Builder includes an assistant that helps you build agents using natural language. Simply describe the agent you want to create, and the assistant will generate the corresponding workflow for you.

### Chat Interface for Testing

Test your agents in real-time using the built-in chat interface. You can interact with your agent, inspect its responses, and debug its behavior without leaving the Visual Agent Builder.

### Real-time Building and Debugging

The Visual Agent Builder is integrated with the `adk web` command, allowing you to build and debug your agents in real-time. Any changes you make in the visual designer are immediately reflected in the running agent, providing a seamless development experience.
