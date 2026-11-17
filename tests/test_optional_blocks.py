"""Unit tests for Phase 8 optional blocks: LeetCode, Blog RSS, WakaTime, and Stats Card."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.build_readme import render_readme
from scripts.external_feeds import (
    enrich_external_feeds,
    fetch_blog_posts,
    fetch_wakatime_stats,
    parse_feed_xml,
    parse_wakatime_json,
)
from scripts.schema import validate_profile_dict

RSS_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Saksham's Engineering Blog</title>
    <link>https://saksham.dev/blog</link>
    <item>
      <title>Scaling ML Pipelines on Cloud Run</title>
      <link>https://saksham.dev/blog/scaling-ml-pipelines</link>
      <pubDate>Thu, 12 Nov 2026 10:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Building Resilient Edge AI</title>
      <link>https://saksham.dev/blog/resilient-edge-ai</link>
      <pubDate>Mon, 02 Nov 2026 08:30:00 GMT</pubDate>
    </item>
    <item>
      <title>External Post Linking Elsewhere</title>
      <link>https://evil-phishing.com/scam</link>
      <pubDate>Fri, 20 Oct 2026 00:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Clean Architecture with Next.js and Supabase</title>
      <link>https://subdomain.saksham.dev/posts/nextjs-clean-arch</link>
      <pubDate>Sun, 15 Oct 2026 14:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""

ATOM_SAMPLE = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Saksham's Tech Notes</title>
  <link href="https://blog.saksham.me"/>
  <entry>
    <title>Deep Dive into Transformer Quantization</title>
    <link href="https://blog.saksham.me/quantization"/>
    <updated>2026-11-01T12:00:00Z</updated>
  </entry>
</feed>
"""

WAKATIME_SAMPLE = {
    "data": [
        {"name": "Python", "percent": 62.4, "text": "18 hrs 20 mins"},
        {"name": "TypeScript", "percent": 24.1, "text": "7 hrs 10 mins"},
        {"name": "SQL", "percent": 13.5, "text": "4 hrs"},
    ]
}


# --- 1. LeetCode Block Tests ---

def test_leetcode_block_rendered_when_enabled_with_data() -> None:
    data = {
        "identity": {"name": "Saksham", "handle": "sakshamgupta04"},
        "links": {"leetcode": "https://leetcode.com/u/saksham04/"},
        "leetcode": {"solved": 320, "rating": 1785, "as_of": "2026-11"},
        "features": {"leetcode_block": True},
    }
    profile = validate_profile_dict(data)
    rendered = render_readme(profile, Path("templates"), "README.md.j2")

    assert "LeetCode Stats" in rendered
    assert "320" in rendered
    assert "1785" in rendered
    assert "2026-11" in rendered
    assert "https://leetcode.com/u/saksham04/" in rendered
    assert "[LeetCode](#leetcode)" not in rendered


def test_leetcode_block_hidden_when_data_missing() -> None:
    data = {
        "identity": {"name": "Saksham", "handle": "sakshamgupta04"},
        "leetcode": {"solved": None, "rating": None},
        "features": {"leetcode_block": True},
    }
    profile = validate_profile_dict(data)
    rendered = render_readme(profile, Path("templates"), "README.md.j2")

    assert "LeetCode Stats" not in rendered
    assert "[LeetCode](#leetcode)" not in rendered


def test_leetcode_block_hidden_when_disabled() -> None:
    data = {
        "identity": {"name": "Saksham", "handle": "sakshamgupta04"},
        "leetcode": {"solved": 500, "rating": 1900},
        "features": {"leetcode_block": False},
    }
    profile = validate_profile_dict(data)
    rendered = render_readme(profile, Path("templates"), "README.md.j2")

    assert "LeetCode Stats" not in rendered


# --- 2. Blog RSS Tests ---

