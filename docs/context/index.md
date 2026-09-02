# Agent context

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

In the Agent Development Kit (ADK), *context* refers to the crucial bundle of information available to your agent and its tools during specific operations. Think of it as the necessary background knowledge and resources needed to handle a current task or conversation turn effectively.

Agents often need more than just the latest user message to perform well. Context is essential because it enables:

1. **Maintaining State:** Remembering details across multiple steps in a conversation (e.g., user preferences, previous calculations, items in a shopping cart). This is primarily managed through **session state**.
2. **Passing Data:** Sharing information discovered or generated in one step (like an LLM call or a tool execution) with subsequent steps. Session state is key here too.
3. **Accessing Services:** Interacting with framework capabilities like:
    * **Artifact Storage:** Saving or loading files or data blobs (like PDFs, images, configuration files) associated with the session.
    * **Memory:** Searching for relevant information from past interactions or external knowledge sources connected to the user.
    * **Authentication:** Requesting and retrieving credentials needed by tools to access external APIs securely.
4. **Identity and Tracking:** Knowing which agent is currently running (`agent.name`) and uniquely identifying the current request-response cycle (`invocation_id`) for logging and debugging.
5. **Tool-Specific Actions:** Enabling specialized operations within tools, such as requesting authentication or searching memory, which require access to the current interaction's details.


The central piece holding all this information together for a single, complete user-request-to-final-response cycle (an **invocation**) is the `InvocationContext`. However, you typically won't create or manage this object directly. The ADK framework creates it when an invocation starts (e.g., via `runner.run_async`) and passes the relevant contextual information implicitly to your agent code, callbacks, and tools.

=== "Python"

    ```python
    --8<-- "examples/inline/python/context/index/001-agent-context.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/context/index/002-agent-context.ts"
    ```

=== "Go"

    ```go
    --8<-- "examples/inline/go/context/index/003-agent-context.go.txt"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/context/index/004-agent-context.java"
    ```

## Types of context

ADK uses the `Context` class as the central mechanism to manage an agent's environment, state, and resources. While `Context` serves as the foundational base for all agent interactions, it manifests in specialized "flavors" designed to provide the right balance of capabilities and permissions depending on where they are used in the agent's execution flow.
If you use these specific context types, ADK ensures that your agent has access to necessary information, such as memory, session state, or credentials, exactly when and where you need them.
Here are the primary context flavors you will encounter:

- **`InvocationContext`**: Used during core agent runs (`_run_async_impl`, `_run_live_impl`) to provide a comprehensive view of the entire invocation, including service references and lifecycle management.

- **`ReadonlyContext`**: A lightweight, restricted view of fundamental contextual details used in scenarios where mutation is disallowed, such as within instruction providers.

- **`Context`**: Used in agent lifecycle and model callbacks. It provides a robust set of features for reading/writing session state, managing artifacts, and injecting data into the memory service.

- **`ToolContext`**: Tailored for tool execution and tool-related callbacks. In addition to the capabilities of Context, it includes specialized methods for authentication flows, memory searching, and artifact discovery.

!!! note
    **About compatibility**: In Python and TypeScript, `CallbackContext` and `ToolContext` have been replaced by the `Context` type. The `CallbackContext` class is maintained as an alias for `Context` to ensure backward compatibility. While you may encounter `CallbackContext` in existing codebases, **you should use the `Context` class** for all new development to take advantage of the full, unified feature set.

### `InvocationContext`
- **Where Used:** Received as the `ctx` argument directly within an agent's core implementation methods (`_run_async_impl`, `_run_live_impl`).
- **Purpose:** Provides access to the entire state of the current invocation. This is the most comprehensive context object.
- **Key Contents:** Direct access to `session` (including `state` and `events`), the current `agent` instance, `invocation_id`, initial `user_content`, references to configured services (`artifact_service`, `memory_service`, `session_service`), and fields related to live/streaming modes.
- **Use Case:** Primarily used when the agent's core logic needs direct access to the overall session or services, though often state and artifact interactions are delegated to callbacks/tools which use their own contexts. Also used to control the invocation itself (e.g., setting `ctx.end_invocation = True`).

    === "Python"

        ```python
        --8<-- "examples/inline/python/context/index/005-invocationcontext.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/inline/typescript/context/index/006-invocationcontext.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/inline/go/context/index/007-invocationcontext.go.txt"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/context/index/008-invocationcontext.java"
        ```

### `ReadonlyContext`
- **Where Used:** Provided in scenarios where only read access to basic information is needed and mutation is disallowed (e.g., `InstructionProvider` functions). It's also the base class for other contexts.
- **Purpose:** Offers a safe, read-only view of fundamental contextual details.
- **Key Contents:** `invocation_id`, `agent_name`, and a read-only *view* of the current `state`.

    === "Python"

        ```python
        --8<-- "examples/inline/python/context/index/009-readonlycontext.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/inline/typescript/context/index/010-readonlycontext.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/inline/go/context/index/011-readonlycontext.go.txt"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/context/index/012-readonlycontext.java"
        ```

