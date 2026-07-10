from flatten_md import flat_md_target, rewrite_index_links

SITE = "https://adk.dev"


def test_flat_md_target_regular_page():
    assert flat_md_target("agents/config/index.md") == "agents/config.md"


def test_flat_md_target_section_index():
    assert flat_md_target("agents/index.md") == "agents.md"


def test_flat_md_target_root_index_stays():
    assert flat_md_target("index.md") is None


def test_flat_md_target_non_index_ignored():
    assert flat_md_target("agents/config.md") is None


def test_rewrite_links_regular_page():
    text = "[cfg](https://adk.dev/agents/config/index.md)"
    assert rewrite_index_links(text, SITE) == "[cfg](https://adk.dev/agents/config.md)"


def test_rewrite_links_section_index():
    text = "See https://adk.dev/agents/index.md for details"
    assert rewrite_index_links(text, SITE) == "See https://adk.dev/agents.md for details"


def test_rewrite_links_homepage_unchanged():
    text = "Home: https://adk.dev/index.md"
    assert rewrite_index_links(text, SITE) == "Home: https://adk.dev/index.md"


def test_rewrite_links_trailing_slash_site_url():
    text = "https://adk.dev/agents/config/index.md"
    assert rewrite_index_links(text, "https://adk.dev/") == "https://adk.dev/agents/config.md"


def test_rewrite_links_idempotent():
    once = rewrite_index_links("https://adk.dev/agents/config/index.md", SITE)
    assert rewrite_index_links(once, SITE) == once
