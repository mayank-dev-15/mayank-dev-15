import json, urllib.request, os

token = os.environ["GITHUB_TOKEN"]

def gql(query, variables=None):
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    headers = {
        "Authorization": f"bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
    }
    req = urllib.request.Request("https://api.github.com/graphql", data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

# Get total repo count
r = gql('query { user(login: "mayank-dev-15") { repositories(ownerAffiliations: OWNER) { totalCount } } }')
total = r["data"]["user"]["repositories"]["totalCount"]
print(f"Total repos: {total}")

# Get language count
r2 = gql("""
query {
  user(login: "mayank-dev-15") {
    repositories(first: 100, ownerAffiliations: OWNER) {
      nodes { languages(first: 1) { totalCount } }
    }
  }
}
""")
nodes = r2["data"]["user"]["repositories"]["nodes"]
# Count unique languages from first 100 repos - broader query
r3 = gql("""
query {
  user(login: "mayank-dev-15") {
    repositories(first: 100, orderBy: {field: PUSHED_AT, direction: DESC}, ownerAffiliations: OWNER) {
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { node { name } }
        }
      }
    }
  }
}
""")
langs = set()
for repo in r3["data"]["user"]["repositories"]["nodes"]:
    for edge in (repo.get("languages") or {}).get("edges", []):
        langs.add(edge["node"]["name"])
print(f"Languages (from recent 100): {len(langs)}")
print(f"Total repos: {total}")
