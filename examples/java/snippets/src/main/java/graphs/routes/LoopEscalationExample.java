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

// A loop is a BACK-EDGE in the graph: a downstream node routes back to an
// earlier node, and the engine re-activates that node with a fresh lifecycle on
// each iteration. The loop exits when the critic picks the terminal branch.
//
//   START -> seed_draft -> critic --REVISE--> refine --+
//                            ^                         |
//                            +-------------------------+
//                          critic --DONE--> finalize

// --8<-- [start:loop-escalation]
import com.google.adk.agents.Context;
import com.google.adk.workflow.Node;
import com.google.adk.workflow.Route;
import com.google.adk.workflow.Workflow;
import com.google.genai.types.Content;
import io.reactivex.rxjava3.core.Flowable;
import java.util.ArrayList;
import java.util.List;
import java.util.function.BiFunction;
import java.util.stream.Collectors;

public final class LoopEscalationExample {

  /** The critic is satisfied once the draft has at least this many bullets. */
  private static final int REQUIRED_BULLETS = 3;

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
    // The draft is its list of bullets; the topic is kept in session state.
    Node seedDraft =
        node(
            "seed_draft",
            (ctx, input) -> {
              String topic = asText(input).trim();
              ctx.state().put("topic", topic);
              return Flowable.just(List.of(topic + " — point 1"));
            });

    Node critic =
        node(
            "critic",
            (ctx, input) -> {
              List<?> bullets = (List<?>) input;
              String route = bullets.size() >= REQUIRED_BULLETS ? "DONE" : "REVISE";
              ctx.routes(List.of(new Route.Tag(route)));
              return Flowable.just(bullets);
            });

    Node refine =
        node(
            "refine",
            (ctx, input) -> {
              List<?> bullets = (List<?>) input;
              List<Object> updated = new ArrayList<>(bullets);
              updated.add(ctx.state().get("topic") + " — point " + (bullets.size() + 1));
              return Flowable.just(List.copyOf(updated));
            });

    Node finalize =
        node(
            "finalize",
            (ctx, input) -> {
              List<?> bullets = (List<?>) input;
              String body =
                  bullets.stream().map(b -> "  • " + b).collect(Collectors.joining("\n"));
              return Flowable.just("Approved after " + bullets.size() + " bullets:\n" + body);
            });

    return Workflow.builder()
        .name("loop_workflow")
        .edges(
            g -> {
              g.fromStart()
                  .chain(seedDraft, critic)
                  .route(
                      r -> {
                        r.on("REVISE").then(refine);
                        r.on("DONE").then(finalize);
                      });
              g.from(refine).then(critic); // back-edge: loop back for another review
            })
        .build();
  }
}
// --8<-- [end:loop-escalation]
