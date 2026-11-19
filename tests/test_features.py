"""Unit tests for feature toggles and workflow summary generation."""

from __future__ import annotations

from pathlib import Path

from scripts.build_readme import render_readme
from scripts.helpers import write_step_summary
from scripts.schema import validate_profile_dict


def test_snake_hidden_by_default() -> None:
    data = {
        "identity": {
            "name": "Saksham Gupta",
            "handle": "sakshamgupta04",
        },
        "features": {
            "snake": False,
        },
    }
    profile = validate_profile_dict(data)
    rendered = render_readme(
        profile=profile,
        template_dir=Path("templates"),
        template_name="README.md.j2",
    )
    assert "github-snake" not in rendered
    assert "[Contributions](#contributions)" not in rendered


def test_snake_rendered_when_enabled() -> None:
    data = {
        "identity": {
            "name": "Saksham Gupta",
            "handle": "sakshamgupta04",
        },
        "features": {
            "snake": True,
        },
    }
    profile = validate_profile_dict(data)
    rendered = render_readme(
        profile=profile,
        template_dir=Path("templates"),
        template_name="README.md.j2",
    )
    assert "github-snake" in rendered
    assert "[Contributions](#contributions)" not in rendered
    assert "github-snake-dark.svg" in rendered


def test_write_step_summary(tmp_path: Path) -> None:
    summary_file = tmp_path / "step_summary.md"
    data = {
        "identity": {
            "name": "Saksham Gupta",
            "handle": "sakshamgupta04",
        },
    }
    profile = validate_profile_dict(data)
    dynamic_data = {
        "languages": {"Python": {"bytes": 1000, "percentage": 100.0, "color": "#3572A5"}},
        "recent_activity": [{"repo": "sakshamgupta04/sakshamgupta04", "title": "Commit"}],
        "project_last_updated": {"sakshamgupta04/sakshamgupta04": "2026-11-13"},
    }

    write_step_summary(
        summary_path=summary_file,
        profile=profile,
        dynamic_data=dynamic_data,
        cache_note="Live GitHub API",
        size_bytes=15000,
        offline=False,
    )

    content = summary_file.read_text(encoding="utf-8")
    assert "Profile README Refresh Report" in content
    assert "15,000 bytes" in content
    assert "Live GitHub API" in content
    assert "Language Statistics Bar" in content
    assert "Recent Public Activity" in content



def test_statistics_refresh_key_and_transparent_cards() -> None:
    profile = validate_profile_dict({
        "identity": {"name": "Saksham Gupta", "handle": "sakshamgupta04"},
        "features": {"stats_card": True},
    })
    output = render_readme(
        profile=profile,
        template_dir=Path("templates"),
        template_name="README.md.j2",
        dynamic_data={
            "fetched_at": "2026-11-20T12:45:00Z",
            "github_stats": {"public_repos": 10, "total_stars": 2},
        },
    )
    assert "GitHub Statistics" in output
    assert "refresh=2026112012" in output
    assert "theme=transparent" in output
    assert "timezone=Asia/Kolkata" in output
    assert "cache_seconds=3600" in output
    assert "include_all_commits=false" in output
    assert "include_all_commits=true" not in output
    assert "cache_seconds=86400" in output
    assert "rank_icon=default&amp;cache_seconds=86400" in output
