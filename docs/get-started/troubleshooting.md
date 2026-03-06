# ADK roubleshooting guide

## Gemini troubleshooting

### Error Code 429 - RESOURCE_EXHAUSTED

This error usually happens if the number of your requests exceeds the capacity allocated to process requests.

To mitigate this, you can do one of the following:

1.  Request higher quota limits for the model you are trying to use.

2.  Enable client-side retries. Retries allow the client to automatically retry the request after a delay, which can help if the quota issue is temporary.

    There are two ways you can set retry options:

    **Option 1:** Set retry options on the Agent as a part of generate_content_config.

    You would use this option if you are instantiating this model adapter by
    yourself.

    ```python
    root_agent = Agent(
        model='gemini-2.5-flash',
        ...
        generate_content_config=types.GenerateContentConfig(
            ...
            http_options=types.HttpOptions(
                ...
                retry_options=types.HttpRetryOptions(initial_delay=1, attempts=2),
                ...
            ),
            ...
        )
    ```

    **Option 2:** Retry options on this model adapter.

    You would use this option if you were instantiating the instance of adapter
    by yourself.

    ```python
    from google.genai import types

    # ...

    agent = Agent(
        model=Gemini(
        retry_options=types.HttpRetryOptions(initial_delay=1, attempts=2),
        )
    )
    ```