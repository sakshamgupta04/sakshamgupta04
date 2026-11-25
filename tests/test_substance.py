"""Unit tests for Phase 5 substance: projects, experience, research, education, and diagram validation."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.build_readme import render_readme
from scripts.helpers import (
    format_cert_kind,
    format_project_status,
    validate_mermaid_diagram,
)
from scripts.schema import Profile, ProjectItem, PublicationItem, validate_profile_dict


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


def test_diagram_validation_rules() -> None:
    # 1. Valid diagrams
    valid_fc = "flowchart TD\n  A[Client] --> B[API]\n  B --> C[(DB)]"
    valid_graph = "graph LR\n  In --> Out"
    assert validate_mermaid_diagram(valid_fc) == valid_fc
    assert validate_mermaid_diagram(valid_graph) == valid_graph

    # 2. Invalid starter token
    assert validate_mermaid_diagram("sequenceDiagram\n  Alice->>Bob: Hello") is None
    assert validate_mermaid_diagram("invalid token here") is None

    # 3. HTML tags rejected
    assert validate_mermaid_diagram("flowchart LR\n  A[<b>Client</b>] --> B") is None
    assert validate_mermaid_diagram("flowchart LR\n  A --> B<script>evil()</script>") is None

    # 4. Click or href directives rejected
    assert validate_mermaid_diagram('flowchart LR\n  A --> B\n  click A "https://evil.com"') is None
    assert validate_mermaid_diagram('graph TD\n  A --> B\n  href B "https://evil.com"') is None

    # 5. Max size limit exceeded
    huge_diagram = "flowchart LR\n" + ("  A --> B\n" * 500)
    assert validate_mermaid_diagram(huge_diagram, max_chars=100) is None

    # 6. None or empty
    assert validate_mermaid_diagram(None) is None
    assert validate_mermaid_diagram("   ") is None


def test_featured_projects_ordered_first(profile_fixture: Profile) -> None:
    p = copy.deepcopy(profile_fixture)
    p.projects.insert(0, ProjectItem(slug="paperlens", title="PaperLens", featured=False))
    output = render(p)
    pos_echonotes = output.find("EchoNotes")
    pos_paperlens = output.find("PaperLens")
    assert pos_echonotes != -1
    assert pos_paperlens != -1
    assert pos_echonotes < pos_paperlens


def test_project_measured_results_hiding(profile_fixture: Profile) -> None:
    # In fixture, all projects have results: []
    output_empty = render(profile_fixture)
    assert "Measured Evaluation &amp; Benchmarks:" not in output_empty

    # When results exist, section renders
    p = copy.deepcopy(profile_fixture)
    p.projects[0].results = ["WER: 8.2% on LibriSpeech clean", "Latency: 280ms p95"]
    output_populated = render(p)
    assert "Benchmarks:" in output_populated
    assert "WER: 8.2% on LibriSpeech clean" in output_populated


def test_research_publications_remain_hidden_even_when_data_exists(profile_fixture: Profile) -> None:
    # Publication metadata is retained but intentionally omitted from the profile README.
    p = copy.deepcopy(profile_fixture)
    p.publications = [
        PublicationItem(
            title="Privacy-Preserving On-Device Document AI",
            authors=["Saksham Gupta"],
            venue="IEEE Conference on AI",
            year=2026,
            status="Under Review",
            doi="10.1109/EXAMPLE.2026",
        )
    ]
    p.patent.mention = True
    p.patent.text = "System and Method for Automated Candidate Fit Scoring"
    output = render(p)
    assert "Research Publications" not in output
    assert "Privacy-Preserving On-Device Document AI" not in output
    assert "System and Method for Automated Candidate Fit Scoring" not in output


def test_education_and_certifications_formatting(profile_fixture: Profile) -> None:
    # When features.education is False
    p_hidden = copy.deepcopy(profile_fixture)
    p_hidden.features.education = False
    output_hidden = render(p_hidden)
    assert "Education" not in output_hidden

    p = copy.deepcopy(profile_fixture)
    p.features.education = True
    output = render(p)
    assert "Education" in output
    assert "B.Tech in Computer Science &amp; Engineering (AI/ML)" in output
    assert "CGPA 8.5/10" in output

    # Check cert kinds
    assert format_cert_kind("certification") == "Certification"
    assert format_cert_kind("course") == "Course"

    # Verify credential links: only when URL is present
    assert "assets/certifications-dark.svg" in output
    assert "[View credential](https://drive.google.com/file/d/1Bw5bg4Yojz2DPmFDPV0K1wRqYPpmOakV/view?usp=sharing)" in output


def test_status_formatting_helpers() -> None:
    assert format_project_status("shipped") == "🚀 Shipped"
    assert format_project_status("building") == "🔨 Building"
    assert format_project_status("planned") == "💡 Planned"


def test_featured_case_study_details(profile_fixture: Profile) -> None:
    output = render(profile_fixture)
    assert output.count("Challenge:") == 3
    assert output.count("<ul>") >= 3
    assert output.count("Approach:") == 3
    assert "Highlights:" in output
    assert "MediaRecorder" in output
    assert "Measured Evaluation &amp; Benchmarks:" not in output


def test_optional_case_study_details_hide_when_missing(profile_fixture: Profile) -> None:
    p = copy.deepcopy(profile_fixture)
    p.projects[0].challenge = None
    p.projects[0].approach = None
    output = render(p)
    assert output.count("Challenge:") == 2
    assert output.count("Approach:") == 2


def test_three_column_featured_gallery_shows_all_details(profile_fixture: Profile) -> None:
    output = render(profile_fixture)
    assert output.count('<td width="33%" valign="top" style="padding: 12px;">') == 3
    assert output.count('<table width="100%" cellspacing="0" cellpadding="0">') == 1
    assert "<summary><b>Project details ▾</b></summary>" not in output
    assert output.count("Case Study ↗") == 3
    assert "Live Site ↗" in output
    assert "Source Code ↗" in output
    assert output.count('alt="People.ai project screenshot"') == 1
    assert output.count('width="100%"') >= 4
    assert output.count("Challenge:") == 3
    assert output.count("Approach:") == 3
    assert output.count("Highlights:") == 3


def test_premium_gallery_preserves_images_and_link_destinations(profile_fixture: Profile) -> None:
    output = render(profile_fixture)
    for project in profile_fixture.projects[:3]:
        assert f'src="{project.image}"' in output
        assert f'href="{project.links.demo}"' in output
    assert "https://youtube-video-summarizer-sage.vercel.app/" in output
    assert "https://github.com/sakshamgupta04/Youtube-Video-Summarizer" in output
    assert "<summary><b>Project details ▾</b></summary>" not in output
    assert output.count("Challenge:") == 3


def test_balanced_readme_section_order_and_original_project_assets(profile_fixture: Profile) -> None:
    output = render(profile_fixture)
    headings = [
        "## 👤 About Me",
        "## ⚡ Featured Projects",
        "## 🛠️ Technical Stack",
        "## 💼 Professional Experience",
        "## 🎖️ Certifications",
        "## 🎓 Education",
        "## 🚀 Let's Connect",
    ]
    positions = [output.index(heading) for heading in headings]
    assert positions == sorted(positions)
    assert "Building software that connects intelligence with real-world use." in output
    assert output.count('<td width="33%" valign="top" style="padding: 12px;">') == 3
    for project in profile_fixture.projects[:3]:
        assert f'src="{project.image}"' in output
        assert f'href="{project.links.demo}"' in output
        assert project.tagline not in output
    assert "https://youtube-video-summarizer-sage.vercel.app/" in output
    assert "https://github.com/sakshamgupta04/Youtube-Video-Summarizer" in output
