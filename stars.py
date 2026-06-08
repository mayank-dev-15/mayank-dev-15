from github_api import graphql_query, save_json

QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    starredRepositories(first: 100, after: $cursor, orderBy: {field: STARRED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      totalCount
      nodes {
        nameWithOwner
        url
        description
        createdAt
        stargazerCount
        forkCount
        primaryLanguage { name color }
        licenseInfo { spdxId }
        repositoryTopics(first: 5) {
          nodes { topic { name } }
        }
      }
    }
  }
}
"""


def fetch_stars(login="mayank-dev-15"):
    all_stars = []
    cursor = None
    total_count = 0
    while True:
        variables = {"login": login, "cursor": cursor}
        result = graphql_query(QUERY, variables)
        user = result.get("data", {}).get("user", {})
        star_data = user.get("starredRepositories", {})
        total_count = star_data.get("totalCount", 0)
        nodes = star_data.get("nodes", [])
        all_stars.extend(nodes)
        page_info = star_data.get("pageInfo", {})
        if page_info.get("hasNextPage"):
            cursor = page_info["endCursor"]
        else:
            break

    stars = [
        {
            "name_with_owner": s["nameWithOwner"],
            "url": s["url"],
            "description": s.get("description", ""),
            "starred_at": s.get("createdAt"),
            "stars": s.get("stargazerCount", 0),
            "forks": s.get("forkCount", 0),
            "language": (s.get("primaryLanguage") or {}).get("name"),
            "license": (s.get("licenseInfo") or {}).get("spdxId"),
            "topics": [t["topic"]["name"] for t in s.get("repositoryTopics", {}).get("nodes", [])],
        }
        for s in all_stars
    ]

    save_json({"total_count": total_count, "stars": stars}, "stars.json")
    return total_count, stars


if __name__ == "__main__":
    total, stars = fetch_stars()
    print(f"Total starred: {total}")
    for s in stars[:5]:
        print(f"  {s['name_with_owner']}: {s['stars']} stars")
