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
// code: an agent names a random city, a code node looks up the time there,
// a second agent reports it, and a final node emits a completion message.

// --8<-- [start:get-started]
import com.google.adk.agents.Context;
import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.tools.AgentTool;
import com.google.adk.workflow.Node;
import com.google.adk.workflow.ToolNodes;
import com.google.adk.workflow.Workflow;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import com.google.genai.types.Schema;
import io.reactivex.rxjava3.core.Flowable;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public final class GetStarted {

  /** The structured payload handed from the lookup node to the report agent. */
  private static final Schema CITY_TIME_SCHEMA =
      Schema.builder()
          .type("OBJECT")
          .properties(
              Map.of(
                  "time_info",
                  Schema.builder().type("STRING").description("Time information.").build(),
                  "city",
                  Schema.builder().type("STRING").description("City name.").build()))
          .required(List.of("time_info", "city"))
          .build();

  public static final Workflow ROOT_AGENT = create();

  private GetStarted() {}

  public static Workflow create() {
    LlmAgent cityGeneratorAgent =
        LlmAgent.builder()
            .name("city_generator_agent")
            .model("gemini-flash-latest")
            .instruction(
                """
                Return the name of a random city.
                Return only the name, nothing else.
                """)
            .build();
    Node cityGeneratorNode = ToolNodes.asNode(AgentTool.create(cityGeneratorAgent));

    // Simulates returning the current time in the specified city.
    Node lookupTimeNode =
        new Node() {
          @Override
          public String name() {
            return "lookup_time_function";
          }

          @Override
          public Optional<Schema> outputSchema() {
            return Optional.of(CITY_TIME_SCHEMA);
          }

          @Override
          public Flowable<?> runNode(Context context, Object nodeInput) {
            String city =
                nodeInput instanceof Map<?, ?> map
                    ? String.valueOf(map.get("result")).trim()
                    : String.valueOf(nodeInput).trim();
            return Flowable.just(Map.of("time_info", "10:10 AM", "city", city));
          }
        };

    LlmAgent cityReportAgent =
        LlmAgent.builder()
            .name("city_report_agent")
            .model("gemini-flash-latest")
            .inputSchema(CITY_TIME_SCHEMA)
            .instruction(
                """
                You receive a CityTime with time_info and city fields.
                Output a single line stating that it is that time in that city right now.
                """)
            .build();
    Node cityReportNode = ToolNodes.asNode(AgentTool.create(cityReportAgent));

    Node completedMessageNode =
        new Node() {
          @Override
          public String name() {
            return "completed_message_function";
          }

          @Override
          public Flowable<?> runNode(Context context, Object nodeInput) {
            String report =
                nodeInput instanceof Map<?, ?> map
                    ? String.valueOf(map.get("result"))
                    : String.valueOf(nodeInput);
            Event message =
                Event.builder()
                    .id(Event.generateEventId())
                    .author(name())
                    .content(
                        Content.builder()
                            .role("model")
                            .parts(Part.fromText(report + "\n WORKFLOW COMPLETED."))
                            .build())
                    .build();
            return Flowable.just(message);
          }
        };

    return Workflow.builder()
        .name("root_agent")
        .edges(
            g ->
                g.fromStart()
                    .chain(
                        cityGeneratorNode,
                        lookupTimeNode,
                        cityReportNode,
                        completedMessageNode))
        .build();
  }
}
// --8<-- [end:get-started]
