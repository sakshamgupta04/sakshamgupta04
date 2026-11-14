"""Generate animated terminal window SVGs (dark and light themes)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import yaml

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
    handle = profile.identity.handle or "sakshamgupta04"
    name = profile.identity.name or "Saksham Gupta"
    role = "Software Developer · AI/ML Engineer"
    mission = "Building intelligent applications, scalable backend systems, and practical AI-powered solutions."
    tagline = "Building software that connects intelligence with real-world use."

    return {
        "handle": handle,
        "name": name,
        "role": role,
        "mission": mission,
        "tagline": tagline,
    }


def generate_terminal_svg(profile: Profile, theme: str = "dark") -> str:
    """Generate animated SVG terminal matching the specified theme (dark|light)."""
    data = extract_terminal_lines(profile)
    handle = escape_xml(data["handle"])
    name = escape_xml(data["name"])
    role = escape_xml(data["role"])
    mission = escape_xml(data["mission"])
    tagline = escape_xml(data["tagline"])

    if theme == "light":
        bg_color = "#f6f8fa"
        border_color = "#d0d7de"
        titlebar_bg = "#eaeef2"
        title_text = "#57606a"
        prompt_user = "#0969da"
        prompt_sym = "#1a7f37"
        cmd_color = "#24292f"
        name_color = "#24292f"
        role_color = "#0969da"
        mission_color = "#24292f"
        tagline_color = "#57606a"
        cursor_color = "#0969da"
        mini_bg = "#ffffff"
        mini_stroke = "#d0d7de"
        accent_code = "#1a7f37"
        shadow_color = "rgba(0, 0, 0, 0.08)"
    else:  # dark (default)
        bg_color = "#0d1117"
        border_color = "#30363d"
        titlebar_bg = "#161b22"
        title_text = "#8b949e"
        prompt_user = "#58a6ff"
        prompt_sym = "#55d6a0"
        cmd_color = "#f0f6fc"
        name_color = "#f0f6fc"
        role_color = "#55d6a0"
        mission_color = "#a7d3ed"
        tagline_color = "#8b949e"
        cursor_color = "#55d6a0"
        mini_bg = "#161b22"
        mini_stroke = "#30363d"
        accent_code = "#55d6a0"
        shadow_color = "rgba(0, 0, 0, 0.5)"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 220" width="800" height="220">
  <defs>
    <style>
      .window-bg {{ fill: {bg_color}; stroke: {border_color}; stroke-width: 1; }}
      .titlebar-bg {{ fill: {titlebar_bg}; stroke: {border_color}; stroke-width: 1; }}
      .title-text {{ fill: {title_text}; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12px; font-weight: 500; text-anchor: middle; }}
      .terminal-text {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 13px; }}
      .prompt-user {{ fill: {prompt_user}; font-weight: 600; }}
      .prompt-sym {{ fill: {prompt_sym}; font-weight: 600; }}
      .cmd {{ fill: {cmd_color}; font-weight: 600; }}
      .name-text {{ fill: {name_color}; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 18px; font-weight: 700; }}
      .role-tag {{ fill: {role_color}; font-family: ui-monospace, SFMono-Regular, monospace; font-size: 12px; font-weight: 600; }}
      .mission-text {{ fill: {mission_color}; font-size: 12px; }}
      .tagline-text {{ fill: {tagline_color}; font-size: 11.5px; font-style: italic; }}
      .cursor {{ fill: {cursor_color}; animation: blink 0.9s step-end infinite; }}

      .line {{ opacity: 0; clip-path: inset(0 100% 0 0); animation-duration: 14s; animation-iteration-count: infinite; animation-timing-function: ease-in-out; }}
      .line-1 {{ animation-name: anim-line-1; }}
      .line-2 {{ animation-name: anim-line-2; }}
      .line-3 {{ animation-name: anim-line-3; }}
      .line-4 {{ animation-name: anim-line-4; }}
      .line-5 {{ animation-name: anim-line-5; }}
      .line-6 {{ animation-name: anim-line-6; }}

      @keyframes anim-line-1 {{ 0% {{ opacity: 0; clip-path: inset(0 100% 0 0); }} 1% {{ opacity: 1; clip-path: inset(0 100% 0 0); }} 6%, 94% {{ opacity: 1; clip-path: inset(0 0 0 0); }} 97%, 100% {{ opacity: 0; clip-path: inset(0 100% 0 0); }} }}
      @keyframes anim-line-2 {{ 0%, 7% {{ opacity: 0; clip-path: inset(0 100% 0 0); }} 8% {{ opacity: 1; clip-path: inset(0 100% 0 0); }} 15%, 94% {{ opacity: 1; clip-path: inset(0 0 0 0); }} 97%, 100% {{ opacity: 0; clip-path: inset(0 100% 0 0); }} }}
      @keyframes anim-line-3 {{ 0%, 16% {{ opacity: 0; clip-path: inset(0 100% 0 0); }} 17% {{ opacity: 1; clip-path: inset(0 100% 0 0); }} 23%, 94% {{ opacity: 1; clip-path: inset(0 0 0 0); }} 97%, 100% {{ opacity: 0; clip-path: inset(0 100% 0 0); }} }}
      @keyframes anim-line-4 {{ 0%, 24% {{ opacity: 0; clip-path: inset(0 100% 0 0); }} 25% {{ opacity: 1; clip-path: inset(0 100% 0 0); }} 33%, 94% {{ opacity: 1; clip-path: inset(0 0 0 0); }} 97%, 100% {{ opacity: 0; clip-path: inset(0 100% 0 0); }} }}
      @keyframes anim-line-5 {{ 0%, 34% {{ opacity: 0; clip-path: inset(0 100% 0 0); }} 35% {{ opacity: 1; clip-path: inset(0 100% 0 0); }} 42%, 94% {{ opacity: 1; clip-path: inset(0 0 0 0); }} 97%, 100% {{ opacity: 0; clip-path: inset(0 100% 0 0); }} }}
      @keyframes anim-line-6 {{ 0%, 43% {{ opacity: 0; clip-path: inset(0 100% 0 0); }} 44%, 94% {{ opacity: 1; clip-path: inset(0 0 0 0); }} 97%, 100% {{ opacity: 0; clip-path: inset(0 100% 0 0); }} }}

      @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}

      @media (prefers-reduced-motion: reduce) {{
        .line {{ animation: none !important; opacity: 1 !important; clip-path: none !important; }}
        .cursor {{ animation: none !important; opacity: 1 !important; }}
      }}
    </style>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="{shadow_color}" />
    </filter>
  </defs>

  <rect x="2" y="2" width="796" height="216" rx="10" class="window-bg" filter="url(#shadow)" />
  <path d="M 2 12 A 10 10 0 0 1 12 2 L 788 2 A 10 10 0 0 1 798 12 L 798 34 L 2 34 Z" class="titlebar-bg" />

  <circle cx="20" cy="18" r="5.5" fill="#ff5f56" />
  <circle cx="38" cy="18" r="5.5" fill="#ffbd2e" />
  <circle cx="56" cy="18" r="5.5" fill="#27c93f" />

  <text x="400" y="22" class="title-text">{handle}@terminal:~ (zsh)</text>

  <!-- Illustration on top right -->
  <g transform="translate(686, 48)" opacity="0.9">
    <rect x="0" y="0" width="88" height="58" rx="5" fill="{mini_bg}" stroke="{mini_stroke}" stroke-width="1.2" />
    <circle cx="10" cy="9" r="2.2" fill="#ff5f56" />
    <circle cx="17" cy="9" r="2.2" fill="#ffbd2e" />
    <circle cx="24" cy="9" r="2.2" fill="#27c93f" />
    <line x1="0" y1="17" x2="88" y2="17" stroke="{mini_stroke}" stroke-width="1" />
    <line x1="10" y1="26" x2="42" y2="26" stroke="{accent_code}" stroke-width="2" stroke-linecap="round" />
    <line x1="47" y1="26" x2="76" y2="26" stroke="{prompt_user}" stroke-width="2" stroke-linecap="round" />
    <line x1="10" y1="36" x2="60" y2="36" stroke="{mission_color}" stroke-width="2" stroke-linecap="round" />
    <line x1="10" y1="46" x2="32" y2="46" stroke="{tagline_color}" stroke-width="2" stroke-linecap="round" />
    <line x1="38" y1="46" x2="68" y2="46" stroke="{accent_code}" stroke-width="2" stroke-linecap="round" />
  </g>

  <g class="terminal-text">
    <g class="line line-1">
      <text x="24" y="58"><tspan class="prompt-user">{handle}@github</tspan><tspan fill="{title_text}">:</tspan><tspan class="prompt-sym">~$</tspan><tspan fill="{cmd_color}"> whoami</tspan></text>
    </g>
    <g class="line line-2">
      <text x="24" y="86"><tspan class="name-text">{name}</tspan><tspan dx="16" class="role-tag">[ {role} ]</tspan></text>
    </g>
    <g class="line line-3">
      <text x="24" y="116"><tspan class="prompt-user">{handle}@github</tspan><tspan fill="{title_text}">:</tspan><tspan class="prompt-sym">~$</tspan><tspan fill="{cmd_color}"> cat mission.txt</tspan></text>
    </g>
    <g class="line line-4">
      <text x="24" y="142" class="mission-text">{mission}</text>
    </g>
    <g class="line line-5">
      <text x="24" y="168" class="tagline-text">&#x21B3; {tagline}</text>
    </g>
    <g class="line line-6">
      <text x="24" y="196"><tspan class="prompt-user">{handle}@github</tspan><tspan fill="{title_text}">:</tspan><tspan class="prompt-sym">~$</tspan><tspan fill="{cmd_color}"> </tspan><tspan class="cursor">&#x2588;</tspan></text>
    </g>
  </g>
</svg>"""


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
