# Skills for ADK agents

Supported in ADKPython v1.25.0Experimental

An agent ***Skill*** is a self-contained unit of functionality that an ADK agent can use to perform a specific task. An agent Skill encapsulates the necessary instructions, resources, and tools required for a task, based on the [Agent Skill specification](https://agentskills.io/specification). The structure of a Skill allows it to be loaded incrementally to minimize the impact on the operating context window of the agent.

Experimental

The Skills feature is experimental and has some [known limitations](#known-limitations). We welcome your [feedback](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=skills)!

## Get started

Use the `SkillToolset` class to include one or more Skills in your agent definition and then add to your agent's tools list. You can define a [Skill in code](#inline-skills), or load the skill from a file definition, as shown below:

```python
import pathlib

from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

weather_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "weather_skill"
)

my_skill_toolset = skill_toolset.SkillToolset(
    skills=[weather_skill]
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="skill_user_agent",
    description="An agent that can use specialized skills.",
    instruction=(
        "You are a helpful assistant that can leverage skills to perform tasks."
    ),
    tools=[
        my_skill_toolset,
    ],
)
```

For a complete code example of an ADK agent with a Skill, including both file-based and in-line Skill definitions, see the code sample [skills_agent](https://github.com/google/adk-python/tree/main/contributing/samples/skills_agent).

## Define Skills

The Skills feature allows you to create modular packages of Skill instructions and resources that agents can load on demand. This approach helps you organize your agent's capabilities and optimize the context window by only loading instructions when they are needed. The structure of Skills is organized into three levels:

- **L1 (Metadata):** Provides metadata for skill discovery. This information is defined in the frontmatter section of the `SKILL.md` file and includes properties such as the Skill name and description.
- **L2 (Instructions):** Contains the primary instructions for the Skill, loaded when the Skill is triggered by the agent. This information is defined in the body of the `SKILL.md` file.
- **L3 (Resources):** Includes additional resources such as reference materials, assets, and scripts that can be loaded as needed. These resources are organized into the following directories:
  - `references/`: Additional Markdown files with extended instructions, workflows, or guidance.
  - `assets/`: Resource materials such as database schemas, API documentation, templates, or examples.
  - `scripts/`: Executable scripts supported by the agent runtime.

### Define Skills with files

The following directory structure shows the recommended way to include Skills in your ADK agent project. The `example_skill/` directory shown below, and any parallel Skill directories, must follow the [Agent Skill specification](https://agentskills.io/specification) file structure. Only the `SKILL.md` file is required.

```text
my_agent/
    agent.py
    .env
    skills/
        example_skill/        # Skill
            SKILL.md          # main instructions (required)
            references/
                REFERENCE.md  # detailed API reference
                FORMS.md      # form-filling guide
                *.md          # domain-specific information
            assets/
                *.*           # templates, images, data
            scripts/
                *.py          # utility scripts
```

Script execution not supported

Scripts execution is not yet supported and is a [known limitation](#known-limitations).

### Define Skills in code

In ADK agents, you can also define Skills within the code of the agent, using the `Skill` model class, as shown below. This method of Skill definition enables you to dynamically modify skills from your ADK agent code.

```python
from google.adk.skills import models

greeting_skill = models.Skill(
    frontmatter=models.Frontmatter(
        name="greeting-skill",
        description=(
            "A friendly greeting skill that can say hello to a specific person."
        ),
    ),
    instructions=(
        "Step 1: Read the 'references/hello_world.txt' file to understand how"
        " to greet the user. Step 2: Return a greeting based on the reference."
    ),
    resources=models.Resources(
        references={
            "hello_world.txt": "Hello! So glad to have you here!",
            "example.md": "This is an example reference.",
        },
    ),
)
```

## Known limitations

The Skills feature is experimental and includes the following limitations:

- **Script execution:** The Skills feature does not currently support script execution (`scripts/` directory).

## Next steps

Check out these resources for building agents with Skills:

- ADK Skills agent code sample: [skills_agent](https://github.com/google/adk-python/tree/main/contributing/samples/skills_agent).
- Agent Skills [specification documentation](https://agentskills.io/)
