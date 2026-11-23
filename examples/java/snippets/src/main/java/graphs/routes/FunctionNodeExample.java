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

// The simplest node type: a class implementing Node. It takes text in, returns
// text out, and the framework hands that value to the next node as its input.
// No session-state writes needed.

// --8<-- [start:function-node]
import com.google.adk.agents.Context;
import com.google.adk.workflow.Node;
import com.google.adk.workflow.Workflow;
import com.google.genai.types.Content;
import io.reactivex.rxjava3.core.Flowable;

public final class FunctionNodeExample {

  /** Any non-Event value emitted by Flowable becomes the node's output. */
  static final class MyFunctionNode implements Node {
    @Override
    public String name() {
      return "my_function_node";
    }

    @Override
    public Flowable<?> runNode(Context context, Object nodeInput) {
      String text =
          nodeInput instanceof Content content && content.text() != null
              ? content.text()
              : String.valueOf(nodeInput);
      String inputTextModified = text.toUpperCase();
      return Flowable.just(inputTextModified);
    }
  }

  /** The successor receives my_function_node's output as its nodeInput. */
  static final class AddSuffixNode implements Node {
    @Override
    public String name() {
      return "add_suffix";
    }

    @Override
    public Flowable<?> runNode(Context context, Object nodeInput) {
      return Flowable.just(nodeInput + " IS AWESOME!");
    }
  }

  public static Workflow create() {
    return Workflow.builder()
        .name("function_node_pipeline")
        .edges(g -> g.fromStart().chain(new MyFunctionNode(), new AddSuffixNode()))
        .build();
  }
}
// --8<-- [end:function-node]
