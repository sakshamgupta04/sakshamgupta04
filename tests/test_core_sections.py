"""Unit tests for Phase 3 core sections rendering and content hiding rules."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.build_readme import render_readme
from scripts.helpers import format_roadmap_status
from scripts.schema import Profile, validate_profile_dict


@pytest.fixture
def profile_fixture() -> Profile:
    with open("data/profile.yml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return validate_profile_dict(data)


def render(profile: Profile) -> str:
    return render_readme(
        profile=profile,
        template_dir=Path("templates"),
        template_name="README.md.j2",
    )


def test_whoami_renders_populated_fields_and_hides_missing(profile_fixture: Profile) -> None:
    output = render(profile_fixture)
    # Populated fields must be present
    assert "Saksham Gupta" in output
    assert "Full-Stack / Web Developer" in output
    assert "Model Institute of Engineering and Technology" in output

    # Empty/null fields must be hidden
    assert "location:" not in output
    assert "languages_spoken:" not in output
    assert "focus_areas:" not in output


def test_start_here_recruiter_and_engineer(profile_fixture: Profile) -> None:
    output = render(profile_fixture)
    # Recruiter section
    assert "💼 Recruiter &amp; Hiring Manager" in output
    assert "EchoNotes" in output
    assert "AI Video Interview & Emotion Analyzer" in output
    assert "FarmGuard" in output

    # Engineer section
    assert "🛠️ Software Engineer &amp; Tech Lead" in output
    assert "Architecture:" in output
    assert "Next.js, TypeScript, FastAPI" in output


def test_researcher_hidden_when_empty(profile_fixture: Profile) -> None:
    # Profile fixture has empty publications and open_source.interests
    output = render(profile_fixture)
    assert "Researcher &amp; Academic" not in output


def test_researcher_shown_when_populated(profile_fixture: Profile) -> None:
    p = copy.deepcopy(profile_fixture)
    p.open_source.interests = ["Edge AI Optimization", "Offline RAG"]
    output = render(p)
    assert "Researcher &amp; Academic" in output
    assert "Edge AI Optimization" in output


def test_now_hidden_when_empty_and_shown_when_populated(profile_fixture: Profile) -> None:
    # Fixture now is completely empty
    output = render(profile_fixture)
    assert "## ⚡ Now" not in output

    p = copy.deepcopy(profile_fixture)
    p.now.updated = "2026-11"
    p.now.building = ["FarmGuard edge prototype"]
    output_populated = render(p)
    assert "## ⚡ Now" in output_populated
    assert "FarmGuard edge prototype" in output_populated
    assert "Last updated: 2026-11" in output_populated


def test_roadmap_status_icons_and_words() -> None:
    assert "✅" in format_roadmap_status("done")
    assert "Done" in format_roadmap_status("done")
    assert "⚡" in format_roadmap_status("doing")
    assert "doing" in format_roadmap_status("doing").lower()
    assert "📋" in format_roadmap_status("next")
    assert "planned" in format_roadmap_status("next").lower()


def test_principles_table_rendered(profile_fixture: Profile) -> None:
    output = render(profile_fixture)
    assert "## 📐 Working Principles" in output
    assert "Measure before you claim" in output
    assert "Fail gracefully" in output
    assert "Privacy by design" in output
    assert "Ship it" in output


def test_anchors_and_toc_links(profile_fixture: Profile) -> None:
    output = render(profile_fixture)
    assert 'id="about"' in output
    assert 'id="start-here"' in output
    assert 'id="goals"' in output
    assert 'id="principles"' in output
    assert 'id="contact"' in output

    assert "[About](#about)" in output
    assert "[Start Here](#start-here)" in output
    assert "[Roadmap &amp; Goals](#goals)" in output
    assert "[Principles](#principles)" in output
    assert "[Contact](#contact)" in output
