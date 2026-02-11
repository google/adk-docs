# Skills Framework

Skills are modular packages of instructions and resources that agents can load on demand. They provide a structured way to build and manage agent capabilities, making it easier to develop, maintain, and share reusable components.

## Concept

The Skills Framework allows you to define self-contained units of functionality that an agent can use to perform specific tasks. By loading skills on demand, agents can optimize their context window by only loading the instructions and resources they need for the current task.

## Structure

Each skill is organized into three levels:

*   **L1 (Metadata)**: The `SKILL.md` file contains frontmatter with metadata for skill discovery. This includes the skill's name, description, and other relevant information.
*   **L2 (Instructions)**: The body of the `SKILL.md` file contains the primary instructions for the skill. These instructions are loaded when the skill is triggered.
*   **L3 (Resources)**: The `references/`, `assets/`, and `scripts/` directories contain additional resources that the skill can load as needed. These can include additional instructions, data files, or executable scripts.

## Usage

### Defining a Skill

You can define a skill using the `Skill` model, which includes the following attributes:

*   `frontmatter`: Metadata for the skill (L1).
*   `instructions`: The primary instructions for the skill (L2).
*   `resources`: Additional resources for the skill (L3).

### Exposing Skills to an Agent

The `SkillToolset` class allows you to expose a collection of skills to an agent. The toolset automatically generates the following tools for the agent:

*   `load_skill(skill_name)`: Loads the L2 instructions for the specified skill into the agent's context.
*   `load_skill_resource(skill_name, resource_type, resource_id)`: Loads an L3 resource (e.g., a reference, asset, or script) into the agent's context.

By using the `SkillToolset`, you can provide agents with a flexible and efficient way to access the capabilities they need to perform their tasks.

## Benefits

The Skills Framework offers several benefits:

*   **Modular Design**: Skills are self-contained and reusable, making it easier to manage and share agent capabilities.
*   **Context Window Optimization**: By loading instructions and resources only when needed, agents can make more efficient use of their context window.
*   **Improved Development Workflow**: The structured organization of skills simplifies the development and maintenance of agent functionality.