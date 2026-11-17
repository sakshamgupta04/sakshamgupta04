"""Verify floating certification assets and credential links."""

from pathlib import Path
from xml.etree import ElementTree as ET

import yaml

from scripts.build_readme import render_readme
from scripts.schema import validate_profile_dict
from scripts.svg_certifications import render_certification_svg


def test_certification_showcase_preserves_all_credentials() -> None:
    profile = validate_profile_dict(yaml.safe_load(Path("data/profile.yml").read_text(encoding="utf-8")))
    rendered = render_readme(
        profile=profile,
        template_dir=Path("templates"),
        template_name="README.md.j2",
        dynamic_data={},
    )
    section = rendered.split("## 🎖️ Certifications &amp; Achievements", 1)[1].split("\n---", 1)[0]
    for name in ("certifications-dark.svg", "certifications-light.svg",
                 "certifications-mobile-dark.svg", "certifications-mobile-light.svg"):
        assert f"assets/{name}" in section
    assert "<details>" in section
    for credential in profile.certifications:
        assert credential.title in section
        if credential.url:
            assert section.count(credential.url) == 1
    assert section.count("[View credential]") == 6
    assert "AI/ML Hands-on Training Program" in section
    assert "Mar 2025" in section


def test_certification_svgs_have_separate_cards_in_all_variants() -> None:
    profile = validate_profile_dict(yaml.safe_load(Path("data/profile.yml").read_text(encoding="utf-8")))
    for dark in (True, False):
        for mobile in (True, False):
            svg = render_certification_svg(profile, dark=dark, mobile=mobile)
            root = ET.fromstring(svg)
            assert int(root.attrib["height"]) <= (420 if mobile else 270)
            rectangles = root.findall("{http://www.w3.org/2000/svg}rect")
            assert len(rectangles) == 2 * len(profile.certifications) + 1
            assert 'aria-labelledby="title desc"' in svg
            for cert in profile.certifications:
                assert cert.issuer.upper() in svg
