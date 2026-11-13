"""Generate language breakdown bar SVGs (dark and light themes)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Standard GitHub linguist language colors
LANGUAGE_COLORS: dict[str, str] = {
    "Python": "#3572A5",
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "C++": "#f34b7d",
    "C": "#555555",
    "Java": "#b07219",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Shell": "#89e051",
    "Jupyter Notebook": "#DA5B0B",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "SQL": "#e38c00",
    "Dart": "#00B4AB",
}
DEFAULT_LANG_COLOR = "#8b949e"


def compute_top_languages(
    languages: dict[str, int], max_langs: int = 6
) -> list[tuple[str, int, float, str]]:
    """Return top languages with bytes, percentage, and assigned color."""
    if not languages:
        return []
    total_bytes = sum(languages.values())
    if total_bytes <= 0:
        return []

    sorted_langs = sorted(languages.items(), key=lambda kv: kv[1], reverse=True)[:max_langs]
    results: list[tuple[str, int, float, str]] = []
    for lang, count in sorted_langs:
        pct = (count / total_bytes) * 100.0
        color = LANGUAGE_COLORS.get(lang, DEFAULT_LANG_COLOR)
        results.append((lang, count, round(pct, 1), color))
    return results


def format_languages_alt_text(languages: dict[str, int]) -> str:
    """Format language breakdown as alt text string."""
    top = compute_top_languages(languages, max_langs=6)
    if not top:
        return "Top languages: None recorded"
    parts = [f"{lang} {pct}%" for lang, _, pct, _ in top]
    return "Top Languages: " + ", ".join(parts)


def generate_languages_svg(languages: dict[str, int], theme: str = "dark") -> str:
    """Generate proportional language bar SVG with legend and disclaimer."""
    top_langs = compute_top_languages(languages, max_langs=6)
    if not top_langs:
        return ""

    if theme == "light":
        bg_color, border_color = "#f6f8fa", "#d0d7de"
        text_color, note_color = "#24292f", "#57606a"
        bar_bg = "#eaeef2"
    else:  # dark
        bg_color, border_color = "#0d1117", "#30363d"
        text_color, note_color = "#c9d1d9", "#8b949e"
        bar_bg = "#21262d"

    bar_width = 750
    bar_height = 12
    bar_x, bar_y = 25, 24

    # Build segmented bar rects
    segments: list[str] = []
    current_x = float(bar_x)
    for idx, (lang, _, pct, color) in enumerate(top_langs):
        seg_w = (pct / 100.0) * bar_width
        if idx == len(top_langs) - 1:
            seg_w = max(0.0, (bar_x + bar_width) - current_x)
        segments.append(
            f'<rect x="{current_x:.1f}" y="{bar_y}" width="{seg_w:.1f}" height="{bar_height}" fill="{color}" />'
        )
        current_x += seg_w

    # Build legend (2 rows of 3 items)
    legend_items: list[str] = []
    col_x = [25, 275, 525]
    row_y = [64, 88]

    for idx, (lang, _, pct, color) in enumerate(top_langs):
        c_idx = idx % 3
        r_idx = idx // 3
        cx = col_x[c_idx]
        cy = row_y[r_idx]
        legend_items.append(
            f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{color}" />'
            f'<text x="{cx + 16}" y="{cy}" class="lang-text">{lang} <tspan class="lang-pct">{pct}%</tspan></text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 130" width="800" height="130">
  <defs>
    <style>
      .bg {{ fill: {bg_color}; stroke: {border_color}; stroke-width: 1; }}
      .bar-base {{ fill: {bar_bg}; rx: 6px; }}
      .lang-text {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12.5px; fill: {text_color}; font-weight: 500; }}
      .lang-pct {{ fill: {note_color}; font-weight: 400; }}
      .disclaimer {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 11px; fill: {note_color}; font-style: italic; }}
    </style>
    <clipPath id="bar-clip">
      <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" rx="6" />
    </clipPath>
  </defs>

  <rect x="2" y="2" width="796" height="126" rx="8" class="bg" />

  <!-- Segmented Language Bar -->
  <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" class="bar-base" />
  <g clip-path="url(#bar-clip)">
    {"".join(segments)}
  </g>

  <!-- Legend -->
  {"".join(legend_items)}

  <!-- Disclaimer note -->
  <text x="25" y="116" class="disclaimer">* bytes of code in public repos, not a measure of skill</text>
</svg>"""
    return svg


def write_languages_svgs(languages: dict[str, int], output_dir: Path) -> tuple[Path, Path]:
    """Generate and write languages-dark.svg and languages-light.svg."""
    output_dir.mkdir(parents=True, exist_ok=True)
    dark_path = output_dir / "languages-dark.svg"
    light_path = output_dir / "languages-light.svg"

    dark_svg = generate_languages_svg(languages, theme="dark")
    light_svg = generate_languages_svg(languages, theme="light")

    dark_path.write_text(dark_svg, encoding="utf-8")
    light_path.write_text(light_svg, encoding="utf-8")
    return dark_path, light_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate GitHub languages breakdown SVGs.")
    parser.add_argument("--cache", type=Path, default=Path("generated/last_good.json"), help="Path to last_good.json")
    parser.add_argument("--output-dir", type=Path, default=Path("assets"), help="Output directory for SVGs")
    args = parser.parse_args()

    languages = {}
    if args.cache.exists():
        data = json.loads(args.cache.read_text(encoding="utf-8"))
        languages = data.get("languages", {})

    dark_p, light_p = write_languages_svgs(languages, args.output_dir)
    print(f"Generated: {dark_p} and {light_p}")


if __name__ == "__main__":
    main()
