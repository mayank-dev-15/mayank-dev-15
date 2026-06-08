from github_api import graphql_query, save_json

LANGUAGES_QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node { name color }
          }
        }
      }
    }
  }
}
"""


def fetch_languages(login="mayank-dev-15"):
    lang_totals = {}
    repo_langs = {}
    cursor = None

    while True:
        variables = {"login": login, "cursor": cursor}
        result = graphql_query(LANGUAGES_QUERY, variables)
        user = result.get("data", {}).get("user", {})
        repo_data = user.get("repositories", {})
        nodes = repo_data.get("nodes", [])

        for repo in nodes:
            repo_name = repo["name"]
            repo_langs[repo_name] = []
            for edge in repo.get("languages", {}).get("edges", []):
                lang_name = edge["node"]["name"]
                size = edge["size"]
                color = edge["node"].get("color", "#000000")
                repo_langs[repo_name].append({"name": lang_name, "size": size, "color": color})
                lang_totals[lang_name] = lang_totals.get(lang_name, 0) + size

        page_info = repo_data.get("pageInfo", {})
        if page_info.get("hasNextPage"):
            cursor = page_info["endCursor"]
        else:
            break

    total_bytes = sum(lang_totals.values())
    languages = [
        {
            "name": name,
            "bytes": bytes_,
            "percentage": round(bytes_ / total_bytes * 100, 1) if total_bytes > 0 else 0,
            "color": "#000",
        }
        for name, bytes_ in sorted(lang_totals.items(), key=lambda x: -x[1])
    ]

    # Add colors from repo data
    color_map = {}
    for langs in repo_langs.values():
        for l in langs:
            if l["name"] not in color_map:
                color_map[l["name"]] = l["color"]
    for lang in languages:
        lang["color"] = color_map.get(lang["name"], "#000")

    save_json({
        "total_bytes": total_bytes,
        "languages": languages,
        "repo_languages": repo_langs,
    }, "languages.json")
    return languages


if __name__ == "__main__":
    langs = fetch_languages()
    print(f"Languages: {len(langs)}")
    for l in langs[:10]:
        print(f"  {l['name']}: {l['percentage']}%")
