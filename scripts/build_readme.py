"""Build script to validate profile data, fetch dynamic data, and render README.md."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path when invoked directly as a script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import yaml
from jinja2 import Environment, FileSystemLoader

from scripts.external_feeds import enrich_external_feeds
from scripts.github_api import fetch_github_data
from scripts.helpers import (
    find_todo_values,
    format_cert_kind,
    format_project_status,
    format_roadmap_status,
    has,
    validate_mermaid_diagram,
    write_step_summary,
)
from scripts.mermaid_generator import generate_mermaid_skill_map
from scripts.schema import Profile, ProfileValidationError, validate_profile_dict
from scripts.svg_hero import write_hero_svgs
from scripts.svg_tech_stack import write_tech_stack_svgs

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


def render_readme(
    profile: Profile,
    template_dir: Path,
    template_name: str,
    dynamic_data: dict[str, Any] | None = None,
) -> str:
    """Render README template with validated profile and dynamic API data."""
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )
    env.globals.update(has=has, validate_diagram=validate_mermaid_diagram)
    env.filters.update(
        has=has,
        format_status=format_roadmap_status,
        format_project_status=format_project_status,
        format_cert_kind=format_cert_kind,
        validate_diagram=validate_mermaid_diagram,
    )

    data = dynamic_data or {}
    languages = data.get("languages", {})
    recent_activity = data.get("recent_activity", [])
    project_last_updated = data.get("project_last_updated", {})

    template = env.get_template(template_name)
    mermaid_map = generate_mermaid_skill_map(profile)

    return template.render(
        profile=profile,
        has=has,
        mermaid_skill_map=mermaid_map,
        languages=languages,
        recent_activity=recent_activity,
        project_last_updated=project_last_updated,
        github_stats=data.get("github_stats"),
        blog_posts=data.get("blog_posts", []),
        wakatime_stats=data.get("wakatime", []),
    )


def inspect_hidden_elements(profile: Profile, dynamic_data: dict[str, Any] | None = None) -> list[str]:
    """Identify sections or major elements that are hidden because they are empty."""
    hidden: list[str] = []

    for field, name in [
        (profile.identity.location, "identity.location (null)"),
        (profile.identity.languages_spoken, "identity.languages_spoken (empty)"),
        (profile.identity.availability.work_mode, "identity.availability.work_mode (null)"),
    ]:
        if not has(field):
            hidden.append(name)

    for link_name, link_val in profile.links.model_dump().items():
        if not has(link_val):
            hidden.append(f"links.{link_name} (empty/null)")

    for block, name in [
        (profile.now, "now (section empty/null)"),
        (profile.publications, "publications (section empty)"),
        (profile.patent, "patent (mention=false/null)"),
        (profile.open_source, "open_source (section empty)"),
        (profile.leetcode, "leetcode (section empty/null)"),
    ]:
        if not has(block):
            hidden.append(name)

    data = dynamic_data or {}
    if not has(data.get("languages")):
        hidden.append("languages_chart (no language data)")
    if not has(data.get("recent_activity")):
        hidden.append("recent_activity (no activity data)")
    if profile.features.leetcode_block and not (has(profile.leetcode.solved) or has(profile.leetcode.rating)):
        hidden.append("leetcode_block (enabled but no solved/rating)")
    if profile.features.blog_rss and not has(data.get("blog_posts")):
        hidden.append("blog_rss (enabled but no blog posts)")
    if profile.features.wakatime and not has(data.get("wakatime")):
        hidden.append("wakatime (enabled but no wakatime stats)")
    if profile.features.stats_card and not has(data.get("github_stats")):
        hidden.append("stats_card (enabled but no github stats)")

    return hidden


def build(
    data_path: Path,
    output_path: Path,
    template_dir: Path,
    template_name: str = "README.md.j2",
    offline: bool = False,
    check: bool = False,
    cache_path: Path = Path("generated/last_good.json"),
) -> int:
    """Orchestrate profile loading, dynamic fetching, validation, and rendering."""
    raw_data, profile = load_profile_data(data_path)

    # Generate only SVG assets referenced by the active README
    assets_dir = output_path.parent / "assets"
    write_hero_svgs(profile, assets_dir)
    write_tech_stack_svgs(assets_dir)

    # Fetch dynamic GitHub data (or use offline cache)
    project_repos = [p.repo for p in profile.projects if p.repo]
    dynamic_data, cache_note = fetch_github_data(
        handle=profile.identity.handle,
        project_repos=project_repos,
        offline=offline,
        cache_path=cache_path,
    )
    enrich_external_feeds(profile, dynamic_data, offline=offline, cache_path=cache_path)

    rendered = render_readme(
        profile=profile,
        template_dir=template_dir,
        template_name=template_name,
        dynamic_data=dynamic_data,
    )
    size_bytes = len(rendered.encode("utf-8"))

    if size_bytes > MAX_README_BYTES:
        print(f"\n[BUILD ERROR] README size ({size_bytes} bytes) exceeds limit.", file=sys.stderr)
        return 1

    output_path.write_text(rendered, encoding="utf-8")

    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        write_step_summary(Path(summary_file), profile, dynamic_data, cache_note, size_bytes, offline)

    if check:
        hidden = inspect_hidden_elements(profile, dynamic_data)
        todo_values = find_todo_values(raw_data)
        note = cache_note if cache_note else "Live GitHub API synchronization active"

        print(f"\n{'=' * 60}\nPROFILE README GENERATION REPORT\n{'=' * 60}")
        print("Status:             VALIDATION & RENDER PASSED")
        print(f"Offline Mode:       {'ENABLED' if offline else 'DISABLED'}")
        print(f"Dynamic Data Note:  {note}")
        print(f"Output File:        {output_path.resolve()}")
        print(f"README Size:        {size_bytes:,} bytes / {MAX_README_BYTES:,} bytes limit\n{'-' * 60}")
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
