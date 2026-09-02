import com.google.adk.artifacts.BaseArtifactService;
import com.google.adk.artifacts.InMemoryArtifactService;

public class InMemoryServiceSetup {
    public static void main(String[] args) {
        // Simply instantiate the class
        BaseArtifactService inMemoryServiceJava = new InMemoryArtifactService();

        System.out.println("InMemoryArtifactService (Java) instantiated: " + inMemoryServiceJava.getClass().getName());

        // This instance would then be provided to your Runner.
        // Runner runner = new Runner(
        //     /* other services */,
        //     inMemoryServiceJava
        // );
    }
}