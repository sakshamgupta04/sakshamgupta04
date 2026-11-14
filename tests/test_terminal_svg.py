"""Unit tests for SVG terminal generator, XML validity, escaping, and sizing."""

from __future__ import annotations

import copy
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import yaml

from scripts.build_readme import render_readme
from scripts.schema import Profile, validate_profile_dict
from scripts.svg_terminal import generate_terminal_svg, write_terminal_svgs

MAX_SVG_BYTES = 20 * 1024  # 20 KB limit per rules


@pytest.fixture
def profile_fixture() -> Profile:
    with open("data/profile.yml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return validate_profile_dict(data)


def test_svg_is_valid_xml(profile_fixture: Profile) -> None:
    for theme in ("dark", "light"):
        svg_content = generate_terminal_svg(profile_fixture, theme=theme)
        # Parse XML; will raise ParseError if invalid XML
        root = ET.fromstring(svg_content)
        assert root.tag.endswith("svg")
        assert root.attrib["width"] == "800"
        assert root.attrib["height"] == "220"


def test_svg_escapes_hostile_text(profile_fixture: Profile) -> None:
    hostile_profile = copy.deepcopy(profile_fixture)
    hostile_profile.identity.name = "Saksham <script>alert('xss')</script> & Co."
    hostile_profile.identity.headline = 'Dev "ML" <bold>'

    svg_content = generate_terminal_svg(hostile_profile, theme="dark")
    # Must parse without syntax errors
    root = ET.fromstring(svg_content)
    assert root is not None

    # Hostile tags must be safely escaped
    assert "<script>" not in svg_content
    assert "&lt;script&gt;" in svg_content
    assert "&amp;" in svg_content


def test_svg_stays_small(profile_fixture: Profile) -> None:
    for theme in ("dark", "light"):
        svg_content = generate_terminal_svg(profile_fixture, theme=theme)
        size_bytes = len(svg_content.encode("utf-8"))
        assert size_bytes < MAX_SVG_BYTES, f"SVG exceeds {MAX_SVG_BYTES} bytes: {size_bytes}"


def test_svg_prefers_reduced_motion(profile_fixture: Profile) -> None:
    svg_content = generate_terminal_svg(profile_fixture, theme="dark")
    assert "@media (prefers-reduced-motion: reduce)" in svg_content
    assert "animation: none" in svg_content


def test_write_terminal_svgs_creates_files(tmp_path: Path, profile_fixture: Profile) -> None:
    dark_path, light_path = write_terminal_svgs(profile_fixture, tmp_path)
    assert dark_path.exists()
    assert light_path.exists()
    assert dark_path.stat().st_size > 0
    assert light_path.stat().st_size > 0


def test_links_hidden_when_null(profile_fixture: Profile) -> None:
    # Portfolio and resume_pdf set to null to test hiding
    p = copy.deepcopy(profile_fixture)
    p.links.resume_pdf = None
    p.links.portfolio = None
    rendered = render_readme(
        profile=p,
        template_dir=Path("templates"),
        template_name="README.md.j2",
    )
    assert "[📄 Resume]" not in rendered
    assert "[🌐 Portfolio]" not in rendered
    assert "[💼 LinkedIn]" in rendered
    assert "[✉️ Email]" in rendered
    assert "[🧩 LeetCode]" in rendered
