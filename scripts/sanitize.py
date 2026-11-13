"""Sanitization utilities for untrusted text and links."""

from __future__ import annotations

import html
import re
from urllib.parse import urlsplit

# Characters with special syntactic meaning in GitHub Flavored Markdown
_MD_SPECIAL_CHARS = re.compile(r"([\\`*_{}\[\]()#+\-.!|~<>])")
_HTML_TAGS = re.compile(r"<[^>]+>")
_MULTIPLE_SPACES = re.compile(r"\s+")
_SAFE_SCHEMES = frozenset({"http", "https", "mailto"})


def strip_html(text: str) -> str:
    """Strip all HTML tags and unescape remaining HTML entities."""
    if not text:
        return ""
    stripped = _HTML_TAGS.sub("", text)
    return html.unescape(stripped)


def escape_html(text: str) -> str:
    """Escape HTML special characters into safe HTML entities."""
    if not text:
        return ""
    return html.escape(text, quote=True)


def escape_markdown(text: str) -> str:
    """Escape Markdown syntactic characters to prevent formatting injection."""
    if not text:
        return ""
    return _MD_SPECIAL_CHARS.sub(r"\\\1", text)


def remove_newlines(text: str, replacement: str = " ") -> str:
    """Replace all CR/LF newlines with replacement and normalize consecutive whitespace."""
    if not text:
        return ""
    cleaned = text.replace("\r\n", replacement).replace("\r", replacement).replace("\n", replacement)
    return _MULTIPLE_SPACES.sub(" ", cleaned).strip()


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max_length characters, appending suffix if truncated."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    if max_length <= len(suffix):
        return text[:max_length]
    return text[: max_length - len(suffix)] + suffix


def is_safe_url(url: str | None) -> bool:
    """Check whether a URL uses only http, https, or mailto schemes."""
    if not url or not isinstance(url, str):
        return False
    trimmed = url.strip()
    try:
        parts = urlsplit(trimmed)
        return parts.scheme.lower() in _SAFE_SCHEMES
    except (ValueError, AttributeError):
        return False


def sanitize_text(text: str, max_length: int = 100) -> str:
    """Strip HTML, remove newlines, escape markdown, and truncate to max_length."""
    if not text:
        return ""
    clean = strip_html(text)
    single_line = remove_newlines(clean)
    escaped = escape_markdown(single_line)
    return truncate(escaped, max_length=max_length)
