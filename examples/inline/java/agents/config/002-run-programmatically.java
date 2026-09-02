import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.ConfigAgentUtils;

public class AgentApp {
    public static void main(String[] args) throws Exception {
        // Load the agent directly from the YAML config file
        BaseAgent agent = ConfigAgentUtils.fromConfig("my_agent/root_agent.yaml");
        // ...
    }
}