# Skills for ADK agents

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.25.0</span><span class="lst-typescript">TypeScript v0.6.1</span><span class="lst-go">Go v1.2.0</span><span class="lst-kotlin">Kotlin v0.1.0</span><span class="lst-preview">Experimental</span>
</div>

An agent ***Skill*** is a self-contained unit of functionality that an ADK agent
can use to perform a specific task. An agent Skill encapsulates the necessary
instructions, resources, and tools required for a task, based on the
[Agent Skill specification](https://agentskills.io/specification).
The structure of a Skill allows it to be loaded incrementally to minimize the
impact on the operating context window of the agent.

!!! example "Experimental"
    
    The Skills feature is experimental. We welcome your feedback via the
    respective ADK GitHub repositories:
    [ADK Python](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=skills),
    [ADK TypeScript](https://github.com/google/adk-js/issues/new?template=feature_request.md&labels=skills),
    [ADK Go](https://github.com/google/adk-go/issues/new?template=feature_request.md&labels=skills),
    [ADK Kotlin](https://github.com/google/adk-kotlin/issues/new).

## Get started

Use the `SkillToolset` class to make one or more Skills available to your agent.
You can define [skills in code](#inline-skills) or load
[skills from a filesystem](#filesystem-skills).

=== "Python"

    ```python
    --8<-- "examples/inline/python/skills/index/001-get-started.py"
    ```

    For a complete code example of an ADK agent with a Skill, including both
    file-based and in-line Skill definitions, see the code sample
    [skills_agent](https://github.com/google/adk-python/tree/main/contributing/samples/environment_and_skills/skills_agent).

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/skills/get_started.ts:full_example"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/skills/index/002-get-started.go.txt"
    ```

    For a complete example, see the code sample in
    [skills](https://github.com/google/adk-go/tree/main/examples/skills).

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/skills/SkillsExample.kt:get_started"
    ```

    For a complete example, see the code sample in
    [skills](https://github.com/google/adk-kotlin/tree/main/examples/src/main/kotlin/com/google/adk/kt/examples/skills).

!!! note "Check your working directory"

        Ensure that 'skills/' directory exist in your current working directory and contains the sub-directories for the Skills you want to use in your agent.

## Skill structure

The Skills feature allows you to create modular packages of Skill instructions
and resources that agents can load on demand. This approach helps you organize
your agent's capabilities and optimize the context window by only loading
instructions when they are needed. The structure of Skills is organized into
three levels:

-   **L1 (Metadata):** Provides metadata for skill discovery. This information
    is defined in the frontmatter section of the `SKILL.md` file and includes
    properties such as the Skill name and description.
-   **L2 (Instructions):** Contains the primary instructions for the Skill,
    loaded when the Skill is triggered by the agent. This information is defined
    in the body of the `SKILL.md` file.
-   **L3 (Resources):** Includes additional resources such as reference
    materials, assets, and scripts that can be loaded as needed. These resources
    are organized into the following directories:
    -   `references/`: Additional Markdown files with extended instructions,
        workflows, or guidance.
    -   `assets/`: Resource materials such as database schemas, API
        documentation, templates, or examples.
    -   `scripts/`: Executable scripts supported by the agent runtime.

### System instructions for using skills

The `SkillToolset` provides a default system instruction to the agent that
outlines how it should interact with skills. These instructions include the
following key points:

*   You must use the `load_skill` tool to read a skill's instructions before
    using it.
*   You must follow the instructions in the skill definition exactly.
*   You must use the `load_skill_resource` tool to view files within a skill's
    directory.
*   You must use the `run_skill_script` to run scripts from a skill's `scripts/`
    directory.

### Skill validation

The frontmatter of a skill's `SKILL.md` file is validated to ensure that it
meets the following requirements:

*   **name**:
    *   Must be 64 characters or less.
    *   Must be in lowercase, kebab-case (a-z, 0-9, and hyphens).
    *   Must not have leading, trailing, or consecutive hyphens.
*   **description**:
    *   Must not be empty.
    *   Must be 1024 characters or less.

### Skills directory structure

The following directory structure shows the recommended way to include Skills in
your ADK agent project. The `example-skill/` directory shown below, and any
parallel Skill directories, must follow the
[Agent Skill specification](https://agentskills.io/specification) file
structure. Only the `SKILL.md` file is required.

```
my_agent/
    agent.py (or agent.ts / main.go)
    .env
    skills/
        example-skill/        # Skill
            SKILL.md          # main instructions (required)
            references/
                REFERENCE.md  # detailed API reference
                FORMS.md      # form-filling guide
                *.md          # domain-specific information
            assets/
                *.*           # templates, images, data
            scripts/
                *.py          # utility scripts (Python)
                *.js          # utility scripts (JavaScript)
                *.ts          # utility scripts (TypeScript)
```

## Skill sources

You can define [skills within the code](#inline-skills) or read
[skills from a filesystem](#filesystem-skills).

### Define Skills in code {#inline-skills}

You can define Skills within the code of your agent, as shown below.

=== "Python"

    ```python
    --8<-- "examples/inline/python/skills/index/003-define-skills-in-code-inline-skills.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/skills/inline_skill.ts:full_example"
    ```

=== "Go"

    !!! note
        ADK Go does not currently provide a standard Source for inline skills,
        though this may be added in the future.
        To define skills directly in code, you must implement the `skill.Source`
        interface yourself, as shown below.

    ```go
    --8<-- "examples/inline/go/skills/index/004-define-skills-in-code-inline-skills.go.txt"
    ```

=== "Kotlin"

    !!! note
        ADK Kotlin does not currently provide a standard Source for inline skills.
        To define skills directly in code, you must implement the `SkillSource`
        interface yourself, as shown below.

    ```kotlin
    --8<-- "examples/kotlin/snippets/skills/SkillsExample.kt:inline_skill"
    ```

!!! note
    The `Source` interface can be backed by any data store (such as a database)
    to support dynamic use cases like live updates and personalization.

### Read Skills from filesystem {#filesystem-skills}

=== "Python"

    ```python
    --8<-- "examples/inline/python/skills/index/005-read-skills-from-filesystem-filesystem-s.py"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/skills/index/006-read-skills-from-filesystem-filesystem-s.go.txt"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/skills/SkillsExample.kt:filesystem_skill"
    ```

## Skill processing and validation

When you include skills in your agent, the agent uses a standardized process
to interact with them. This process includes a system-level instruction for
how to use skills, a defined format for how skills are represented, and a set
of validation rules for skill definitions.

## Next steps

Check out these resources for building agents with Skills:

- [Skills in Python - code sample](https://github.com/google/adk-python/tree/main/contributing/samples/environment_and_skills/skills_agent)
- [Skills in Go - code sample](https://github.com/google/adk-go/tree/main/examples/skills)
- [Skills in Kotlin - code sample](https://github.com/google/adk-kotlin/tree/main/examples/src/main/kotlin/com/google/adk/kt/examples/skills)
- Agent Skills [specification documentation](https://agentskills.io/)
