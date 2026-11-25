package skills;

// --8<-- [start:full_example]
import com.google.adk.skills.LocalSkillSource;
import com.google.adk.skills.SkillSource;
import com.google.adk.tools.skills.SkillToolset;
import java.nio.file.Path;

public class FilesystemSkillExample {

  public static void main(String[] args) {
    // Every immediate subdirectory of "skills" that contains a SKILL.md is
    // discovered automatically.
    SkillSource filesystemSource = new LocalSkillSource(Path.of("skills"));

    SkillToolset mySkillToolset = new SkillToolset(filesystemSource);
  }
}
// --8<-- [end:full_example]
