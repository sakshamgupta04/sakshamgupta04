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
    cols = 1 if mobile else 2
    gutter = 22
    margin = 14
    card_width = (width - margin * 2 - gutter * (cols - 1)) // cols
    card_height = 154
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
        lines = textwrap.wrap(cert.title, width=42 if mobile else 39, break_long_words=False, break_on_hyphens=False)
        lines = lines[:3]
        parts.append(
            f'<rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" rx="16" fill="{surface}" stroke="{stroke}" stroke-width="1.5"/>'
        )
        parts.append(f'<rect x="{x + 20}" y="{y + 20}" width="4" height="24" rx="2" fill="{accent}"/>')
        parts.append(
            f'<text x="{x + 36}" y="{y + 38}" font-family="Arial, Helvetica, sans-serif" font-size="12" letter-spacing="1.2" font-weight="700" fill="{accent}">{html.escape(cert.issuer.upper())}</text>'
        )
        for j, line in enumerate(lines):
            parts.append(
                f'<text x="{x + 22}" y="{y + 73 + j * 21}" font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="600" fill="{text}">{html.escape(line)}</text>'
            )
        parts.append(
            f'<text x="{x + 22}" y="{y + card_height - 19}" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{muted}">{html.escape(cert.kind.title())}  ·  Credential link below</text>'
        )
        parts.append(
            f'<path d="M {x + card_width - 36} {y + 30} l 12 -12 m -10 0 h 10 v 10" fill="none" stroke="{accent}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
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
