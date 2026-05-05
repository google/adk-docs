<!-- Hero Section -->
<div class="hero-grid">
  <div class="hero-content">
    <h1>Build production agents, <span class="hero-punchline">not prototypes.</span></h1>
    <p>ADK is the open-source agent development framework that lets you build, debug, and deploy reliable AI agents at enterprise scale. Available in Python, TypeScript, Go, and Java.</p>
    <div class="hero-actions">
      <a href="get-started/" class="btn btn-primary">Start building</a>
      <!-- <a href="skills/" class="btn btn-accent">Agent skills</a> -->
    </div>
  </div>
  <div class="hero-visual">
    <!-- Tabbed Code Window -->
    <div class="tabbed-area" id="tabbed-area">
      <div class="mac-window">
        <div class="iterm-tab-bar">
          <div class="iterm-tab active" data-lang="python">Python</div>
          <div class="iterm-tab" data-lang="typescript">TypeScript</div>
          <div class="iterm-tab" data-lang="go">Go</div>
          <div class="iterm-tab" data-lang="java">Java</div>
        </div>
<div class="code-content" id="code-python"><pre><span class="kw">from</span> google.adk <span class="kw">import</span> <span class="fn">Agent</span>
<span class="kw">from</span> google.adk.tools <span class="kw">import</span> google_search

agent = <span class="fn">Agent</span>(
    name=<span class="str">"researcher"</span>,
    model=<span class="str">"gemini-flash-latest"</span>,
    instruction=<span class="str">"You help users research topics thoroughly."</span>,
    tools=[google_search],
)</pre></div>

<div class="code-content" id="code-typescript" style="display:none"><pre><span class="kw">import</span> { <span class="fn">LlmAgent, GOOGLE_SEARCH</span> } <span class="kw">from</span> <span class="str">'@google/adk'</span>;

<span class="kw">const</span> agent = <span class="kw">new</span> <span class="fn">LlmAgent</span>({
  name: <span class="str">'researcher'</span>,
  model: <span class="str">'gemini-flash-latest'</span>,
  instruction: <span class="str">'You help users research topics thoroughly.'</span>,
  tools: [GOOGLE_SEARCH],
});

</pre></div>

<div class="code-content" id="code-go" style="display:none"><pre><span class="kw">import</span> <span class="str">"google.golang.org/adk/agent"</span>

a := agent.<span class="fn">New</span>(<span class="str">"researcher"</span>,
    agent.<span class="fn">WithModel</span>(<span class="str">"gemini-flash-latest"</span>),
    agent.<span class="fn">WithInstruction</span>(<span class="str">"You help users research topics thoroughly."</span>),
    agent.<span class="fn">WithTools</span>(googleSearch),
)


</pre></div>

<div class="code-content" id="code-java" style="display:none"><pre><span class="kw">import</span> com.google.adk.agents.<span class="fn">LlmAgent</span>;
<span class="kw">import</span> com.google.adk.tools.<span class="fn">GoogleSearchTool</span>;

<span class="fn">LlmAgent</span> agent = <span class="fn">LlmAgent</span>.builder()
    .name(<span class="str">"researcher"</span>)
    .model(<span class="str">"gemini-flash-latest"</span>)
    .instruction(<span class="str">"You help users research topics thoroughly."</span>)
    .tools(<span class="kw">new</span> <span class="fn">GoogleSearchTool()</span>)
    .build();</pre></div>

</div>
      <!-- Install info synced with tabs -->
      <div class="install-info" id="install-python">
        <div class="install-cmd">
          <code>pip install google-adk</code>
          <button class="copy-btn" data-copy="pip install google-adk" title="Copy to clipboard">📋</button>
        </div>
      </div>
      <div class="install-info" id="install-typescript" style="display:none">
        <div class="install-cmd">
          <code>npm install @google/adk</code>
          <button class="copy-btn" data-copy="npm install @google/adk" title="Copy to clipboard">📋</button>
        </div>
      </div>
      <div class="install-info" id="install-go" style="display:none">
        <div class="install-cmd">
          <code>go get google.golang.org/adk</code>
          <button class="copy-btn" data-copy="go get google.golang.org/adk" title="Copy to clipboard">📋</button>
        </div>
      </div>
      <div class="install-info" id="install-java" style="display:none">
        <div class="install-cmd">
          <code>com.google.adk:google-adk</code>
          <button class="copy-btn" data-copy="com.google.adk:google-adk" title="Copy to clipboard">📋</button>
        </div>
      </div>
    </div>
  </div>
</div>
