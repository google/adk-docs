---
catalog_title: Mobilebox
catalog_description: Drive cloud Android phones and iPhone simulators, install apps and read the screen
catalog_icon: /integrations/assets/mobilebox.png
catalog_tags: ["mcp"]
---

# Mobilebox MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [Mobilebox MCP server](https://mobilebox.dev/android-mcp-server) connects
your ADK agent to cloud Android phones and iPhone simulators. The agent creates
a phone, reads the screen as a numbered list of elements, taps, types and
swipes, installs apps from a URL, and parks or deletes the phone when it is
done. The server is hosted, so there is no emulator, ADB or Xcode setup on your
machine.

## Use cases

- **Test your mobile app**: Install an Android build from an APK URL, or an iOS
  simulator build, walk a flow such as sign-up, and check what is on the screen
  after each step.
- **Run tasks in Android apps**: Let the agent operate apps that have no web
  version or API, on a fresh phone for each task.
- **Keep app state between runs**: Park an Android phone to stop it while keeping its
  apps, data and logins, then start it again in a later session.

## Prerequisites

- A [Mobilebox](https://mobilebox.dev/signup) account and an API key from its
  dashboard.
- ADK with MCP support:

    ```bash
    pip install "google-adk[mcp]"
    ```

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        MOBILEBOX_API_KEY = "YOUR_MOBILEBOX_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="mobilebox_agent",
            instruction=(
                "You control cloud Android phones. Create one phone per task, read the "
                "screen before you act, and delete the phone when the task is done."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mobilebox.dev/mcp",
                        headers={"Authorization": f"Bearer {MOBILEBOX_API_KEY}"},
                    ),
                )
            ],
        )
        ```

Try a task such as "Open Settings > Display on a new phone and tell me the
brightness level." Phones are billed per minute while they run, so the
instruction asks the agent to delete its phone when the task is done.

## Available tools

Tool | Description
---- | -----------
`create_phone` | Create an Android phone or an iPhone simulator (`platform: "ios"`), wait until it is ready and return its first screen
`list_phones` | List the project's phones with their status
`start_phone` | Resume a parked phone with its apps, data and logins
`park_phone` | Stop a phone and keep its apps, data and logins
`delete_phone` | Delete a phone and everything on it
`observe` | Read the current screen as a numbered element list
`act` | Run 1 to 20 actions in order: tap, type, swipe, scroll, keys, open or close apps, waits
`screenshot` | Take a PNG screenshot
`install_app` | Install an app from a public download URL (APK, split bundle, or a zipped iOS simulator `.app`)
`list_apps` | List the apps installed on the phone
`uninstall_app` | Uninstall an app and delete its data
`app_logs` | Read an installed app's own log lines, crash reports included
`push_file` | Put a file on the phone for an app to import
`pull_file` | Read a file an app wrote to the phone's shared storage
`set_device` | Set country, city, timezone, locale, GPS and network
`watch_phone` | Get a link to watch the phone live
`record_screen` | Record the phone's screen as a video
`publish_proof` | Publish a run summary with screenshots as Markdown for a pull request
`request_capability` | Report something the agent needed that Mobilebox does not offer

## Additional resources

- [Mobilebox Android MCP server](https://mobilebox.dev/android-mcp-server)
- [Agent guide: observe, act, verify, park](https://mobilebox.dev/docs/agents)
- [API reference](https://mobilebox.dev/docs/reference)
- [Examples on GitHub](https://github.com/mobilebox-dev/mobilebox)
