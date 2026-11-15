"""Generate modern 4-row horizontal Technical Stack SVG matching approved reference."""

from __future__ import annotations

import argparse
from pathlib import Path


def get_logo_svg(tech: str) -> str:
    """Return inline SVG paths for verified technology logos."""
    logos = {
        "Python": (
            '<path d="M7.9 0C3.7 0 4 1.8 4 1.8l.02 1.9h4.1V4H2.4S0 3.7 0 8c0 4.2 2.1 4.1 2.1 4.1h1.3v-1.8s-.1-2.1 2.1-2.1h4.1s2 0 2-2V1.8S12 0 7.9 0zM5.5 1.1a.7.7 0 110 1.4.7.7 0 010-1.4z" fill="#38BDF8"/>'
            '<path d="M8.1 16c4.2 0 3.9-1.8 3.9-1.8l-.02-1.9H7.9V12h5.7s2.4.3 2.4-4c0-4.2-2.1-4.1-2.1-4.1h-1.3v1.8s.1 2.1-2.1 2.1H6.4s-2 0-2 2v4.4s-.4 1.8 3.7 1.8zm2.4-1.1a.7.7 0 110-1.4.7.7 0 010 1.4z" fill="#FBBF24"/>'
        ),
        "TypeScript": (
            '<rect width="16" height="16" rx="3" fill="#3178C6"/>'
            '<path d="M2.5 5h5v1.2H5.6v5.8H4.4V6.2H2.5V5zm6.2 2.2h1.2c.4 0 .7.1.9.3.2.2.3.4.3.7 0 .4-.2.7-.5.9l1 .9H10l-.8-.8h-.5v.8H8.7V7.2zm1.2 1.3c.2 0 .3 0 .4-.1.1-.1.1-.2.1-.3 0-.1 0-.2-.1-.3-.1-.1-.2-.1-.4-.1h-.4v.8h.4z" fill="#FFF"/>'
        ),
        "JavaScript": (
            '<rect width="16" height="16" rx="3" fill="#F7DF1E"/>'
            '<path d="M4.5 13.5l1.3-.8c.3.5.5.8.9.8.4 0 .6-.2.6-.7V7.5h1.5v5.3c0 .6-.2 1-.5 1.3-.4.3-.9.5-1.5.5-.9 0-1.7-.5-2.3-1.1zm4.8-.2l1.3-.7c.3.5.7.8 1.2.8.5 0 .8-.2.8-.5 0-.3-.2-.5-.8-.7l-.6-.2c-1-.4-1.6-.9-1.6-1.8 0-.6.2-1 .6-1.3.5-.4 1.1-.5 1.8-.5.7 0 1.3.2 1.8.6l-1 1c-.3-.3-.6-.5-1-.5s-.6.2-.6.4c0 .3.2.4.6.6l.6.2c1.2.5 1.8 1 1.8 2 0 .6-.2 1.1-.7 1.5-.5.4-1.2.6-2 .6-.9 0-1.6-.3-2-.8z" fill="#000"/>'
        ),
        "C++": (
            '<path d="M8 0L14.9 4v8L8 16 1.1 12V4L8 0z" fill="#00599C"/>'
            '<path d="M7 6.2c-.4-.5-.9-.7-1.5-.7-1.3 0-2.2 1-2.2 2.5s.9 2.5 2.2 2.5c.6 0 1.1-.2 1.5-.7l.9.8c-.6.7-1.4 1.1-2.4 1.1-2 0-3.5-1.5-3.5-3.7S3.5 4.3 5.5 4.3c1 0 1.8.4 2.4 1.1l-.9.8zm2.2 1.2h.7v-1h.6v1h.7v.6h-.7v1h-.6v-1h-.7v-.6zm2.6 0h.7v-1h.6v1h.7v.6h-.7v1h-.6v-1h-.7v-.6z" fill="#FFF"/>'
        ),
        "Java": (
            '<path d="M6 13.5s-.8.6 1.5.8c2.8.2 4.3-.2 4.3-.2s-.6.4-2 .5c-2.3.2-4.5-.4-3.8-1.1zm-.6-2s-.7.7 1.4.9c2.5.2 4.2-.2 4.2-.2s-.6.4-1.8.5c-2.1.2-4.4-.3-3.8-1.2zm6.2-3.8s.8.8-.8 2.2c-1.8 1.6-4.1 1.5-4.1 1.5s1.2-.5 2.4-1.2c1.5-.8 2.5-2.5 2.5-2.5zm-5.7 1.6s-.6.6 1.3.8c2.3.2 3.8-.1 3.8-.1s-.6.4-1.7.5c-1.9.2-4.1-.3-3.4-1.2z" fill="#EA2D2E"/>'
            '<path d="M8.5 0s2.2 2.2-1.3 5.4c-2.8 2.6-.6 4 .5 5.5-1.4-1.6-2.5-3.1-.7-4.8 2.3-2.1 2.3-3.6 1.5-6.1z" fill="#5382A1"/>'
        ),
        "SQL": (
            '<ellipse cx="8" cy="3.5" rx="7" ry="2.5" fill="#00758F"/>'
            '<path d="M1 3.5v4c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5v-4C15 4.9 11.9 6 8 6S1 4.9 1 3.5z" fill="#0096B8"/>'
            '<path d="M1 7.5v4c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5v-4c0 1.4-3.1 2.5-7 2.5s-7-1.1-7-2.5z" fill="#005C6E"/>'
        ),
        "React": (
            '<ellipse cx="8" cy="8" rx="2" ry="2" fill="#61DAFB"/>'
            '<ellipse cx="8" cy="8" rx="7.5" ry="3" fill="none" stroke="#61DAFB" stroke-width="1"/>'
            '<ellipse cx="8" cy="8" rx="7.5" ry="3" fill="none" stroke="#61DAFB" stroke-width="1" transform="rotate(60 8 8)"/>'
            '<ellipse cx="8" cy="8" rx="7.5" ry="3" fill="none" stroke="#61DAFB" stroke-width="1" transform="rotate(120 8 8)"/>'
        ),
        "Next.js": (
            '<circle cx="8" cy="8" r="7.5" fill="#000" stroke="#293B59" stroke-width="0.8"/>'
            '<path d="M5 4h1.5l5.2 6.8V4H13v8h-1.5L6.3 5.2V12H5V4z" fill="#FFF"/>'
        ),
        "Node.js": (
            '<path d="M8 1l6.9 4v8L8 17 1.1 13V5L8 1z" fill="#339933"/>'
            '<path d="M8 4.5l4.3 2.5v5L8 14.5 3.7 12V7L8 4.5z" fill="#222"/>'
            '<path d="M6 7.5v4l3.5-2v-4L6 7.5z" fill="#66CC33"/>'
        ),
        "FastAPI": (
            '<circle cx="8" cy="8" r="7.5" fill="#009688"/>'
            '<path d="M8.8 2.5L4 9.2h3.5L7.2 13.5 12 6.8H8.5L8.8 2.5z" fill="#FFF"/>'
        ),
        "Supabase": (
            '<path d="M8.5 1.5c.3-.5 1.1-.3 1.2.3l1.8 7.2h4c.6 0 .9.7.5 1.1l-7.5 7.4c-.4.4-1.1.2-1.2-.4L5.5 10H1.5c-.6 0-.9-.7-.5-1.1l7.5-7.4z" fill="#3ECF8E"/>'
        ),
        "PyTorch": (
            '<path d="M9.8 1.8a5.5 5.5 0 00-6.1 8.8l1.3-1.3a3.7 3.7 0 014.2-5.9l.6-1.6z" fill="#EE4C2C"/>'
            '<circle cx="11.5" cy="4.2" r="1.1" fill="#EE4C2C"/>'
        ),
        "TensorFlow": (
            '<path d="M8 1L1.5 4.8v6.4L5 13.2v-4L8 11l3-1.8v4l3.5-2V4.8L8 1z" fill="#FF6F00"/>'
            '<path d="M8 1v10l3-1.8v4l3.5-2V4.8L8 1z" fill="#FFA800"/>'
        ),
        "Scikit-learn": (
            '<ellipse cx="5" cy="8" rx="4.5" ry="4.5" fill="#F89939"/>'
            '<ellipse cx="11" cy="8" rx="4.5" ry="4.5" fill="#3499CD" opacity="0.85"/>'
        ),
        "OpenCV": (
            '<circle cx="8" cy="4.5" r="3" fill="none" stroke="#E83E3E" stroke-width="1.8"/>'
            '<circle cx="4.5" cy="11.5" r="3" fill="none" stroke="#5C3EE8" stroke-width="1.8"/>'
            '<circle cx="11.5" cy="11.5" r="3" fill="none" stroke="#3EE85C" stroke-width="1.8"/>'
        ),
        "Gemini": (
            '<path d="M8 0c0 4.4-3.6 8-8 8 4.4 0 8 3.6 8 8 0-4.4 3.6-8 8-8-4.4 0-8-3.6-8-8z" fill="url(#geminiGrad)"/>'
        ),
        "GCP": (
            '<path d="M12.4 7a4.2 4.2 0 00-7.8-1.2A3.5 3.5 0 001.5 9a3.5 3.5 0 003.5 3.5h7.2a3 3 0 003-3 3 3 0 00-2.8-2.5z" fill="#4285F4"/>'
            '<path d="M8.2 4.6a4.2 4.2 0 013.9 2.5 3 3 0 012.7 2.4c.1-.4.2-.7.2-1a3.5 3.5 0 00-3.5-3.5h-.6A4.2 4.2 0 008.2 4.6z" fill="#EA4335"/>'
            '<path d="M4.6 12.5h7.6a3 3 0 002.8-2 3 3 0 01-2.8 2H5A3.5 3.5 0 011.5 9c0 .4.1.8.2 1.2a3.5 3.5 0 002.9 2.3z" fill="#34A853"/>'
            '<path d="M1.7 10.2A3.5 3.5 0 011.5 9a3.5 3.5 0 013.1-3.2A4.2 4.2 0 018.2 4.6 4.2 4.2 0 004.6 5.8 3.5 3.5 0 001.7 10.2z" fill="#FBBC05"/>'
        ),
        "Docker": (
            '<path d="M14.5 7.2c-.3 0-.8.1-1.2.3-.5-.6-1.2-1-2.1-1-.1 0-.3 0-.4.1-.4-1.2-1.5-2.1-2.9-2.1v.8c1 0 1.9.7 2.2 1.7-.3.2-.6.4-.8.7-.3 0-.5-.1-.8-.1-.4 0-.7.1-1 .2V5.5H6.2V7H4.9V5.5H3.6V7H2.3V5.5H1V7H0c.1 2.3 1.5 4.3 3.6 5 2.1.8 4.7.7 7-.3 2.1-.9 3.5-2.7 3.9-4.5h.5c.3 0 .7-.1.9-.3.2-.2.3-.5.3-.7s-.2-.7-.7-.7z" fill="#2496ED"/>'
        ),
        "PostgreSQL": (
            '<path d="M8 1.5c-3.6 0-6.5 2.5-6.5 6 0 2.2 1.2 4.1 3 5.2-.2.6-.7 1.3-1.5 1.8 1.2.1 2.5-.4 3.3-1.2.6.2 1.1.2 1.7.2 3.6 0 6.5-2.5 6.5-6s-2.9-6-6.5-6z" fill="#336791"/>'
            '<path d="M7 4.5c.5-.3 1.2-.5 2-.5 1.5 0 2.5.8 2.5 2 0 1-.8 1.8-1.8 2h-1c-.5 0-.8-.3-.8-.8V4.5z" fill="#FFF" opacity="0.8"/>'
        ),
        "Actions": (
            '<circle cx="4.5" cy="8" r="2.5" fill="#2088FF"/>'
            '<circle cx="11.5" cy="4.5" r="2.5" fill="#2088FF"/>'
            '<circle cx="11.5" cy="11.5" r="2.5" fill="#2088FF"/>'
            '<path d="M4.5 8h4l3-3.5m-3 3.5l3 3.5" fill="none" stroke="#2088FF" stroke-width="1.2"/>'
        ),
        "Git": (
            '<path d="M15.7 7.2L8.8.3c-.4-.4-1-.4-1.4 0L6 1.7l1.8 1.8c.4-.1.9 0 1.2.3.4.4.4 1 0 1.4-.4.4-1 .4-1.4 0-.3-.3-.4-.8-.3-1.2L5.6 2.2.3 7.5c-.4.4-.4 1 0 1.4l6.9 6.9c.4.4 1 .4 1.4 0l6.9-6.9c.4-.4.4-1 .2-1.7z" fill="#F05032"/>'
            '<circle cx="7.2" cy="11.5" r="1.3" fill="#FFF"/>'
            '<circle cx="10.5" cy="8.2" r="1.3" fill="#FFF"/>'
            '<path d="M7.2 11.5l3.3-3.3" stroke="#FFF" stroke-width="1"/>'
        ),
    }
    return logos.get(tech, '<circle cx="8" cy="8" r="7" fill="#38BDF8"/>')


