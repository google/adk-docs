# Configuring streaming behaviour

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.5.0</span><span class="lst-preview">Experimental</span>
</div>

There are some configurations you can set for live(streaming) agents. 

It's set by [RunConfig](https://github.com/google/adk-python/blob/main/src/google/adk/agents/run_config.py). You should use RunConfig with your [Runner.run_live(...)](https://github.com/google/adk-python/blob/main/src/google/adk/runners.py). 

For example, if you want to set voice config, you can leverage speech_config. 

==="Python"
```python
voice_config = genai_types.VoiceConfig(
    prebuilt_voice_config=genai_types.PrebuiltVoiceConfigDict(
        voice_name='Aoede'
    )
)
speech_config = genai_types.SpeechConfig(voice_config=voice_config)
run_config = RunConfig(speech_config=speech_config)

runner.run_live(
    ...,
    run_config=run_config,
)
```
==="Java"
```
package agents;

import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import io.reactivex.rxjava3.core.Flowable;

public class GeminiStreamingAgent {
  public static BaseAgent ROOT_AGENT = initAgent();

  private static BaseAgent initAgent() {
    return LlmAgent.builder()
        .name("gemini-streaming-agent")
        .description("Agent demonstrating Gemini Live streaming")
        .model("gemini-2.0-flash-live-001")
        .instruction("Respond in streaming mode. Use concise messages.")
        .build();
  }

  public static void main(String[] args) {
    InMemorySessionService sessionService = new InMemorySessionService();
    Runner runner = new Runner(ROOT_AGENT, "GeminiLiveApp", null, sessionService);

    var session = sessionService.createSession("GeminiLiveApp", "user1").blockingGet();

    // Demonstrate streaming via console
    Flowable<Event> stream = runner.runLive(session.userId(), session.id(), "What's trending in AI today?");

    stream.subscribe(event -> {
      System.out.print(event.stringifyContent());
    }, err -> {
      err.printStackTrace();
    }, () -> {
      System.out.println("\n［Stream Complete］");
    });
  }
}
```