### `CallbackContext` and `Context`

- **Where Used:** Passed as `callback_context` to agent lifecycle callbacks (`before_agent_callback`, `after_agent_callback`) and model interaction callbacks (`before_model_callback`, `after_model_callback`).
- **Purpose:** Facilitates inspecting and modifying state, interacting with artifacts, and accessing invocation details *specifically within callbacks*.
- **Key Capabilities (Adds to `ReadonlyContext`):**
    - **Mutable `state` Property:** Allows reading and writing to session state. Changes made here (`callback_context.state['key'] = value`) are tracked and associated with the event generated by the framework after the callback.
    - **Artifact Methods:** `load_artifact(filename)` and `save_artifact(filename, part)` methods for interacting with the configured `artifact_service`.
    - Direct `user_content` access.

!!! note
  In Python and TypeScript, `CallbackContext` and `ToolContext` have been replaced by the `Context` type.

    === "Python"

        ```python
        --8<-- "examples/inline/python/context/index/013-callbackcontext-and-context.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/inline/typescript/context/index/014-callbackcontext-and-context.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/inline/go/context/index/015-callbackcontext-and-context.go.txt"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/context/index/016-callbackcontext-and-context.java"
        ```

### `ToolContext`
- **Where Used:** Passed as `tool_context` to the functions backing `FunctionTool`s and to tool execution callbacks (`before_tool_callback`, `after_tool_callback`).
- **Purpose:** Provides everything `CallbackContext` does, plus specialized methods essential for tool execution, like handling authentication, searching memory, and listing artifacts.
- **Key Capabilities (Adds to `CallbackContext`):**
    - **Authentication Methods:** `request_credential(auth_config)` to trigger an auth flow, and `get_auth_response(auth_config)` to retrieve credentials provided by the user/system.
    - **Artifact Listing:** `list_artifacts()` to discover available artifacts in the session.
    - **Memory Search:** `search_memory(query)` to query the configured `memory_service`.
    - **`function_call_id` Property:** Identifies the specific function call from the LLM that triggered this tool execution, crucial for linking authentication requests or responses back correctly.
    - **`actions` Property:** Direct access to the `EventActions` object for this step, allowing the tool to signal state changes, auth requests, etc.

    === "Python"

        ```python
        --8<-- "examples/inline/python/context/index/017-toolcontext.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/inline/typescript/context/index/018-toolcontext.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/inline/go/context/index/019-toolcontext.go.txt"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/context/index/020-toolcontext.java"
        ```

Understanding these different context objects and when to use them is key to effectively managing state, accessing services, and controlling the flow of your ADK application. The next section will detail common tasks you can perform using these contexts.


## Common tasks using context

Now that you understand the different context objects, let's focus on how to use them for common tasks when building your agents and tools.

### Access information

You'll frequently need to read information stored within the context.

*   **Read session state:** Access data saved in previous steps or user/app-level settings. Use dictionary-like access on the `state` property.

    === "Python"

        ```python
        --8<-- "examples/inline/python/context/index/021-access-information.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/inline/typescript/context/index/022-access-information.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/inline/go/context/index/023-access-information.go.txt"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/context/index/024-access-information.java"
        ```

*   **Get current identifiers:** Useful for logging or custom logic based on the current operation.

    === "Python"

        ```python
        --8<-- "examples/inline/python/context/index/025-access-information.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/inline/typescript/context/index/026-access-information.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/inline/go/context/index/027-access-information.go.txt"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/context/index/028-access-information.java"
        ```

*   **Access the initial user input:** Refer back to the message that started the current invocation.

    === "Python"

        ```python
        --8<-- "examples/inline/python/context/index/029-access-information.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/inline/typescript/context/index/030-access-information.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/inline/go/context/index/031-access-information.go.txt"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/context/index/032-access-information.java"
        ```

### Manage state

State is crucial for memory and data flow. When you modify state using `CallbackContext` or `ToolContext`, the changes are automatically tracked and persisted by the framework.

*   **How it Works:** Writing to `callback_context.state['my_key'] = my_value` or `tool_context.state['my_key'] = my_value` adds this change to the `EventActions.state_delta` associated with the current step's event. The `SessionService` then applies these deltas when persisting the event.

*  **Pass data between tools**

    === "Python"

        ```python
        --8<-- "examples/inline/python/context/index/033-manage-state.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/inline/typescript/context/index/034-manage-state.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/inline/go/context/index/035-manage-state.go.txt"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/context/index/036-manage-state.java"
        ```

*   **Update user preferences:**

    === "Python"

        ```python
        --8<-- "examples/inline/python/context/index/037-manage-state.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/inline/typescript/context/index/038-manage-state.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/inline/go/context/index/039-manage-state.go.txt"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/context/index/040-manage-state.java"
        ```

