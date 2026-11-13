"""GitHub REST API client for dynamic data: activity, languages, and repo updates."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from scripts.sanitize import is_safe_url, sanitize_text

GITHUB_API_BASE = "https://api.github.com"
DEFAULT_TIMEOUT = 10


def create_github_session(token: str | None = None) -> requests.Session:
    """Create a configured requests Session with retries and authentication."""
    session = requests.Session()
    session.headers.update({
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Profile-README/1.0",
    })
    auth_token = token or os.environ.get("GITHUB_TOKEN")
    if auth_token:
        session.headers["Authorization"] = f"Bearer {auth_token}"

    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504], raise_on_status=False)
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def is_github_url(url: str | None) -> bool:
    """Ensure a URL is safe and points strictly to github.com."""
    if not is_safe_url(url) or not url:
        return False
    parts = urlsplit(url)
    return parts.netloc.lower() in ("github.com", "www.github.com", "api.github.com")


def compute_relative_time(iso_str: str, now: datetime | None = None) -> str:
    """Convert ISO timestamp to human-friendly relative string."""
    try:
        dt = datetime.fromisoformat(iso_str)
        diff = (now or datetime.now(UTC)) - dt
        seconds = max(0, int(diff.total_seconds()))
        if seconds < 60:
            return "just now"
        minutes, hours, days = seconds // 60, seconds // 3600, seconds // 86400
        if minutes < 60:
            return f"{minutes}m ago"
        if hours < 24:
            return f"{hours}h ago"
        if days < 30:
            return f"{days}d ago"
        months = days // 30
        return f"{months}mo ago" if months < 12 else f"{months // 12}y ago"
    except (ValueError, TypeError, AttributeError):
        return iso_str[:10] if iso_str else "recently"


def get_user_public_repos(handle: str, session: requests.Session) -> list[dict[str, Any]]:
    """Fetch non-fork public repositories for a user."""
    url = f"{GITHUB_API_BASE}/users/{handle}/repos?type=public&per_page=100"
    resp = session.get(url, timeout=DEFAULT_TIMEOUT)
    if resp.status_code != 200:
        return []
    repos = resp.json()
    if not isinstance(repos, list):
        return []
    return [r for r in repos if not r.get("fork")]


def get_languages_bytes(
    handle: str, repos: list[dict[str, Any]], session: requests.Session
) -> dict[str, int]:
    """Aggregate language bytes across public repositories."""
    aggregated: dict[str, int] = {}
    for repo in repos:
        lang_url = repo.get("languages_url")
        if not lang_url:
            continue
        try:
            resp = session.get(lang_url, timeout=DEFAULT_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict):
                    for lang, bytes_count in data.items():
                        aggregated[lang] = aggregated.get(lang, 0) + int(bytes_count)
        except (requests.RequestException, ValueError):
            pass
    return aggregated


def get_project_last_pushed(
    repos: list[dict[str, Any]], project_repos: list[str]
) -> dict[str, str]:
    """Map project repo identifiers to their last push date (YYYY-MM-DD)."""
    pushed_map: dict[str, str] = {}
    clean_target_repos = {r.strip().lower() for r in project_repos if r}

    for repo in repos:
        full_name = repo.get("full_name", "").strip().lower()
        name = repo.get("name", "").strip().lower()
        pushed_at = repo.get("pushed_at") or repo.get("updated_at")
        if not pushed_at:
            continue

        date_str = str(pushed_at)[:10]
        if full_name in clean_target_repos:
            pushed_map[repo.get("full_name")] = date_str
        elif name in clean_target_repos:
            pushed_map[repo.get("name")] = date_str

    return pushed_map


def parse_recent_activity(events: list[dict[str, Any]], max_items: int = 5) -> list[dict[str, str]]:
    """Filter and sanitize public events into meaningful timeline activity items."""
    meaningful: list[dict[str, str]] = []
    if not isinstance(events, list):
        return meaningful

    for ev in events:
        ev_type = ev.get("type")
        repo_data = ev.get("repo", {})
        repo_name = repo_data.get("name", "")
        repo_url = f"https://github.com/{repo_name}" if repo_name else ""
        created_at = ev.get("created_at", "")
        rel_time = compute_relative_time(created_at)
        abs_time = created_at.replace("T", " ").replace("Z", " UTC")[:19]

        payload = ev.get("payload", {})
        title = ""
        link = repo_url

        if ev_type == "PushEvent":
            commits = payload.get("commits", [])
            head = payload.get("head", "")[:7]
            full_sha = payload.get("head", "")
            ref = payload.get("ref", "refs/heads/main").replace("refs/heads/", "")
            commit_msg = ""
            commit_sha = head

            if commits:
                first = commits[0]
                commit_sha = first.get("sha", head)[:7]
                full_sha = first.get("sha", full_sha)
                if first.get("message"):
                    commit_msg = first["message"].splitlines()[0]

            if commit_msg:
                clean_msg = sanitize_text(commit_msg, max_length=75)
                title = f"Pushed `{commit_sha}` to `{repo_name}`: {clean_msg}"
            else:
                title = f"Pushed `{commit_sha}` to `{repo_name}` (`{ref}`)"
            link = f"https://github.com/{repo_name}/commit/{full_sha}" if full_sha else repo_url

        elif ev_type == "PullRequestEvent":
            pr = payload.get("pull_request", {})
            action = payload.get("action", "worked on")
            pr_title = sanitize_text(pr.get("title", ""), max_length=75)
            pr_num = payload.get("number") or pr.get("number", "")
            pr_tag = f" #{pr_num}" if pr_num else ""
            title = f"{action.capitalize()} PR{pr_tag} in `{repo_name}`: {pr_title}"
            link = pr.get("html_url") or repo_url

        elif ev_type == "ReleaseEvent":
            rel = payload.get("release", {})
            tag = rel.get("tag_name") or rel.get("name") or "new release"
            clean_tag = sanitize_text(tag, max_length=50)
            title = f"Published release `{clean_tag}` in `{repo_name}`"
            link = rel.get("html_url") or repo_url

        elif ev_type == "CreateEvent" and payload.get("ref_type") == "repository":
            title = f"Created public repository `{repo_name}`"
            link = repo_url

        if title and is_github_url(link):
            meaningful.append({
                "description": title,
                "url": link,
                "relative_time": rel_time,
                "absolute_time": abs_time,
            })
            if len(meaningful) >= max_items:
                break

    return meaningful


def get_user_events(handle: str, session: requests.Session) -> list[dict[str, Any]]:
    """Fetch recent public events for a user."""
    url = f"{GITHUB_API_BASE}/users/{handle}/events/public?per_page=30"
    resp = session.get(url, timeout=DEFAULT_TIMEOUT)
    if resp.status_code != 200:
        return []
    data = resp.json()
    return data if isinstance(data, list) else []


def fetch_github_data(
    handle: str,
    project_repos: list[str],
    offline: bool = False,
    cache_path: Path = Path("generated/last_good.json"),
    token: str | None = None,
) -> tuple[dict[str, Any], str | None]:
    """Fetch GitHub data with caching and graceful offline fallback."""
    if offline:
        if cache_path.exists():
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            return data, f"showing cached data from {data.get('fetched_at', 'previous run')}"
        return {}, "offline mode: no cache found"

    session = create_github_session(token)
    try:
        repos = get_user_public_repos(handle, session)
        langs = get_languages_bytes(handle, repos, session)
        pushed = get_project_last_pushed(repos, project_repos)
        raw_events = get_user_events(handle, session)
        activity = parse_recent_activity(raw_events, max_items=5)

        data = {
            "fetched_at": datetime.now(UTC).isoformat()[:19] + "Z",
            "languages": langs,
            "project_last_updated": pushed,
            "recent_activity": activity,
        }
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data, None
    except (requests.RequestException, ValueError, OSError) as exc:
        if cache_path.exists():
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            return cached, f"showing cached data from {cached.get('fetched_at', 'previous run')} (API error: {exc})"
        return {}, f"fetch failed: {exc}"
