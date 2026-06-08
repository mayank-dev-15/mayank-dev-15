from github_api import graphql_query, save_json

QUERY = """
query($login: String!) {
  user(login: $login) {
    name
    login
    bio
    location
    avatarUrl
    websiteUrl
    email
    twitterUsername
    createdAt
    updatedAt
    isHireable
    status { emoji message }
    pinnedItems(first: 6, types: REPOSITORY) {
      nodes {
        ... on Repository {
          name
          url
          description
          primaryLanguage { name color }
          stargazerCount
          forkCount
        }
      }
    }
  }
}
"""


def fetch_profile(login="mayank-dev-15"):
    result = graphql_query(QUERY, {"login": login})
    user = result.get("data", {}).get("user", {})
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
                "name": p["name"],
                "url": p["url"],
                "description": p.get("description", ""),
                "language": (p.get("primaryLanguage") or {}).get("name"),
                "stars": p.get("stargazerCount", 0),
                "forks": p.get("forkCount", 0),
            }
            for p in user.get("pinnedItems", {}).get("nodes", [])
        ],
    }
    save_json(profile, "profile.json")
    return profile


if __name__ == "__main__":
    p = fetch_profile()
    print(f"Profile: {p['name']} ({p['login']})")
    print(f"  Location: {p['location']}")
    print(f"  Pinned repos: {len(p['pinned_repos'])}")
