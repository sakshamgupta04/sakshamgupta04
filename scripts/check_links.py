"""Link checker to extract and verify URLs in profile data and rendered README."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import requests
import yaml

from scripts.sanitize import is_safe_url

DEFAULT_TIMEOUT = 5
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ProfileReadmeLinkChecker/1.0"


def extract_urls_from_dict(data: Any) -> set[str]:
    """Recursively collect URLs from nested dictionaries and lists."""
    urls: set[str] = set()
    if isinstance(data, dict):
        for v in data.values():
            urls.update(extract_urls_from_dict(v))
    elif isinstance(data, list):
        for item in data:
            urls.update(extract_urls_from_dict(item))
    elif isinstance(data, str):
        val = data.strip()
        if val.startswith(("http://", "https://")) and is_safe_url(val):
            urls.add(val)
    return urls


def extract_urls_from_markdown(text: str) -> set[str]:
    """Extract http/https URLs from Markdown links and HTML attributes."""
    urls: set[str] = set()

    # Markdown links: [text](http...)
    md_pattern = re.compile(r"\[.*?\]\((https?://[^\s\)]+)\)")
    for match in md_pattern.finditer(text):
        url = match.group(1).strip()
        if is_safe_url(url):
            urls.add(url)

    # HTML tags: <a href="http..."> or <img src="http...">
    html_pattern = re.compile(r"""(?:href|src|srcset)=["'](https?://[^"'\s,]+)""")
    for match in html_pattern.finditer(text):
        url = match.group(1).strip()
        if is_safe_url(url):
            urls.add(url)

    return urls


def check_url(url: str, timeout: int = DEFAULT_TIMEOUT) -> tuple[bool, str]:
    """Perform HEAD request (fallback to GET) on URL, returning success and message."""
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True, headers=headers)
        if resp.status_code in (403, 405, 500, 503):
            # Fallback to GET for sites blocking HEAD requests
            resp = requests.get(url, timeout=timeout, stream=True, allow_redirects=True, headers=headers)

        if resp.status_code < 400:
            return True, f"{resp.status_code} OK"
        return False, f"HTTP {resp.status_code}"
    except requests.Timeout:
        return False, f"Timed out after {timeout}s"
    except requests.RequestException as exc:
        return False, f"Request failed ({type(exc).__name__})"


def run_link_check(
    data_path: Path,
    readme_path: Path,
    offline: bool = False,
    timeout: int = DEFAULT_TIMEOUT,
) -> int:
    """Collect all URLs from data and README and check reachability."""
    urls: set[str] = set()

    if data_path.exists():
        try:
            with data_path.open("r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f) or {}
            urls.update(extract_urls_from_dict(raw_data))
        except (OSError, yaml.YAMLError) as exc:
            print(f"[LINK WARN] Failed to read data file {data_path}: {exc}", file=sys.stderr)

    if readme_path.exists():
        try:
            content = readme_path.read_text(encoding="utf-8")
            urls.update(extract_urls_from_markdown(content))
        except OSError as exc:
            print(f"[LINK WARN] Failed to read README {readme_path}: {exc}", file=sys.stderr)

    sorted_urls = sorted(urls)
    print("\n" + "=" * 60)
    print(f"LINK CHECKER REPORT ({len(sorted_urls)} unique URLs found)")
    print("=" * 60)

    if offline:
        print("[OFFLINE] Offline mode enabled; skipping HTTP reachability checks.")
        for u in sorted_urls:
            domain = urlparse(u).netloc
            print(f"  [FOUND] {domain} -> {u}")
        print("=" * 60 + "\n")
        return 0

    warnings_count = 0
    for u in sorted_urls:
        ok, msg = check_url(u, timeout=timeout)
        if ok:
            print(f"  [OK]       {msg:<15} {u}")
        else:
            print(f"  [WARNING]  {msg:<15} {u}")
            warnings_count += 1

    print("-" * 60)
    print(f"Total checked: {len(sorted_urls)} | Warnings: {warnings_count}")
    print("Link check completed (warnings do not fail build).")
    print("=" * 60 + "\n")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Check URLs in profile data and README.")
    parser.add_argument("--data", type=Path, default=Path("data/profile.yml"), help="Path to data/profile.yml")
    parser.add_argument("--readme", type=Path, default=Path("README.md"), help="Path to README.md")
    parser.add_argument("--offline", action="store_true", help="Skip network reachability requests")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Request timeout in seconds")

    args = parser.parse_args()
    code = run_link_check(
        data_path=args.data,
        readme_path=args.readme,
        offline=args.offline,
        timeout=args.timeout,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()

