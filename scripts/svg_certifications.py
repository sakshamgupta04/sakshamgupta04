"""Render GitHub-safe floating certification cards as static SVG assets."""

from __future__ import annotations

import html
import textwrap
from pathlib import Path
from xml.etree import ElementTree as ET

from scripts.schema import Profile


def render_certification_svg(profile: Profile, *, dark: bool, mobile: bool) -> str:
    """Create accessible cards with spacious gutters and no external assets."""
    certs = profile.certifications
    width = 560 if mobile else 1120
    cols = 2 if mobile else 3
    gutter = 12
    margin = 10
    card_width = (width - margin * 2 - gutter * (cols - 1)) // cols
    card_height = 124 if mobile else 116
    row_step = card_height + gutter
    rows = (len(certs) + cols - 1) // cols
    height = margin * 2 + rows * card_height + max(rows - 1, 0) * gutter
    bg = "#0B1426" if dark else "#F7F9FE"
    surface = "#15243A" if dark else "#FFFFFF"
    stroke = "#344762" if dark else "#D8E2F1"
    text = "#F3F7FF" if dark else "#17243C"
    muted = "#B3C4DB" if dark else "#50637D"
    accent = "#80C9FF" if dark else "#1766B2"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Certifications and achievements</title>',
        '<desc id="desc">Six individual credential cards with issuer and course information. Verification links are provided below the graphic.</desc>',
        f'<rect width="{width}" height="{height}" fill="{bg}" rx="16"/>',
    ]
    for i, cert in enumerate(certs):
        x = margin + (i % cols) * (card_width + gutter)
        y = margin + (i // cols) * row_step
        lines = textwrap.wrap(cert.title, width=29 if mobile else 30, break_long_words=False, break_on_hyphens=False)
        lines = lines[:3]
        parts.append(
            f'<rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" rx="12" fill="{surface}" stroke="{stroke}" stroke-width="1.5"/>'
        )
        parts.append(f'<rect x="{x + 13}" y="{y + 13}" width="4" height="16" rx="2" fill="{accent}"/>')
        parts.append(
            f'<text x="{x + 25}" y="{y + 26}" font-family="Arial, Helvetica, sans-serif" font-size="11" letter-spacing="0.7" font-weight="700" fill="{accent}">{html.escape(cert.issuer.upper())}</text>'
        )
        for j, line in enumerate(lines):
            parts.append(
                f'<text x="{x + 14}" y="{y + 49 + j * 17}" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" fill="{text}">{html.escape(line)}</text>'
            )
        parts.append(
            f'<text x="{x + 22}" y="{y + card_height - 10}" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="{muted}">{html.escape(cert.kind.title())}  ·  Verify below</text>'
        )
        parts.append(
            f'<path d="M {x + card_width - 30} {y + 23} l 12 -12 m -10 0 h 10 v 10" fill="none" stroke="{accent}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        )
    parts.append("</svg>")
    svg = "\n".join(parts) + "\n"
    ET.fromstring(svg)
    return svg


def write_certification_svgs(profile: Profile, assets_dir: Path) -> None:
    """Write light/dark desktop and mobile SVGs from the profile source of truth."""
    assets_dir.mkdir(parents=True, exist_ok=True)
    for dark in (True, False):
        for mobile in (True, False):
            name = f"certifications-{'mobile-' if mobile else ''}{'dark' if dark else 'light'}.svg"
            (assets_dir / name).write_text(
                render_certification_svg(profile, dark=dark, mobile=mobile),
                encoding="utf-8",
            )
