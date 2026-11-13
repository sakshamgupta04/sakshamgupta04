"""Error classes and formatting for profile validation."""

from __future__ import annotations

from pydantic import ValidationError


class ProfileValidationError(Exception):
    """Raised when profile validation fails with actionable error messages."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("\n".join(errors))


def format_validation_error(err: ValidationError) -> list[str]:
    """Format Pydantic ValidationError into explicit 'Field -> How to fix' strings."""
    messages = []
    for item in err.errors():
        loc = " -> ".join(str(e) for e in item["loc"])
        msg, err_type = item["msg"], item["type"]
        if "enum" in err_type:
            exp = item.get("ctx", {}).get("expected", "")
            messages.append(
                f"Field '{loc}': Value invalid ({msg}). Fix in data/profile.yml by choosing one of: {exp}."
            )
        elif "missing" in err_type:
            messages.append(
                f"Field '{loc}': Missing required value. Fix in data/profile.yml by defining this field."
            )
        else:
            messages.append(f"Field '{loc}': {msg}. Fix this in data/profile.yml.")
    return messages
