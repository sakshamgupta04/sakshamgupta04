# Profile README generator: project rules
Goal: generate a long, technical GitHub profile README for Saksham Gupta from one data file, and keep its dynamic parts fresh with a scheduled GitHub Action. Style is a MIX of terminal-technical (animated header, whoami block, status tables) and clean engineering docs (tables, Mermaid diagrams, collapsible sections). Audience: recruiters, engineers and researchers equally.

## Stack (do not add libraries without asking)
Python 3.11, PyYAML, Jinja2, requests, pydantic, pytest, ruff. No Node. No third-party image or stats services. One optional third-party GitHub Action (contribution snake), off by default.

## Hard rules
1. README.md is GENERATED. Never edit it by hand. All content comes from data/profile.yml.
2. If a field is null, empty or missing, hide that element or the whole section. Never render "null", "None", "TODO" or an empty box.
3. All untrusted text (commit messages, event titles, repo descriptions) goes through scripts/sanitize.py: strip HTML, escape markdown, remove newlines, truncate.
4. Every dynamic part has a fallback. API failure must NOT fail the build: use generated/last_good.json, or hide the block. Never blank a section that already had content.
5. Images: every image has meaningful alt text and light and dark variants through <picture> with prefers-color-scheme.
6. No trackers, no visitor counters, no third-party stat cards, no fake activity.
7. The workflow commits as github-actions[bot], only when generated files changed, with permissions limited to contents: write.
8. Do not invent facts, levels, metrics or links. Use only what is in data/profile.yml. Measured results only; empty results are hidden.
9. Keep README.md under about 100 KB; fail the build with a clear message if larger.
10. Small typed modules (under about 250 lines), tests with offline fixtures (no network in tests). Do only the phase I ask for.

## GIT STEP (end of every phase)
1. Run "python scripts/verify.py" (ruff, pytest, and "python scripts/build_readme.py --offline --check"). If anything fails, fix it; if you cannot, STOP and tell me; do not push.
2. Only if everything passes: "git add -A", "git commit -m 'feat(phase-N): <summary>'", "git push origin main".
3. Never force-push. Undo with "git revert".
4. List the files changed and how I can see the result.
