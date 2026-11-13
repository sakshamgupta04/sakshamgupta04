"""Template helpers, validation utilities, and content visibility filters."""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel


def has(val: Any) -> bool:
    """Determine whether a value is considered present and non-empty.

    Returns False for None, empty strings, strings that equal 'null'/'none'/'todo'
    (case-insensitive), empty collections, or models where all fields are empty.
    """
    if val is None:
        return False
    if isinstance(val, str):
        cleaned = val.strip().lower()
        return bool(cleaned and cleaned not in ("null", "none", "todo"))
    if isinstance(val, (list, tuple, set)):
        return any(has(item) for item in val)
    if isinstance(val, dict):
        return any(has(v) for v in val.values())
    if isinstance(val, BaseModel):
        return any(has(v) for _, v in val.model_dump().items())
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return True
    return bool(val)


def find_todo_values(data: Any, path: str = "") -> list[tuple[str, str]]:
    """Recursively search for values containing 'TODO'."""
    results: list[tuple[str, str]] = []
    if isinstance(data, dict):
        for k, v in data.items():
            sub_path = f"{path}.{k}" if path else str(k)
            results.extend(find_todo_values(v, sub_path))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            sub_path = f"{path}[{idx}]"
            results.extend(find_todo_values(item, sub_path))
    elif isinstance(data, BaseModel):
        results.extend(find_todo_values(data.model_dump(), path))
    elif isinstance(data, str) and "todo" in data.lower():
        results.append((path, data))
    return results


def format_roadmap_status(status: str | Any) -> str:
    """Format roadmap status with both an icon and plain text word."""
    raw = str(getattr(status, "value", status)).strip().lower()
    mapping = {
        "done": "✅ Done",
        "doing": "⚡ In progress (doing)",
        "next": "📋 Next (planned)",
    }
    return mapping.get(raw, str(status))


def format_project_status(status: str | Any) -> str:
    """Format project status with icon and title-cased word."""
    raw = str(getattr(status, "value", status)).strip().lower()
    mapping = {
        "shipped": "🚀 Shipped",
        "building": "🔨 Building",
        "planned": "💡 Planned",
    }
    return mapping.get(raw, str(status).title())


def format_cert_kind(kind: str | Any) -> str:
    """Format certification kind into 'Certification' or 'Course'."""
    raw = str(getattr(kind, "value", kind)).strip().lower()
    return "Certification" if raw == "certification" else "Course"


def validate_mermaid_diagram(diagram: str | None, max_chars: int = 2000) -> str | None:
    """Validate project.diagram ensuring it starts with flowchart/graph, has no HTML/click/href, and respects size limits."""
    if not diagram or not isinstance(diagram, str):
        return None
    cleaned = diagram.strip()
    if not cleaned or len(cleaned) > max_chars:
        return None

    # Must start with flowchart or graph
    first_token = cleaned.split()[0].lower() if cleaned.split() else ""
    if first_token not in ("flowchart", "graph"):
        return None

    # No HTML tags permitted
    if re.search(r"<\/?[a-zA-Z][^>]*>", cleaned):
        return None

    # No click or href directives
    lowered = cleaned.lower()
    if re.search(r"\bclick\b", lowered) or re.search(r"\bhref\b", lowered):
        return None

    return cleaned
