"""Unit tests for GitHub dynamic data parsing, sanitization, and offline fallback."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from scripts.build_readme import render_readme
from scripts.github_api import (
    fetch_github_data,
    get_project_last_pushed,
    is_github_url,
    parse_recent_activity,
)
from scripts.schema import Profile, validate_profile_dict

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def profile_fixture() -> Profile:
    with open("data/profile.yml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return validate_profile_dict(data)


@pytest.fixture
def sample_events() -> list[dict]:
    return json.loads((FIXTURES_DIR / "events.json").read_text(encoding="utf-8"))


def test_parse_recent_activity_filtering(sample_events: list[dict]) -> None:
    activity = parse_recent_activity(sample_events, max_items=5)
    # Must capture meaningful items (Push, PR, Release, Create) and ignore WatchEvent
    assert len(activity) == 4
    descriptions = [a["description"] for a in activity]
    assert any("Pushed `a1b2c3d`" in d for d in descriptions)
    assert any("Opened PR #14" in d for d in descriptions)
    assert any("Published release" in d for d in descriptions)
    assert any("Created public repository `sakshamgupta04/paperlens`" in d for d in descriptions)
    assert not any("pytorch" in d for d in descriptions)


def test_parse_recent_activity_hostile_sanitization() -> None:
    hostile_data = json.loads((FIXTURES_DIR / "hostile_events.json").read_text(encoding="utf-8"))
    activity = parse_recent_activity(hostile_data, max_items=5)
    # Push item has hostile script in message: must be stripped and escaped
    assert len(activity) >= 1
    push_item = activity[0]
    assert "<script>" not in push_item["description"]
    assert "\n" not in push_item["description"]

    # PR item with javascript: URL must be skipped from having a dangerous link
    for item in activity:
        assert item["url"].startswith("https://github.com/")


def test_is_github_url_validation() -> None:
    assert is_github_url("https://github.com/sakshamgupta04/echonotes") is True
    assert is_github_url("https://api.github.com/users/sakshamgupta04") is True
    assert is_github_url("https://evil.com/github.com") is False
    assert is_github_url("javascript:alert(1)") is False
    assert is_github_url("") is False
    assert is_github_url(None) is False


def test_project_last_pushed_mapping() -> None:
    repos_data = json.loads((FIXTURES_DIR / "repos.json").read_text(encoding="utf-8"))
    targets = ["sakshamgupta04/echonotes", "farmguard"]
    pushed = get_project_last_pushed(repos_data, targets)
    assert pushed.get("sakshamgupta04/echonotes") == "2026-11-10"
    assert pushed.get("farmguard") == "2026-11-08"


def test_cache_fallback_and_offline_mode(tmp_path: Path) -> None:
    cache_file = tmp_path / "last_good.json"
    cache_data = {
        "fetched_at": "2026-11-10T12:00:00Z",
        "languages": {"Python": 50000},
        "project_last_updated": {},
        "recent_activity": [],
    }
    cache_file.write_text(json.dumps(cache_data), encoding="utf-8")

    # 1. Offline mode with cache
    data, note = fetch_github_data("sakshamgupta04", [], offline=True, cache_path=cache_file)
    assert data["languages"]["Python"] == 50000
    assert note is not None
    assert "showing cached data from" in note

    # 2. Offline mode without cache
    data_empty, note_empty = fetch_github_data(
        "sakshamgupta04", [], offline=True, cache_path=tmp_path / "nonexistent.json"
    )
    assert data_empty == {}
    assert "no cache found" in str(note_empty)


def test_empty_results_hides_dynamic_sections(profile_fixture: Profile) -> None:
    # Empty dynamic data
    rendered = render_readme(
        profile=profile_fixture,
        template_dir=Path("templates"),
        template_name="README.md.j2",
        dynamic_data={},
    )
    assert "## ⚡ Recent Activity" not in rendered
    assert "Codebase Distribution by Bytes" not in rendered
    assert "null" not in rendered.lower()
    assert "none" not in rendered.lower()
