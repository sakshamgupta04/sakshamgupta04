"""Template helpers, validation utilities, and content visibility filters."""

from __future__ import annotations

import re
import sys
from pathlib import Path
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


def write_step_summary(
    summary_path: Path,
    profile: Any,
    dynamic_data: dict[str, Any],
    cache_note: str | None,
    size_bytes: int,
    offline: bool,
) -> None:
    """Write GitHub Action step summary markdown to GITHUB_STEP_SUMMARY."""
    data_source = cache_note if cache_note else "Live GitHub API (Synchronized)"
    refreshed: list[str] = [
        "💻 Terminal Header SVGs (`assets/terminal-*.svg`)",
        "📄 Main Profile README (`README.md`)",
    ]
    if has(dynamic_data.get("languages")):
        refreshed.append("📊 Language Statistics Bar SVGs (`assets/languages-*.svg`)")
    if has(dynamic_data.get("recent_activity")):
        refreshed.append("⚡ Recent Public Activity Stream")
    if has(dynamic_data.get("project_last_updated")):
        refreshed.append("⏱️ Featured Project Repository Timestamps")

    content = [
        "## 🚀 Profile README Refresh Report",
        "",
        "| Metric | Details |",
        "| :--- | :--- |",
        "| **Status** | ✅ Success |",
        f"| **README Size** | `{size_bytes:,} bytes` (Limit: 102,400 bytes) |",
        f"| **Data Source** | {data_source} |",
        f"| **Offline Mode** | `{'Enabled' if offline else 'Disabled'}` |",
        "",
        "### 🔄 Refreshed Sections & Components",
        "",
    ]
    for item in refreshed:
        content.append(f"- {item}")
    content.append("")

    try:
        with summary_path.open("a", encoding="utf-8") as f:
            f.write("\n".join(content) + "\n")
    except OSError as exc:
        print(f"[WARN] Failed to write GitHub step summary: {exc}", file=sys.stderr)

