"""Ensure the certification showcase is compact and preserves credential links."""

from pathlib import Path

import yaml

from scripts.build_readme import render_readme
from scripts.schema import validate_profile_dict


def test_certification_showcase_preserves_all_credentials() -> None:
    profile = validate_profile_dict(yaml.safe_load(Path("data/profile.yml").read_text(encoding="utf-8")))
    rendered = render_readme(
        profile=profile,
        template_dir=Path("templates"),
        template_name="README.md.j2",
        dynamic_data={},
    )
    section = rendered.split("## 🎖️ Certifications &amp; Achievements", 1)[1].split("\n---", 1)[0]
    assert "| Machine Learning &amp; Python | Cloud, Web &amp; Tools |" in section
    for credential in profile.certifications:
        assert credential.title in section
        if credential.url:
            assert section.count(credential.url) == 1
    assert section.count("[View credential]") == 6
    assert "AI/ML Hands-on Training Program" in section
    assert "March 2025" in section
