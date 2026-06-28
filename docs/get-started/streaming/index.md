# Build a streaming agent

The Agent Development Kit (ADK) enables real-time, interactive experiences with your AI agents through streaming. This allows for features like live voice conversations, real-time tool use, and continuous updates from your agent.

This page provides quickstart examples to get you up and running with streaming capabilities in both Python and Java ADK.

<div class.="grid cards" markdown>

-   :fontawesome-brands-python:{ .lg .middle } **Python ADK: Streaming agent**

    ---
    This example demonstrates how to set up a basic streaming interaction with an agent using Python ADK. It typically involves using the `Runner.run_live()` method and handling asynchronous events.

    [:octicons-arrow-right-24: View Python Streaming Quickstart](quickstart-streaming.md) <br>
    <!-- [:octicons-arrow-right-24: View Python Streaming Quickstart](python/quickstart-streaming.md) -->

<!-- This comment forces a block separation -->

-   :fontawesome-brands-java:{ .lg .middle } **Java ADK: Streaming agent**

    ---
    This example demonstrates how to set up a basic streaming interaction with an agent using Java ADK. It involves using the `Runner.runLive()` method, a `LiveRequestQueue`, and handling the `Flowable<Event>` stream.

    [:octicons-arrow-right-24: View Java Streaming Quickstart](quickstart-streaming-java.md) <br>
    <!-- [:octicons-arrow-right-24: View Java Streaming Quickstart](java/quickstart-streaming-java.md)) -->

</div>
