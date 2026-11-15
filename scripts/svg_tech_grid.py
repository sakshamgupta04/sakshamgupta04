"""Generate clean visual tech grid SVG matching approved modern mockup."""

from __future__ import annotations

import argparse
from pathlib import Path


def generate_tech_grid_svg(theme: str = "dark") -> str:
    """Generate 3x6 technology icon grid matching mockup."""
    if theme == "light":
        bg_card = "#FFFFFF"
        tile_bg = "#F1F5F9"
        border_col = "#CBD5E1"
        text_sub = "#475569"
    else:
        bg_card = "#111C31"
        tile_bg = "#17243C"
        border_col = "#293B59"
        text_sub = "#A5B4CF"

    techs = [
        # Row 1
        ("Python", "🐍", "#38BDF8", 0, 0),
        ("C++", "⚡", "#0284C7", 1, 0),
        ("Java", "☕", "#EA580C", 2, 0),
        ("JavaScript", "JS", "#FBBF24", 3, 0),
        ("TypeScript", "TS", "#38BDF8", 4, 0),
        ("SQL", "🗄️", "#06B6D4", 5, 0),
        # Row 2
        ("React", "⚛️", "#38BDF8", 0, 1),
        ("Next.js", "▲", "#F4F7FF", 1, 1),
        ("Node.js", "🟢", "#22C55E", 2, 1),
        ("FastAPI", "⚡", "#2DD4BF", 3, 1),
        ("Supabase", "⚡", "#34D399", 4, 1),
        ("PostgreSQL", "🐘", "#38BDF8", 5, 1),
        # Row 3
        ("Scikit-learn", "🔬", "#F97316", 0, 2),
        ("TensorFlow", "🧠", "#FB923C", 1, 2),
        ("PyTorch", "🔥", "#EF4444", 2, 2),
        ("OpenCV", "👁️", "#818CF8", 3, 2),
        ("Docker", "🐳", "#38BDF8", 4, 2),
        ("GCP", "☁️", "#38BDF8", 5, 2),
    ]

    tile_w, tile_h = 64, 62
    gap_x, gap_y = 9, 10
    start_x, start_y = 12, 12

    svg_parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 230" width="460" height="230">',
        '  <defs>',
        '    <style>',
        '      .tech-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 9.5px; font-weight: 600; text-anchor: middle; }',
        '      .tech-icon { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; font-weight: 800; text-anchor: middle; }',
        '    </style>',
        '  </defs>',
        f'  <rect x="0" y="0" width="460" height="230" rx="12" fill="{bg_card}" stroke="{border_col}" stroke-width="1" />',
    ]

    for name, icon, color, col, row in techs:
        x = start_x + col * (tile_w + gap_x)
        y = start_y + row * (tile_h + gap_y)
        svg_parts.append(
            f'  <g transform="translate({x}, {y})">'
            f'    <rect x="0" y="0" width="{tile_w}" height="{tile_h}" rx="9" fill="{tile_bg}" stroke="{border_col}" stroke-width="0.8" />'
            f'    <text x="{tile_w/2}" y="28" class="tech-icon" fill="{color}">{icon}</text>'
            f'    <text x="{tile_w/2}" y="48" class="tech-title" fill="{text_sub}">{name}</text>'
            f'  </g>'
        )

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


def write_tech_grid_svgs(output_dir: Path) -> tuple[Path, Path]:
    """Write dark and light tech grid SVGs."""
    output_dir.mkdir(parents=True, exist_ok=True)
    dark_path = output_dir / "tech-grid-dark.svg"
    light_path = output_dir / "tech-grid-light.svg"
    dark_path.write_text(generate_tech_grid_svg("dark"), encoding="utf-8")
    light_path.write_text(generate_tech_grid_svg("light"), encoding="utf-8")
    return dark_path, light_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate tech grid SVGs.")
    parser.add_argument("--output-dir", type=Path, default=Path("assets"), help="Output directory")
    args = parser.parse_args()
    d, l = write_tech_grid_svgs(args.output_dir)
    print(f"Generated: {d} ({d.stat().st_size} bytes)")
    print(f"Generated: {l} ({l.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
