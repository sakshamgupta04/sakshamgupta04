"""Unit tests for skills flowchart generation, normalization, node limits, and level tables."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.build_readme import render_readme
from scripts.mermaid_generator import (
    escape_mermaid_label,
    generate_mermaid_skill_map,
    match_skill_to_stack,
    normalize_token,
)
from scripts.schema import Profile, SkillItem, SkillLevel, validate_profile_dict


@pytest.fixture
def profile_fixture() -> Profile:
    with open("data/profile.yml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return validate_profile_dict(data)


def test_normalization_tokens() -> None:
    assert normalize_token("Next.js") == "nextjs"
    assert normalize_token("C++") == "c"
    assert normalize_token("faster-whisper") == "fasterwhisper"
    assert normalize_token("Supabase (PostgreSQL, Auth)") == "supabasepostgresqlauth"
    assert normalize_token("") == ""


def test_match_skill_to_stack() -> None:
    stack = ["Next.js", "TypeScript", "FastAPI", "Supabase", "faster-whisper", "PyTorch"]
    assert match_skill_to_stack("next.js", stack) is True
    assert match_skill_to_stack("NextJS", stack) is True
    assert match_skill_to_stack("Supabase (PostgreSQL, Auth)", stack) is True
    assert match_skill_to_stack("PyTorch", stack) is True
    assert match_skill_to_stack("Ruby on Rails", stack) is False


def test_escape_mermaid_label() -> None:
    hostile = 'Dangerous "Tool" <script>evil()</script> (v1.0) [stable]'
    escaped = escape_mermaid_label(hostile)
    assert "<script>" not in escaped
    assert '"' not in escaped
    assert "[" not in escaped
    assert "]" not in escaped
    assert "(" not in escaped
    assert ")" not in escaped


def test_mermaid_empty_input_handling(profile_fixture: Profile) -> None:
    # 1. Empty skills groups
    p_empty_skills = copy.deepcopy(profile_fixture)
    p_empty_skills.skills.groups = []
    assert generate_mermaid_skill_map(p_empty_skills) == ""

    # 2. Empty projects
    p_empty_projects = copy.deepcopy(profile_fixture)
    p_empty_projects.projects = []
    assert generate_mermaid_skill_map(p_empty_projects) == ""

    # 3. Feature turned off
    p_disabled = copy.deepcopy(profile_fixture)
    p_disabled.features.mermaid_skill_map = False
    assert generate_mermaid_skill_map(p_disabled) == ""

    # 4. Not enough links
    p_isolated = copy.deepcopy(profile_fixture)
    for proj in p_isolated.projects:
        proj.stack = ["CompletelyUnrelatedTech123"]
    assert generate_mermaid_skill_map(p_isolated) == ""


def test_mermaid_node_limit(profile_fixture: Profile) -> None:
    # Test strict max_nodes enforcement
    diagram = generate_mermaid_skill_map(profile_fixture, max_nodes=10)
    assert diagram != ""
    # Extract unique node IDs from edges: grp_... --> tech_... or tech_... --> prj_...
    node_ids = set()
    for line in diagram.splitlines():
        if "-->" in line:
            parts = line.strip().split("-->")
            for part in parts:
                node_token = part.strip().split("[")[0].strip()
                if node_token:
                    node_ids.add(node_token)

    assert len(node_ids) <= 10


def test_skill_levels_honest_rendering(profile_fixture: Profile) -> None:
    p = copy.deepcopy(profile_fixture)
    # Set one skill to daily, one to comfortable, others null
    p.skills.groups[0].items[0] = SkillItem(name="Python", level=SkillLevel.DAILY)
    p.skills.groups[0].items[1] = SkillItem(name="TypeScript", level=SkillLevel.COMFORTABLE)
    p.skills.groups[0].items[2] = SkillItem(name="JavaScript", level=None)

    output = render_readme(
        profile=p,
        template_dir=Path("templates"),
        template_name="README.md.j2",
    )

    # Daily and comfortable labels must appear
    assert "`daily`" in output
    assert "`comfortable`" in output
    # JavaScript must be present, but without any level
    assert "**JavaScript**" in output


def test_currently_learning_line(profile_fixture: Profile) -> None:
    # When now.learning is empty, line must not appear
    output_empty = render_readme(
        profile=profile_fixture,
        template_dir=Path("templates"),
        template_name="README.md.j2",
    )
    assert "Currently learning:" not in output_empty

    # When populated, line must appear
    p = copy.deepcopy(profile_fixture)
    p.now.learning = ["RAG evaluation", "Edge ML deployment"]
    output_populated = render_readme(
        profile=p,
        template_dir=Path("templates"),
        template_name="README.md.j2",
    )
    assert "🌱 **Currently learning:** RAG evaluation • Edge ML deployment" in output_populated

