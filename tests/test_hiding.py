"""Unit tests for content visibility and the has() helper."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from scripts.build_readme import render_readme
from scripts.helpers import has
from scripts.schema import Identity, Patent, validate_profile_dict


class DummyEmpty(BaseModel):
    field_a: str | None = None
    field_b: list[str] = []


def test_has_with_empty_and_null_values() -> None:
    assert has(None) is False
    assert has("") is False
    assert has("   ") is False
    assert has("null") is False
    assert has("NULL") is False
    assert has("None") is False
    assert has("none") is False
    assert has("TODO") is False
    assert has("todo") is False
    assert has([]) is False
    assert has({}) is False
    assert has([None, ""]) is False
    assert has(DummyEmpty()) is False
    assert has(Patent(mention=False, text=None)) is False


def test_has_with_valid_content() -> None:
    assert has("Saksham") is True
    assert has(0) is True
    assert has(42) is True
    assert has(True) is True
    assert has(["Python"]) is True
    assert has({"key": "val"}) is True
    assert has(Identity(name="Saksham", handle="sakshamgupta04")) is True


def test_readme_render_hides_empty_fields() -> None:
    data = {
        "identity": {
            "name": "Saksham Gupta",
            "handle": "sakshamgupta04",
            "headline": "Full-stack developer",
            "location": None,  # Should be completely hidden
            "tagline": "",     # Should be hidden
        }
    }
    profile = validate_profile_dict(data)
    rendered = render_readme(
        profile=profile,
        template_dir=Path("templates"),
        template_name="README.md.j2",
    )

    assert "Saksham Gupta" in rendered
    assert "Full-stack developer" in rendered
    assert "location:" not in rendered
    assert "tagline:" not in rendered
    assert "null" not in rendered.lower()
    assert "none" not in rendered.lower()
    assert "todo" not in rendered.lower()
