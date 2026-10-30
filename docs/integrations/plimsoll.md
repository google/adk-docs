---
catalog_title: plimsoll
catalog_description: Run agent-written Python in self-hosted sandboxes with an isolation floor
catalog_icon: /integrations/assets/plimsoll.png
catalog_tags: ["code"]
---

# plimsoll code executor for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[plimsoll](https://github.com/plimsollmark/plimsoll) is an open-source (Apache-2.0)
sandbox service you run on your own infrastructure. Its `PlimsollCodeExecutor` is an
ADK code executor: each Python code block the model writes runs in a fresh sandbox on
your plimsoll service instead of on the agent's host. Every result states the
sandbox's isolation tier, and by default the executor refuses to send code to a
service weaker than [gVisor](https://gvisor.dev/) or a virtual machine.

## Use cases

- **Self-hosted code execution**: Run model-written Python on machines you operate,
  with no network inside the sandbox, when a hosted sandbox service is not an option.

- **Enforced isolation**: Require gVisor or virtual-machine isolation for every block.
  A service below that floor refuses before any code runs, and the model is told that
  nothing ran.

- **Files in, files out**: Pass input files to a block and collect the output files
  you name as ADK artifacts, with their bytes intact.

- **Checked results**: Each run returns a record of the request and the result
  (SHA-256 digests) that the client recomputes before ADK sees the result.

## Prerequisites

- A plimsoll service (plimsolld) your agent can reach, and the caller token it
  issued you. The
  [getting-started guide](https://github.com/plimsollmark/plimsoll/blob/main/docs/getting-started.md)
  runs one on a single machine.
- For the default isolation floor: Linux with Docker and gVisor (the plimsoll
  repository's `docker/install-gvisor.sh` installs a pinned release), or a
  virtual-machine provider (E2B or Docker Cloud Sandboxes).
- A sandbox image with Python and the libraries your agent may import. The sandbox
  has no network and installs nothing at run time; `plimsoll/sandbox-python` carries
  NumPy and SciPy.

## Installation

```bash
pip install "plimsoll-client[adk]"
```

The client and the service must be the same plimsoll release; upgrade them together.

## Use with agent

```python
import os

from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from plimsoll_client import Client
from plimsoll_client.adk import PlimsollCodeExecutor, PlimsollCodeExecutorGuard

executor = PlimsollCodeExecutor(
    client=Client(os.environ["PLIMSOLL_URL"], token=os.environ.get("PLIMSOLL_TOKEN")),
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="calculator",
    instruction="Write and run Python code to answer questions that need calculation.",
    code_executor=executor,
)

runner = Runner(
    agent=root_agent,
    app_name="calculator",
    session_service=InMemorySessionService(),
    # ADK saves every code execution result as an artifact.
    artifact_service=InMemoryArtifactService(),
    # Refuses a Runner that cannot save results before any code is sent.
    plugins=[PlimsollCodeExecutorGuard()],
)
```

Register `PlimsollCodeExecutorGuard` first among your plugins. Besides checking the
Runner, it tells the model to write fenced Python blocks and that each block starts
fresh.

## Configuration

The executor's keyword arguments:

- **`minimum_isolation`**: the weakest isolation tier the executor accepts. The
  default, `"kernel"`, means gVisor or stronger; `"vm"` requires a virtual machine.
  A service below the floor refuses the block before it runs. Use `"container"`
  only for development on your own code.
- **`artifact_paths`**: relative paths of output files to collect, for example
  `("answer.json",)`. The service returns only these files, and they come back as
  the result's `output_files` with their bytes intact.

## Limitations

- **Every block starts fresh.** Variables, imports and files from one block are gone
  in the next; `stateful=True` and `optimize_data_file=True` are refused. The model
  must `print` a value to return it.
- **Python only** in ADK's code-block flow.
- **Keep `RunConfig.support_cfc` false.** With it on, ADK replaces a custom executor
  with Gemini's built-in code execution, so no code reaches plimsoll. The guard
  refuses that combination before any model or code request.
- **No automatic repeat of an uncertain run.** If a block may have run but its answer
  was lost, the executor raises instead of running it again.

## Additional resources

- [plimsoll on GitHub](https://github.com/plimsollmark/plimsoll)
- [ADK executor guide](https://github.com/plimsollmark/plimsoll/blob/main/docs/google-adk.md):
  input file encoding, refusals, retries and every option
- [Recorded runs through this executor](https://plimsollmark.github.io/plimsoll/integrations/google-adk/index.html),
  from a CSV sum to a refused isolation floor
- [plimsoll-client on PyPI](https://pypi.org/project/plimsoll-client/)
