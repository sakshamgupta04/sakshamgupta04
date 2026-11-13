"""Template helpers and content visibility utilities."""

from __future__ import annotations

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
        # Model is non-empty if at least one field has non-empty content
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
