# Local Development

The command-line interface (CLI) tools provided by the Agent Development Kit (ADK) helps developers run, evaluate, serve, and deploy agents.

The most common command is `adk web` which starts a local development UI for rapid experimentation and debugging with your agents.

**General Usage:**

```bash
adk [OPTIONS] COMMAND [ARGS]...
```

---

## Top-Level Commands

The main entry point `adk` provides access to the following commands:

* `web`: Start a FastAPI web server with a UI for interacting with agents.
* `run`: Run an interactive CLI session with a specific agent.
* `eval`: Evaluate an agent against predefined evaluation sets.
* `api_server`: Start a FastAPI server providing an API endpoint for agents (no UI).
* `deploy`: Deploy agents (contains subcommands like `cloud_run`).

---

## Command Details

---

### `adk web`

Starts a FastAPI server that includes a web user interface (UI) for interacting with agents located within a specified directory.

**Usage:**

```bash
adk web [OPTIONS] [AGENTS_DIR]
```

**Arguments:**

* `AGENTS_DIR` (Optional): The path to the directory containing agent subdirectories. Each subdirectory represents a single agent and must contain at least `__init__.py` and `agent.py`. Defaults to the current working directory (`.`).

**Options:**

* `--session_db_url` (Optional): Database connection URL for storing session state.
    * Vertex managed service: `agentengine://<agent_engine_resource_id>`
    * SQLite: `sqlite://<path_to_sqlite_file>`
    * See [SQLAlchemy URL docs](https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls) for others.
* `--port <port_number>` (Optional): Port number for the server. Default: `8000`.
* `--allow_origins <origin>` (Optional, Multiple): Additional origins to permit for Cross-Origin Resource Sharing (CORS). Can be specified multiple times.
* `--log_level <level>` (Optional): Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Case-insensitive. Default: `INFO`.
* `--log_to_tmp` (Flag): Log output to a file in the system's temporary directory instead of the console (stderr). Useful for local debugging. Default: `False`.
* `--trace_to_cloud` (Flag): Enable Cloud Trace integration for telemetry. Default: `False`.

**Example:**

```bash
# Start the web server for agents in the current directory on port 8080
adk web --port 8080

# Start the web server for agents in './all_my_agents' using a SQLite DB
adk web --session_db_url sqlite:///sessions.db ./all_my_agents

# Start with debug logging and allow a specific origin
adk web --log_level DEBUG --allow_origins http://localhost:3000 ./agents
```


### `adk run`

Runs an interactive command-line interface for a specific agent, allowing you to interact with it turn by turn.

**Usage:**

```bash
adk run [OPTIONS] AGENT
```

**Arguments:**

* `AGENT` (Required): The path to the directory containing the agent's source code (must exist).

**Options:**

* `--save_session` (Flag): If set, saves the interactive session history to a JSON file upon exiting. Default: `False`.

**Example:**

```bash
# Run the agent located in the 'my_chatbot' directory
adk run path/to/my_chatbot

# Run the agent and save the session on exit
adk run --save_session path/to/my_chatbot
```

---

### `adk eval`

Evaluates an agent's performance based on one or more evaluation sets defined in JSON files.

**Usage:**

```bash
adk eval [OPTIONS] AGENT_MODULE_FILE_PATH [EVAL_SET_FILE_PATH]...
```

**Arguments:**

* `AGENT_MODULE_FILE_PATH` (Required): The path to the directory containing the agent's `__init__.py` file, where the root agent module (`agent`) is defined.
* `EVAL_SET_FILE_PATH` (Required, one or more): Paths to the JSON files containing evaluation sets.
    * You can specify multiple files.
    * To run only specific evaluations within a file, append a colon (`:`) followed by a comma-separated list of evaluation names (e.g., `my_evals.json:eval_greeting,eval_completion`).

**Options:**

* `--config_file_path` (Optional): Path to a configuration file specifying evaluation criteria (metrics and thresholds).
* `--print_detailed_results` (Flag): If set, prints detailed results for each evaluation case to the console. Default: `False`.

**Example:**

