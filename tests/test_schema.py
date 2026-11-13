"""Unit tests for schema validation and descriptive error reporting."""

from __future__ import annotations

import copy
from typing import Any

import pytest
import yaml

from scripts.schema import ProfileValidationError, validate_profile_dict


@pytest.fixture
def valid_profile_data() -> dict[str, Any]:
    with open("data/profile.yml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_valid_profile(valid_profile_data: dict[str, Any]) -> None:
    profile = validate_profile_dict(valid_profile_data)
    assert profile.identity.name == "Saksham Gupta"
    assert profile.identity.handle == "sakshamgupta04"


def test_invalid_project_status(valid_profile_data: dict[str, Any]) -> None:
    data = copy.deepcopy(valid_profile_data)
    data["projects"][0]["status"] = "finished"  # invalid status
    with pytest.raises(ProfileValidationError) as exc_info:
        validate_profile_dict(data)

    err_text = str(exc_info.value)
    assert "projects -> 0 -> status" in err_text
    assert "Fix in data/profile.yml by choosing one of:" in err_text


def test_invalid_roadmap_status(valid_profile_data: dict[str, Any]) -> None:
    data = copy.deepcopy(valid_profile_data)
    data["goals"]["roadmap"][0]["status"] = "pending"
    with pytest.raises(ProfileValidationError) as exc_info:
        validate_profile_dict(data)

    err_text = str(exc_info.value)
    assert "goals -> roadmap -> 0 -> status" in err_text
    assert "Fix in data/profile.yml by choosing one of:" in err_text


def test_invalid_certification_kind(valid_profile_data: dict[str, Any]) -> None:
    data = copy.deepcopy(valid_profile_data)
    data["certifications"][0]["kind"] = "diploma"
    with pytest.raises(ProfileValidationError) as exc_info:
        validate_profile_dict(data)

    err_text = str(exc_info.value)
    assert "certifications -> 0 -> kind" in err_text
    assert "Fix in data/profile.yml by choosing one of:" in err_text


def test_invalid_skill_level(valid_profile_data: dict[str, Any]) -> None:
    data = copy.deepcopy(valid_profile_data)
    data["skills"]["groups"][0]["items"][0]["level"] = "godmode"
    with pytest.raises(ProfileValidationError) as exc_info:
        validate_profile_dict(data)

    err_text = str(exc_info.value)
    assert "skills -> groups -> 0 -> items -> 0 -> level" in err_text
    assert "Fix in data/profile.yml by choosing one of:" in err_text


def test_invalid_availability_status(valid_profile_data: dict[str, Any]) -> None:
    data = copy.deepcopy(valid_profile_data)
    data["identity"]["availability"]["status"] = "busy"
    with pytest.raises(ProfileValidationError) as exc_info:
        validate_profile_dict(data)

    err_text = str(exc_info.value)
    assert "identity -> availability -> status" in err_text
    assert "Fix in data/profile.yml by choosing one of:" in err_text


def test_missing_required_name(valid_profile_data: dict[str, Any]) -> None:
    data = copy.deepcopy(valid_profile_data)
    del data["identity"]["name"]
    with pytest.raises(ProfileValidationError) as exc_info:
        validate_profile_dict(data)

    err_text = str(exc_info.value)
    assert "identity -> name" in err_text
    assert "Missing required value" in err_text


def test_unsafe_link_rejected(valid_profile_data: dict[str, Any]) -> None:
    data = copy.deepcopy(valid_profile_data)
    data["links"]["portfolio"] = "javascript:alert(1)"
    with pytest.raises(ProfileValidationError) as exc_info:
        validate_profile_dict(data)

    err_text = str(exc_info.value)
    assert "links -> portfolio" in err_text
    assert "Must start with http://, https://, or mailto:" in err_text
