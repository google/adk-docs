# ADK Web Server API Reference

The ADK web server provides a set of RESTful APIs to interact with your
applications.

## Endpoints

### /list-apps

*   **Method:** `GET`
*   **Description:** Lists the available applications.
*   **Query Parameters:**
    *   `detailed` (optional, boolean, default: `false`): If `true`, returns
        a detailed list of applications.
*   **Response:**
    *   If `detailed` is `false` or not provided, the response is a JSON
        array of strings, where each string is the name of an application.

        **Example:**

        ```json
        [
          "app1",
          "app2"
        ]
        ```
    *   If `detailed` is `true`, the response is a JSON object containing a
        list of application information objects.

        **Example:**

        ```json
        {
          "apps": [
            {
              "name": "my-app",
              "root_agent_name": "my-agent",
              "description": "A sample application.",
              "language": "python"
            }
          ]
        }
        ```
*   **Example Usage:**
    *   `curl http://localhost:8080/list-apps`
    *   `curl http://localhost:8080/list-apps?detailed=true`
