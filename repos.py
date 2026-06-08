from github_api import graphql_query, save_json

QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    repositories(first: 100, after: $cursor, orderBy: {field: UPDATED_AT, direction: DESC}, ownerAffiliations: OWNER) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        url
        description
        homepageUrl
        createdAt
        updatedAt
        pushedAt
        isPrivate
        isFork
        isArchived
        isTemplate
        stargazerCount
        forkCount
        watchCount
        primaryLanguage { name color }
        repositoryTopics(first: 10) {
          nodes { topic { name } }
        }
        licenseInfo { spdxId name }
        defaultBranchRef { name }
      }
    }
  }
}
"""


def fetch_repos(login="mayank-dev-15"):
    all_repos = []
    cursor = None
    while True:
        variables = {"login": login, "cursor": cursor}
        result = graphql_query(QUERY, variables)
        user = result.get("data", {}).get("user", {})
        repo_data = user.get("repositories", {})
        nodes = repo_data.get("nodes", [])
        all_repos.extend(nodes)
        page_info = repo_data.get("pageInfo", {})
        if page_info.get("hasNextPage"):
            cursor = page_info["endCursor"]
        else:
            break

    repos = [
        {
            "name": r["name"],
            "url": r["url"],
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
            "watchers": r.get("watchCount", 0),
            "language": (r.get("primaryLanguage") or {}).get("name"),
            "language_color": (r.get("primaryLanguage") or {}).get("color"),
            "topics": [t["topic"]["name"] for t in r.get("repositoryTopics", {}).get("nodes", [])],
            "license": (r.get("licenseInfo") or {}).get("spdxId"),
            "default_branch": (r.get("defaultBranchRef") or {}).get("name"),
        }
        for r in all_repos
        if not r.get("isPrivate", False)
    ]

    save_json(repos, "repos.json")
    return repos


if __name__ == "__main__":
    repos = fetch_repos()
    print(f"Public repos: {len(repos)}")
    for r in repos[:5]:
        print(f"  {r['name']}: {r['stars']} stars, {r['forks']} forks")
