# Computer Use Toolset with Gemini

The Computer Use Toolset allows an agent to operate a user interface
of a computer, such as a browsers, to complete tasks. This tool uses
a specific Gemini model and the [Playwright](https://playwright.dev/) 
testing tool to control a Chromium browser and can interact with
web pages by taking screenshots, clicking, typing, and navigating.

For more information about the computer use model, see 
Gemini API [Computer use](https://ai.google.dev/gemini-api/docs/computer-use)
or the Google Cloud Vertex AI API 
[Computer use](https://cloud.google.com/vertex-ai/generative-ai/docs/computer-use).

!!! example "Preview release"
    The Computer Use model and tool is a Preview release. For
    more information, see the
    [launch stage descriptions](https://cloud.google.com/products#product-launch-stages).

## Setup

You must install Playwright and its dependencies, including Chromium,
to be able to use the Computer Use Toolset.

??? tip "Recommended: create and activate a Python virtual environment"

    Create a Python virtual environment:

    ```shell
    python -m venv .venv
    ```

    Activate the Python virtual environment:

    === "Windows CMD"

        ```console
        .venv\Scripts\activate.bat
        ```

    === "Windows Powershell"

        ```console
        .venv\Scripts\Activate.ps1
        ```

    === "MacOS / Linux"

        ```bash
        source .venv/bin/activate
        ```

To set up the required software libraries for the Computer Use Toolset:

1.  Install Python dependencies:
    ```console
    pip install termcolor==3.1.0
    pip install playwright==1.52.0
    pip install browserbase==1.3.0
    pip install rich
    ```
2.  Install the Playwright dependencies, including the Chromium browser:
    ```console
    playwright install-deps chromium
    playwright install chromium
    ```

## Use the tool

Use the Computer Use Toolset by adding it as a tool to your agent. When you
configure the tool, you must provide a implementation of the `BaseComputer`
class which defines an interface for an agent to use a computer. In the
following example, the `PlaywrightComputer` class is defined for this purpose.
You can find the code for this implementation in `playwright.py` file of the
[computer_use](https://github.com/google/adk-python/blob/main/contributing/samples/computer_use/playwright.py)
agent sample project.

```python
from google.adk import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.computer_use.computer_use_toolset import ComputerUseToolset
from typing_extensions import override

from .playwright import PlaywrightComputer

root_agent = Agent(
    model='gemini-2.5-computer-use-preview-10-2025',
    name='hello_world_agent',
    description=(
        'computer use agent that can operate a browser on a computer to finish'
        ' user tasks'
    ),
    instruction='you are a computer use agent',
    tools=[
        ComputerUseToolset(computer=PlaywrightComputer(screen_size=(1280, 936)))
    ],
)
```

For a complete code example, see the
[computer_use](https://github.com/google/adk-python/tree/main/contributing/samples/computer_use)
agent sample project.
