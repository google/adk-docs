    import com.google.adk.tools.applicationintegrationtoolset.ApplicationIntegrationToolset;
    import com.google.common.collect.ImmutableList;
    import com.google.common.collect.ImmutableMap;

    public class Tools {
        private static ApplicationIntegrationToolset integrationTool;
        private static ApplicationIntegrationToolset connectionsTool;

        static {
            integrationTool = new ApplicationIntegrationToolset(
                    "test-project",
                    "us-central1",
                    "test-integration",
                    ImmutableList.of("api_trigger/test-api"),
                    null,
                    null,
                    null,
                    "{...}",
                    "tool_prefix1",
                    "...");

            connectionsTool = new ApplicationIntegrationToolset(
                    "test-project",
                    "us-central1",
                    null,
                    null,
                    "test-connection",
                    ImmutableMap.of("Issue", ImmutableList.of("GET")),
                    ImmutableList.of("ExecuteCustomQuery"),
                    "{...}",
                    "tool_prefix",
                    "...");
        }
    }