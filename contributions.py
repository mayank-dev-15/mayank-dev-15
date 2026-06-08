from github_api import graphql_query, save_json

CONTRIBUTION_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            color
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
    issues(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
      totalCount
    }
    pullRequests(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
      totalCount
    }
    repositories(first: 0) {
      totalCount
    }
  }
}
"""

# Contribution years query for multi-year data
YEARS_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
      }
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalRepositoryContributions
    }
  }
}
"""


def fetch_contributions(login="mayank-dev-15"):
    result = graphql_query(CONTRIBUTION_QUERY, {"login": login})
    user = result.get("data", {}).get("user", {})
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
        "total_repos": user.get("repositories", {}).get("totalCount", 0),
        "calendar": cal,
    }

    save_json(contributions, "contributions.json")
    return contributions


if __name__ == "__main__":
    c = fetch_contributions()
    print(f"Total contributions: {c['total_contributions']}")
    print(f"  Commits: {c['commits']}")
    print(f"  Issues: {c['issues']}")
    print(f"  PRs: {c['pull_requests']}")
    print(f"  PR reviews: {c['pr_reviews']}")
