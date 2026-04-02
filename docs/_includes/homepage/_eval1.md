<!-- Eval Section -->
<div class="feature-split">
  <div class="feature-text">
    <span class="feature-badge">Evaluation</span>
    <h2>Go beyond vibes. Evaluate everything.</h2>
    <p>Engage ADK's open evaluation framework and partner tools to test your entire agent execution trajectory. Simulate user interactions, build custom performance metrics, and optimize agents against your evaluation results.</p>
    <a href="evaluate/" class="btn btn-accent" style="margin-top:12px">Learn more</a>
  </div>
  <div class="feature-visual">
    <div class="eval-grid">
      <div class="eval-card fail">
        <div class="eval-title"><span>test_prm_safety_filter</span><span class="eval-status fail">✗ FAIL</span></div>
        <div class="eval-desc">Agent bypassed safety node in graph path.</div>
      </div>
      <div class="eval-card pass">
        <div class="eval-title"><span>test_latency_budget</span><span class="eval-status pass">✓ PASS</span></div>
        <div class="eval-desc">Execution completed in 842ms (Budget: 1500ms).</div>
      </div>
    </div>

    <!-- Metrics Chart -->
    <div class="metrics-dashboard">
      <div class="metrics-chart">
        <div class="metrics-chart-label">Agent v2.1 vs v2.0 — Response Quality</div>
        <svg viewBox="0 0 400 160" class="metrics-svg">
          <line x1="40" y1="20" x2="40" y2="130" stroke-width="1"/>
          <line x1="40" y1="130" x2="380" y2="130" stroke-width="1"/>
          <line x1="40" y1="75" x2="380" y2="75" stroke-width="0.5" stroke-dasharray="4"/>
          <line x1="40" y1="45" x2="380" y2="45" stroke-width="0.5" stroke-dasharray="4"/>
          <polyline points="40,95 90,93 140,96 190,94 240,95 290,93 340,94 380,95" fill="none" stroke="#6b7280" stroke-width="2" opacity="0.7"/>
          <polyline points="40,92 90,85 140,78 190,68 240,58 290,50 340,42 380,35" fill="none" stroke="#3b82f6" stroke-width="2.5"/>
          <polyline points="40,92 90,85 140,78 190,68 240,58 290,50 340,42 380,35 380,130 40,130" fill="url(#blueGrad)" opacity="0.15"/>
          <defs><linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#3b82f6"/><stop offset="100%" stop-color="transparent"/></linearGradient></defs>
          <text x="385" y="98" fill="#6b7280" font-size="10" font-family="Inter">v2.0</text>
          <text x="385" y="38" fill="#3b82f6" font-size="10" font-family="Inter">v2.1</text>
          <text x="40" y="148" fill="#71717a" font-size="9" font-family="Inter">Day 1</text>
          <text x="360" y="148" fill="#71717a" font-size="9" font-family="Inter">Day 7</text>
        </svg>
      </div>
      <div class="metrics-table-wrap">
        <table class="metrics-table">
          <thead><tr><th>Metric</th><th>v2.0</th><th>v2.1</th><th>Δ</th></tr></thead>
          <tbody>
            <tr class="metric-green"><td>Groundedness</td><td>76%</td><td>88%</td><td class="delta-green">+12%</td></tr>
            <tr class="metric-green"><td>Latency p50</td><td>620ms</td><td>440ms</td><td class="delta-green">−180ms</td></tr>
            <tr class="metric-green"><td>Tool accuracy</td><td>81%</td><td>89%</td><td class="delta-green">+8%</td></tr>
            <tr class="metric-neutral"><td>Safety filter</td><td>99.2%</td><td>99.2%</td><td class="delta-neutral">+0%</td></tr>
            <tr class="metric-red"><td>Hallucination rate</td><td>4.1%</td><td>6.1%</td><td class="delta-red">+2%</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
