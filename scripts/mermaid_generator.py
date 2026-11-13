"""Generate Mermaid flowchart linking skill groups, technologies, and projects."""

from __future__ import annotations

import re

from scripts.helpers import has
from scripts.schema import Profile


def normalize_token(name: str) -> str:
    """Normalize text for tolerant matching (lowercase, alphanumeric only)."""
    if not name:
        return ""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def escape_mermaid_label(text: str) -> str:
    """Escape text so it is completely safe inside Mermaid node quotes."""
    if not text:
        return ""
    # Strip HTML and replace double quotes
    clean = re.sub(r"<[^>]+>", "", text).replace('"', "'").strip()
    # Remove characters that can break Mermaid syntax
    clean = clean.replace("(", "（").replace(")", "）").replace("[", "【").replace("]", "】")
    return clean


def sanitize_node_id(prefix: str, text: str) -> str:
    """Create a safe alphanumeric node identifier for Mermaid."""
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", text.strip())
    return f"{prefix}_{cleaned}".strip("_")


def match_skill_to_stack(skill_name: str, stack_items: list[str]) -> bool:
    """Check if a skill matches any item in a project's stack."""
    norm_skill = normalize_token(skill_name)
    if not norm_skill:
        return False
    for item in stack_items:
        norm_item = normalize_token(item)
        if not norm_item:
            continue
        if norm_skill == norm_item:
            return True
        # Match if one is a substring of the other (e.g., Supabase in Supabase PostgreSQL)
        if (
            len(norm_skill) >= 4
            and len(norm_item) >= 4
            and (norm_skill in norm_item or norm_item in norm_skill)
        ):
            return True
    return False


def generate_mermaid_skill_map(profile: Profile, max_nodes: int = 30) -> str:
    """Generate a Mermaid flowchart (LR) mapping skill groups -> tech -> projects."""
    if not getattr(profile.features, "mermaid_skill_map", True):
        return ""

    if not has(profile.skills.groups) or not has(profile.projects):
        return ""

    # Prefer featured projects first, then others
    candidate_projects = [p for p in profile.projects if p.featured and has(p.stack)]
    if not candidate_projects:
        candidate_projects = [p for p in profile.projects if has(p.stack)]
    if not candidate_projects:
        return ""

    # Map groups -> technologies -> projects
    # connections: group_name -> { tech_name: set(project_titles) }
    connections: dict[str, dict[str, set[str]]] = {}
    total_techs: set[str] = set()
    used_projects: set[str] = set()

    for group in profile.skills.groups:
        if not has(group.items):
            continue
        g_name = group.name.strip()
        for item in group.items:
            tech_name = item.name.strip()
            matching_projects = set()
            for proj in candidate_projects:
                if match_skill_to_stack(tech_name, proj.stack):
                    matching_projects.add(proj.title.strip())

            if matching_projects:
                if g_name not in connections:
                    connections[g_name] = {}
                connections[g_name][tech_name] = matching_projects
                total_techs.add(tech_name)
                used_projects.update(matching_projects)

    # Check if there are enough links to justify a diagram
    total_links = sum(
        len(projs) for g in connections.values() for projs in g.values()
    )
    if total_links < 3 or not connections or not used_projects:
        return ""

    # Calculate total unique nodes: groups + techs + projects
    # If exceeding max_nodes, prune least-connected technologies
    used_groups = set(connections.keys())
    while (len(used_groups) + len(total_techs) + len(used_projects)) > max_nodes and total_techs:
        # Find technology with fewest connections
        least_tech = min(
            total_techs,
            key=lambda t: sum(
                len(connections[g][t]) for g in connections if t in connections[g]
            ),
        )
        total_techs.remove(least_tech)
        for g in list(connections.keys()):
            connections[g].pop(least_tech, None)
            if not connections[g]:
                del connections[g]
        used_groups = set(connections.keys())
        used_projects = {
            p for g in connections.values() for projs in g.values() for p in projs
        }

    if not connections or not total_techs or not used_projects:
        return ""

    # Build Mermaid diagram
    lines: list[str] = ["```mermaid", "flowchart LR"]

    # Define Node IDs and labels
    # 1. Group to Tech edges
    for g_name, techs in connections.items():
        g_id = sanitize_node_id("grp", g_name)
        g_label = escape_mermaid_label(g_name)
        for t_name, projs in techs.items():
            t_id = sanitize_node_id("tech", t_name)
            t_label = escape_mermaid_label(t_name)
            lines.append(f'  {g_id}["{g_label}"] --> {t_id}["{t_label}"]')
            for p_title in sorted(projs):
                p_id = sanitize_node_id("prj", p_title)
                p_label = escape_mermaid_label(p_title)
                lines.append(f'  {t_id} --> {p_id}["{p_label}"]')

    lines.append("```")
    return "\n".join(lines)
