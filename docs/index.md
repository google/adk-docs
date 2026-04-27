---
title: Agent Development Kit (ADK)
hide:
  - navigation
  - toc
---
<link rel="stylesheet" type="text/css" href="stylesheets/homepage.css" />
<link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/asciinema-player@3.9.0/dist/bundle/asciinema-player.css" />
<script src="https://cdn.jsdelivr.net/npm/asciinema-player@3.9.0/dist/bundle/asciinema-player.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script>document.body.classList.add('adk-landing-page');</script>

<div class="adk-landing">

<!-- Ambient Glows -->
<div class="glow glow-tl"></div>
<div class="glow glow-tr"></div>
<div class="glow glow-mr"></div>

<!-- Hero Section -->
{{% include '_includes/homepage/_hero.md' %}}

<!-- Framework -->
{{% include '_includes/homepage/_framework.md' %}}

<!-- Ecosystem -->
{{% include '_includes/homepage/_ecosystem.md' %}}

<!-- AI Dev Tools -->
{{% include '_includes/homepage/_ai-dev-tools.md' %}}

<!-- Eval Section -->
{{% include '_includes/homepage/_eval.md' %}}

<!-- Ready to Build CTA Section -->
{{% include '_includes/homepage/_build-cta.md' %}}

<!-- Community Section -->
{{% include '_includes/homepage/_community.md' %}}

<!-- FAQ Section -->
{{% include '_includes/homepage/_faq.md' %}}

<script>
function initHomepage() {
  // Asciinema player (for _agent-cli.md)
  var playerEl = document.getElementById('asciinema-demo');
  if (playerEl && !playerEl.hasChildNodes() && typeof AsciinemaPlayer !== 'undefined') {
    AsciinemaPlayer.create('assets/adk-demo.cast', playerEl, {
      theme: 'monokai',
      fit: 'width',
      autoPlay: true,
      loop: true,
      speed: 1,
      idleTimeLimit: 2,
      cols: 85,
      rows: 24,
      poster: 'npt:0:18'
    });
  }
}

// Event delegation for tab switching and copy buttons.
// Attaching to `document` means these handlers survive DOM replacement
// during MkDocs Material instant (SPA) navigation.
document.addEventListener('click', function(e) {
  // Tab switching
  var tab = e.target.closest('.iterm-tab');
  if (tab) {
    var lang = tab.getAttribute('data-lang');
    var allTabs = document.querySelectorAll('.iterm-tab');
    var langs = ['python', 'go', 'java', 'typescript'];
    allTabs.forEach(function(t) { t.classList.remove('active'); });
    tab.classList.add('active');
    langs.forEach(function(l) {
      var codeEl = document.getElementById('code-' + l);
      var installEl = document.getElementById('install-' + l);
      if (codeEl) codeEl.style.display = l === lang ? 'block' : 'none';
      if (installEl) installEl.style.display = l === lang ? 'flex' : 'none';
    });
    return;
  }

  // Copy-to-clipboard buttons
  var btn = e.target.closest('.copy-btn');
  if (btn) {
    var text = btn.getAttribute('data-copy');
    navigator.clipboard.writeText(text).then(function() {
      var orig = btn.textContent;
      btn.textContent = '✅';
      setTimeout(function() { btn.textContent = orig; }, 1500);
    });
  }
});

// Initialize on first load
document.addEventListener('DOMContentLoaded', initHomepage);

// Re-initialize after MkDocs Material instant navigation
if (typeof document$ !== 'undefined') {
  document$.subscribe(function() { initHomepage(); });
}
</script>