*   **State prefixes:** While basic state is session-specific, prefixes like `app:` and `user:` can be used with persistent `SessionService` implementations (like `DatabaseSessionService` or `VertexAiSessionService`) to indicate broader scope (app-wide or user-wide across sessions). `temp:` can denote data only relevant within the current invocation.

### Work with artifacts

Use artifacts to handle files or large data blobs associated with the session. Common use case: processing uploaded documents.

*   **Document summarizer example flow:**

    1.  **Ingest Reference (e.g., in a Setup Tool or Callback):** Save the *path or URI* of the document, not the entire content, as an artifact.

        === "Python"

               ```python
               --8<-- "examples/inline/python/context/index/041-work-with-artifacts.py"
               ```

        === "TypeScript"

               ```typescript
               --8<-- "examples/inline/typescript/context/index/042-work-with-artifacts.ts"
               ```

        === "Go"

            ```go
            --8<-- "examples/inline/go/context/index/043-work-with-artifacts.go.txt"
            ```

        === "Java"

               ```java
               --8<-- "examples/inline/java/context/index/044-work-with-artifacts.java"
               ```

    2.  **Summarizer Tool:** Load the artifact to get the path/URI, read the actual document content using appropriate libraries, summarize, and return the result.

        === "Python"

            ```python
            --8<-- "examples/inline/python/context/index/045-work-with-artifacts.py"
            ```

        === "TypeScript"

            ```typescript
            --8<-- "examples/inline/typescript/context/index/046-work-with-artifacts.ts"
            ```

        === "Go"

            ```go
            --8<-- "examples/inline/go/context/index/047-work-with-artifacts.go.txt"
            ```

        === "Java"

            ```java
            --8<-- "examples/inline/java/context/index/048-work-with-artifacts.java"
            ```

*   **List Artifacts:** Discover what files are available.

    === "Python"

        ```python
        --8<-- "examples/inline/python/context/index/049-work-with-artifacts.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/inline/typescript/context/index/050-work-with-artifacts.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/inline/go/context/index/051-work-with-artifacts.go.txt"
        ```

    === "Java"

        ```java
        --8<-- "examples/inline/java/context/index/052-work-with-artifacts.java"
        ```

### Handle tool authentication

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-java">Java v0.2.0</span>
</div>

Securely manage API keys or other credentials needed by tools.

=== "Python"

    ```python
    --8<-- "examples/inline/python/context/index/053-handle-tool-authentication.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/context/index/054-handle-tool-authentication.ts"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/context/index/055-handle-tool-authentication.java"
    ```

*Remember: `request_credential` pauses the tool and signals the need for authentication. The user/system provides credentials, and on a subsequent call, `get_auth_response` (or checking state again) allows the tool to proceed.* The `tool_context.function_call_id` is used implicitly by the framework to link the request and response.

### Leveraging Memory

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-java">Java v0.2.0</span>
</div>

Access relevant information from the past or external sources.

=== "Python"

    ```python
    --8<-- "examples/inline/python/context/index/056-leveraging-memory.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/context/index/057-leveraging-memory.ts"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/context/index/058-leveraging-memory.java"
    ```

### Advanced: Direct `InvocationContext` Usage

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-java">Java v0.2.0</span>
</div>

While most interactions happen via `CallbackContext` or `ToolContext`, sometimes the agent's core logic (`_run_async_impl`/`_run_live_impl`) needs direct access.

=== "Python"

    ```python
    --8<-- "examples/inline/python/context/index/059-advanced-direct-invocationcontext-usage.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/inline/typescript/context/index/060-advanced-direct-invocationcontext-usage.ts"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/context/index/061-advanced-direct-invocationcontext-usage.java"
    ```

Setting `ctx.end_invocation = True` is a way to gracefully stop the entire request-response cycle from within the agent or its callbacks/tools (via their respective context objects which also have access to modify the underlying `InvocationContext`'s flag).

## Key Takeaways & Best Practices

*   **Use the Right Context:** Always use the most specific context object provided (`ToolContext` in tools/tool-callbacks, `CallbackContext` in agent/model-callbacks, `ReadonlyContext` where applicable). Use the full `InvocationContext` (`ctx`) directly in `_run_async_impl` / `_run_live_impl` only when necessary.
*   **State for Data Flow:** `context.state` is the primary way to share data, remember preferences, and manage conversational memory *within* an invocation. Use prefixes (`app:`, `user:`, `temp:`) thoughtfully when using persistent storage.
*   **Artifacts for Files:** Use `context.save_artifact` and `context.load_artifact` for managing file references (like paths or URIs) or larger data blobs. Store references, load content on demand.
*   **Tracked Changes:** Modifications to state or artifacts made via context methods are automatically linked to the current step's `EventActions` and handled by the `SessionService`.
*   **Start Simple:** Focus on `state` and basic artifact usage first. Explore authentication, memory, and advanced `InvocationContext` fields (like those for live streaming) as your needs become more complex.

By understanding and effectively using these context objects, you can build more sophisticated, stateful, and capable agents with ADK.
