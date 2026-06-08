#!/usr/bin/env python3
"""
Master fetcher — single GraphQL batch for everything.
Run: python fetch.py
"""
import sys
import time
from github_api import graphql_query, save_json

MASTER_QUERY = """
query($login: String!) {
  user(login: $login) {
    name login bio location avatarUrl websiteUrl email
    twitterUsername createdAt updatedAt isHireable
    status { emoji message }
    pinnedItems(first: 6, types: REPOSITORY) {
      nodes {
        ... on Repository {
          name url description
          primaryLanguage { name color }
          stargazerCount forkCount
        }
      }
    }
    repositories(first: 100, orderBy: {field: UPDATED_AT, direction: DESC}, ownerAffiliations: OWNER) {
      pageInfo { hasNextPage endCursor }
      totalCount
      nodes {
        name url description homepageUrl createdAt updatedAt pushedAt
        isPrivate isFork isArchived isTemplate
        stargazerCount forkCount
        watchers { totalCount }
        primaryLanguage { name color }
        repositoryTopics(first: 10) { nodes { topic { name } } }
        licenseInfo { spdxId name }
        defaultBranchRef { name }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    starredRepositories(first: 100, orderBy: {field: STARRED_AT, direction: DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        nameWithOwner url description createdAt
        stargazerCount forkCount
        primaryLanguage { name color }
        licenseInfo { spdxId }
        repositoryTopics(first: 5) { nodes { topic { name } } }
      }
    }
    followers(first: 100) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        login name avatarUrl url bio location
        repositories { totalCount }
      }
    }
    following(first: 1) { totalCount }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount date color
          }
        }
      }
      contributionYears
      totalCommitContributions
      restrictedContributionsCount
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalRepositoryContributions
    }
    issues(first: 1) { totalCount }
    pullRequests(first: 1) { totalCount }
  }
}
"""


