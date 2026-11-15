"""Generate modern dark/light portfolio hero banner SVGs matching approved mockup."""

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


def generate_modern_hero_svg(profile: Profile, theme: str = "dark") -> str:
    """Generate modern portfolio hero SVG matching mockup specifications."""
    headline = escape_xml(profile.identity.headline or "Software Developer · AI/ML Engineer")
    location = escape_xml(profile.identity.location or "Jammu, India")
    cgpa = "8.5 / 10"

    if theme == "light":
        bg_main, bg_card, bg_pill = "#F8FAFC", "#FFFFFF", "#F1F5F9"
        border_col, text_primary, text_secondary = "#CBD5E1", "#0F172A", "#475569"
        accent_blue, accent_violet, accent_teal = "#0284C7", "#7C3AED", "#0D9488"
        laptop_screen_bg, laptop_body = "#0F172A", "#CBD5E1"
    else:  # dark (default)
        bg_main, bg_card, bg_pill = "#080F1F", "#111C31", "#17243C"
        border_col, text_primary, text_secondary = "#293B59", "#F4F7FF", "#A5B4CF"
        accent_blue, accent_violet, accent_teal = "#38BDF8", "#8B5CF6", "#2DD4BF"
        laptop_screen_bg, laptop_body = "#0B132B", "#1E293B"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 340" width="880" height="340">
  <defs>
    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg_card}" />
      <stop offset="100%" stop-color="{bg_main}" />
    </linearGradient>
    <linearGradient id="waveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent_blue}" stop-opacity="0.8" />
      <stop offset="50%" stop-color="{accent_violet}" stop-opacity="0.9" />
      <stop offset="100%" stop-color="{accent_teal}" stop-opacity="0.6" />
    </linearGradient>
    <linearGradient id="nameGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent_violet}" />
      <stop offset="100%" stop-color="{accent_blue}" />
    </linearGradient>
    <linearGradient id="btnGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent_blue}" />
      <stop offset="100%" stop-color="{accent_violet}" />
    </linearGradient>
    <linearGradient id="laptopGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#334155" />
      <stop offset="100%" stop-color="#0F172A" />
    </linearGradient>
    <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
    <style>
      .txt-sans {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
      .txt-mono {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; }}
    </style>
  </defs>

  <!-- Outer Card Frame -->
  <rect x="2" y="2" width="876" height="336" rx="16" fill="url(#cardBg)" stroke="{border_col}" stroke-width="1.5" />

  <!-- Flowing Ribbon Waves -->
  <g opacity="0.55" filter="url(#softGlow)">
    <path d="M 300 200 Q 430 70, 560 150 T 800 110" fill="none" stroke="url(#waveGrad)" stroke-width="6" stroke-linecap="round" />
    <path d="M 320 215 Q 450 85, 580 165 T 820 125" fill="none" stroke="url(#waveGrad)" stroke-width="3" opacity="0.7" />
    <path d="M 270 240 Q 410 140, 540 210 T 760 170" fill="none" stroke="{accent_teal}" stroke-width="2.5" opacity="0.4" />
  </g>

  <!-- LEFT COLUMN CONTENT -->
  <text x="36" y="50" class="txt-sans" fill="{text_secondary}" font-size="14" font-weight="500">Hi, I&apos;m</text>
  <text x="36" y="92" class="txt-sans" font-size="36" font-weight="800" letter-spacing="-0.5">
    <tspan fill="{text_primary}">Saksham </tspan><tspan fill="url(#nameGrad)">Gupta</tspan>
  </text>
  <text x="36" y="120" class="txt-sans" fill="{accent_blue}" font-size="15" font-weight="600">{headline}</text>
  <text x="36" y="146" class="txt-sans" fill="{text_secondary}" font-size="12" font-weight="400">
    <tspan x="36" dy="0">Building intelligent, scalable, and user-centric applications</tspan>
    <tspan x="36" dy="18">that bridge AI, full-stack development, and cloud infrastructure.</tspan>
  </text>

  <!-- Role Status Pills -->
  <g transform="translate(36, 188)">
    <rect x="0" y="0" width="160" height="25" rx="12.5" fill="{bg_pill}" stroke="{accent_teal}" stroke-opacity="0.6" stroke-width="1" />
    <circle cx="14" cy="12.5" r="3.5" fill="{accent_teal}" />
    <text x="24" y="16.5" class="txt-sans" fill="{text_primary}" font-size="10.5" font-weight="600">Open to Full-Time Roles</text>
  </g>
  <g transform="translate(204, 188)">
    <rect x="0" y="0" width="105" height="25" rx="12.5" fill="{bg_pill}" stroke="{border_col}" stroke-width="1" />
    <text x="12" y="16.5" class="txt-sans" fill="{text_secondary}" font-size="10" font-weight="500">Software Engineer</text>
  </g>
  <g transform="translate(317, 188)">
    <rect x="0" y="0" width="98" height="25" rx="12.5" fill="{bg_pill}" stroke="{border_col}" stroke-width="1" />
    <text x="12" y="16.5" class="txt-sans" fill="{text_secondary}" font-size="10" font-weight="500">AI/ML Developer</text>
  </g>
  <g transform="translate(423, 188)">
    <rect x="0" y="0" width="106" height="25" rx="12.5" fill="{bg_pill}" stroke="{border_col}" stroke-width="1" />
    <text x="11" y="16.5" class="txt-sans" fill="{text_secondary}" font-size="10" font-weight="500">Full-Stack Engineer</text>
  </g>

  <!-- 5 Action Buttons Row matching Mockup -->
  <g transform="translate(36, 230)">
    <rect x="0" y="0" width="106" height="32" rx="7" fill="url(#btnGrad)" />
    <text x="14" y="20" class="txt-sans" fill="#FFFFFF" font-size="11.5" font-weight="700">🚀 Portfolio ↗</text>
  </g>
  <g transform="translate(150, 230)">
    <rect x="0" y="0" width="88" height="32" rx="7" fill="{bg_pill}" stroke="{border_col}" stroke-width="1.2" />
    <text x="12" y="20" class="txt-sans" fill="{text_primary}" font-size="11.5" font-weight="600">🐙 GitHub ↗</text>
  </g>
  <g transform="translate(246, 230)">
    <rect x="0" y="0" width="94" height="32" rx="7" fill="{bg_pill}" stroke="{border_col}" stroke-width="1.2" />
    <text x="12" y="20" class="txt-sans" fill="{text_primary}" font-size="11.5" font-weight="600">💼 LinkedIn ↗</text>
  </g>
  <g transform="translate(348, 230)">
    <rect x="0" y="0" width="82" height="32" rx="7" fill="{bg_pill}" stroke="{border_col}" stroke-width="1.2" />
    <text x="12" y="20" class="txt-sans" fill="{text_primary}" font-size="11.5" font-weight="600">✉️ Email ↗</text>
  </g>
  <g transform="translate(438, 230)">
    <rect x="0" y="0" width="92" height="32" rx="7" fill="{bg_pill}" stroke="{border_col}" stroke-width="1.2" />
    <text x="12" y="20" class="txt-sans" fill="{text_primary}" font-size="11.5" font-weight="600">📄 Resume ↓</text>
  </g>

  <!-- CENTER 3D LAPTOP ILLUSTRATION -->
  <g transform="translate(500, 75)">
    <ellipse cx="90" cy="85" rx="75" ry="55" fill="{accent_blue}" opacity="0.22" filter="url(#softGlow)" />
    <ellipse cx="90" cy="85" rx="50" ry="35" fill="{accent_violet}" opacity="0.28" filter="url(#softGlow)" />
    <path d="M 30 18 L 150 10 L 146 115 L 26 125 Z" fill="{laptop_body}" stroke="{border_col}" stroke-width="1" />
    <path d="M 34 22 L 146 14 L 142 110 L 30 119 Z" fill="{laptop_screen_bg}" />
    <text x="86" y="74" class="txt-mono" fill="{accent_blue}" font-size="28" font-weight="700" text-anchor="middle" filter="url(#softGlow)">&lt; / &gt;</text>
    <path d="M 12 124 L 158 114 L 180 152 L 2 164 Z" fill="url(#laptopGrad)" stroke="{border_col}" stroke-width="1" />
    <path d="M 72 138 L 114 135 L 118 152 L 74 155 Z" fill="{bg_pill}" stroke="{border_col}" stroke-width="0.8" opacity="0.8" />
    <path d="M 2 164 L 180 152 L 182 156 L 0 168 Z" fill="{accent_blue}" opacity="0.6" />
  </g>

  <!-- RIGHT COLUMN: STAT BADGES -->
  <g transform="translate(686, 38)">
    <rect x="0" y="0" width="170" height="52" rx="10" fill="{bg_pill}" stroke="{border_col}" stroke-width="1" />
    <circle cx="22" cy="26" r="13" fill="{bg_card}" stroke="{border_col}" stroke-width="0.8" />
    <text x="22" y="30" class="txt-sans" font-size="12" text-anchor="middle">🎓</text>
    <text x="44" y="22" class="txt-sans" fill="{text_primary}" font-size="11" font-weight="700">B.Tech CSE (AI/ML)</text>
    <text x="44" y="38" class="txt-sans" fill="{text_secondary}" font-size="9.5" font-weight="500">MIET, Jammu</text>
  </g>
  <g transform="translate(686, 102)">
    <rect x="0" y="0" width="170" height="52" rx="10" fill="{bg_pill}" stroke="{border_col}" stroke-width="1" />
    <circle cx="22" cy="26" r="13" fill="{bg_card}" stroke="{border_col}" stroke-width="0.8" />
    <text x="22" y="30" class="txt-sans" font-size="12" text-anchor="middle">📅</text>
    <text x="44" y="22" class="txt-sans" fill="{text_primary}" font-size="11" font-weight="700">2022 — 2026</text>
    <text x="44" y="38" class="txt-sans" fill="{text_secondary}" font-size="9.5" font-weight="500">Academic Period</text>
  </g>
  <g transform="translate(686, 166)">
    <rect x="0" y="0" width="170" height="52" rx="10" fill="{bg_pill}" stroke="{border_col}" stroke-width="1" />
    <circle cx="22" cy="26" r="13" fill="{bg_card}" stroke="{border_col}" stroke-width="0.8" />
    <text x="22" y="30" class="txt-sans" font-size="12" text-anchor="middle">⭐</text>
    <text x="44" y="22" class="txt-sans" fill="{text_primary}" font-size="11" font-weight="700">{cgpa}</text>
    <text x="44" y="38" class="txt-sans" fill="{text_secondary}" font-size="9.5" font-weight="500">CGPA</text>
  </g>
  <g transform="translate(686, 230)">
    <rect x="0" y="0" width="170" height="52" rx="10" fill="{bg_pill}" stroke="{border_col}" stroke-width="1" />
    <circle cx="22" cy="26" r="13" fill="{bg_card}" stroke="{border_col}" stroke-width="0.8" />
    <text x="22" y="30" class="txt-sans" font-size="12" text-anchor="middle">📍</text>
    <text x="44" y="22" class="txt-sans" fill="{text_primary}" font-size="11" font-weight="700">{location}</text>
    <text x="44" y="38" class="txt-sans" fill="{text_secondary}" font-size="9.5" font-weight="500">Location</text>
  </g>
</svg>"""


def write_hero_svgs(profile: Profile, output_dir: Path) -> tuple[Path, Path]:
    """Generate and write hero-dark.svg and hero-light.svg."""
    output_dir.mkdir(parents=True, exist_ok=True)
    dark_path = output_dir / "hero-dark.svg"
    light_path = output_dir / "hero-light.svg"
    dark_path.write_text(generate_modern_hero_svg(profile, theme="dark"), encoding="utf-8")
    light_path.write_text(generate_modern_hero_svg(profile, theme="light"), encoding="utf-8")
    return dark_path, light_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate modern portfolio hero SVG banner.")
    parser.add_argument("--data", type=Path, default=Path("data/profile.yml"), help="Path to profile.yml")
    parser.add_argument("--output-dir", type=Path, default=Path("assets"), help="Output directory for SVGs")
    args = parser.parse_args()
    with args.data.open("r", encoding="utf-8") as f:
        raw_data = yaml.safe_load(f) or {}
    profile = validate_profile_dict(raw_data)
    dark_path, light_path = write_hero_svgs(profile, args.output_dir)
    print(f"Generated: {dark_path} ({dark_path.stat().st_size} bytes)")
    print(f"Generated: {light_path} ({light_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
