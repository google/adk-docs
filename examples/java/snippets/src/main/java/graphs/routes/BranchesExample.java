/*
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package graphs.routes;

// Branching is a node that selects a route, plus a routing map from each route
// value to the node that handles it. A branch target can be any Node:
// `taskBNode` here is an `LlmAgent`, and `taskCNode` is a custom node.

// --8<-- [start:branches]
import com.google.adk.agents.Context;
import com.google.adk.agents.LlmAgent;
import com.google.adk.workflow.Node;
import com.google.adk.workflow.Route;
import com.google.adk.workflow.Workflow;
import com.google.genai.types.Content;
import io.reactivex.rxjava3.core.Flowable;
import java.util.List;
import java.util.function.BiFunction;

public final class BranchesExample {

  private static Node node(String name, BiFunction<Context, Object, Flowable<?>> fn) {
    return new Node() {
      @Override
      public String name() {
        return name;
      }

      @Override
      public Flowable<?> runNode(Context context, Object nodeInput) {
        return fn.apply(context, nodeInput);
      }
    };
  }

  private static String asText(Object nodeInput) {
    if (nodeInput instanceof Content content && content.text() != null) {
      return content.text();
    }
    return nodeInput != null ? nodeInput.toString() : "";
  }

  /** Stands in for an application-specific branch condition. */
  private static boolean condition(String nodeInput) {
    return nodeInput.chars().anyMatch(Character::isDigit);
  }

  public static Workflow create() {
    Node taskANode = node("task_A_node", (ctx, input) -> Flowable.just(asText(input).trim()));

    // Routes to task B or C based on nodeInput.
    Node router =
        node(
            "router",
            (ctx, input) -> {
              String text = (String) input;
              String route = condition(text) ? "RUN_TASK_C" : "RUN_TASK_B";
              ctx.routes(List.of(new Route.Tag(route)));
              return Flowable.just(text);
            });

    LlmAgent taskBNode =
        LlmAgent.builder()
            .name("task_B_agent")
            .model("gemini-flash-latest")
            .instruction("Answer the user in a single short sentence.")
            .build();

    Node taskCNode = node("task_C_node", (ctx, input) -> Flowable.just("Task C completed"));

    return Workflow.builder()
        .name("routing_workflow")
        .edges(
            g ->
                g.fromStart()
                    .chain(taskANode, router)
                    .route(
                        r -> {
                          // "route value" -> node to run
                          r.on("RUN_TASK_B").then(taskBNode);
                          r.on("RUN_TASK_C").then(taskCNode);
                        }))
        .build();
  }
}
// --8<-- [end:branches]
