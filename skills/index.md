# Skills for ADK agents

Supported in ADKPython v1.25.0TypeScript v0.6.1Go v1.2.0Experimental

An agent ***Skill*** is a self-contained unit of functionality that an ADK agent can use to perform a specific task. An agent Skill encapsulates the necessary instructions, resources, and tools required for a task, based on the [Agent Skill specification](https://agentskills.io/specification). The structure of a Skill allows it to be loaded incrementally to minimize the impact on the operating context window of the agent.

Experimental

The Skills feature is experimental. We welcome your feedback via the respective ADK GitHub repositories: [ADK Python](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=skills), [ADK TypeScript](https://github.com/google/adk-js/issues/new?template=feature_request.md&labels=skills), [ADK Go](https://github.com/google/adk-go/issues/new?template=feature_request.md&labels=skills).

## Get started

Use the `SkillToolset` class to make one or more Skills available to your agent. You can define [skills in code](#inline-skills) or load [skills from a filesystem](#filesystem-skills).

```python
import pathlib

from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

weather_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "weather_skill"
)

my_skill_toolset = skill_toolset.SkillToolset(
    skills=[weather_skill],
    additional_tools=[get_weather_tool],
)

root_agent = Agent(
    model="gemini-flash-latest",
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

```typescript
import {Agent, FunctionTool, SkillToolset, loadSkillFromDir} from '@google/adk';
import * as path from 'node:path';
import {z} from 'zod';

const weatherSkill = await loadSkillFromDir(
  path.join(__dirname, 'skills/weather_skill')
);

const getWeatherTool = new FunctionTool({
  name: 'get_weather',
  description: 'Gets the weather for a given location.',
  parameters: z.object({
    location: z.string().describe('The city and state, e.g. San Francisco, CA'),
  }),
  execute: async ({location}) => {
    return {
      location,
      temperature: '72°F',
      condition: 'Sunny',
    };
  },
});

const mySkillToolset = new SkillToolset([weatherSkill], {
  additionalTools: [getWeatherTool],
});

const rootAgent = new Agent({
  model: 'gemini-flash-latest',
  name: 'skill_user_agent',
  description: 'An agent that can use specialized skills.',
  instruction:
    'You are a helpful assistant that can leverage skills to perform tasks.',
  tools: [mySkillToolset],
});

export default rootAgent;
```

```go
import (
    "context"
    "os"

    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/tool/skilltoolset/skill"
    "google.golang.org/adk/tool/skilltoolset"
    "google.golang.org/adk/tool"
)

mySkillToolset, err := skilltoolset.New(ctx, skilltoolset.Config{
    Source: skill.NewFileSystemSource(os.DirFS("./skills")),
})
if err != nil {
    // handle error
}

rootAgent, err := llmagent.New(llmagent.Config{
    Name:        "skill_user_agent",
    Model:       model,
    Description: "An agent that can use specialized skills.",
    Instruction: "You are a helpful assistant that can leverage skills to perform tasks.",
    Toolsets:    []tool.Toolset{mySkillToolset},
})
if err != nil {
    // handle error
}
```

For a complete example, see the code sample in [skills](https://github.com/google/adk-go/tree/main/examples/skills).

## Understand Skills

The Skills feature allows you to create modular packages of Skill instructions and resources that agents can load on demand. This approach helps you organize your agent's capabilities and optimize the context window by only loading instructions when they are needed. The structure of Skills is organized into three levels:

- **L1 (Metadata):** Provides metadata for skill discovery. This information is defined in the frontmatter section of the `SKILL.md` file and includes properties such as the Skill name and description.
- **L2 (Instructions):** Contains the primary instructions for the Skill, loaded when the Skill is triggered by the agent. This information is defined in the body of the `SKILL.md` file.
- **L3 (Resources):** Includes additional resources such as reference materials, assets, and scripts that can be loaded as needed. These resources are organized into the following directories:
  - `references/`: Additional Markdown files with extended instructions, workflows, or guidance.
  - `assets/`: Resource materials such as database schemas, API documentation, templates, or examples.
  - `scripts/`: Executable scripts supported by the agent runtime.

### Skills directory structure

The following directory structure shows the recommended way to include Skills in your ADK agent project. The `example-skill/` directory shown below, and any parallel Skill directories, must follow the [Agent Skill specification](https://agentskills.io/specification) file structure. Only the `SKILL.md` file is required.

```text
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

You can define [skills within the code](#inline-skills) or read [skills from a filesystem](#filesystem-skills).

### Define Skills in code

You can define Skills within the code of your agent, as shown below.

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

```typescript
import {Agent, Skill, SkillToolset} from '@google/adk';

const greetingSkill: Skill = {
  frontmatter: {
    name: 'greeting-skill',
    description: 'A friendly greeting skill that can say hello to a specific person.',
  },
  instructions:
    "Step 1: Read the 'references/hello_world.txt' file to understand how to greet the user. Step 2: Return a greeting based on the reference.",
  resources: {
    references: {
      'hello_world.txt': 'Hello! So glad to have you here!',
      'example.md': 'This is an example reference.',
    },
  },
};

const mySkillToolset = new SkillToolset([greetingSkill]);

const rootAgent = new Agent({
  model: 'gemini-flash-latest',
  name: 'greeting_agent',
  description: 'An agent that uses an inline greeting skill.',
  instruction: 'You are a helpful assistant that uses skills to greet people.',
  tools: [mySkillToolset],
});

export default rootAgent;
```

Note

ADK Go does not currently provide a standard Source for inline skills, though this may be added in the future. To define skills directly in code, you must implement the `skill.Source` interface yourself, as shown below.

```go
import (
    "context"
    "io"
    "slices"
    "strings"

    "google.golang.org/adk/tool/skilltoolset/skill"
)

// Example implementation of a static in-memory skill.Source:
type StaticSource struct{}

func (s *StaticSource) ListFrontmatters(ctx context.Context) ([]*skill.Frontmatter, error) {
    return []*skill.Frontmatter{
        {Name: "greeting-skill", Description: "A friendly greeting skill that can say hello to a specific person."},
    }, nil
}

func (s *StaticSource) LoadFrontmatter(ctx context.Context, name string) (*skill.Frontmatter, error) {
    if name != "greeting-skill" {
        return nil, skill.ErrSkillNotFound
    }
    return &skill.Frontmatter{Name: "greeting-skill", Description: "A friendly greeting skill that can say hello to a specific person."}, nil
}

func (s *StaticSource) LoadInstructions(ctx context.Context, name string) (string, error) {
    if name != "greeting-skill" {
        return "", skill.ErrSkillNotFound
    }
    return "Step 1: Read the 'references/hello_world.txt' file to understand how to greet the user. Step 2: Return a greeting based on the reference.", nil
}

func (s *StaticSource) ListResources(ctx context.Context, name, subpath string) ([]string, error) {
    if name != "greeting-skill" {
        return nil, skill.ErrSkillNotFound
    }
    if !slices.Contains([]string{"", ".", "references", "references/"}, subpath) {
        return nil, skill.ErrResourceNotFound
    }
    return []string{"references/hello_world.txt", "references/example.md"}, nil
}

func (s *StaticSource) LoadResource(ctx context.Context, name, resourcePath string) (io.ReadCloser, error) {
    if name != "greeting-skill" {
        return nil, skill.ErrSkillNotFound
    }
    switch resourcePath {
    case "references/hello_world.txt":
        return io.NopCloser(strings.NewReader("Hello! So glad to have you here!")), nil
    case "references/example.md":
        return io.NopCloser(strings.NewReader("This is an example reference.")), nil
    default:
        return nil, skill.ErrResourceNotFound
    }
}
```

Note

The `Source` interface can be backed by any data store (such as a database) to support dynamic use cases like live updates and personalization.

### Read Skills from filesystem

```python
import pathlib

from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

greeting_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "greeting-skill"
)
weather_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "weather-skill"
)

my_skill_toolset = skill_toolset.SkillToolset(
    skills=[weather_skill, greeting_skill],
)
```

```go
import (
    "os"

    "google.golang.org/adk/tool/skilltoolset/skill"
    "google.golang.org/adk/tool/skilltoolset"
)

// ...

source := skill.NewFileSystemSource(os.DirFS("./skills"))

// This example doesn't use any optional wrappers, but you can use them if
// needed, e.g.:
//   source, _, err = skill.WithFrontmatterPreloadSource(ctx, source)
//   source, _, err = skill.WithCompletePreloadSource(ctx, source)
// For more information about these and other wrappers, see
// https://pkg.go.dev/google.golang.org/adk/tool/skilltoolset/skill#Source.

skillToolset, err := skilltoolset.New(ctx, skilltoolset.Config{
    Source: source,
})
if err != nil {
    // handle error
}
```

## Next steps

Check out these resources for building agents with Skills:

- [Skills in Python - code sample](https://github.com/google/adk-python/tree/main/contributing/samples/skills_agent)
- [Skills in Go - code sample](https://github.com/google/adk-go/tree/main/examples/skills)
- Agent Skills [specification documentation](https://agentskills.io/)
