# GitHub profile README — maintenance rules

## Purpose
Maintain Saksham Gupta's professional, modern, non-terminal GitHub profile README. Preserve the single-column editorial layout, accessible typography, real project screenshots, and dark/light hero and technology-stack SVGs.

## Architecture
- `data/profile.yml` is the content source of truth.
- `templates/README.md.j2` and `templates/sections/*.md.j2` define the layout.
- `scripts/build_readme.py` renders `README.md` and generates only active SVG assets.
- `assets/projects/` contains the three real featured-project screenshots.
- `.github/workflows/update.yml` refreshes generated content on `main`.
- `generated/last_good.json` is a fallback cache and must be retained.

## Rules
1. Never manually edit generated `README.md`; edit the YAML, templates, or generators.
2. Do not restore terminal headers, legacy tech grids, or unused SVG assets.
3. Keep user-facing links clickable, claims factual, and project images genuine.
4. Keep the current single-column layout readable on desktop and narrow mobile screens.
5. Hide missing data; never publish placeholders or invented metrics.
6. Sanitize untrusted dynamic content and preserve cached fallbacks.
7. Avoid third-party tracking widgets and unnecessary dependencies.
8. Keep README under 100 KB; preserve accessibility and meaningful image alt text.
9. Verify changes using `python scripts/verify.py`, including Ruff, pytest, offline generation, and link checks.
10. Use a feature branch and pull request for changes. Do not push directly to `main`, force-push, or rewrite history. Merge only after review.
11. Keep design-validation screenshots out of the public repository; use pull request attachments or temporary local files instead.
12. Preserve the scheduled GitHub Actions refresh and ensure deleted legacy assets are not regenerated.

## Active generated assets
- `assets/hero-dark.svg`, `assets/hero-light.svg`
- `assets/tech-stack-dark.svg`, `assets/tech-stack-light.svg`
- `assets/tech-stack-mobile-dark.svg`, `assets/tech-stack-mobile-light.svg`

## Review checklist
- The generated README preserves its current sections and live links.
- All six active SVG assets are valid XML.
- The three featured-project PNGs remain unchanged.
- Offline generation and test suite pass.
- GitHub Actions can refresh the README without recreating deleted assets.
- The PR contains no changes to `main` until explicitly approved.
