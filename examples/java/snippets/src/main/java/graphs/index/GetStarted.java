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

// A sequential graph workflow that alternates between model reasoning and plain
// code: an agent names a random city, a code node looks up the time there, a
// second agent reports it, and a final node appends a completion message.

// --8<-- [start:get-started]
import com.google.adk.agents.Context;
import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.workflow.Node;
import com.google.adk.workflow.Workflow;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import com.google.genai.types.Schema;
import com.google.genai.types.Type;
import io.reactivex.rxjava3.core.Flowable;
import java.util.Map;
import java.util.Optional;

public final class GetStarted {

  public static Workflow createRootAgent() {
    LlmAgent cityGeneratorAgent =
        LlmAgent.builder()
            .name("city_generator_agent")
            .model("gemini-flash-latest")
            .instruction(
                """
                Return the name of a random city.
                Return only the name, nothing else.
                """)
            .outputKey("city")
            .build();

    // The structured payload schema handed from the lookup node to the report agent.
    Schema cityTimeSchema =
        Schema.builder()
            .type(Type.Known.OBJECT)
            .properties(
                Map.of(
                    "time_info",
                    Schema.builder()
                        .type(Type.Known.STRING)
                        .description("Time information.")
                        .build(),
                    "city",
                    Schema.builder().type(Type.Known.STRING).description("City name.").build()))
            .required("time_info", "city")
            .build();

    // Simulates returning the current time in the specified city.
    Node lookupTimeFunction =
        new Node() {
          @Override
          public String name() {
            return "lookup_time_function";
          }

          @Override
          public Optional<Schema> outputSchema() {
            return Optional.of(cityTimeSchema);
          }

          @Override
          public Flowable<?> runNode(Context context, Object nodeInput) {
            String city = String.valueOf(context.state().get("city")).trim();
            String timeInfo = "10:10 AM";
            context.state().put("time_info", timeInfo);
            context.state().put("city", city);
            return Flowable.just(Map.of("time_info", timeInfo, "city", city));
          }
        };

    LlmAgent cityReportAgent =
        LlmAgent.builder()
            .name("city_report_agent")
            .model("gemini-flash-latest")
            .inputSchema(cityTimeSchema)
            .instruction(
                """
                Output a single line stating that it is {time_info} in {city} right now.
                """)
            .outputKey("city_report")
            .build();

    Node completedMessageFunction =
        new Node() {
          @Override
          public String name() {
            return "completed_message_function";
          }

          @Override
          public Flowable<?> runNode(Context context, Object nodeInput) {
            String report = String.valueOf(context.state().get("city_report"));
            return Flowable.just(
                Event.builder()
                    .id(context.invocationContext().newUuid())
                    .content(
                        Content.builder()
                            .role("model")
                            .parts(Part.fromText(report + "\n WORKFLOW COMPLETED."))
                            .build())
                    .build());
          }
        };

    return Workflow.builder()
        .name("root_agent")
        .edges(
            g ->
                g.fromStart()
                    .chain(
                        cityGeneratorAgent,
                        lookupTimeFunction,
                        cityReportAgent,
                        completedMessageFunction))
        .build();
  }
}
// --8<-- [end:get-started]
