---
catalog_title: Google API Toolsets
catalog_description: Work with Calendar, Gmail, Docs, Sheets, Slides, and YouTube
catalog_icon: /integrations/assets/adk.png
catalog_tags: ["google", "connectors"]
---

# Google API toolsets for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.0.0</span>
</div>

The Google API toolsets give ADK agents access to Google Calendar, Gmail,
Google Docs, Google Sheets, Google Slides, and YouTube. Each toolset is
generated from the API's
[Google API Discovery](https://developers.google.com/discovery) document: every
method in the API becomes one tool that the agent can call, and the toolset
handles OAuth 2.0 authentication for those calls.

The toolsets are built on `GoogleApiToolset`, which you can also use directly to
connect an agent to any other Google API that publishes a discovery document.

## Use cases

- **Scheduling assistant**: Find free time, list upcoming events, and create or
  update Calendar events on the user's behalf.
- **Email triage**: Search, read, label, and draft Gmail messages, or send a
  reply after the user confirms it.
- **Document generation**: Create Google Docs and Slides presentations and fill
  them with content produced by the agent.
- **Spreadsheet automation**: Read ranges from a Google Sheet, append rows, and
  update cell values as part of a workflow.
- **Channel management**: Search YouTube, list a channel's videos and
  playlists, and moderate comments.

## Prerequisites

- A [Google Cloud project](https://developers.google.com/workspace/guides/create-project).
- The API for each toolset you use enabled in that project, for example the
  Google Calendar API or the Gmail API. See
  [Enable Google Workspace APIs](https://developers.google.com/workspace/guides/enable-apis).
- An OAuth 2.0 client ID and client secret of type **Web application**. See
  [Obtain OAuth 2.0 credentials](https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred).
- If you test with the [ADK web interface](/runtime/web-interface/), add the
  web interface URL, for example `http://localhost:8000/dev-ui/`, to the
  **Authorized redirect URIs** of the OAuth client.

## Installation

The toolsets depend on the Google API Python client, which is part of the
`tools` extra:

```bash
pip install "google-adk[tools]"
```

## Use with agent

Create a toolset with your OAuth client credentials and add it to the agent's
`tools` list. Use `tool_filter` to expose only the tools the agent needs. Most
of these APIs have dozens of methods, and a short tool list keeps the model's
context small and its tool choices accurate.

```python
import os

from google.adk.agents import Agent
from google.adk.tools.google_api_tool import CalendarToolset

calendar_toolset = CalendarToolset(
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    tool_filter=[
        "calendar_events_list",
        "calendar_events_get",
        "calendar_events_insert",
        "calendar_freebusy_query",
    ],
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="calendar_agent",
    instruction=(
        "Help the user manage their Google Calendar. Use 'primary' as the "
        "calendarId unless the user names another calendar."
    ),
    tools=[calendar_toolset],
)
```

The first time the agent calls one of these tools, ADK asks the user to sign in
with Google and grant access. The ADK web interface opens the consent screen in
a pop-up window. If you build your own client application, it must handle this
request. See [Authenticating with tools](/tools-custom/authentication/).

Tool names follow the pattern `<api>_<resource>_<method>` in snake case, based
on the method ID in the discovery document. For example, the Calendar API method
`calendar.events.quickAdd` becomes the tool `calendar_events_quick_add`.

## Available toolsets

All toolsets are imported from `google.adk.tools.google_api_tool`.

Toolset | API | Tools
------- | --- | -----
`CalendarToolset` | [Google Calendar API v3](https://developers.google.com/workspace/calendar/api/v3/reference) | 38
`DocsToolset` | [Google Docs API v1](https://developers.google.com/workspace/docs/api/reference/rest) | 3
`GmailToolset` | [Gmail API v1](https://developers.google.com/workspace/gmail/api/reference/rest) | 79
`SheetsToolset` | [Google Sheets API v4](https://developers.google.com/workspace/sheets/api/reference/rest) | 17
`SlidesToolset` | [Google Slides API v1](https://developers.google.com/workspace/slides/api/reference/rest) | 5
`YoutubeToolset` | [YouTube Data API v3](https://developers.google.com/youtube/v3/docs) | 83

Tool counts are from ADK Python v2.13.0 with `google-api-python-client` 2.x.
They change when the underlying API adds or removes methods.

Each toolset accepts the same constructor arguments:

Argument | Description
-------- | -----------
`client_id` | OAuth 2.0 client ID used for the user sign-in flow.
`client_secret` | OAuth 2.0 client secret used for the user sign-in flow.
`tool_filter` | A list of tool names to expose, or a predicate function that receives each tool and returns `True` to expose it.
`service_account` | A `ServiceAccount` to authenticate as a service account instead of a user. See [Authenticate with a service account](#authenticate-with-a-service-account).
`tool_name_prefix` | A prefix added to every tool name, followed by an underscore.

### Calendar

`CalendarToolset` manages calendars, events, access control lists, and
free/busy queries.

```python
calendar_toolset = CalendarToolset(
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    tool_filter=[
        "calendar_events_list",
        "calendar_events_quick_add",
        "calendar_events_patch",
        "calendar_events_delete",
    ],
)
```

Tool | Description
---- | -----------
`calendar_events_list` | Lists events on a calendar, with optional time range and search query.
`calendar_events_get` | Returns one event.
`calendar_events_insert` | Creates an event.
`calendar_events_quick_add` | Creates an event from a text string such as "Lunch with Ana tomorrow at noon".
`calendar_events_patch` | Updates fields of an event.
`calendar_events_delete` | Deletes an event.
`calendar_freebusy_query` | Returns free/busy information for a set of calendars.
`calendar_calendar_list_list` | Lists the calendars on the user's calendar list.

Other tools cover `acl`, `calendars`, `calendar_list`, `colors`, `settings`, and
notification channels.

### Docs

`DocsToolset` creates, reads, and edits Google Docs.

```python
docs_toolset = DocsToolset(
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
)
```

Tool | Description
---- | -----------
`docs_documents_create` | Creates a blank document with the given title.
`docs_documents_get` | Returns the content and structure of a document.
`docs_documents_batch_update` | Applies edits to a document, such as inserting text, replacing text, or adding tables.

### Gmail

`GmailToolset` reads and manages messages, threads, drafts, labels, and mailbox
settings.

```python
gmail_toolset = GmailToolset(
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    tool_filter=[
        "gmail_users_messages_list",
        "gmail_users_messages_get",
        "gmail_users_drafts_create",
        "gmail_users_labels_list",
    ],
)
```

Tool | Description
---- | -----------
`gmail_users_messages_list` | Lists messages, with an optional Gmail search query such as `is:unread`.
`gmail_users_messages_get` | Returns one message.
`gmail_users_messages_send` | Sends a message.
`gmail_users_messages_modify` | Adds or removes labels on a message.
`gmail_users_threads_list` | Lists conversation threads.
`gmail_users_threads_get` | Returns all messages in a thread.
`gmail_users_drafts_create` | Creates a draft.
`gmail_users_labels_list` | Lists the labels in the mailbox.

Gmail methods take a `userId` parameter. Tell the agent to use `me` for the
signed-in user. Other tools cover history, attachments, and mailbox settings
such as filters, forwarding, and vacation replies.

### Sheets

`SheetsToolset` reads and writes spreadsheet values and changes spreadsheet
structure.

```python
sheets_toolset = SheetsToolset(
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    tool_filter=[
        "sheets_spreadsheets_get",
        "sheets_spreadsheets_values_get",
        "sheets_spreadsheets_values_append",
        "sheets_spreadsheets_values_update",
    ],
)
```

Tool | Description
---- | -----------
`sheets_spreadsheets_create` | Creates a spreadsheet.
`sheets_spreadsheets_get` | Returns spreadsheet metadata, such as sheet names and properties.
`sheets_spreadsheets_batch_update` | Applies structural changes, such as adding sheets or formatting cells.
`sheets_spreadsheets_values_get` | Returns the values in a range, such as `Sheet1!A1:D10`.
`sheets_spreadsheets_values_batch_get` | Returns the values in several ranges.
`sheets_spreadsheets_values_append` | Appends rows after the last row of data in a range.
`sheets_spreadsheets_values_update` | Writes values to a range.
`sheets_spreadsheets_values_clear` | Clears the values in a range.

### Slides

`SlidesToolset` creates, reads, and edits Google Slides presentations.

```python
slides_toolset = SlidesToolset(
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
)
```

Tool | Description
---- | -----------
`slides_presentations_create` | Creates a blank presentation.
`slides_presentations_get` | Returns the content of a presentation.
`slides_presentations_batch_update` | Applies edits, such as adding slides, shapes, text, or images.
`slides_presentations_pages_get` | Returns one slide.
`slides_presentations_pages_get_thumbnail` | Returns a thumbnail image URL for one slide.

### YouTube

`YoutubeToolset` searches YouTube and manages a channel's videos, playlists,
comments, and live broadcasts.

```python
youtube_toolset = YoutubeToolset(
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    tool_filter=[
        "youtube_search_list",
        "youtube_videos_list",
        "youtube_playlists_list",
        "youtube_playlist_items_list",
    ],
)
```

Tool | Description
---- | -----------
`youtube_search_list` | Searches for videos, channels, and playlists.
`youtube_videos_list` | Returns details and statistics for videos.
`youtube_channels_list` | Returns details for channels.
`youtube_playlists_list` | Lists playlists.
`youtube_playlist_items_list` | Lists the videos in a playlist.
`youtube_comment_threads_list` | Lists comment threads for a video or channel.
`youtube_comments_set_moderation_status` | Approves, rejects, or holds comments for review.
`youtube_subscriptions_list` | Lists subscriptions.

Other tools cover captions, channel sections, live broadcasts and streams, live
chat, and thumbnails.

## Authentication

### Authenticate users with OAuth 2.0

When you pass `client_id` and `client_secret`, each tool call runs as the
signed-in user. ADK starts the OAuth 2.0 authorization code flow the first time a
tool needs a token, stores the resulting credential, and reuses it for later
calls in the session.

You can also set the client credentials after you create the toolset:

```python
calendar_toolset = CalendarToolset()
calendar_toolset.configure_auth(
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
)
```

### OAuth scopes

A toolset requests one OAuth scope: the first scope listed in the API's
discovery document. With the discovery documents in `google-api-python-client`
2.x, these scopes grant full access:

Toolset | Default scope
------- | -------------
`CalendarToolset` | `https://www.googleapis.com/auth/calendar`
`DocsToolset` | `https://www.googleapis.com/auth/documents`
`GmailToolset` | `https://mail.google.com/`
`SheetsToolset` | `https://www.googleapis.com/auth/drive`
`SlidesToolset` | `https://www.googleapis.com/auth/drive`
`YoutubeToolset` | `https://www.googleapis.com/auth/youtube`

`tool_filter` limits which tools the agent can call, but it does not reduce the
scope the user grants. Review the consent screen your users see, and limit
destructive tools with `tool_filter` and agent instructions.

To request more scopes, create a `GoogleApiToolset` directly and pass
`additional_scopes`. The toolset adds these to the default scope:

```python
from google.adk.tools.google_api_tool import GoogleApiToolset

gmail_toolset = GoogleApiToolset(
    "gmail",
    "v1",
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    additional_scopes=["https://www.googleapis.com/auth/gmail.settings.basic"],
)
```

### Authenticate with a service account

Pass a `ServiceAccount` to call the API as a service account instead of a user.
The service account can only reach data it has been given access to, such as a
spreadsheet or document shared with the service account's email address. Set
`scopes` to the scopes the API calls need.

```python
import json

from google.adk.auth.auth_credential import ServiceAccount
from google.adk.auth.auth_credential import ServiceAccountCredential
from google.adk.tools.google_api_tool import SheetsToolset

with open("path/to/key.json") as f:
  key = ServiceAccountCredential.model_validate(json.load(f))

sheets_toolset = SheetsToolset(
    service_account=ServiceAccount(
        service_account_credential=key,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    ),
    tool_filter=[
        "sheets_spreadsheets_values_get",
        "sheets_spreadsheets_values_append",
    ],
)
```

To use Application Default Credentials instead of a key file, pass
`ServiceAccount(use_default_credential=True, scopes=[...])`.

## Configuration

### Prefix tool names

Set `tool_name_prefix` to avoid name collisions when an agent uses tools from
several sources. The prefix and an underscore are added to every tool name the
model sees. Values in `tool_filter` use the names without the prefix.

```python
calendar_toolset = CalendarToolset(
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    tool_filter=["calendar_events_list"],
    tool_name_prefix="google",
)
# The model sees the tool as "google_calendar_events_list".
```

### Filter tools with a predicate

Pass a function as `tool_filter` to select tools by rule instead of by name.
For example, to expose only read operations:

```python
def is_read_only(tool, readonly_context=None) -> bool:
  return tool.name.endswith(("_get", "_list"))

gmail_toolset = GmailToolset(
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    tool_filter=is_read_only,
)
```

## Use other Google APIs

`GoogleApiToolset` generates tools for any Google API that has a discovery
document. Pass the API name and version as they appear in the
[APIs Explorer](https://developers.google.com/apis-explorer). For example, to
use the Google Drive API:

```python
from google.adk.tools.google_api_tool import GoogleApiToolset

drive_toolset = GoogleApiToolset(
    "drive",
    "v3",
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    tool_filter=["drive_files_list", "drive_files_get"],
)
```

`GoogleApiToolset` also accepts these keyword-only arguments:

Argument | Description
-------- | -----------
`additional_scopes` | Extra OAuth scopes to request with the default scope.
`additional_headers` | HTTP headers added to every request the toolset sends.
`discovery_url` | A custom discovery service URL, passed to the Google API client's `build()` function as `discoveryServiceUrl`.

## Additional resources

- [Authenticating with tools](/tools-custom/authentication/)
- [Google API tools sample agent](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/google_api)
- [`GoogleApiToolset` source code](https://github.com/google/adk-python/blob/main/src/google/adk/tools/google_api_tool/google_api_toolset.py)
- [Google API Discovery Service](https://developers.google.com/discovery)
