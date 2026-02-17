#!/usr/bin/env python3
"""Brave Search API helper for deep-research skill.

Usage:
  python3 ~/skills/deep-research/brave_search.py search "query here"
  python3 ~/skills/deep-research/brave_search.py fetch "https://example.com"

Requires BRAVE_SEARCH_API_KEY in environment or in a .env file.
"""

import json
import os
import pathlib
import re
import sys
import urllib.parse


def _load_env():
    """Load .env from several candidate locations until BRAVE_SEARCH_API_KEY is found."""
    if os.environ.get("BRAVE_SEARCH_API_KEY"):
        return  # Already set in environment

    try:
        from dotenv import load_dotenv
    except ImportError:
        return  # No dotenv; rely on env vars being set directly

    # Candidate .env locations, tried in order
    candidates = [
        pathlib.Path.cwd() / ".env",
        pathlib.Path(__file__).resolve().parent / ".env",
        pathlib.Path.home() / ".env",
        pathlib.Path.home() / "claude" / ".env",
        # WSL: project dir mounted from Windows
        pathlib.Path("/mnt/c/Users") / os.environ.get("USER", "_") / "claude" / ".env",
    ]

    for p in candidates:
        if p.is_file():
            load_dotenv(p)
            if os.environ.get("BRAVE_SEARCH_API_KEY"):
                return


_load_env()

import requests


def search(query: str) -> None:
    """Search Brave and print simplified JSON results."""
    api_key = os.environ.get("BRAVE_SEARCH_API_KEY")
    if not api_key:
        print(json.dumps({"error": "BRAVE_SEARCH_API_KEY not set"}))
        sys.exit(1)

    url = "https://api.search.brave.com/res/v1/web/search"
    params = {"q": query, "count": 10}
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key,
    }

    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for item in data.get("web", {}).get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "description": item.get("description", ""),
            "age": item.get("age", ""),
        })

    print(json.dumps(results, indent=2))


def fetch(url: str) -> None:
    """Fetch a URL and print cleaned text content."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)",
    }
    resp = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
    resp.raise_for_status()
    html = resp.text

    # Strip script and style tags with contents
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # Strip all remaining HTML tags
    text = re.sub(r"<[^>]+>", " ", html)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Decode common HTML entities
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")

    # Limit output to ~15,000 chars
    if len(text) > 15000:
        text = text[:15000] + "\n\n[... truncated at 15,000 characters ...]"

    print(text)


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage:")
        print('  python3 brave_search.py search "query"')
        print('  python3 brave_search.py fetch "https://example.com"')
        sys.exit(1)

    mode = sys.argv[1]
    arg = sys.argv[2]

    if mode == "search":
        search(arg)
    elif mode == "fetch":
        fetch(arg)
    else:
        print(f"Unknown mode: {mode}. Use 'search' or 'fetch'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
