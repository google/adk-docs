<!-- FAQ Section -->
<div class="faq-section">
  <h2>Frequently Asked Questions</h2>
  <p class="section-subtitle">Still have questions about ADK? Here are some answers:</p>

  <div class="faq-grid">

  <details class="faq-item-arrow">
    <summary>Can I vibe code agents with ADK?</summary>
    <p>Yes! ADK is designed to be written by both humans and AI. Connect your favorite coding assistant to our ADK developer Skills and AI-aware developer resources, and generate agents in seconds. Find out more about AI-powered coding of agents in our <a href="tutorials/coding-with-ai/">Coding with AI</a> guide.</p>
  </details>

  <details class="faq-item-arrow">
    <summary>What AI models can I use with ADK?</summary>
    <p>ADK can work with almost any generative AI model. The framework provides easy access to Gemini as well as other leading models, and we provide adapters that let you connect with many other models and model providers, including locally running models. For enterprises, ADK can connect to models on hosted services, including Google Cloud which provides a wide range of models and lets you closely manage performance, reliability, security, access, safety, and costs.</p>
  </details>

  <details class="faq-item-arrow">
    <summary>What makes ADK different?</summary>
    <p>With ADK, we are focused on building an open development framework that lets you build professional, production grade agents, without requiring a pile of code to get started. Our goal is to get you building agents quickly, and let you add functionality and complexity as you need it. ADK provides a basic structure for agents that is easy to build, and that structure is designed with the flexibility to let you extend, expand, and build complex, robust, useful agentic systems. We've put a lot of effort into providing you with development tools for interacting with agents you build, and providing ways to use AI-powered tools for building ADK agents. We are also quite proud of our approach to agent context management and how we manage context to keep it efficient, and also let you tune context management to your needs. We could go on, and if you are interested, you can find more details in our <a href="get-started/about/">developer docs</a>.</p>
  </details>

  <details class="faq-item-arrow">
    <summary>How does ADK handle context management?</summary>
    <p>Unlike tools that simply paste strings together until the context window overflows, ADK <b>manages</b> your context. We treat context like source code—sessions, memory, tool outputs, and artifacts are assembled into a structured view where every token earns its place. ADK automatically filters irrelevant events, summarizes older conversational turns, lazy-loads artifacts, and tracks token usage. This approach keeps your agents fast, efficient, and reliable by default, while giving you the controls to fully customize how context is managed for complex tasks.</p>
  </details>

  <details class="faq-item-arrow">
    <summary>How does ADK deploy to production?</summary>
    <p>ADK is built for <em>deploy anywhere</em> flexibility. You can containerize and run ADK on your own infrastructure, or take advantage of our native, one-command deployment to Google Cloud. When deploying to Google Cloud via Agent Engine (Vertex AI), Cloud Run, or GKE, your agents instantly inherit managed infrastructure, built-in authentication, Cloud Trace observability, and enterprise-grade security—all without requiring you to change a single line of your agent code. Develop locally, scale globally.</p>
  </details>

  <details class="faq-item-arrow">
    <summary>When should I use an agent framework to work with generative AI?</summary>
    <p>AI chat conversations can accomplish many tasks, but when you need to accomplish complex, multi-step processes, an agent framework lets you create a managed, repeatable task structure that can run <em>hands-off</em> with minimal human input. Agent frameworks like ADK can automatically initiate tasks, make multiple iterative AI model requests, manage context, handle tool calls, record data, run parallel jobs, handle failures, and resume tasks if they get stopped.</p>
  </details>

  </div>
</div>
