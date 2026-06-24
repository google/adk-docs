package a2a;

import com.google.adk.core.BaseAgent;
import com.google.adk.core.LlmAgent;
import com.google.adk.a2a.RemoteA2AAgent;
import io.a2a.client.Client;
import io.a2a.client.config.ClientConfig;
import io.a2a.client.http.A2ACardResolver;
import io.a2a.client.http.JdkA2AHttpClient;
import io.a2a.client.transport.jsonrpc.JSONRPCTransport;
import io.a2a.client.transport.jsonrpc.JSONRPCTransportConfig;
import io.a2a.spec.AgentCard;

public class A2aConsumerSnippet {
    public static void main(String[] args) throws Exception {
        // --8<-- [start:new-prime-agent]
        String primeAgentBaseUrl = "http://localhost:9090";
        String agentCardUrl = primeAgentBaseUrl + "/.well-known/agent-card.json";
        
        // 1. Resolve the public AgentCard from the remote agent's .well-known endpoint
        AgentCard publicAgentCard = new A2ACardResolver(
            new JdkA2AHttpClient(), 
            primeAgentBaseUrl, 
            agentCardUrl
        ).getAgentCard();

        // 2. Build the official A2A SDK Client using the resolved card and transport
        Client a2aClient = Client.builder(publicAgentCard)
            .withTransport(JSONRPCTransport.class, new JSONRPCTransportConfig())
            .clientConfig(
                new ClientConfig.Builder()
                    .setStreaming(publicAgentCard.capabilities().streaming())
                    .build()
            )
            .build();

        // 3. Wrap it in the ADK's RemoteA2AAgent natively
        BaseAgent remotePrimeAgent = RemoteA2AAgent.builder()
            .name(publicAgentCard.name())
            .a2aClient(a2aClient)
            .agentCard(publicAgentCard)
            .build();
        // --8<-- [end:new-prime-agent]

        // --8<-- [start:new-root-agent]
        BaseAgent rootAgent = LlmAgent.builder()
            .name("root_agent")
            .model("gemini-2.5-flash")
            .instruction("You are a helpful assistant that can check prime numbers by delegating to prime_agent.")
            .subAgents(remotePrimeAgent)
            .build();
        // --8<-- [end:new-root-agent]
    }
}
