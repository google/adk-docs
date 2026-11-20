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

// A `JoinNode` is a fan-in barrier: it waits for EVERY predecessor to finish
// and then hands the next node a map keyed by predecessor node name.

// --8<-- [start:fan-out-join]
import com.google.adk.agents.Context;
import com.google.adk.workflow.JoinNode;
import com.google.adk.workflow.Node;
import com.google.adk.workflow.Workflow;
import com.google.genai.types.Content;
import io.reactivex.rxjava3.core.Flowable;
import java.util.Map;
import java.util.function.BiFunction;

public final class FanOutJoinExample {

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

  public static Workflow create() {
    Node parallelTaskA =
        node("parallel_task_A", (ctx, input) -> Flowable.just(asText(input).toUpperCase()));

    Node parallelTaskB =
        node("parallel_task_B", (ctx, input) -> Flowable.just(asText(input).length()));

    Node parallelTaskC =
        node(
            "parallel_task_C",
            (ctx, input) -> Flowable.just(new StringBuilder(asText(input)).reverse().toString()));

    JoinNode myJoinNode = JoinNode.builder().name("my_join_node").build();

    Node finalTaskD =
        node(
            "final_task_D",
            (ctx, input) -> {
              Map<?, ?> results = (Map<?, ?>) input;
              return Flowable.just(
                  String.join(
                      "\n",
                      "Uppercase: " + results.get("parallel_task_A"),
                      "Length:    " + results.get("parallel_task_B"),
                      "Reversed:  " + results.get("parallel_task_C")));
            });

    return Workflow.builder()
        .name("fan_out_workflow")
        .edges(
            g ->
                g.fromStart()
                    .then(parallelTaskA, parallelTaskB, parallelTaskC)
                    .joinTo(myJoinNode)
                    .then(finalTaskD))
        .build();
  }
}
// --8<-- [end:fan-out-join]
