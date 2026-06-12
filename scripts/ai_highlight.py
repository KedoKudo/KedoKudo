# /// script
# requires-python = ">=3.11"
# dependencies = ["openai"]
# ///
"""Ask an LLM (via OpenRouter) to summarize recent public GitHub activity into data/highlight.md.

Runs with `uv run scripts/ai_highlight.py`. The generated markdown is inserted
into the "Currently Exploring" section of README.md by scripts/update_profile.py.

Environment variables:
    OPENROUTER_API_KEY  required — exits cleanly (keeping the previous
                        highlight) when absent, so the stats pipeline still works
    OPENROUTER_MODEL    model slug (default: anthropic/claude-opus-4.8)
    GITHUB_USERNAME     GitHub login to summarize (default: KedoKudo)
    GITHUB_TOKEN        optional token for the GitHub events API
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HIGHLIGHT_PATH = REPO_ROOT / "data" / "highlight.md"

USERNAME = os.environ.get("GITHUB_USERNAME", "KedoKudo")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
MODEL = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-opus-4.8")

SYSTEM_PROMPT = """\
You write the "Currently Exploring" section of a GitHub profile README for Chen
(KedoKudo), a computational scientist at Oak Ridge National Laboratory who works
on neutron scattering software, AI research, and scientific software development.

You will receive a digest of his recent public GitHub activity. Write 2-4
markdown bullet points, first person, describing what he is currently working on
or exploring. Ground every bullet in the activity digest — never invent projects,
technologies, or claims that are not supported by it. Keep the tone professional
but personable; each bullet should be a single sentence. Link repository names
to https://github.com/<full_name> when you mention them.

Return ONLY the markdown bullet list, with no preamble or code fences.
"""


def fetch_activity_digest() -> str:
    headers = {
        "User-Agent": "kedokudo-profile-automation",
        "Accept": "application/vnd.github+json",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    url = f"https://api.github.com/users/{USERNAME}/events/public?per_page=100"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as resp:
        events = json.load(resp)

    lines = []
    for event in events:
        repo = event.get("repo", {}).get("name", "unknown")
        etype = event.get("type", "Event")
        created = (event.get("created_at") or "")[:10]
        detail = ""
        payload = event.get("payload", {})
        if etype == "PushEvent":
            messages = [
                c.get("message", "").splitlines()[0]
                for c in payload.get("commits", [])[:3]
                if c.get("message")
            ]
            detail = "; ".join(messages)
        elif etype in ("PullRequestEvent", "IssuesEvent"):
            item = payload.get("pull_request") or payload.get("issue") or {}
            detail = f"{payload.get('action', '')}: {item.get('title', '')}"
        elif etype == "CreateEvent":
            detail = f"created {payload.get('ref_type', '')} {payload.get('ref') or ''}".strip()
        lines.append(f"{created} {etype} in {repo}: {detail}".strip().rstrip(":"))

    return "\n".join(lines[:80])


def main() -> None:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY not set; keeping the existing highlight.", file=sys.stderr)
        return

    digest = fetch_activity_digest()
    if not digest.strip():
        print("No recent public activity found; keeping the existing highlight.", file=sys.stderr)
        return

    from openai import OpenAI

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=1024,
        extra_headers={
            # Optional OpenRouter attribution headers
            "HTTP-Referer": f"https://github.com/{USERNAME}",
            "X-Title": "KedoKudo profile automation",
        },
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Recent public GitHub activity for {USERNAME}:\n\n{digest}",
            },
        ],
    )

    text = (response.choices[0].message.content or "").strip()
    if not text.startswith("-"):
        print(f"Unexpected response shape; keeping the existing highlight:\n{text}", file=sys.stderr)
        return

    HIGHLIGHT_PATH.parent.mkdir(exist_ok=True)
    HIGHLIGHT_PATH.write_text(text + "\n")
    print(f"AI highlight refreshed via {MODEL}.")


if __name__ == "__main__":
    main()
