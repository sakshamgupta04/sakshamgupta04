"""Regression test for hiding unavailable contact links."""

import copy
from pathlib import Path

import yaml

from scripts.build_readme import render_readme
from scripts.schema import validate_profile_dict


def test_links_hidden_when_null() -> None:
    with open("data/profile.yml", encoding="utf-8") as f:
        profile = validate_profile_dict(yaml.safe_load(f))
    p = copy.deepcopy(profile)
    p.links.resume_pdf = None
    p.links.portfolio = None
    rendered = render_readme(profile=p, template_dir=Path("templates"), template_name="README.md.j2")
    assert "[📄 Resume]" not in rendered
    assert "[🌐 Portfolio]" not in rendered
    assert "[💼 **LinkedIn**]" in rendered
    assert "[✉️ **Email**]" in rendered
    assert "[🧩 **LeetCode**]" in rendered
