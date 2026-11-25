package skills;

// --8<-- [start:full_example]
import com.google.adk.agents.LlmAgent;
import com.google.adk.skills.Frontmatter;
import com.google.adk.skills.InMemorySkillSource;
import com.google.adk.skills.SkillSource;
import com.google.adk.tools.skills.SkillToolset;

public class InlineSkillExample {

  public static void main(String[] args) {
    SkillSource skillSource =
        InMemorySkillSource.builder()
            .skill("greeting-skill")
            .frontmatter(
                Frontmatter.builder()
                    .name("greeting-skill")
                    .description(
                        "A friendly greeting skill that can say hello to a specific person.")
                    .build())
            .instructions(
                "Step 1: Read the 'references/hello_world.txt' file to understand how"
                    + " to greet the user. Step 2: Return a greeting based on the reference.")
            .addResource("references/hello_world.txt", "Hello! So glad to have you here!")
            .addResource("references/example.md", "This is an example reference.")
            .build();

    SkillToolset mySkillToolset = new SkillToolset(skillSource);

    LlmAgent rootAgent =
        LlmAgent.builder()
            .model("gemini-flash-latest")
            .name("greeting_agent")
            .description("An agent that uses an inline greeting skill.")
            .instruction("You are a helpful assistant that uses skills to greet people.")
            .tools(mySkillToolset)
            .build();
  }
}
// --8<-- [end:full_example]
