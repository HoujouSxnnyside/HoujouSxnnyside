#!/usr/bin/env python3
"""
HoujouSxnnyside Cute-Weirdcore Card Telemetry Updater
Direct GitHub API updater with zero third-party dependencies.
Gracefully preserves existing aesthetic cards on rate limits or API outages.
"""

import os
import sys
import json
import re
import urllib.request
import urllib.error

USERNAME = os.environ.get("GITHUB_ACTOR", "HoujouSxnnyside")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
STATS_PATH = "profile/stats.svg"
LANGS_PATH = "profile/top-langs.svg"

def make_request(url):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Houjou-Aesthetic-Stats")
    req.add_header("Accept", "application/vnd.github.v3+json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    return req

def fetch_telemetry():
    try:
        # Fetch user profile
        user_url = f"https://api.github.com/users/{USERNAME}"
        with urllib.request.urlopen(make_request(user_url), timeout=10) as resp:
            user_data = json.loads(resp.read().decode())
        
        # Fetch repos
        repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner&sort=updated"
        with urllib.request.urlopen(make_request(repos_url), timeout=10) as resp:
            repos_data = json.loads(resp.read().decode())

        total_repos = user_data.get("public_repos", len(repos_data))
        total_stars = sum(r.get("stargazers_count", 0) for r in repos_data if isinstance(r, dict))
        
        # Count primary languages
        lang_counts = {}
        for r in repos_data:
            if isinstance(r, dict):
                lang = r.get("language")
                if lang:
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1
                    
        return {
            "repos": total_repos,
            "stars": total_stars,
            "languages": lang_counts
        }
    except Exception as e:
        print(f"[!] Telemetry fetch warning (gracefully falling back to cached cards): {e}")
        return None

def update_stats_svg(telemetry):
    if not telemetry or not os.path.exists(STATS_PATH):
        return

    with open(STATS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Update stars if fetched
    stars = telemetry.get("stars", 0)
    if stars > 0:
        content = re.sub(
            r'(<text[^>]*id="stat-stars"[^>]*>)([^<]*)(</text>)',
            rf'\g<1>{stars}★\g<3>',
            content
        )

    # Update repos
    repos = telemetry.get("repos", 0)
    if repos > 0:
        content = re.sub(
            r'(<text[^>]*id="stat-repos"[^>]*>)([^<]*)(</text>)',
            rf'\g<1>{repos}\g<3>',
            content
        )

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("✦ profile/stats.svg updated cleanly!")

def main():
    print("✦ Starting HoujouSxnnyside Cute-Weirdcore Telemetry check...")
    telemetry = fetch_telemetry()
    if telemetry:
        print(f"✦ Fetched stats: Repos={telemetry.get('repos')}, Stars={telemetry.get('stars')}")
        update_stats_svg(telemetry)
    else:
        print("✦ Keeping existing high-aesthetic vector cards intact.")

if __name__ == "__main__":
    main()

