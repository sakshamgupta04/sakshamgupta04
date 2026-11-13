"""Fetch external feeds for optional blocks: Blog RSS/Atom and WakaTime stats."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from scripts.sanitize import is_safe_url, sanitize_text

DEFAULT_TIMEOUT = 10


def is_same_or_subdomain(target_url: str, base_url: str) -> bool:
    """Check if target_url domain matches or is a subdomain of base_url domain."""
    base_host = urlparse(base_url).netloc.lower().split(":")[0]
    target_host = urlparse(target_url).netloc.lower().split(":")[0]
    if not base_host or not target_host:
        return False
    return target_host == base_host or target_host.endswith("." + base_host)


def find_child_tag(element: ET.Element, tag_name: str) -> ET.Element | None:
    """Find direct child element matching tag_name, ignoring XML namespaces."""
    target = tag_name.lower()
    for child in element:
        tag = child.tag.split("}")[-1].lower() if "}" in child.tag else child.tag.lower()
        if tag == target:
            return child
    return None


def parse_feed_xml(xml_content: str | bytes, base_url: str, max_items: int = 3) -> list[dict[str, str]]:
    """Parse RSS 2.0 or Atom XML content safely."""
    posts: list[dict[str, str]] = []
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return []

    entries: list[ET.Element] = []
    for elem in root.iter():
        tag = elem.tag.split("}")[-1].lower() if "}" in elem.tag else elem.tag.lower()
        if tag in ("item", "entry"):
            entries.append(elem)

    for item in entries:
        title_elem = find_child_tag(item, "title")
        link_elem = find_child_tag(item, "link")
        date_elem = None
        for tag_candidate in ("pubdate", "updated", "published", "date"):
            cand = find_child_tag(item, tag_candidate)
            if cand is not None:
                date_elem = cand
                break

        title = sanitize_text(title_elem.text or "") if title_elem is not None else ""
        link = ""
        if link_elem is not None:
            link = link_elem.attrib.get("href", "").strip() or (link_elem.text or "").strip()
        date_str = (date_elem.text or "").strip() if date_elem is not None else ""

        if not title or not link or not is_safe_url(link):
            continue
        if not is_same_or_subdomain(link, base_url):
            continue

        if "T" in date_str:
            date_val = date_str.split("T")[0]
        else:
            date_val = date_str[:16] if date_str else "Recent"
        posts.append({"title": title, "url": link, "date": date_val})
        if len(posts) >= max_items:
            break

    return posts


def fetch_blog_posts(
    blog_url: str | None,
    timeout: int = DEFAULT_TIMEOUT,
    max_items: int = 3,
) -> list[dict[str, str]]:
    """Fetch and parse latest blog posts from RSS/Atom feed."""
    if not blog_url or not is_safe_url(blog_url):
        return []

    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ProfileReadmeBot/1.0)"}
        resp = requests.get(blog_url, timeout=timeout, headers=headers)
        if resp.status_code != 200:
            return []
        return parse_feed_xml(resp.content, base_url=blog_url, max_items=max_items)
    except (requests.RequestException, OSError):
        return []


def parse_wakatime_json(data: Any, max_items: int = 6) -> list[dict[str, Any]]:
    """Extract language share from WakaTime share JSON data."""
    if not isinstance(data, dict):
        return []
    items = data.get("data", [])
    if not isinstance(items, list):
        return []

    results: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = sanitize_text(str(item.get("name", "")))
        if not name:
            continue
        try:
            percent = round(float(item.get("percent", 0.0)), 1)
        except (ValueError, TypeError):
            percent = 0.0
        time_text = sanitize_text(str(item.get("text", "")))
        results.append({"name": name, "percent": percent, "text": time_text})
        if len(results) >= max_items:
            break

    return results


def fetch_wakatime_stats(
    wakatime_url: str | None,
    timeout: int = DEFAULT_TIMEOUT,
    max_items: int = 6,
) -> list[dict[str, Any]]:
    """Fetch WakaTime weekly language breakdown from public share JSON URL."""
    if not wakatime_url or not is_safe_url(wakatime_url):
        return []

    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ProfileReadmeBot/1.0)"}
        resp = requests.get(wakatime_url, timeout=timeout, headers=headers)
        if resp.status_code != 200:
            return []
        return parse_wakatime_json(resp.json(), max_items=max_items)
    except (requests.RequestException, ValueError, OSError):
        return []


def enrich_external_feeds(
    profile: Any,
    dynamic_data: dict[str, Any],
    offline: bool,
    cache_path: Path,
) -> None:
    """Fetch or load cached external feed data (Blog RSS, WakaTime)."""
    cached: dict[str, Any] = {}
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cached = {}

    # Blog RSS
    if getattr(profile.features, "blog_rss", False):
        blog_url = getattr(profile.links, "blog", None)
        if offline or not blog_url:
            dynamic_data["blog_posts"] = cached.get("blog_posts", [])
        else:
            posts = fetch_blog_posts(blog_url)
            dynamic_data["blog_posts"] = posts if posts else cached.get("blog_posts", [])

    # WakaTime
    if getattr(profile.features, "wakatime", False):
        wakatime_url = getattr(profile.links, "wakatime", None) or getattr(profile, "wakatime", None)
        if offline or not wakatime_url:
            dynamic_data["wakatime"] = cached.get("wakatime", [])
        else:
            stats = fetch_wakatime_stats(wakatime_url)
            dynamic_data["wakatime"] = stats if stats else cached.get("wakatime", [])

    # Stats card fallback from cache if not present
    if getattr(profile.features, "stats_card", False) and not dynamic_data.get("github_stats"):
        dynamic_data["github_stats"] = cached.get("github_stats")

    # If online, persist updated keys to cache
    if not offline and cache_path.exists():
        try:
            disk_cache = json.loads(cache_path.read_text(encoding="utf-8"))
            updated = False
            for key in ("blog_posts", "wakatime", "github_stats"):
                val = dynamic_data.get(key)
                if val:
                    disk_cache[key] = val
                    updated = True
            if updated:
                cache_path.write_text(json.dumps(disk_cache, indent=2), encoding="utf-8")
        except (OSError, json.JSONDecodeError):
            pass