def fetch_all(login="mayank-dev-15"):
    t0 = time.time()
    print(f"Fetching all data for @{login} in 1 GraphQL request...")
    result = graphql_query(MASTER_QUERY, {"login": login})
    elapsed = time.time() - t0
    user = result.get("data", {}).get("user", {})

    if not user:
        print("ERROR: No user data returned")
        sys.exit(1)

    # 1. Profile
    profile = {
        "name": user.get("name"),
        "login": user.get("login"),
        "bio": user.get("bio"),
        "location": user.get("location"),
        "avatar_url": user.get("avatarUrl"),
        "website": user.get("websiteUrl"),
        "email": user.get("email"),
        "twitter": user.get("twitterUsername"),
        "created_at": user.get("createdAt"),
        "updated_at": user.get("updatedAt"),
        "hireable": user.get("isHireable"),
        "status": user.get("status"),
        "pinned_repos": [
            {
                "name": p["name"], "url": p["url"],
                "description": p.get("description", ""),
                "language": (p.get("primaryLanguage") or {}).get("name"),
                "stars": p.get("stargazerCount", 0),
                "forks": p.get("forkCount", 0),
            }
            for p in user.get("pinnedItems", {}).get("nodes", [])
        ],
    }
    save_json(profile, "profile.json")

    # 2. Repos
    repos_data = user.get("repositories", {})
    repos = [
        {
            "name": r["name"], "url": r["url"],
            "description": r.get("description", ""),
            "homepage": r.get("homepageUrl"),
            "created_at": r.get("createdAt"),
            "updated_at": r.get("updatedAt"),
            "pushed_at": r.get("pushedAt"),
            "is_private": r.get("isPrivate", False),
            "is_fork": r.get("isFork", False),
            "is_archived": r.get("isArchived", False),
            "is_template": r.get("isTemplate", False),
            "stars": r.get("stargazerCount", 0),
            "forks": r.get("forkCount", 0),
            "watchers": r.get("watchers", {}).get("totalCount", 0) if isinstance(r.get("watchers"), dict) else 0,
            "language": (r.get("primaryLanguage") or {}).get("name"),
            "language_color": (r.get("primaryLanguage") or {}).get("color"),
            "topics": [t["topic"]["name"] for t in r.get("repositoryTopics", {}).get("nodes", [])],
            "license": (r.get("licenseInfo") or {}).get("spdxId"),
            "default_branch": (r.get("defaultBranchRef") or {}).get("name"),
        }
        for r in repos_data.get("nodes", [])
        if not r.get("isPrivate", False)
    ]
    save_json(repos, "repos.json")

    # 3. Stars
    stars_data = user.get("starredRepositories", {})
    stars = [
        {
            "name_with_owner": s["nameWithOwner"], "url": s["url"],
            "description": s.get("description", ""),
            "starred_at": s.get("createdAt"),
            "stars": s.get("stargazerCount", 0),
            "forks": s.get("forkCount", 0),
            "language": (s.get("primaryLanguage") or {}).get("name"),
            "license": (s.get("licenseInfo") or {}).get("spdxId"),
            "topics": [t["topic"]["name"] for t in s.get("repositoryTopics", {}).get("nodes", [])],
        }
        for s in stars_data.get("nodes", [])
    ]
    save_json({"total_count": stars_data.get("totalCount", 0), "stars": stars}, "stars.json")

    # 4. Followers
    followers_data = user.get("followers", {})
    followers = [
        {
            "login": f["login"], "name": f.get("name"),
            "avatar_url": f.get("avatarUrl"), "url": f.get("url"),
            "bio": f.get("bio", ""), "location": f.get("location", ""),
            "repos": f.get("repositories", {}).get("totalCount", 0),
        }
        for f in followers_data.get("nodes", [])
    ]
    save_json({
        "total_followers": followers_data.get("totalCount", 0),
        "total_following": user.get("following", {}).get("totalCount", 0),
        "followers": followers,
    }, "followers.json")

    # 5. Contributions
    coll = user.get("contributionsCollection", {})
    cal = coll.get("contributionCalendar", {})
    contributions = {
        "total_contributions": cal.get("totalContributions", 0),
        "contribution_years": coll.get("contributionYears", []),
        "commits": coll.get("totalCommitContributions", 0),
        "restricted_commits": coll.get("restrictedContributionsCount", 0),
        "issues": coll.get("totalIssueContributions", 0),
        "pull_requests": coll.get("totalPullRequestContributions", 0),
        "pr_reviews": coll.get("totalPullRequestReviewContributions", 0),
        "repos_created": coll.get("totalRepositoryContributions", 0),
        "total_issues": user.get("issues", {}).get("totalCount", 0),
        "total_prs": user.get("pullRequests", {}).get("totalCount", 0),
        "total_repos": repos_data.get("totalCount", 0),
        "calendar": cal,
    }
    save_json(contributions, "contributions.json")

    # 6. Languages (aggregate from repos)
    lang_totals = {}
    for repo in repos_data.get("nodes", []):
        for edge in repo.get("languages", {}).get("edges", []):
            lang_name = edge["node"]["name"]
            size = edge["size"]
            lang_totals[lang_name] = lang_totals.get(lang_name, 0) + size

    total_bytes = sum(lang_totals.values())
    languages = []
    color_map = {}
    for repo in repos_data.get("nodes", []):
        for edge in repo.get("languages", {}).get("edges", []):
            n = edge["node"]["name"]
            if n not in color_map:
                color_map[n] = edge["node"].get("color", "#000000")

    for name, bytes_ in sorted(lang_totals.items(), key=lambda x: -x[1]):
        languages.append({
            "name": name,
            "bytes": bytes_,
            "percentage": round(bytes_ / total_bytes * 100, 1) if total_bytes > 0 else 0,
            "color": color_map.get(name, "#000"),
        })
    save_json({"total_bytes": total_bytes, "languages": languages}, "languages.json")

    # 7. Summary stats
    summary = {
        "total_repos": repos_data.get("totalCount", 0),
        "public_repos": len(repos),
        "total_stars": stars_data.get("totalCount", 0),
        "total_followers": followers_data.get("totalCount", 0),
        "total_following": user.get("following", {}).get("totalCount", 0),
        "total_contributions": cal.get("totalContributions", 0),
        "total_commits": coll.get("totalCommitContributions", 0),
        "total_prs": coll.get("totalPullRequestContributions", 0),
        "total_issues": coll.get("totalIssueContributions", 0),
        "total_pr_reviews": coll.get("totalPullRequestReviewContributions", 0),
        "languages_count": len(languages),
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fetch_time_seconds": round(elapsed, 2),
    }
    save_json(summary, "summary.json")

    print(f"Done in {elapsed:.1f}s — {len(repos)} repos, {len(stars)} stars, "
          f"{followers_data.get('totalCount', 0)} followers, "
          f"{cal.get('totalContributions', 0)} contributions")
    return summary


if __name__ == "__main__":
    fetch_all()
