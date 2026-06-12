# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fetch GitHub stats, render assets/stats.svg, and generate README.md from a template.

Runs with zero installed dependencies: `uv run scripts/update_profile.py`.

Environment variables:
    GITHUB_USERNAME       GitHub login to profile (default: KedoKudo)
    GITHUB_TOKEN          token for authenticated API calls (recommended in CI)
    ORG_NAMES             comma-separated orgs whose repos should also be tracked
    ORG_REPO_FILTER       "contributed" (default) only counts org repos the user
                          contributed to; "all" counts every public org repo
    ORG_REPO_LIMIT        cap on org repos after filtering (0/unset = no cap)
    EXCLUDED_LANGUAGES    comma-separated languages to drop from the breakdown
    LANGUAGE_MODE         "bytes" (per-repo language bytes) or "primary"
    LANGUAGE_REPO_LIMIT   max repos sampled for byte counts (default: 120)
    TOP_LANGUAGES_LIMIT   languages shown in the breakdown (default: 6)
    STATS_SOURCE_FILE     read stats from this JSON file instead of the API
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from string import Template
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parent.parent
API_BASE = "https://api.github.com"
PROFILE_TIME_ZONE = ZoneInfo("America/Chicago")

USERNAME = os.environ.get("GITHUB_USERNAME", "KedoKudo")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ORG_NAMES = [o.strip() for o in os.environ.get("ORG_NAMES", "").split(",") if o.strip()]
ORG_REPO_FILTER = os.environ.get("ORG_REPO_FILTER", "contributed").lower()
ORG_REPO_LIMIT = int(os.environ.get("ORG_REPO_LIMIT", "0") or 0)
EXCLUDED_LANGUAGES = {
    lang.strip().lower()
    for lang in os.environ.get("EXCLUDED_LANGUAGES", "Makefile,Jupyter Notebook").split(",")
    if lang.strip()
}
LANGUAGE_MODE = os.environ.get("LANGUAGE_MODE", "primary").lower()
LANGUAGE_REPO_LIMIT = int(os.environ.get("LANGUAGE_REPO_LIMIT", "120") or 120)
TOP_LANGUAGES_LIMIT = max(1, int(os.environ.get("TOP_LANGUAGES_LIMIT", "6") or 6))


