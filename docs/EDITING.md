# Profile Maintenance & Editing Guide

This guide explains how to edit `data/profile.yml`, run builds and checks locally, trigger the GitHub Action refresh workflow, toggle feature flags, and understand third-party action security considerations.

---

## 1. Core Architecture & Rules

1. **`README.md` is strictly generated.** Never edit `README.md` directly by hand. All changes are driven by `data/profile.yml` and templates in `templates/`.
2. **Clean hiding behavior:** If any field in `data/profile.yml` is `null`, empty (`""`), or omitted, its line or enclosing section is completely hidden. It will never render `"None"`, `"null"`, or empty boxes.
3. **No placeholders:** Never commit `"TODO"`, `"TBD"`, or placeholder metrics. Validation will detect and warn on any `"TODO"` substrings.
4. **Resilient fallbacks:** Dynamic data (recent GitHub activity, language breakdown) caches to `generated/last_good.json`. If the GitHub API is unavailable or rate-limited, the build seamlessly falls back to cached data without failing.

---

## 2. Editing `data/profile.yml`

All profile information resides in `data/profile.yml`.

### Key Sections:

- **`identity`**:
  - `name`, `handle`, `headline`, `tagline`
  - `location`: string or `null` (hidden if `null`)
  - `languages_spoken`: list of languages (hidden if empty)
  - `availability`: `status` (`available` | `open` | `busy` | `unavailable`), `text`, `work_mode`
- **`links`**:
  - `portfolio`, `resume_pdf`, `linkedin`, `email`, `leetcode`, `scholar`, `x_twitter`, etc.
  - Only populated links are rendered in quick badges, contact blocks, and table of contents.
- **`now`**:
  - Current activities: `building`, `learning`, `reading`, `exploring`, and `updated` date.
- **`skills`**:
  - Categorized under `groups` (e.g., Languages, Backend & Distributed Systems, Machine Learning).
  - `level`: `daily`, `comfortable`, `learning`, or omitted.
  - Powers both the skills table and the Mermaid architecture dependency flowchart.
- **`projects`**:
  - List of featured and secondary projects.
  - `status`: `shipped`, `building`, or `planned`.
  - `stack`: technology tags used to connect with skills.
  - `highlights` and `measured_results`: bulleted impact metrics.
  - `diagram`: optional Mermaid diagram (`flowchart` or `graph`) showing system architecture.
- **`experience`**:
  - Roles, organizations, date ranges, and achievements inside collapsible `<details>` tags.
- **`education` & `certifications`**:
  - Degrees, scores, certifications, and course credentials with verification links.
- **`features`**:
  - Boolean flags enabling or disabling dynamic modules (`recent_activity`, `languages`, `snake`).

---

## 3. Running & Verifying Locally

### Setup
Ensure Python 3.11+ is installed. Activate your virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Build the README
Generate `README.md` and print a validation inspection report:

```bash
# Offline mode (uses existing cache in generated/last_good.json, no network required):
python scripts/build_readme.py --offline --check

# Online mode (fetches live GitHub stats and activity):
python scripts/build_readme.py --check
```

### Run Full Verification Suite
The project enforces linting, automated unit tests, and build checks before any commit:

```bash
python scripts/verify.py
```
This runs:
1. `ruff check .` (code quality and formatting)
2. `pytest tests` (offline unit test suite)
3. `python scripts/build_readme.py --offline --check` (schema and size validation)

---

## 4. GitHub Actions Workflow Automation

The refresh workflow is located at `.github/workflows/update.yml`.

### Triggers:
1. **Scheduled Daily Cron:** Runs automatically once a day at an odd minute (`03:17 UTC`) to keep activity feeds and project timestamps fresh.
2. **Push to Code/Data:** Runs whenever changes are pushed to `data/**`, `templates/**`, or `scripts/**`.
3. **Manual Trigger (`workflow_dispatch`):** Can be triggered on demand via the GitHub Actions UI.

### How to Run Manually:
1. Go to your repository on GitHub: `https://github.com/sakshamgupta04/sakshamgupta04`.
2. Click the **Actions** tab.
3. In the left sidebar, select **Refresh Profile README**.
4. Click the **Run workflow** dropdown button, select branch `main`, and click **Run workflow**.

### What to Expect:
- **Job Summary:** In the workflow run details, view the **Profile README Refresh Report** table summarizing generated file size, data synchronization source, and updated components.
- **Smart Bot Commits:**
  - If changes occurred (e.g. new commits, changed stars, or language shifts), the bot commits with message: `chore: refresh profile README` under `github-actions[bot]`.
  - If nothing changed, **no commit is created**, preventing noise and clutter in your commit history.

---

## 5. Feature Flags & Optional Blocks

In `data/profile.yml`, feature flags are configured under the `features` dictionary (all optional blocks are disabled by default):

```yaml
features:
  terminal_header: true        # Self-generated animated SVG header
  mermaid_skill_map: true      # Mermaid dependency flowchart
  languages_chart: true        # Top 6 languages by code bytes SVG chart
  recent_activity: true        # Displays 5 most recent public GitHub events
  projects_last_updated: true  # Commit timestamps for featured project repos
  snake: false                 # Contribution snake animation (disabled by default)
  stats_card: false            # Simple text table (public repos, total stars)
  leetcode_block: false        # Solved count and rating from leetcode.* (no network calls)
  blog_rss: false              # Latest 3 post titles from links.blog RSS/Atom feed
  wakatime: false              # Weekly language breakdown from public WakaTime share link
```

### Optional Blocks Details:
1. **`leetcode_block`**:
   - Reads directly from `leetcode.solved`, `leetcode.rating`, and `leetcode.as_of`.
   - Never makes network or scraping calls; strictly static numbers you control.
   - Automatically hidden if both `solved` and `rating` are empty or null.
2. **`blog_rss`**:
   - Requires `links.blog` to be set to a valid RSS 2.0 or Atom feed.
   - Fetches with a 10s timeout, sanitizes titles, and restricts links strictly to the blog's domain or subdomains.
   - Caches to `generated/last_good.json` and gracefully hides on network failure.
3. **`wakatime`**:
   - Requires a public WakaTime share JSON URL in `links.wakatime`.
   - Displays a clean weekly language split table with percentages and time tracked.
   - Zero secrets or API keys required; caches and hides gracefully on failure.
4. **`stats_card`**:
   - Computes public non-fork repository count and total stargazer count across your repositories.
   - Rendered as a simple markdown table without third-party badge services.
5. **`snake` (Contribution Snake Animation)**:

- **Security Risk:** Running third-party actions in GitHub workflows involves executing external containerized code. If a third-party action is compromised, it could attempt to exfiltrate workflow secrets or abuse write permissions.
- **Safety Measures in this Repository:**
  1. **Disabled by default:** `features.snake` is set to `false`.
  2. **Pinned to Immutable Commit SHA:** Instead of mutable tags, `update.yml` pins `Platane/snk` directly to commit SHA `d8f6715049803e982ee5ff501b6b9b7d5deeb09b # v3.5.0`.
  3. **Isolated Output Branch:** If enabled, the generated snake SVGs are deployed to an independent orphan `output` branch. The action never touches or modifies the repository's `main` branch codebase.
  4. **Strict Minimal Permissions:** The workflow only grants `contents: write`, with no access to external environments, identities, or extra secrets.

To turn the contribution snake animation on, simply set `features.snake: true` in `data/profile.yml` and run `python scripts/verify.py`.

