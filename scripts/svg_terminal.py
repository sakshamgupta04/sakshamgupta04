"""Generate animated terminal window SVGs (dark and light themes)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import yaml

from scripts.helpers import has
from scripts.schema import Profile, validate_profile_dict


def escape_xml(text: str) -> str:
    """Escape XML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def extract_terminal_lines(profile: Profile) -> dict[str, str]:
    """Extract and sanitize terminal display lines from profile data."""
    handle = profile.identity.handle or "user"
    name = profile.identity.name or ""
    role = profile.identity.headline or ""
    status = ""
    if has(profile.identity.availability.text):
        status = str(profile.identity.availability.text)
    elif has(profile.identity.tagline):
        status = str(profile.identity.tagline)

    return {
        "handle": handle,
        "name": name,
        "role": role,
        "status": status,
    }


def generate_terminal_svg(profile: Profile, theme: str = "dark") -> str:
    """Generate animated SVG terminal matching the specified theme (dark|light)."""
    data = extract_terminal_lines(profile)
    handle = escape_xml(data["handle"])
    name = escape_xml(data["name"])
    role = escape_xml(data["role"])
    status = escape_xml(data["status"])

    # Color palettes
    if theme == "light":
        bg_color = "#f6f8fa"
        border_color = "#d0d7de"
        titlebar_bg = "#eaeef2"
        title_text = "#57606a"
        prompt_user = "#0969da"
        prompt_sym = "#1a7f37"
        cmd_color = "#24292f"
        label_color = "#0550ae"
        text_color = "#24292f"
        cursor_color = "#0969da"
        shadow_color = "rgba(0, 0, 0, 0.08)"
    else:  # dark (default)
        bg_color = "#0d1117"
        border_color = "#30363d"
        titlebar_bg = "#161b22"
        title_text = "#8b949e"
        prompt_user = "#58a6ff"
        prompt_sym = "#7ee787"
        cmd_color = "#f0f6fc"
        label_color = "#79c0ff"
        text_color = "#c9d1d9"
        cursor_color = "#58a6ff"
        shadow_color = "rgba(0, 0, 0, 0.5)"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 220" width="800" height="220">
  <defs>
    <style>
      .window-bg {{ fill: {bg_color}; stroke: {border_color}; stroke-width: 1; }}
      .titlebar-bg {{ fill: {titlebar_bg}; stroke: {border_color}; stroke-width: 1; }}
      .title-text {{ fill: {title_text}; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12px; font-weight: 500; text-anchor: middle; }}
      .terminal-text {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 13.5px; fill: {text_color}; }}
      .prompt-user {{ fill: {prompt_user}; font-weight: 600; }}
      .prompt-sym {{ fill: {prompt_sym}; font-weight: 600; }}
      .cmd {{ fill: {cmd_color}; font-weight: 600; }}
      .label {{ fill: {label_color}; font-weight: 600; }}
      .val {{ fill: {text_color}; }}
      .cursor {{ fill: {cursor_color}; animation: blink 0.9s step-end infinite; }}

      .line {{ opacity: 0; clip-path: inset(0 100% 0 0); animation-duration: 12s; animation-iteration-count: infinite; animation-timing-function: ease-in-out; }}
      .line-1 {{ animation-name: anim-line-1; }}
      .line-2 {{ animation-name: anim-line-2; }}
      .line-3 {{ animation-name: anim-line-3; }}
      .line-4 {{ animation-name: anim-line-4; }}
      .line-5 {{ animation-name: anim-line-5; }}

      @keyframes anim-line-1 {{
        0% {{ opacity: 0; clip-path: inset(0 100% 0 0); }}
        1% {{ opacity: 1; clip-path: inset(0 100% 0 0); }}
        7%, 93% {{ opacity: 1; clip-path: inset(0 0 0 0); }}
        96%, 100% {{ opacity: 0; clip-path: inset(0 100% 0 0); }}
      }}
      @keyframes anim-line-2 {{
        0%, 8% {{ opacity: 0; clip-path: inset(0 100% 0 0); }}
        9% {{ opacity: 1; clip-path: inset(0 100% 0 0); }}
        15%, 93% {{ opacity: 1; clip-path: inset(0 0 0 0); }}
        96%, 100% {{ opacity: 0; clip-path: inset(0 100% 0 0); }}
      }}
      @keyframes anim-line-3 {{
        0%, 16% {{ opacity: 0; clip-path: inset(0 100% 0 0); }}
        17% {{ opacity: 1; clip-path: inset(0 100% 0 0); }}
        24%, 93% {{ opacity: 1; clip-path: inset(0 0 0 0); }}
        96%, 100% {{ opacity: 0; clip-path: inset(0 100% 0 0); }}
      }}
      @keyframes anim-line-4 {{
        0%, 25% {{ opacity: 0; clip-path: inset(0 100% 0 0); }}
        26% {{ opacity: 1; clip-path: inset(0 100% 0 0); }}
        35%, 93% {{ opacity: 1; clip-path: inset(0 0 0 0); }}
        96%, 100% {{ opacity: 0; clip-path: inset(0 100% 0 0); }}
      }}
      @keyframes anim-line-5 {{
        0%, 36% {{ opacity: 0; clip-path: inset(0 100% 0 0); }}
        37%, 93% {{ opacity: 1; clip-path: inset(0 0 0 0); }}
        96%, 100% {{ opacity: 0; clip-path: inset(0 100% 0 0); }}
      }}
      @keyframes blink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0; }}
      }}

      @media (prefers-reduced-motion: reduce) {{
        .line {{ animation: none !important; opacity: 1 !important; clip-path: none !important; }}
        .cursor {{ animation: none !important; opacity: 1 !important; }}
      }}
    </style>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="{shadow_color}" />
    </filter>
  </defs>

  <!-- Window frame with shadow -->
  <rect x="2" y="2" width="796" height="216" rx="8" class="window-bg" filter="url(#shadow)" />
  <path d="M 2 10 A 8 8 0 0 1 10 2 L 790 2 A 8 8 0 0 1 798 10 L 798 34 L 2 34 Z" class="titlebar-bg" />

  <!-- Window controls -->
  <circle cx="20" cy="18" r="5.5" fill="#ff5f56" />
  <circle cx="38" cy="18" r="5.5" fill="#ffbd2e" />
  <circle cx="56" cy="18" r="5.5" fill="#27c93f" />

  <!-- Title -->
  <text x="400" y="22" class="title-text">{handle}@github:~ (zsh)</text>

  <!-- Terminal content -->
  <g class="terminal-text">
    <g class="line line-1">
      <text x="24" y="66"><tspan class="prompt-user">{handle}@github</tspan><tspan class="val">:</tspan><tspan class="prompt-sym">~$</tspan><tspan class="val"> </tspan><tspan class="cmd">whoami</tspan></text>
    </g>
    <g class="line line-2">
      <text x="24" y="94"><tspan class="label">name:     </tspan><tspan class="val">{name}</tspan></text>
    </g>
    <g class="line line-3">
      <text x="24" y="122"><tspan class="label">role:     </tspan><tspan class="val">{role}</tspan></text>
    </g>
    <g class="line line-4">
      <text x="24" y="150"><tspan class="label">status:   </tspan><tspan class="val">{status}</tspan></text>
    </g>
    <g class="line line-5">
      <text x="24" y="178"><tspan class="prompt-user">{handle}@github</tspan><tspan class="val">:</tspan><tspan class="prompt-sym">~$</tspan><tspan class="val"> </tspan><tspan class="cursor">&#x2588;</tspan></text>
    </g>
  </g>
