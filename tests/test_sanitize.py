"""Unit tests for untrusted text sanitization and safe URL validation."""

from __future__ import annotations

import pytest

from scripts.sanitize import (
    escape_html,
    escape_markdown,
    is_safe_url,
    remove_newlines,
    sanitize_text,
    strip_html,
    truncate,
)


def test_strip_html_hostile_tags() -> None:
    hostile = "<script>alert('xss')</script><b>Hello</b><img src=x onerror=alert(1)>"
    assert strip_html(hostile) == "alert('xss')Hello"


def test_escape_html() -> None:
    hostile = '<div class="alert">& "danger"</div>'
    expected = '&lt;div class=&quot;alert&quot;&gt;&amp; &quot;danger&quot;&lt;/div&gt;'
    assert escape_html(hostile) == expected


def test_escape_markdown() -> None:
    injection = "## Heading *bold* [link](http://test.com) `code`"
    escaped = escape_markdown(injection)
    assert "\\#\\#" in escaped
    assert "\\*bold\\*" in escaped
    assert "\\[link\\]" in escaped
    assert "\\`code\\`" in escaped


def test_remove_newlines() -> None:
    multiline = "Line 1\r\nLine 2\n\nLine 3\rLine 4"
    assert remove_newlines(multiline) == "Line 1 Line 2 Line 3 Line 4"


def test_truncate() -> None:
    text = "The quick brown fox jumps over the lazy dog"
    assert truncate(text, max_length=20) == "The quick brown f..."
    assert truncate(text, max_length=100) == text
    assert truncate(text, max_length=3) == "The"


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://github.com/sakshamgupta04", True),
        ("http://example.com/demo", True),
        ("mailto:work.saksham04@gmail.com", True),
        ("javascript:alert(1)", False),
        ("data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==", False),
        ("file:///etc/passwd", False),
        ("ftp://files.example.com", False),
        ("vbscript:msgbox(1)", False),
        ("//protocol-relative.com", False),
        ("", False),
        (None, False),
    ],
)
def test_is_safe_url(url: str | None, expected: bool) -> None:
    assert is_safe_url(url) is expected


def test_sanitize_text_composite() -> None:
    hostile = "<b>Commit title</b>:\nfeat: add [feature]\r\n<script>evil()</script>"
    clean = sanitize_text(hostile, max_length=40)
    assert "<" not in clean
    assert "\n" not in clean
    assert "\\[feature\\]" in clean