def request_json(url: str):
    headers = {
        "User-Agent": "kedokudo-profile-automation",
        "Accept": "application/vnd.github+json",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def fetch_paginated(url: str) -> list[dict]:
    items: list[dict] = []
    page = 1
    while True:
        sep = "&" if "?" in url else "?"
        batch = request_json(f"{url}{sep}per_page=100&page={page}")
        if not isinstance(batch, list) or not batch:
            return items
        items.extend(batch)
        if len(batch) < 100:
            return items
        page += 1


def is_contributor(full_name: str) -> bool:
    target = USERNAME.lower()
    for page in range(1, 25):
        try:
            contributors = request_json(
                f"{API_BASE}/repos/{full_name}/contributors?per_page=100&page={page}"
            )
        except urllib.error.HTTPError:
            return False
        if not isinstance(contributors, list) or not contributors:
            return False
        if any((c.get("login") or "").lower() == target for c in contributors):
            return True
        if len(contributors) < 100:
            return False
    return False


def collect_org_repos() -> list[dict]:
    repos: list[dict] = []
    for org in ORG_NAMES:
        repos.extend(fetch_paginated(f"{API_BASE}/orgs/{org}/repos?type=public"))
    if ORG_REPO_FILTER != "all":
        filtered = []
        for repo in repos:
            if repo.get("full_name") and is_contributor(repo["full_name"]):
                filtered.append(repo)
            if ORG_REPO_LIMIT and len(filtered) >= ORG_REPO_LIMIT:
                break
        repos = filtered
    if ORG_REPO_LIMIT:
        repos = repos[:ORG_REPO_LIMIT]
    return repos


def merge_repos(primary: list[dict], extra: list[dict]) -> list[dict]:
    by_name: dict[str, dict] = {}
    for repo in primary + extra:
        full_name = repo.get("full_name")
        if full_name and full_name not in by_name:
            by_name[full_name] = repo
    return list(by_name.values())


def summarize_languages(repos: list[dict]) -> dict:
    if LANGUAGE_MODE == "bytes":
        return summarize_languages_by_bytes(repos)
    return summarize_languages_by_primary(repos)


def summarize_languages_by_primary(repos: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for repo in repos:
        lang = repo.get("language")
        if lang and lang.lower() not in EXCLUDED_LANGUAGES:
            counts[lang] = counts.get(lang, 0) + 1
    return build_language_entries(counts, sampled=len(repos))


def summarize_languages_by_bytes(repos: list[dict]) -> dict:
    repos = sorted(repos, key=lambda r: r.get("pushed_at") or "", reverse=True)
    if LANGUAGE_REPO_LIMIT:
        repos = repos[:LANGUAGE_REPO_LIMIT]

    counts: dict[str, int] = {}

    def fetch_languages(repo: dict) -> dict:
        try:
            return request_json(f"{API_BASE}/repos/{repo['full_name']}/languages")
        except (urllib.error.URLError, KeyError) as err:
            print(f"Skipping {repo.get('full_name')} language stats: {err}", file=sys.stderr)
            return {}

    with ThreadPoolExecutor(max_workers=8) as pool:
        for lang_map in pool.map(fetch_languages, repos):
            for lang, nbytes in lang_map.items():
                if lang.lower() not in EXCLUDED_LANGUAGES:
                    counts[lang] = counts.get(lang, 0) + nbytes

    return build_language_entries(counts, sampled=len(repos))


def build_language_entries(counts: dict[str, int], sampled: int) -> dict:
    total = sum(counts.values())
    entries = [
        {
            "language": lang,
            "bytes": weight,
            "percent": round(weight / total * 100, 1) if total else 0,
        }
        for lang, weight in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    ][:TOP_LANGUAGES_LIMIT]
    text = (
        ", ".join(f"{e['language']} ({e['percent']}%)" for e in entries)
        if entries
        else "Not enough public repositories to determine top languages."
    )
    return {"topLanguages": entries, "topLanguagesText": text, "languageSampledRepos": sampled}


def fetch_stats() -> dict:
    user = request_json(f"{API_BASE}/users/{USERNAME}")
    user_repos = fetch_paginated(f"{API_BASE}/users/{USERNAME}/repos")
    org_repos = collect_org_repos() if ORG_NAMES else []
    tracked = merge_repos(user_repos, org_repos)
    languages = summarize_languages(tracked)
    return {
        "username": USERNAME,
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "followers": user["followers"],
        "following": user["following"],
        "publicRepos": user["public_repos"],
        "trackedRepos": len(tracked),
        "totalStars": sum(r.get("stargazers_count") or 0 for r in tracked),
        **languages,
        "orgsIncluded": ORG_NAMES,
        "orgRepoFilter": ORG_REPO_FILTER,
    }


def load_stats() -> dict:
    source = os.environ.get("STATS_SOURCE_FILE")
    if source:
        stats = json.loads(Path(source).read_text())
        stats.setdefault("generatedAt", datetime.now(timezone.utc).isoformat())
        stats.setdefault("trackedRepos", stats.get("publicRepos"))
        return stats
    return fetch_stats()


def build_svg(stats: dict) -> str:
    width, height, padding = 600, 320, 24
    max_bar_width = width - padding * 2 - 140
    title_y = padding + 20
    base_y = title_y + 30
    line_spacing = 24

    lines = [
        f"Followers: {stats['followers']:,}",
        f"Following: {stats['following']:,}",
        f"Repos tracked: {stats.get('trackedRepos') or stats['publicRepos']:,}",
        f"Stars earned: {stats['totalStars']:,}",
    ]
    stat_lines = "\n".join(
        f'<text x="{padding}" y="{base_y + i * line_spacing}" class="stat-line">{line}</text>'
        for i, line in enumerate(lines)
    )

    bar_start_y = base_y + len(lines) * line_spacing + 48
    bars = []
    for idx, lang in enumerate(stats.get("topLanguages", [])):
        bar_width = lang["percent"] / 100 * max_bar_width
        y = bar_start_y + idx * 28
        bars.append(
            f'<text x="{padding}" y="{y}" class="lang-name">{lang["language"]}</text>\n'
            f'<rect x="{padding + 110}" y="{y - 14}" width="{bar_width:.1f}" height="16" rx="4" class="bar"></rect>\n'
            f'<text x="{padding + 110 + bar_width + 8:.1f}" y="{y}" class="lang-percent">{lang["percent"]}%</text>'
        )
    bars_svg = "\n".join(bars) or (
        f'<text x="{padding}" y="{bar_start_y + 4}" class="lang-name">No data yet</text>'
    )

    generated = datetime.fromisoformat(stats["generatedAt"].replace("Z", "+00:00"))
    title_date = generated.astimezone(PROFILE_TIME_ZONE).strftime("%-m/%-d/%Y")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .card {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; rx: 16; }}
    .title {{ font: 700 20px 'Segoe UI', Ubuntu, Sans-Serif; fill: #f0f6fc; }}
    .stat-line {{ font: 400 16px 'Segoe UI', Ubuntu, Sans-Serif; fill: #c9d1d9; }}
    .lang-name {{ font: 600 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: #58a6ff; }}
    .lang-percent {{ font: 400 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: #8b949e; }}
    .bar {{ fill: #2ea043; }}
  </style>
  <rect class="card" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="16" />
  <text x="{padding}" y="{title_y}" class="title">GitHub Snapshot · {title_date}</text>
  {stat_lines}
  <text x="{padding}" y="{bar_start_y - 24}" class="stat-line">Top languages</text>
  {bars_svg}
</svg>"""


def format_timestamp(value: str | datetime) -> str:
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    local = value.astimezone(PROFILE_TIME_ZONE)
    return local.strftime("%A, %B %-d, %Y at %-I:%M %p %Z")


def load_ai_highlight() -> str:
    highlight_path = REPO_ROOT / "data" / "highlight.md"
    if highlight_path.exists() and highlight_path.read_text().strip():
        return highlight_path.read_text().strip()
    return (
        "- Neutron data reduction workflows, agentic AI for scientific computing, "
        "and whatever my commit history says I should be doing."
    )


def render_readme(stats: dict) -> None:
    template = Template((REPO_ROOT / "templates" / "README.md.tmpl").read_text())
    readme = template.substitute(
        date=format_timestamp(datetime.now(timezone.utc)),
        ai_highlight=load_ai_highlight(),
        stats_generated_at=format_timestamp(stats["generatedAt"]),
        stats_followers=f"{stats['followers']:,}",
        stats_tracked_repos=f"{stats.get('trackedRepos') or stats['publicRepos']:,}",
        stats_public_repos=f"{stats['publicRepos']:,}",
        stats_total_stars=f"{stats['totalStars']:,}",
        stats_top_languages=stats["topLanguagesText"],
    )
    (REPO_ROOT / "README.md").write_text(readme)


def main() -> None:
    stats = load_stats()

    (REPO_ROOT / "data").mkdir(exist_ok=True)
    (REPO_ROOT / "assets").mkdir(exist_ok=True)
    (REPO_ROOT / "data" / "stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    (REPO_ROOT / "assets" / "stats.svg").write_text(build_svg(stats))
    render_readme(stats)
    print("Profile README, stats.json, and stats.svg updated.")


if __name__ == "__main__":
    main()
