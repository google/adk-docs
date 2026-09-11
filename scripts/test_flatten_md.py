from flatten_md import flat_md_target, on_post_build, rewrite_index_links

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


def _build_fake_site(site_root):
    """Create a realistic post-build site layout under ``site_root``.

    Returns the ``config`` dict expected by ``on_post_build``.
    """
    (site_root / "agents" / "config").mkdir(parents=True)
    (site_root / "agents" / "config" / "index.md").write_text(
        "[agents](https://adk.dev/agents/index.md)\n"
        "[qs](https://adk.dev/get-started/quickstart/index.md)\n",
        encoding="utf8",
    )
    (site_root / "agents" / "index.md").write_text(
        "[cfg](https://adk.dev/agents/config/index.md)\n",
        encoding="utf8",
    )
    (site_root / "index.md").write_text(
        "Home: https://adk.dev/index.md\n",
        encoding="utf8",
    )
    (site_root / "llms.txt").write_text(
        "- [X](https://adk.dev/agents/config/index.md)\n",
        encoding="utf8",
    )
    (site_root / "llms-full.txt").write_text(
        "See https://adk.dev/agents/index.md for details\n",
        encoding="utf8",
    )
    return {"site_dir": str(site_root), "site_url": SITE}


def test_on_post_build_renames_layout(tmp_path):
    site_root = tmp_path / "site"
    config = _build_fake_site(site_root)

    on_post_build(config)

    # Flat targets exist; original nested index.md files are gone.
    assert (site_root / "agents" / "config.md").exists()
    assert not (site_root / "agents" / "config" / "index.md").exists()
    assert (site_root / "agents.md").exists()
    assert not (site_root / "agents" / "index.md").exists()

    # Root index.md is left in place (not renamed).
    assert (site_root / "index.md").exists()


def test_on_post_build_rewrites_links(tmp_path):
    site_root = tmp_path / "site"
    config = _build_fake_site(site_root)

    on_post_build(config)

    config_md = (site_root / "agents" / "config.md").read_text(encoding="utf8")
    assert "https://adk.dev/agents.md" in config_md
    assert "https://adk.dev/get-started/quickstart.md" in config_md
    assert "index.md" not in config_md

    agents_md = (site_root / "agents.md").read_text(encoding="utf8")
    assert "https://adk.dev/agents/config.md" in agents_md
    assert "index.md" not in agents_md

    llms = (site_root / "llms.txt").read_text(encoding="utf8")
    assert "https://adk.dev/agents/config.md" in llms
    assert "index.md" not in llms

    llms_full = (site_root / "llms-full.txt").read_text(encoding="utf8")
    assert "https://adk.dev/agents.md" in llms_full
    assert "index.md" not in llms_full

    # Bare homepage link is preserved unchanged.
    root_md = (site_root / "index.md").read_text(encoding="utf8")
    assert root_md == "Home: https://adk.dev/index.md\n"
