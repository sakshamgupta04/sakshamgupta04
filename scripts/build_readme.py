"""Build script to validate profile data and render README.md."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path when invoked directly as a script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import yaml
from jinja2 import Environment, FileSystemLoader

from scripts.helpers import find_todo_values, format_roadmap_status, has
from scripts.schema import Profile, ProfileValidationError, validate_profile_dict
from scripts.svg_terminal import write_terminal_svgs

MAX_README_BYTES = 100 * 1024  # 100 KB limit per project rules


def load_profile_data(path: Path) -> tuple[dict[str, Any], Profile]:
    """Load profile YAML and validate against schema."""
    if not path.exists():
        raise FileNotFoundError(f"Profile data file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw_data = yaml.safe_load(f) or {}

    try:
        profile = validate_profile_dict(raw_data)
        return raw_data, profile
    except ProfileValidationError as err:
        print("\n[VALIDATION FAILED] Errors found in profile.yml:", file=sys.stderr)
        for msg in err.errors:
            print(f"  - {msg}", file=sys.stderr)
        sys.exit(1)


def render_readme(profile: Profile, template_dir: Path, template_name: str) -> str:
    """Render README template with validated profile."""
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )
    env.globals["has"] = has
    env.filters["has"] = has
    env.filters["format_status"] = format_roadmap_status

    template = env.get_template(template_name)
    return template.render(profile=profile, has=has)


def inspect_hidden_elements(profile: Profile) -> list[str]:
    """Identify sections or major elements that are hidden because they are empty."""
    hidden: list[str] = []

    if not has(profile.identity.location):
        hidden.append("identity.location (null)")
    if not has(profile.identity.languages_spoken):
        hidden.append("identity.languages_spoken (empty)")
    if not has(profile.identity.availability.work_mode):
        hidden.append("identity.availability.work_mode (null)")

    link_dump = profile.links.model_dump()
    for link_name, link_val in link_dump.items():
        if not has(link_val):
            hidden.append(f"links.{link_name} (empty/null)")

    if not has(profile.now):
        hidden.append("now (section empty/null)")
    if not has(profile.publications):
        hidden.append("publications (section empty)")
    if not has(profile.patent):
        hidden.append("patent (mention=false/null)")
    if not has(profile.open_source):
        hidden.append("open_source (section empty)")
    if not has(profile.leetcode):
        hidden.append("leetcode (section empty/null)")

    return hidden


def build(
    data_path: Path,
    output_path: Path,
    template_dir: Path,
    template_name: str = "README.md.j2",
    offline: bool = False,
    check: bool = False,
) -> int:
    """Orchestrate profile loading, validation, rendering, and report generation."""
    raw_data, profile = load_profile_data(data_path)

    # Generate terminal header SVGs
    assets_dir = output_path.parent / "assets"
    write_terminal_svgs(profile, assets_dir)

    rendered = render_readme(profile, template_dir, template_name)
    size_bytes = len(rendered.encode("utf-8"))

    if size_bytes > MAX_README_BYTES:
        print(
            f"\n[BUILD ERROR] Generated README.md size ({size_bytes} bytes) "
            f"exceeds the 100 KB limit ({MAX_README_BYTES} bytes).",
            file=sys.stderr,
        )
        return 1

    output_path.write_text(rendered, encoding="utf-8")

    if check:
        hidden = inspect_hidden_elements(profile)
        todo_values = find_todo_values(raw_data)

        print("\n" + "=" * 60)
        print("PROFILE README GENERATION REPORT")
        print("=" * 60)
        print("Status:             VALIDATION & RENDER PASSED")
        print(f"Offline Mode:       {'ENABLED (no network calls made)' if offline else 'DISABLED'}")
        print(f"Output File:        {output_path.resolve()}")
        print(f"README Size:        {size_bytes:,} bytes / {MAX_README_BYTES:,} bytes limit")
        print("-" * 60)
        print(f"Hidden Elements / Sections ({len(hidden)}):")
        for item in hidden:
            print(f"  [HIDDEN] {item}")
        print("-" * 60)
        print(f"TODO Findings in Field Values ({len(todo_values)}):")
        if not todo_values:
            print("  None. (All populated values are free of 'TODO' text)")
        else:
            for field, val in todo_values:
                print(f"  [TODO] {field}: {val}")
        print("=" * 60 + "\n")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Build GitHub Profile README.")
    parser.add_argument("--data", type=Path, default=Path("data/profile.yml"), help="Path to profile.yml")
    parser.add_argument("--output", type=Path, default=Path("README.md"), help="Path to write README.md")
    parser.add_argument("--template-dir", type=Path, default=Path("templates"), help="Directory containing templates")
    parser.add_argument("--offline", action="store_true", help="Run without network calls")
    parser.add_argument("--check", action="store_true", help="Validate, render, size-check and print report")

    args = parser.parse_args()
    code = build(
        data_path=args.data,
        output_path=args.output,
        template_dir=args.template_dir,
        offline=args.offline,
        check=args.check,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
