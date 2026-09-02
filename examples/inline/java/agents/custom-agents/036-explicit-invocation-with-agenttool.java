// Conceptual Setup: Agent as a Tool
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.AgentTool;

// Example custom agent (could be LlmAgent or custom BaseAgent)
public class ImageGeneratorAgent extends BaseAgent  {


  public ImageGeneratorAgent(String name, String description) {
    super(name, description, List.of(), null, null);
  }


  // ... internal logic ...
  @Override
  protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) { // Simplified run logic
    invocationContext.session().state().get("image_prompt");
    // Generate image bytes
    // ...


    Event responseEvent = Event.builder()
        .author(this.name())
        .content(Content.fromParts(Part.fromText("...")))
        .build();


    return Flowable.just(responseEvent);
  }


  @Override
  protected Flowable<Event> runLiveImpl(InvocationContext invocationContext) {
    return null;
  }
}

// Wrap the agent using AgentTool
ImageGeneratorAgent imageAgent = new ImageGeneratorAgent("image_agent", "generates images");
AgentTool imageTool = AgentTool.create(imageAgent);


// Parent agent uses the AgentTool
LlmAgent artistAgent = LlmAgent.builder()
        .name("Artist")
        .model("gemini-flash-latest")
        .instruction(
                "You are an artist. Create a detailed prompt for an image and then " +
                        "use the 'ImageGen' tool to generate the image. " +
                        "The 'ImageGen' tool expects a single string argument named 'request' " +
                        "containing the image prompt. The tool will return a JSON string in its " +
                        "'result' field, containing 'image_base64', 'mime_type', and 'status'."
        )
        .description("An agent that can create images using a generation tool.")
        .tools(imageTool) // Include the AgentTool
        .build();


// Artist LLM generates a prompt, then calls:
// FunctionCall(name='ImageGen', args={'imagePrompt': 'a cat wearing a hat'})
// Framework calls imageTool.runAsync(...), which runs ImageGeneratorAgent.
// The resulting image Part is returned to the Artist agent as the tool result.