package agents.workflow;

// --8<-- [start:init]

import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.SequentialAgent;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;

public class SequentialAgentExample {

  private static final String APP_NAME = "CodePipelineAgent";
  private static final String USER_ID = "test_user_456";
  private static final String MODEL_NAME = "gemini-2.0-flash";

  public static void main(String[] args) {
    SequentialAgentExample sequentialAgentExample = new SequentialAgentExample();
    sequentialAgentExample.runAgent(
        "Write a Java function to calculate the factorial of a number.");
  }

  public void runAgent(String prompt) {

    LlmAgent codeWriterAgent =
        LlmAgent.builder()
            .model(MODEL_NAME)
            .name("CodeWriterAgent")
            .description("Writes initial Java code based on a specification.")
            .instruction(
                """
                You are a Java Code Generator.
                Based *only* on the user's request, write Java code that fulfills the requirement.
                Output *only* the complete Java code block, enclosed in triple backticks (```java ... ```).
                Do not add any other text before or after the code block.
                """)
            .outputKey("generated_code")
            .build();

    LlmAgent codeReviewerAgent =
        LlmAgent.builder()
            .model(MODEL_NAME)
            .name("CodeReviewerAgent")
            .description("Reviews code and provides feedback.")
            .instruction(
                """
                    You are an expert Java Code Reviewer.
                    Your task is to provide constructive feedback on the provided code.

                    **Code to Review:**
                    ```java
                    {generated_code}
                    ```

                    **Review Criteria:**
                    1.  **Correctness:** Does the code work as intended? Are there logic errors?
                    2.  **Readability:** Is the code clear and easy to understand? Follows Java style guidelines?
                    3.  **Efficiency:** Is the code reasonably efficient? Any obvious performance bottlenecks?
                    4.  **Edge Cases:** Does the code handle potential edge cases or invalid inputs gracefully?
                    5.  **Best Practices:** Does the code follow common Java best practices?

                    **Output:**
                    Provide your feedback as a concise, bulleted list. Focus on the most important points for improvement.
                    If the code is excellent and requires no changes, simply state: "No major issues found."
                    Output *only* the review comments or the "No major issues" statement.
                """)
            .outputKey("review_comments")
            .build();

    LlmAgent codeRefactorerAgent =
        LlmAgent.builder()
            .model(MODEL_NAME)
            .name("CodeRefactorerAgent")
            .description("Refactors code based on review comments.")
            .instruction(
                """
                You are a Java Code Refactoring AI.
                Your goal is to improve the given Java code based on the provided review comments.

                  **Original Code:**
                  ```java
                  {generated_code}
                  ```

                  **Review Comments:**
                  {review_comments}

                **Task:**
                Carefully apply the suggestions from the review comments to refactor the original code.
                If the review comments state "No major issues found," return the original code unchanged.
                Ensure the final code is complete, functional, and includes necessary imports and docstrings.

                **Output:**
                Output *only* the final, refactored Java code block, enclosed in triple backticks (```java ... ```).
                Do not add any other text before or after the code block.
                """)
            .outputKey("refactored_code")
            .build();

    SequentialAgent codePipelineAgent =
        SequentialAgent.builder()
            .name(APP_NAME)
            .description("Executes a sequence of code writing, reviewing, and refactoring.")
            // The agents will run in the order provided: Writer -> Reviewer -> Refactorer
            .subAgents(codeWriterAgent, codeReviewerAgent, codeRefactorerAgent)
            .build();

    // Create an InMemoryRunner
    InMemoryRunner runner = new InMemoryRunner(codePipelineAgent, APP_NAME);
    // InMemoryRunner automatically creates a session service. Create a session using the service
    Session session = runner.sessionService().createSession(APP_NAME, USER_ID).blockingGet();
    Content userMessage = Content.fromParts(Part.fromText(prompt));

    // Run the agent
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    // Stream event response
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }
}
// --8<-- [end:init]
