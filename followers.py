from github_api import graphql_query, save_json

QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    followers(first: 100, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      totalCount
      nodes {
        login
        name
        avatarUrl
        url
        bio
        location
        repositories {
          totalCount
        }
      }
    }
    following(first: 100) {
      totalCount
    }
  }
}
"""


def fetch_followers(login="mayank-dev-15"):
    all_followers = []
    cursor = None
    total_followers = 0
    total_following = 0
    while True:
        variables = {"login": login, "cursor": cursor}
        result = graphql_query(QUERY, variables)
        user = result.get("data", {}).get("user", {})
        followers_data = user.get("followers", {})
        total_followers = followers_data.get("totalCount", 0)
        total_following = user.get("following", {}).get("totalCount", 0)
        nodes = followers_data.get("nodes", [])
        all_followers.extend(nodes)
        page_info = followers_data.get("pageInfo", {})
        if page_info.get("hasNextPage"):
            cursor = page_info["endCursor"]
        else:
            break

    followers = [
        {
            "login": f["login"],
            "name": f.get("name"),
            "avatar_url": f.get("avatarUrl"),
            "url": f.get("url"),
            "bio": f.get("bio", ""),
            "location": f.get("location", ""),
            "repos": f.get("repositories", {}).get("totalCount", 0),
        }
        for f in all_followers
    ]

    save_json({
        "total_followers": total_followers,
        "total_following": total_following,
        "followers": followers,
    }, "followers.json")
    return total_followers, total_following, followers


if __name__ == "__main__":
    followers_count, following_count, followers = fetch_followers()
    print(f"Followers: {followers_count} | Following: {following_count}")
    for f in followers[:5]:
        print(f"  @{f['login']} ({f['name']})")
