# Safety and Security for AI Agents

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

As AI agents grow in capability, ensuring they operate safely, securely, and align with your brand values is paramount. Uncontrolled agents can pose risks, including executing misaligned or harmful actions, such as data exfiltration, and generating inappropriate content that can impact your brand’s reputation. **Sources of risk include vague instructions, model hallucination, jailbreaks and prompt injections from adversarial users, and indirect prompt injections via tool use.**

[Google Cloud Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/overview) provides a multi-layered approach to mitigate these risks, enabling you to build powerful *and* trustworthy agents. It offers several mechanisms to establish strict boundaries, ensuring agents only perform actions you've explicitly allowed:

1. **Identity and Authorization**: Control who the agent **acts as** by defining agent and user auth.
2. **Guardrails to screen inputs and outputs:** Control your model and tool calls precisely.

    * *In-Tool Guardrails:* Design tools defensively, using developer-set tool context to enforce policies (e.g., allowing queries only on specific tables).
    * *Built-in Gemini Safety Features:* If using Gemini models, benefit from content filters to block harmful outputs and system Instructions to guide the model's behavior and safety guidelines
    * *Callbacks and Plugins:* Validate model and tool calls before or after execution, checking parameters against agent state or external policies.
    * *Using Gemini as a safety guardrail:* Implement an additional safety layer using a cheap and fast model (like Gemini Flash Lite) configured via callbacks  to screen inputs and outputs.

3. **Sandboxed code execution:** Prevent model-generated code to cause security issues by sandboxing the environment
4. **Evaluation and tracing**: Use evaluation tools to assess the quality, relevance, and correctness of the agent's final output. Use tracing to gain visibility into agent actions to analyze the steps an agent takes to reach a solution, including its choice of tools, strategies, and the efficiency of its approach.
5. **Network Controls and VPC-SC:** Confine agent activity within secure perimeters (like VPC Service Controls) to prevent data exfiltration and limit the potential impact radius.

# Safety and Security Risks

Before implementing safety measures, perform a thorough risk assessment specific to your agent's capabilities, domain, and deployment context.

***Sources*** **of risk** include:

* Ambiguous agent instructions
* Prompt injection and jailbreak attempts from adversarial users
* Indirect prompt injections via tool use

**Risk categories** include:

* **Misalignment & goal corruption**
    * Pursuing unintended or proxy goals that lead to harmful outcomes ("reward hacking")
    * Misinterpreting complex or ambiguous instructions
* **Harmful content generation, including brand safety**
    * Generating toxic, hateful, biased, sexually explicit, discriminatory, or illegal content
    * Brand safety risks such as Using language that goes against the brand’s values or off-topic conversations
* **Unsafe actions**
    * Executing commands that damage systems
    * Making unauthorized purchases or financial transactions.
    * Leaking sensitive personal data (PII)
    * Data exfiltration
