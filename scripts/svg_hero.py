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
    name = escape_xml(profile.identity.name or "Saksham Gupta")
    headline = escape_xml(profile.identity.headline or "Software Developer · AI/ML Engineer")
    location = escape_xml(profile.identity.location or "Jammu, India")
    cgpa = "8.5 / 10"

    if theme == "light":
        bg_main = "#F8FAFC"
        bg_card = "#FFFFFF"
        bg_pill = "#F1F5F9"
        border_col = "#CBD5E1"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        accent_blue = "#0284C7"
        accent_violet = "#7C3AED"
        accent_teal = "#0D9488"
        laptop_screen_bg = "#0F172A"
        laptop_body = "#CBD5E1"
    else:  # dark (default)
        bg_main = "#080F1F"
        bg_card = "#111C31"
        bg_pill = "#17243C"
        border_col = "#293B59"
        text_primary = "#F4F7FF"
        text_secondary = "#A5B4CF"
        accent_blue = "#38BDF8"
        accent_violet = "#8B5CF6"
        accent_teal = "#2DD4BF"
        laptop_screen_bg = "#0B132B"
        laptop_body = "#1E293B"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 320" width="880" height="320">
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
    <linearGradient id="btnGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent_violet}" />
      <stop offset="100%" stop-color="{accent_blue}" />
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
      @media (prefers-reduced-motion: reduce) {{
        .animated-wave {{ animation: none !important; }}
      }}
    </style>
  </defs>

  <!-- Outer Card Frame -->
  <rect x="2" y="2" width="876" height="316" rx="16" fill="url(#cardBg)" stroke="{border_col}" stroke-width="1.5" />

  <!-- Flowing Abstract Ribbon Wave Background -->
  <g opacity="0.65" filter="url(#softGlow)">
    <path d="M 320 180 Q 440 60, 560 140 T 780 100" fill="none" stroke="url(#waveGrad)" stroke-width="6" stroke-linecap="round" />
    <path d="M 340 195 Q 460 75, 580 155 T 800 115" fill="none" stroke="url(#waveGrad)" stroke-width="3" opacity="0.7" />
    <path d="M 310 165 Q 430 45, 550 125 T 770 85" fill="none" stroke="url(#waveGrad)" stroke-width="2" opacity="0.5" />
    <!-- Secondary soft wave -->
    <path d="M 280 220 Q 420 130, 540 200 T 750 160" fill="none" stroke="{accent_teal}" stroke-width="2.5" opacity="0.4" />
  </g>

  <!-- LEFT CONTENT -->
  <!-- Hi, I'm -->
  <text x="36" y="52" class="txt-sans" fill="{text_secondary}" font-size="14" font-weight="500">Hi, I&apos;m</text>

  <!-- Name -->
  <text x="36" y="90" class="txt-sans" fill="{text_primary}" font-size="34" font-weight="800" letter-spacing="-0.5">{name}</text>

  <!-- Headline -->
  <text x="36" y="118" class="txt-sans" fill="{accent_blue}" font-size="15" font-weight="600">{headline}</text>

  <!-- Subtitle Paragraph -->
  <text x="36" y="145" class="txt-sans" fill="{text_secondary}" font-size="12" font-weight="400">
    <tspan x="36" dy="0">Building intelligent, scalable, and user-centric applications</tspan>
    <tspan x="36" dy="18">that bridge AI, full-stack development, and cloud infrastructure.</tspan>
  </text>

  <!-- Status & Role Pills -->
  <!-- Open to Roles Pill -->
  <g transform="translate(36, 185)">
    <rect x="0" y="0" width="168" height="26" rx="13" fill="{bg_pill}" stroke="{accent_teal}" stroke-opacity="0.6" stroke-width="1" />
    <circle cx="14" cy="13" r="4" fill="{accent_teal}" />
    <text x="24" y="17" class="txt-sans" fill="{text_primary}" font-size="11" font-weight="600">Open to Full-Time Roles</text>
  </g>

  <!-- Role tags -->
  <g transform="translate(212, 185)">
    <rect x="0" y="0" width="108" height="26" rx="13" fill="{bg_pill}" stroke="{border_col}" stroke-width="1" />
    <text x="12" y="17" class="txt-sans" fill="{text_secondary}" font-size="10.5" font-weight="500">Software Engineer</text>
  </g>
  <g transform="translate(328, 185)">
    <rect x="0" y="0" width="98" height="26" rx="13" fill="{bg_pill}" stroke="{border_col}" stroke-width="1" />
    <text x="12" y="17" class="txt-sans" fill="{text_secondary}" font-size="10.5" font-weight="500">AI/ML Developer</text>
  </g>

  <!-- Action Buttons Row -->
  <!-- Explore My Work -->
  <g transform="translate(36, 230)">
    <rect x="0" y="0" width="144" height="34" rx="8" fill="url(#btnGrad)" />
    <text x="24" y="22" class="txt-sans" fill="#FFFFFF" font-size="12.5" font-weight="700">🚀 Explore My Work ↗</text>
  </g>
  <!-- Get in Touch -->
  <g transform="translate(190, 230)">
    <rect x="0" y="0" width="118" height="34" rx="8" fill="{bg_pill}" stroke="{border_col}" stroke-width="1.2" />
    <text x="20" y="22" class="txt-sans" fill="{text_primary}" font-size="12.5" font-weight="600">✉️ Get in Touch</text>
  </g>

  <!-- CENTER 3D LAPTOP ILLUSTRATION -->
  <g transform="translate(490, 65)">
    <!-- Ambient Screen Glow -->
    <ellipse cx="90" cy="85" rx="75" ry="55" fill="{accent_blue}" opacity="0.18" filter="url(#softGlow)" />
    <ellipse cx="90" cy="85" rx="50" ry="35" fill="{accent_violet}" opacity="0.22" filter="url(#softGlow)" />

    <!-- Screen Bezel (Perspective) -->
    <path d="M 30 18 L 150 10 L 146 115 L 26 125 Z" fill="{laptop_body}" stroke="{border_col}" stroke-width="1" />
    <!-- Screen Display -->
    <path d="M 34 22 L 146 14 L 142 110 L 30 119 Z" fill="{laptop_screen_bg}" />
    <!-- Code Glyph on Screen: < / > -->
    <text x="86" y="74" class="txt-mono" fill="{accent_blue}" font-size="28" font-weight="700" text-anchor="middle" filter="url(#softGlow)">&lt; / &gt;</text>

    <!-- Laptop Base / Keyboard Deck -->
    <path d="M 12 124 L 158 114 L 180 152 L 2 164 Z" fill="url(#laptopGrad)" stroke="{border_col}" stroke-width="1" />
    <!-- Trackpad -->
    <path d="M 72 138 L 114 135 L 118 152 L 74 155 Z" fill="{bg_pill}" stroke="{border_col}" stroke-width="0.8" opacity="0.8" />
    <!-- Front Edge Accent -->
    <path d="M 2 164 L 180 152 L 182 156 L 0 168 Z" fill="{accent_blue}" opacity="0.6" />
  </g>

  <!-- RIGHT COLUMN: STAT BADGES -->
  <!-- Badge 1: Degree -->
  <g transform="translate(680, 42)">
    <rect x="0" y="0" width="176" height="52" rx="10" fill="{bg_pill}" stroke="{border_col}" stroke-width="1" />
    <circle cx="24" cy="26" r="13" fill="{bg_card}" stroke="{border_col}" stroke-width="0.8" />
    <text x="24" y="30" class="txt-sans" font-size="12" text-anchor="middle">🎓</text>
    <text x="46" y="22" class="txt-sans" fill="{text_primary}" font-size="11.5" font-weight="700">B.Tech CSE (AI/ML)</text>
    <text x="46" y="38" class="txt-sans" fill="{text_secondary}" font-size="10" font-weight="500">MIET Jammu</text>
  </g>

  <!-- Badge 2: Academic Period -->
  <g transform="translate(680, 104)">
    <rect x="0" y="0" width="176" height="52" rx="10" fill="{bg_pill}" stroke="{border_col}" stroke-width="1" />
    <circle cx="24" cy="26" r="13" fill="{bg_card}" stroke="{border_col}" stroke-width="0.8" />
    <text x="24" y="30" class="txt-sans" font-size="12" text-anchor="middle">📅</text>
    <text x="46" y="22" class="txt-sans" fill="{text_primary}" font-size="11.5" font-weight="700">2022 — 2026</text>
    <text x="46" y="38" class="txt-sans" fill="{text_secondary}" font-size="10" font-weight="500">Academic Period</text>
  </g>

  <!-- Badge 3: CGPA -->
  <g transform="translate(680, 166)">
    <rect x="0" y="0" width="176" height="52" rx="10" fill="{bg_pill}" stroke="{border_col}" stroke-width="1" />
    <circle cx="24" cy="26" r="13" fill="{bg_card}" stroke="{border_col}" stroke-width="0.8" />
    <text x="24" y="30" class="txt-sans" font-size="12" text-anchor="middle">⭐</text>
    <text x="46" y="22" class="txt-sans" fill="{text_primary}" font-size="11.5" font-weight="700">{cgpa}</text>
    <text x="46" y="38" class="txt-sans" fill="{text_secondary}" font-size="10" font-weight="500">CGPA Standing</text>
  </g>

  <!-- Badge 4: Location -->
  <g transform="translate(680, 228)">
    <rect x="0" y="0" width="176" height="52" rx="10" fill="{bg_pill}" stroke="{border_col}" stroke-width="1" />
    <circle cx="24" cy="26" r="13" fill="{bg_card}" stroke="{border_col}" stroke-width="0.8" />
    <text x="24" y="30" class="txt-sans" font-size="12" text-anchor="middle">📍</text>
    <text x="46" y="22" class="txt-sans" fill="{text_primary}" font-size="11.5" font-weight="700">{location}</text>
    <text x="46" y="38" class="txt-sans" fill="{text_secondary}" font-size="10" font-weight="500">Location</text>
  </g>
</svg>"""


def write_hero_svgs(profile: Profile, output_dir: Path) -> tuple[Path, Path]:
    """Generate and write hero-dark.svg and hero-light.svg."""
    output_dir.mkdir(parents=True, exist_ok=True)
    dark_path = output_dir / "hero-dark.svg"
    light_path = output_dir / "hero-light.svg"

    dark_svg = generate_modern_hero_svg(profile, theme="dark")
    light_svg = generate_modern_hero_svg(profile, theme="light")

    dark_path.write_text(dark_svg, encoding="utf-8")
    light_path.write_text(light_svg, encoding="utf-8")

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
