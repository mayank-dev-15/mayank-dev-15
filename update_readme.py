#!/usr/bin/env python3
"""
Updates README.md with live GitHub data from cached JSON files.
Run after fetch.py: python update_readme.py
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).parent
README = BASE / "README.md"
DATA = BASE / "data"


def load(filename):
    p = DATA / filename
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def main():
    if not README.exists():
        print("README.md not found")
        return

    summary = load("summary.json")
    profile = load("profile.json")
    contributions = load("contributions.json")
    languages = load("languages.json")
    repos = load("repos.json")
    stars = load("stars.json")
    followers = load("followers.json")

    readme = README.read_text(encoding="utf-8")

    # === Update header stats line ===
    total_repos = summary.get("total_repos", len(repos))
    total_stars = summary.get("total_stars", 0)
    total_followers = summary.get("total_followers", 0)
    total_contributions = summary.get("total_contributions", 0)
    total_commits = summary.get("total_commits", 0)
    total_prs = summary.get("total_prs", 0)
    total_issues = summary.get("total_issues", 0)
    lang_count = summary.get("languages_count", 0)

    # Update "87 repos" count in header
    readme = re.sub(
        r'(\d+) repos',
        f'{total_repos} repos',
        readme,
        count=1
    )

    # Update "30+ languages" → actual count
    readme = re.sub(
        r'(\d+)\+ langs',
        f'{lang_count}+ langs',
        readme,
        count=1
    )

    # === Update Trophy Wall ===
    trophy_lines = []
    trophy_lines.append(f"🥇 Security Toolmaker       — {sum(1 for r in repos if any(t in (r.get('topics', []) + [r.get('name', '')]) for t in ['security', 'pentest', 'audit', 'vulnerability', 'ids', 'nids']))} security tools")
    trophy_lines.append(f"🥇 Visualization Master     — {sum(1 for r in repos if any(t in (r.get('topics', []) + [r.get('name', '')]) for t in ['visualization', 'simulator', 'explorer', 'particle', 'fractal', 'neural', 'gravity', 'maze', 'wave', 'spectrograph', 'hexagonal', 'cyberpunk']))} visualization projects")
    trophy_lines.append(f"🥇 Open Source Contributor  — {contributions.get('pr_reviews', 0) + contributions.get('pull_requests', 0)} PRs merged")
    trophy_lines.append(f"🥇 Linux & OS Architect    — {sum(1 for r in repos if any(t in (r.get('topics', []) + [r.get('name', '')]) for t in ['os', 'linux', 'pentestos', 'shieldos', 'vaultos', 'androidfw', 'firmware', 'kernel']))} OS projects")
    trophy_lines.append(f"🥇 Full-Stack Builder       — {sum(1 for r in repos if any(t in (r.get('topics', []) + [r.get('name', '')]) for t in ['flask', 'react', 'fastapi', 'admin', 'dashboard', 'studyhub', 'devforge', 'taskflow']))} apps + admin panels")
    trophy_lines.append(f"🥇 Hardware Hacker          — Arduino winner, SBCs")
    trophy_lines.append(f"🥇 Polyglot Developer       — {lang_count}+ languages")

    trophy_block = (
        "```\n"
        "🏆 DEVELOPER TROPHY CASE 🏆\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        + "\n".join(trophy_lines)
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⭐ Total Trophies: 7/7 ⭐\n"
        "```"
    )

    readme = re.sub(
        r'```\n.*?Total Trophies.*?```',
        trophy_block,
        readme,
        flags=re.DOTALL
    )

    # === Update "All Projects" heading with count ===
    readme = re.sub(
        r'### 🚀 All Projects \(\d+ Repos\)',
        f'### 🚀 All Projects ({total_repos} Repos)',
        readme
    )

    # === Add live stats section after "What I Do" ===
    stats_block = f"""### 📊 Live GitHub Stats

| Metric | Value |
|--------|-------|
| 📦 Public Repos | {total_repos} |
| ⭐ Total Stars Earned | {total_stars} |
| 👥 Followers | {total_followers} |
| 👤 Following | {followers.get('total_following', 0)} |
| 📝 Total Contributions | {total_contributions} |
| 💻 Total Commits | {total_commits} |
| 🔀 Pull Requests | {total_prs} |
| 🐛 Issues Opened | {total_issues} |
| 🗣️ Languages Used | {lang_count}+ |
| ⏱️ Last Synced | {summary.get('fetched_at', 'N/A')} |

"""

    if "### 📊 Live GitHub Stats" in readme:
        readme = re.sub(
            r'### 📊 Live GitHub Stats\n\n\| Metric.*?\| ⏱️ Last Synced.*?\|',
            stats_block.rstrip(),
            readme,
            flags=re.DOTALL
        )
    else:
        readme = readme.replace(
            "### 🚀 All Projects",
            stats_block + "### 🚀 All Projects",
            1
        )

    # === Add contribution calendar at bottom ===
    calendar = contributions.get("calendar", {})
    weeks = calendar.get("weeks", [])
    if weeks:
        cal_lines = []
        for week in weeks:
            for day in week.get("contributionDays", []):
                count = day.get("contributionCount", 0)
                cal_lines.append(f"{day['date']}: {count}")
        # Just keep total, don't bloat the README with daily data

    README.write_text(readme, encoding="utf-8")
    print(f"README.md updated with live stats:")
    print(f"  Repos: {total_repos}")
    print(f"  Stars: {total_stars}")
    print(f"  Followers: {total_followers}")
    print(f"  Contributions: {total_contributions}")
    print(f"  Languages: {lang_count}+")


if __name__ == "__main__":
    main()
