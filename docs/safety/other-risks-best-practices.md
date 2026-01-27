# Other Risks and Best Practices

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

## Sandboxed Code Execution

Code execution is a special tool that has extra security implications: sandboxing must be used to prevent model-generated code to compromise the local environment, potentially creating security issues.

Google and the ADK provide several options for safe code execution. [Vertex Gemini Enterprise API code execution feature](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/code-execution-api) enables agents to take advantage of sandboxed code execution server-side by enabling the tool\_execution tool. For code performing data analysis, you can use the [Code Executor](/adk-docs/tools/gemini-api/code-execution/) tool in ADK to call the [Vertex Code Interpreter Extension](https://cloud.google.com/vertex-ai/generative-ai/docs/extensions/code-interpreter).

If none of these options satisfy your requirements, you can build your own code executor using the building blocks provided by the ADK. We recommend creating execution environments that are hermetic: no network connections and API calls permitted to avoid uncontrolled data exfiltration; and full clean up of data across execution to not create cross-user exfiltration concerns.

## Evaluations

See [Evaluate Agents](../evaluate/index.md).

## VPC-SC Perimeters and Network Controls

If you are executing your agent into a VPC-SC perimeter, that will guarantee that all API calls will only be manipulating resources within the perimeter, reducing the chance of data exfiltration.

However, identity and perimeters only provide coarse controls around agent actions. Tool-use guardrails mitigate such limitations, and give more power to agent developers to finely control which actions to allow.

## Other Security Risks

#### Always Escape Model-Generated Content in UIs

Care must be taken when agent output is visualized in a browser: if HTML or JS content isn't properly escaped in the UI, the text returned by the model could be executed, leading to data exfiltration. For example, an indirect prompt injection can trick a model to include an img tag tricking the browser to send the session content to a 3rd party site; or construct URLs that, if clicked, send data to external sites. Proper escaping of such content must ensure that model-generated text isn't interpreted as code by browsers.