```bash
# Evaluate the agent against all evals in 'eval_set1.json' and 'eval_set2.json'
adk eval path/to/my_agent eval_set1.json eval_set2.json

# Evaluate only 'eval_greeting' and 'eval_farewell' from 'main_evals.json'
adk eval path/to/my_agent main_evals.json:eval_greeting,eval_farewell

# Evaluate using a specific config and print details
adk eval --config_file_path eval_config.yaml --print_detailed_results path/to/my_agent tests.json
```

*(Note: This command requires additional dependencies. If missing, an error message will be displayed.)*

---

### `adk api_server`

Starts a FastAPI server providing only the API endpoints for agents within a specified directory (no web UI).

**Usage:**

```bash
adk api_server [OPTIONS] [AGENTS_DIR]
```

**Arguments:**

* `AGENTS_DIR` (Optional): The path to the directory containing agent subdirectories. Each subdirectory represents a single agent and must contain at least `__init__.py` and `agent.py`. Defaults to the current working directory (`.`).

**Options:**

* `--session_db_url` (Optional): Database connection URL for storing session state. (See `adk web` for formats).
* `--port <port_number>` (Optional): Port number for the server. Default: `8000`.
* `--allow_origins <origin>` (Optional, Multiple): Additional origins to permit for Cross-Origin Resource Sharing (CORS). Can be specified multiple times.
* `--log_level <level>` (Optional): Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Case-insensitive. Default: `INFO`.
* `--log_to_tmp` (Flag): Log output to a file in the system's temporary directory instead of the console (stderr). Default: `False`.
* `--trace_to_cloud` (Flag): Enable Cloud Trace integration for telemetry. Default: `False`.

**Example:**

```bash
# Start the API server for agents in the current directory on port 9000
adk api_server --port 9000

# Start the API server for agents in './my_prod_agents' using Vertex session service
adk api_server --session_db_url agentengine://my-agent-engine-id ./my_prod_agents
```

---

### `adk deploy`

A group of commands for deploying agents.  For more detailed information on deployment options, see [deployment documentation](../deploy/) and also check out [the Agent Starter Pack](http://goo.gle/agent-starter-pack).

**Usage:**

```bash
adk deploy [COMMAND] [ARGS]...
```

#### `adk deploy cloud_run`

Deploys a specific agent to Google Cloud Run as a containerized application (either API server or Web UI).

**Usage:**

```bash
adk deploy cloud_run [OPTIONS] AGENT
```

**Arguments:**

* `AGENT` (Required): The path to the directory containing the specific agent's source code to be deployed.

**Options:**

* `--project <gcp_project_id>` (Optional): Google Cloud Project ID. If omitted, uses the default project from your `gcloud` configuration. **Required if no default is set.**
* `--region <gcp_region>` (Optional): Google Cloud Region for deployment. If omitted, `gcloud run deploy` will prompt for it. **Required if no default is set.**
* `--service_name <name>` (Optional): Name for the Cloud Run service. Default: `adk-default-service-name`.
* `--app_name <name>` (Optional): Application name for the ADK server within the container. Defaults to the base name of the `AGENT` directory.
* `--port <port_number>` (Optional): Port the ADK server will listen on inside the container. Default: `8000`. (Cloud Run routes external port 443 to this port).
* `--with_cloud_trace` (Flag): Enable Cloud Trace integration for the deployed Cloud Run service. Default: `False`.
* `--with_ui` (Flag): Deploy the ADK Web UI server. If not set, deploys the ADK API server only. Default: `False`.
* `--temp_folder <path>` (Optional): Specifies a temporary directory to store generated source files for the Cloud Run deployment. Defaults to a timestamped subfolder within the system's temp directory (e.g., `/tmp/cloud_run_deploy_src/YYYYMMDD_HHMMSS`).

**Example:**

```bash
# Deploy the agent in 'my_agent' to Cloud Run (API only)
adk deploy cloud_run --project my-gcp-project --region us-central1 path/to/my_agent

# Deploy the agent in 'my_ui_agent' with the Web UI and custom service name
adk deploy cloud_run --project my-gcp-project --region europe-west1 \
    --service_name my-agent-service --with_ui path/to/my_ui_agent

# Deploy with Cloud Trace enabled
adk deploy cloud_run --project my-gcp-project --region us-central1 \
    --with_cloud_trace path/to/my_agent
```
