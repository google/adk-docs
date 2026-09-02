---
catalog_title: Apigee API Hub
catalog_description: Turn any documented API from Apigee API hub into a tool
catalog_icon: /integrations/assets/apigee.png
catalog_tags: ["connectors", "google"]
---

# Apigee API Hub tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

**ApiHubToolset** lets you turn any documented API from Apigee API hub into a
tool with a few lines of code. This section shows you the step-by-step
instructions including setting up authentication for a secure connection to your
APIs.

**Prerequisites**

1. [Install ADK](/get-started/installation/)
2. Install the
   [Google Cloud CLI](https://cloud.google.com/sdk/docs/install?db=bigtable-docs#installation_instructions).
3. [Apigee API hub](https://cloud.google.com/apigee/docs/apihub/what-is-api-hub)
    instance with documented (i.e. OpenAPI spec) APIs
4. Set up your project structure and create required files

```console
project_root_folder
 |
 `-- my_agent
     |-- .env
     |-- __init__.py
     |-- agent.py
     `__ tool.py
```

## Create an API Hub Toolset

Note: This tutorial includes an agent creation. If you already have an agent,
you only need to follow a subset of these steps.

1. Get your access token, so that APIHubToolset can fetch spec from API Hub API.
   In your terminal run the following command

    ```shell
    gcloud auth print-access-token
    # Prints your access token like 'ya29....'
    ```

2. Ensure that the account used has the required permissions. You can use the
   pre-defined role `roles/apihub.viewer` or assign the following permissions:

    1. **apihub.specs.get (required)**
    2. apihub.apis.get (optional)
    3. apihub.apis.list (optional)
    4. apihub.versions.get (optional)
    5. apihub.versions.list (optional)
    6. apihub.specs.list (optional)

3. Create a tool with `APIHubToolset`. Add the below to `tools.py`

    If your API requires authentication, you must configure authentication for
    the tool. The following code sample demonstrates how to configure an API
    key. ADK supports token based auth (API Key, Bearer token), service account,
    and OpenID Connect. We will soon add support for various OAuth2 flows.

    ```py
    --8<-- "examples/inline/python/integrations/apigee-api-hub/001-create-an-api-hub-toolset.py"
    ```

    For production deployment we recommend using a service account instead of an
    access token. In the code snippet above, use
    `service_account_json=service_account_cred_json_str` and provide your
    security account credentials instead of the token.

    For apihub\_resource\_name, if you know the specific ID of the OpenAPI Spec
    being used for your API, use
    `` `projects/my-project-id/locations/us-west1/apis/my-api-id/versions/version-id/specs/spec-id` ``.
    If you would like the Toolset to automatically pull the first available spec
    from the API, use
    `` `projects/my-project-id/locations/us-west1/apis/my-api-id` ``

4. Create your agent file Agent.py and add the created tools to your agent
   definition:

    ```py
    --8<-- "examples/inline/python/integrations/apigee-api-hub/002-create-an-api-hub-toolset.py"
    ```

5. Configure your `__init__.py` to expose your agent

    ```py
    --8<-- "examples/inline/python/integrations/apigee-api-hub/003-create-an-api-hub-toolset.py"
    ```

6. Start the Google ADK Web UI and try your agent:

    ```shell
    # make sure to run `adk web` from your project_root_folder
    adk web
    ```

   Then go to [http://localhost:8000](http://localhost:8000) to try your agent from the Web UI.