</svg>"""
    return svg


def write_terminal_svgs(profile: Profile, output_dir: Path) -> tuple[Path, Path]:
    """Generate and write terminal-dark.svg and terminal-light.svg."""
    output_dir.mkdir(parents=True, exist_ok=True)
    dark_path = output_dir / "terminal-dark.svg"
    light_path = output_dir / "terminal-light.svg"

    dark_svg = generate_terminal_svg(profile, theme="dark")
    light_svg = generate_terminal_svg(profile, theme="light")

    dark_path.write_text(dark_svg, encoding="utf-8")
    light_path.write_text(light_svg, encoding="utf-8")

    return dark_path, light_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate animated SVG terminals.")
    parser.add_argument("--data", type=Path, default=Path("data/profile.yml"), help="Path to profile.yml")
    parser.add_argument("--output-dir", type=Path, default=Path("assets"), help="Output directory for SVGs")
    args = parser.parse_args()

    with args.data.open("r", encoding="utf-8") as f:
        raw_data = yaml.safe_load(f) or {}

    profile = validate_profile_dict(raw_data)
    dark_path, light_path = write_terminal_svgs(profile, args.output_dir)
    print(f"Generated: {dark_path} ({dark_path.stat().st_size} bytes)")
    print(f"Generated: {light_path} ({light_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
