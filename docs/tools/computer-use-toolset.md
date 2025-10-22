# Computer Use Toolset

The `ComputerUseToolset` allows an agent to operate a browser to complete user tasks. It uses Playwright to control a Chromium browser and can interact with web pages by taking screenshots, clicking, typing, and navigating.

## Setup

1.  **Install Python Dependencies**:
    ```bash
    uv pip install -r internal/samples/computer_use/requirements.txt
    ```
2.  **Install Playwright Dependencies**:
    ```bash
    playwright install-deps chromium
    ```
3.  **Install Chromium Browser**:
    ```bash
    playwright install chromium
    ```

## Usage

To use the `ComputerUseToolset`, you need to provide a `Computer` implementation. The `PlaywrightComputer` is provided for this purpose.

**Example:**
```python
from google.adk import Agent
from google.adk.tools.computer_use.computer_use_toolset import ComputerUseToolset
from .playwright import PlaywrightComputer

root_agent = Agent(
    model='gemini-2.5-computer-use-preview-10-2025',
    name='computer_use_agent',
    description='A computer use agent that can operate a browser to finish user tasks.',
    instruction="you are a computer use agent",
    tools=[
        ComputerUseToolset(computer=PlaywrightComputer(screen_size=(1280, 936)))
    ],
)
```
For a complete example, see the [computer_use sample](https://github.com/google/adk-python/tree/main/contributing/samples/computer_use).