def test_parse_feed_xml_rss_and_domain_safety() -> None:
    posts = parse_feed_xml(RSS_SAMPLE, base_url="https://saksham.dev/blog", max_items=3)
    assert len(posts) == 3
    assert posts[0]["title"] == "Scaling ML Pipelines on Cloud Run"
    assert posts[0]["url"] == "https://saksham.dev/blog/scaling-ml-pipelines"
    assert posts[1]["title"] == "Building Resilient Edge AI"

    # Hostile domain https://evil-phishing.com/scam was skipped; subdomain was accepted:
    assert posts[2]["title"] == "Clean Architecture with Next\\.js and Supabase"
    assert posts[2]["url"] == "https://subdomain.saksham.dev/posts/nextjs-clean-arch"


def test_parse_feed_xml_atom() -> None:
    posts = parse_feed_xml(ATOM_SAMPLE, base_url="https://blog.saksham.me", max_items=3)
    assert len(posts) == 1
    assert posts[0]["title"] == "Deep Dive into Transformer Quantization"
    assert posts[0]["url"] == "https://blog.saksham.me/quantization"
    assert posts[0]["date"] == "2026-11-01"


def test_blog_rss_rendered_when_enabled_with_data() -> None:
    data = {
        "identity": {"name": "Saksham", "handle": "sakshamgupta04"},
        "links": {"blog": "https://saksham.dev/blog"},
        "features": {"blog_rss": True},
    }
    profile = validate_profile_dict(data)
    dynamic_data = {
        "blog_posts": [
            {"title": "Scaling ML Pipelines", "url": "https://saksham.dev/blog/p1", "date": "2026-11-12"}
        ]
    }
    rendered = render_readme(profile, Path("templates"), "README.md.j2", dynamic_data=dynamic_data)

    assert "Latest Articles" in rendered
    assert "Scaling ML Pipelines" in rendered
    assert "https://saksham.dev/blog/p1" in rendered
    assert "[Articles](#blog)" not in rendered


def test_blog_rss_hidden_when_empty() -> None:
    data = {
        "identity": {"name": "Saksham", "handle": "sakshamgupta04"},
        "links": {"blog": "https://saksham.dev/blog"},
        "features": {"blog_rss": True},
    }
    profile = validate_profile_dict(data)
    rendered = render_readme(profile, Path("templates"), "README.md.j2", dynamic_data={"blog_posts": []})

    assert "Latest Articles" not in rendered
    assert "[Articles](#blog)" not in rendered


def test_blog_rss_network_failure_fallback_to_cache(tmp_path: Path) -> None:
    cache_file = tmp_path / "last_good.json"
    cache_file.write_text(
        json.dumps({
            "blog_posts": [{"title": "Cached Post", "url": "https://saksham.dev/cached", "date": "2026-10-01"}]
        }),
        encoding="utf-8",
    )
    data = {
        "identity": {"name": "Saksham", "handle": "sakshamgupta04"},
        "links": {"blog": "http://127.0.0.1:9999/nonexistent-rss"},
        "features": {"blog_rss": True},
    }
    profile = validate_profile_dict(data)
    dynamic_data: dict = {}

    # Run offline enrichment
    enrich_external_feeds(profile, dynamic_data, offline=True, cache_path=cache_file)
    assert len(dynamic_data.get("blog_posts", [])) == 1
    assert dynamic_data["blog_posts"][0]["title"] == "Cached Post"


# --- 3. WakaTime Tests ---

def test_parse_wakatime_json() -> None:
    stats = parse_wakatime_json(WAKATIME_SAMPLE, max_items=2)
    assert len(stats) == 2
    assert stats[0]["name"] == "Python"
    assert stats[0]["percent"] == 62.4
    assert stats[0]["text"] == "18 hrs 20 mins"


