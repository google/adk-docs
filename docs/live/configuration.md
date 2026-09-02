# Configuring streaming behavior

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.5.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-preview">Experimental</span>
</div>

There are some configurations you can set for live(streaming) agents. 

It's set by [RunConfig](https://github.com/google/adk-python/blob/main/src/google/adk/agents/run_config.py). You should use RunConfig with your [Runner.run_live(...)](https://github.com/google/adk-python/blob/main/src/google/adk/runners.py). 

For example, if you want to set voice config, you can leverage speech_config. 

=== "Python"

    ```python
    --8<-- "examples/inline/python/live/configuration/001-configuring-streaming-behavior.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/inline/java/live/configuration/002-configuring-streaming-behavior.java"
    ```


