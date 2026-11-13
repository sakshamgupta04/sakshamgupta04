"""Comprehensive Quality & Accessibility tests (Phase 9)."""

from __future__ import annotations

import re
from pathlib import Path

from scripts.build_readme import MAX_README_BYTES, load_profile_data, render_readme
from scripts.check_links import extract_urls_from_dict, extract_urls_from_markdown
from scripts.schema import validate_profile_dict


def test_production_readme_cleanliness() -> None:
    """Validate that rendered production README has no placeholder leaks or forbidden tokens."""
    _, profile = load_profile_data(Path("data/profile.yml"))
    rendered = render_readme(
        profile=profile,
        template_dir=Path("templates"),
        template_name="README.md.j2",
    )

    lowered = rendered.lower()
    # Check forbidden words
    assert "todo" not in lowered
    assert "undefined" not in lowered

    # Verify no un-rendered 'None' or 'null' in values
    tokens = re.findall(r"\b(null|none)\b", lowered)
    assert not tokens, f"Found leaked tokens in rendered README: {tokens}"

    # Verify size
    size_bytes = len(rendered.encode("utf-8"))
    assert size_bytes < MAX_README_BYTES


def test_table_of_contents_anchors_match_headings() -> None:
    """Validate that every link in the Table of Contents resolves to an anchor in the document."""
    _, profile = load_profile_data(Path("data/profile.yml"))
    rendered = render_readme(
        profile=profile,
        template_dir=Path("templates"),
        template_name="README.md.j2",
    )

    # Extract TOC line: **Jump to:** [About](#about) • ...
    toc_match = re.search(r"\*\*Jump to:\*\*\s*(.+)", rendered)
    assert toc_match, "Table of Contents not found"
    toc_line = toc_match.group(1)

    # Find all anchor links in TOC: (#anchor-name)
    toc_anchors = re.findall(r"\(#([^\)]+)\)", toc_line)
    assert len(toc_anchors) >= 5, "Too few TOC anchors found"

    # Find all anchor definitions: id="anchor-name"
    defined_anchors = set(re.findall(r"""id=["']([^"']+)["']""", rendered))

    for anchor in toc_anchors:
        assert anchor in defined_anchors, f"TOC anchor '#{anchor}' does not exist in rendered README"


def test_heading_hierarchy_consistency() -> None:
    """Ensure heading levels follow a structured, non-skipping hierarchy."""
    _, profile = load_profile_data(Path("data/profile.yml"))
    rendered = render_readme(
        profile=profile,
        template_dir=Path("templates"),
        template_name="README.md.j2",
    )

    lines = rendered.splitlines()
    prev_level = 1  # Top of document is effectively Level 1
    for line in lines:
        match = re.match(r"^(#{1,6})\s+", line)
        if match:
            level = len(match.group(1))
            # Heading level should not jump more than 1 level downwards (e.g. h1 -> h3)
            assert level <= prev_level + 1, f"Heading jump from H{prev_level} to H{level}: {line}"
            prev_level = level


def test_nearly_empty_profile_renders_safely() -> None:
    """Test with a minimal profile where almost all fields are missing or null."""
    minimal_data = {
        "identity": {
            "name": "Minimal User",
            "handle": "minuser",
        }
    }
    profile = validate_profile_dict(minimal_data)
    rendered = render_readme(
        profile=profile,
        template_dir=Path("templates"),
        template_name="README.md.j2",
    )

    assert "Minimal User" in rendered
    assert "minuser@github" in rendered
    assert "todo" not in rendered.lower()
    assert "undefined" not in rendered.lower()
    assert not re.findall(r"\b(null|none)\b", rendered.lower())
    assert len(rendered.encode("utf-8")) < MAX_README_BYTES


def test_all_features_enabled_renders_without_errors() -> None:
    """Test with every single optional feature toggled ON."""
    data = {
        "identity": {
            "name": "Full User",
            "handle": "fulluser",
            "headline": "Lead Architect",
            "tagline": "Full feature test",
            "location": "Global",
            "languages_spoken": ["English"],
            "availability": {"status": "open_to_work", "text": "Available now"},
            "education": [{"school": "Tech Univ", "degree": "B.S. CS", "start": "2020", "end": "2024"}],
        },
        "links": {
            "github": "https://github.com/fulluser",
            "linkedin": "https://linkedin.com/in/fulluser",
            "leetcode": "https://leetcode.com/u/fulluser",
            "blog": "https://fulluser.dev/blog",
            "wakatime": "https://wakatime.com/share/@fulluser/chart.json",
        },
        "leetcode": {"solved": 450, "rating": 1950, "as_of": "2026-11"},
        "features": {
            "terminal_header": True,
            "mermaid_skill_map": True,
            "languages_chart": True,
            "recent_activity": True,
            "projects_last_updated": True,
            "snake": True,
            "stats_card": True,
            "leetcode_block": True,
            "blog_rss": True,
            "wakatime": True,
        },
    }
    profile = validate_profile_dict(data)
    dynamic_data = {
        "languages": {"Python": 50000, "TypeScript": 12000},
        "recent_activity": [{"description": "Commit to repo", "url": "https://github.com/fulluser/repo", "relative_time": "1d ago", "absolute_time": "2026-11-12"}],
        "github_stats": {"public_repos": 20, "total_stars": 150},
        "blog_posts": [{"title": "Scaling Systems", "url": "https://fulluser.dev/blog/scaling", "date": "2026-11-01"}],
        "wakatime": [{"name": "Python", "percent": 75.0, "text": "20 hrs"}],
    }

    rendered = render_readme(
        profile=profile,
        template_dir=Path("templates"),
        template_name="README.md.j2",
        dynamic_data=dynamic_data,
    )

    assert "Full User" in rendered
    assert "GitHub Metrics" in rendered
    assert "Weekly Coding Activity (WakaTime)" in rendered
    assert "LeetCode Stats" in rendered
    assert "Latest Articles" in rendered
    assert "Contribution Graph" in rendered
    assert "todo" not in rendered.lower()
    assert "undefined" not in rendered.lower()
    assert len(rendered.encode("utf-8")) < MAX_README_BYTES


def test_link_extractor_utils() -> None:
    """Test URL extraction from dictionaries and markdown strings."""
    sample_dict = {
        "a": "https://example.com/one",
        "b": ["https://example.com/two", "ftp://ignored.com", 123, None],
        "c": {"d": "https://example.com/three"},
    }
    urls = extract_urls_from_dict(sample_dict)
    assert "https://example.com/one" in urls
    assert "https://example.com/two" in urls
    assert "https://example.com/three" in urls
    assert "ftp://ignored.com" not in urls

    sample_md = """
    Check [Doc](https://docs.example.com) and <img src="https://images.example.com/pic.png">
    Relative link [Local](assets/pic.png) should not be captured.
    """
    md_urls = extract_urls_from_markdown(sample_md)
    assert "https://docs.example.com" in md_urls
    assert "https://images.example.com/pic.png" in md_urls
    assert "assets/pic.png" not in md_urls