def test_wakatime_rendered_when_enabled_with_data() -> None:
    data = {
        "identity": {"name": "Saksham", "handle": "sakshamgupta04"},
        "links": {"wakatime": "https://wakatime.com/share/@saksham/abc.json"},
        "features": {"wakatime": True},
    }
    profile = validate_profile_dict(data)
    dynamic_data = {
        "wakatime": [
            {"name": "Python", "percent": 70.0, "text": "14 hrs"},
            {"name": "TypeScript", "percent": 30.0, "text": "6 hrs"},
        ]
    }
    rendered = render_readme(profile, Path("templates"), "README.md.j2", dynamic_data=dynamic_data)

    assert "Weekly Coding Activity (WakaTime)" in rendered
    assert "Python" in rendered
    assert "70.0%" in rendered
    assert "14 hrs" in rendered
    assert "[WakaTime](#wakatime)" not in rendered


def test_wakatime_hidden_when_empty() -> None:
    data = {
        "identity": {"name": "Saksham", "handle": "sakshamgupta04"},
        "links": {"wakatime": "https://wakatime.com/share/@saksham/abc.json"},
        "features": {"wakatime": True},
    }
    profile = validate_profile_dict(data)
    rendered = render_readme(profile, Path("templates"), "README.md.j2", dynamic_data={"wakatime": []})

    assert "Weekly Coding Activity (WakaTime)" not in rendered


def test_wakatime_network_failure_fallback_to_cache(tmp_path: Path) -> None:
    cache_file = tmp_path / "last_good.json"
    cache_file.write_text(
        json.dumps({
            "wakatime": [{"name": "Rust", "percent": 100.0, "text": "5 hrs"}]
        }),
        encoding="utf-8",
    )
    data = {
        "identity": {"name": "Saksham", "handle": "sakshamgupta04"},
        "links": {"wakatime": "http://127.0.0.1:9999/nonexistent-wakatime"},
        "features": {"wakatime": True},
    }
    profile = validate_profile_dict(data)
    dynamic_data: dict = {}

    enrich_external_feeds(profile, dynamic_data, offline=True, cache_path=cache_file)
    assert len(dynamic_data.get("wakatime", [])) == 1
    assert dynamic_data["wakatime"][0]["name"] == "Rust"


# --- 4. Stats Card Tests ---

def test_stats_card_rendered_when_enabled_with_data() -> None:
    data = {
        "identity": {"name": "Saksham", "handle": "sakshamgupta04"},
        "features": {"stats_card": True},
    }
    profile = validate_profile_dict(data)
    dynamic_data = {
        "github_stats": {"public_repos": 15, "total_stars": 42}
    }
    rendered = render_readme(profile, Path("templates"), "README.md.j2", dynamic_data=dynamic_data)

    assert "GitHub Metrics" in rendered
    assert "Public Repositories" in rendered
    assert "15" in rendered
    assert "Total Stargazers" in rendered
    assert "42" in rendered
    assert "[GitHub Metrics](#github-stats)" not in rendered


def test_stats_card_hidden_when_disabled_or_empty() -> None:
    data = {
        "identity": {"name": "Saksham", "handle": "sakshamgupta04"},
        "features": {"stats_card": False},
    }
    profile = validate_profile_dict(data)
    rendered = render_readme(profile, Path("templates"), "README.md.j2", dynamic_data={"github_stats": {"public_repos": 10, "total_stars": 5}})
    assert "GitHub Metrics" not in rendered

    # Enabled but empty
    data["features"]["stats_card"] = True
    profile_enabled = validate_profile_dict(data)
    rendered_empty = render_readme(profile_enabled, Path("templates"), "README.md.j2", dynamic_data={})
    assert "GitHub Metrics" not in rendered_empty


# --- 5. Empty inputs to fetchers ---

def test_fetchers_empty_or_invalid_inputs() -> None:
    assert fetch_blog_posts(None) == []
    assert fetch_blog_posts("") == []
    assert fetch_blog_posts("ftp://invalid-url.com") == []
    assert fetch_wakatime_stats(None) == []
    assert fetch_wakatime_stats("") == []
    assert fetch_wakatime_stats("javascript:alert(1)") == []
