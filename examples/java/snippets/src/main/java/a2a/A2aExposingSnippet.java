package a2a;

// --8<-- [start:a2a-launcher]
import com.google.adk.a2a.executor.AgentExecutorConfig;
import com.google.adk.core.BaseAgent;
import com.google.adk.core.LlmAgent;
import com.google.adk.sessions.InMemorySessionService;
import io.a2a.server.agentexecution.AgentExecutor;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Produces;

import com.google.adk.artifacts.InMemoryArtifactService;

/**
 * Exposing an agent to the A2A network using ADK's Quarkus module.
 * By defining an AgentExecutor as a CDI @Produces, the framework
 * automatically binds your agent to the A2A endpoint.
 */
@ApplicationScoped
public class A2aExposingSnippet {
    
    @Produces
    public AgentExecutor agentExecutor() {
        BaseAgent myRemoteAgent = LlmAgent.builder()
            .name("prime_agent")
            .model("gemini-2.5-flash")
            .instruction("You are an expert in mathematics. Check if numbers are prime.")
            .build();

        return new com.google.adk.a2a.executor.AgentExecutor.Builder()
            .agent(myRemoteAgent)
            .appName("my-adk-a2a-server")
            .sessionService(new InMemorySessionService())
            .artifactService(new InMemoryArtifactService())
            .agentExecutorConfig(AgentExecutorConfig.builder().build())
            .build();
    }
}
// --8<-- [end:a2a-launcher]
