import com.google.adk.agents.LlmAgent;
import com.google.adk.models.ApigeeLlm;
import com.google.common.collect.ImmutableMap;

ApigeeLlm apigeeLlm =
        ApigeeLlm.builder()
            .modelName("apigee/gemini-flash-latest") // Specify the Apigee route to your model. For more info, check out the ApigeeLlm documentation
            .proxyUrl(APIGEE_PROXY_URL) //The proxy URL of your deployed Apigee proxy including the base path
            .customHeaders(ImmutableMap.of("foo", "bar")) //Pass necessary authentication/authorization headers (like an API key)
            .build();
LlmAgent agent =
    LlmAgent.builder()
        .model(apigeeLlm)
        .name("my_governed_agent")
        .description("my_governed_agent")
        .instruction("You are a helpful assistant powered by Gemini and governed by Apigee.")
        // tools will be added next
        .build();