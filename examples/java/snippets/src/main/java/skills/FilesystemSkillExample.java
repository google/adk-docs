package skills;

// --8<-- [start:full_example]
import com.google.adk.skills.LocalSkillSource;
import com.google.adk.skills.SkillSource;
import com.google.adk.tools.skills.SkillToolset;
import java.nio.file.Path;

public class FilesystemSkillExample {

  public static SkillToolset createSkillToolset() {
    // LocalSkillSource discovers every immediate subdirectory of "skills" that
    // contains a SKILL.md file. To load skills from the classpath instead, use
    // new ClassPathSkillSource("skills/").
    SkillSource filesystemSource = new LocalSkillSource(Path.of("skills"));

    return new SkillToolset(filesystemSource);
  }
}
// --8<-- [end:full_example]
