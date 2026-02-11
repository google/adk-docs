# Skills Framework

The Skills Framework allows you to create modular packages of instructions and resources that agents can load on demand. This approach helps you organize your agent's capabilities and optimize the context window by only loading instructions when they are needed.

## Concept

A skill is a self-contained unit of functionality that an agent can use to perform a specific task. It encapsulates the necessary instructions, resources, and tools required for that task. By breaking down an agent's abilities into skills, you can create a more modular and maintainable agent architecture.

## Structure

The Skills Framework is organized into three levels:

-   **L1 (Metadata):** Provides metadata for skill discovery. This is defined in the frontmatter of the `SKILL.md` file and includes properties like the skill's name and description.
-   **L2 (Instructions):** Contains the primary instructions for the skill, loaded when the skill is triggered. This is the body of the `SKILL.md` file.
-   **L3 (Resources):** Includes additional resources such as reference materials, assets, and scripts that can be loaded as needed. These resources are organized into the following directories:
    -   `references/`: Additional Markdown files with extended instructions, workflows, or guidance.
    -   `assets/`: Resource materials like database schemas, API documentation, templates, or examples.
    -   `scripts/`: Executable scripts that can be run via `bash`.

## Usage

### Defining a Skill

You define a skill using the `Skill` model, which combines the L1, L2, and L3 content. The `SKIL.md` file is the core of a skill's definition.

**Example `SKILL.md`:**

```markdown
---
name: code-generator
description: A skill that generates code in a specified language.
---

You are a code generation expert. When asked to generate code, follow the best practices for the specified language.
```

### Exposing Skills to an Agent

You can expose skills to an agent using the `SkillToolset`. The `SkillToolset` provides tools for loading skills and their resources.

### Loading Skills and Resources

The `SkillToolset` includes the following tools:

-   **`load_skill`:** Loads the L2 instructions for a specified skill into the context.
-   **`load_skill_resource`:** Loads an L3 resource (reference, asset, or script) into the context.

## Benefits

-   **Modular Design:** Skills promote a modular design, making it easier to manage and reuse agent capabilities.
-   **Context Window Optimization:** By loading instructions and resources only when needed, you can significantly optimize the context window, allowing for more complex and capable agents.
