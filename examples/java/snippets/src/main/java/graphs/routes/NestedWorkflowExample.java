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

// A `Workflow` is itself a node, so you can use one inside another workflow's
// edges to encapsulate a reusable sub-process.

// --8<-- [start:nested-workflow]
import com.google.adk.agents.Context;
import com.google.adk.workflow.Node;
import com.google.adk.workflow.Route;
import com.google.adk.workflow.Workflow;
import com.google.genai.types.Content;
import io.reactivex.rxjava3.core.Flowable;
import java.util.Arrays;
import java.util.List;
import java.util.function.BiFunction;
import java.util.stream.Collectors;

public final class NestedWorkflowExample {

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

  /** Upper-cases the first letter of each word. */
  private static String titleCase(String text) {
    return Arrays.stream(text.split(" ", -1))
        .map(
            word ->
                word.isEmpty()
                    ? word
                    : Character.toTitleCase(word.charAt(0)) + word.substring(1))
        .collect(Collectors.joining(" "));
  }

  public static Workflow create() {
    Node taskA1 = node("task_A1", (ctx, input) -> Flowable.just(asText(input).trim()));

    Node router =
        node(
            "router",
            (ctx, input) -> {
              String text = (String) input;
              String route = text.equals(text.toUpperCase()) ? "RUN_WORKFLOW_C" : "RUN_WORKFLOW_B";
              ctx.routes(List.of(new Route.Tag(route)));
              return Flowable.just(text);
            });

    Workflow workflowB =
        Workflow.builder()
            .name("workflow_B")
            .edges(
                g ->
                    g.fromStart()
                        .chain(
                            node("b_title_case", (ctx, text) -> Flowable.just(titleCase((String) text))),
                            node("b_frame", (ctx, text) -> Flowable.just("[B] " + text))))
            .build();

    Workflow workflowC =
        Workflow.builder()
            .name("workflow_C")
            .edges(
                g ->
                    g.fromStart()
                        .chain(
                            node("c_lower_case", (ctx, text) -> Flowable.just(((String) text).toLowerCase())),
                            node("c_frame", (ctx, text) -> Flowable.just("[C] " + text))))
            .build();

    return Workflow.builder()
        .name("parent_workflow")
        .edges(
            g ->
                g.fromStart()
                    .chain(taskA1, router)
                    .route(
                        r -> {
                          r.on("RUN_WORKFLOW_B").then(workflowB);
                          r.on("RUN_WORKFLOW_C").then(workflowC);
                        }))
        .build();
  }
}
// --8<-- [end:nested-workflow]