def generate_tech_stack_svg(theme: str = "dark") -> str:
    """Generate 4-row horizontal Technical Stack SVG."""
    if theme == "light":
        bg_card, border_col = "#FFFFFF", "#CBD5E1"
        bg_squircle, bg_pill = "#F1F5F9", "#FFFFFF"
        text_primary, text_secondary = "#0F172A", "#475569"
        divider_col = "#E2E8F0"
    else:  # dark
        bg_card, border_col = "#0B132B", "#293B59"
        bg_squircle, bg_pill = "#111C31", "#17243C"
        text_primary, text_secondary = "#F4F7FF", "#A5B4CF"
        divider_col = "#1E293B"

    rows = [
        {
            "icon_svg": '<text x="19" y="24" font-family="monospace" font-size="16" font-weight="800" fill="#38BDF8" text-anchor="middle">&lt;/&gt;</text>',
            "accent": "#38BDF8",
            "title": "Languages & Core",
            "desc": "Programming, algorithms, and application logic.",
            "techs": [
                ("Python", 82),
                ("TypeScript", 100),
                ("JavaScript", 98),
                ("C++", 66),
                ("Java", 70),
                ("SQL", 64),
            ],
        },
        {
            "icon_svg": '<path d="M19 12L10 17L19 22L28 17L19 12Z" fill="none" stroke="#8B5CF6" stroke-width="1.8"/><path d="M10 20.5L19 25.5L28 20.5" fill="none" stroke="#8B5CF6" stroke-width="1.8"/>',
            "accent": "#8B5CF6",
            "title": "Full-Stack Development",
            "desc": "Responsive web apps, backend services, & APIs.",
            "techs": [
                ("React", 80),
                ("Next.js", 86),
                ("Node.js", 88),
                ("FastAPI", 86),
                ("Supabase", 98),
            ],
        },
        {
            "icon_svg": '<path d="M15 13a4 4 0 00-4 4c0 1.5.8 2.8 2 3.5V23h3v-2.5a4 4 0 00-1-7.5zm8 0a4 4 0 00-1 7.5V23h3v-2.5c1.2-.7 2-2 2-3.5a4 4 0 00-4-4z" fill="#2DD4BF"/>',
            "accent": "#2DD4BF",
            "title": "AI & Machine Learning",
            "desc": "Predictive models, vision systems, & AI integrations.",
            "techs": [
                ("PyTorch", 90),
                ("TensorFlow", 106),
                ("Scikit-learn", 104),
                ("OpenCV", 88),
                ("Gemini", 84),
            ],
        },
        {
            "icon_svg": '<path d="M24 21h-9.5a4.5 4.5 0 01-1-8.9 6 6 0 0111.5-1.1A4.5 4.5 0 0124 21z" fill="none" stroke="#38BDF8" stroke-width="1.8"/>',
            "accent": "#38BDF8",
            "title": "Cloud, Data & DevOps",
            "desc": "Cloud deployment, data infrastructure, & CI/CD.",
            "techs": [
                ("GCP", 74),
                ("Docker", 84),
                ("PostgreSQL", 106),
                ("Actions", 88),
                ("Git", 66),
            ],
        },
    ]

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 352" width="880" height="352">',
        "  <defs>",
        '    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        f'      <stop offset="0%" stop-color="{bg_card}"/>',
        f'      <stop offset="100%" stop-color="{bg_card}" stop-opacity="0.95"/>',
        "    </linearGradient>",
        '    <linearGradient id="geminiGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#38BDF8"/>',
        '      <stop offset="100%" stop-color="#8B5CF6"/>',
        "    </linearGradient>",
        "    <style>",
        '      .txt-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14.5px; font-weight: 700; }',
        '      .txt-desc { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 11px; font-weight: 400; }',
        '      .txt-badge { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 11.5px; font-weight: 600; }',
        "    </style>",
        "  </defs>",
        f'  <rect x="1" y="1" width="878" height="350" rx="14" fill="url(#cardGrad)" stroke="{border_col}" stroke-width="1.2"/>',
    ]

    row_h = 88
    for i, r in enumerate(rows):
        y = i * row_h
        if i > 0:
            lines.append(
                f'  <line x1="20" y1="{y}" x2="860" y2="{y}" stroke="{divider_col}" stroke-width="1"/>'
            )

        # Left squircle + vertical accent bar + text
        lines.append(f'  <g transform="translate(24, {y + 24})">')
        lines.append(
            f'    <rect width="38" height="38" rx="10" fill="{bg_squircle}" stroke="{border_col}" stroke-width="1"/>'
        )
        lines.append(f"    {r['icon_svg']}")
        lines.append("  </g>")

        lines.append(
            f'  <rect x="74" y="{y + 22}" width="3" height="42" rx="1.5" fill="{r["accent"]}"/>'
        )
        lines.append(
            f'  <text x="88" y="{y + 39}" class="txt-title" fill="{text_primary}">{r["title"]}</text>'
        )
        lines.append(
            f'  <text x="88" y="{y + 57}" class="txt-desc" fill="{text_secondary}">{r["desc"]}</text>'
        )

        # Right badges
        cur_x = 356
        badge_y = y + 28
        for tech, badge_w in r["techs"]:
            lines.append(f'  <g transform="translate({cur_x}, {badge_y})">')
            lines.append(
                f'    <rect width="{badge_w}" height="30" rx="15" fill="{bg_pill}" stroke="{border_col}" stroke-width="1"/>'
            )
            lines.append('    <g transform="translate(8, 7)">')
            lines.append(f"      {get_logo_svg(tech)}")
            lines.append("    </g>")
            lines.append(
                f'    <text x="30" y="19" class="txt-badge" fill="{text_primary}">{tech}</text>'
            )
            lines.append("  </g>")
            cur_x += badge_w + 8

    lines.append("</svg>")
    return "\n".join(lines)


def write_tech_stack_svgs(output_dir: Path) -> tuple[Path, Path]:
    """Write dark and light Technical Stack SVGs."""
    output_dir.mkdir(parents=True, exist_ok=True)
    d = output_dir / "tech-stack-dark.svg"
    l = output_dir / "tech-stack-light.svg"
    d.write_text(generate_tech_stack_svg("dark"), encoding="utf-8")
    l.write_text(generate_tech_stack_svg("light"), encoding="utf-8")
    return d, l


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Technical Stack SVGs.")
    parser.add_argument(
        "--output-dir", type=Path, default=Path("assets"), help="Output directory"
    )
    args = parser.parse_args()
    d, l = write_tech_stack_svgs(args.output_dir)
    print(f"Generated: {d} ({d.stat().st_size} bytes)")
    print(f"Generated: {l} ({l.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
