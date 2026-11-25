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

package graphs.index;

// A prompt-based agent turned into a graph: one agent classifies the message,
// a router node selects the categories as routes, and the graph dispatches to
// the matching handler(s). Because the classifier may return more than one
// category, the router selects a list of routes and every matching branch fires.

// --8<-- [start:process-pipeline]
import com.google.adk.agents.Context;
import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.workflow.Node;
import com.google.adk.workflow.Route;
import com.google.adk.workflow.Workflow;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import java.util.Arrays;
import java.util.List;

public final class ProcessPipeline {

  private static Node messageNode(String name, String text) {
    return new Node() {
      @Override
      public String name() {
        return name;
      }

      @Override
      public Flowable<?> runNode(Context context, Object nodeInput) {
        return Flowable.just(
            Event.builder()
                .id(context.invocationContext().newUuid())
                .content(Content.builder().role("model").parts(Part.fromText(text)).build())
                .build());
      }
    };
  }

  public static Workflow createRootAgent() {
    LlmAgent processMessage =
        LlmAgent.builder()
            .name("process_message")
            .model("gemini-flash-latest")
            .instruction(
                """
                Classify user message into either "BUG", "CUSTOMER_SUPPORT",
                or "LOGISTICS". If you think a message applies to more than one category,
                reply with a comma separated list of categories.
                """)
            .outputKey("categories")
            .build();

    Node router =
        new Node() {
          @Override
          public String name() {
            return "router";
          }

          @Override
          public Flowable<?> runNode(Context context, Object nodeInput) {
            String classification = String.valueOf(context.state().get("categories"));
            List<Route> routes =
                Arrays.stream(classification.split(","))
                    .map(String::trim)
                    .filter(tag -> !tag.isEmpty())
                    .<Route>map(Route.Tag::new)
                    .toList();
            context.routes(routes);
            return Flowable.empty();
          }
        };

    Node response1Bug = messageNode("response_1_bug", "Handling bug...");
    Node response2Support = messageNode("response_2_support", "Handling customer support...");
    Node response3Logistics = messageNode("response_3_logistics", "Handling logistics...");

    return Workflow.builder()
        .name("routing_workflow")
        .edges(
            g ->
                g.fromStart()
                    .chain(processMessage, router)
                    .route(
                        r -> {
                          r.on("BUG").then(response1Bug);
                          r.on("CUSTOMER_SUPPORT").then(response2Support);
                          r.on("LOGISTICS").then(response3Logistics);
                        }))
        .build();
  }
}
// --8<-- [end:process-pipeline]
