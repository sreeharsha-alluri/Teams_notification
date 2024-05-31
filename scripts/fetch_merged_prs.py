import os
import subprocess
import re
from github import Github
from github.Repository import Repository

def get_pull_title(pull_id: int, repo: Repository) -> str:
    pr = repo.get_pull(pull_id)
    pr_url = pr.html_url
    return f"<a href=\"{pr_url}\">PR #{pr.number}</a> {pr.title} by {pr.user.login}"

def check_pr_titles(repo: Repository, src_branch: str, dest_branch: str, regex: str) -> list:
    # Run git log command to find merged PRs
    gitlog = subprocess.check_output(
        [
            "git",
            "log",
            f"origin/{dest_branch}..origin/{src_branch}",
            "--merges",
            "--pretty=format:%s",
        ]
    ).decode()

    # Debug print
    print("Git log output:\n", gitlog)

    merge_pattern = re.compile(r"^Merge pull request #(\d+) from .*\$")

    merged_prs = []

    # Parse each line of the git log output
    for line in gitlog.split("\n"):
        print("Processing line:", line)  # Debug print
        merge_match = re.match(merge_pattern, line)
        if merge_match:
            pr_id = int(merge_match.group(1))
            title = get_pull_title(pr_id, repo)
            merged_prs.append(title)
        else:
            print("No match found for line:", line)  # Debug print

    return merged_prs

def main():
    github_personal_access_token = os.getenv("GITHUB_TOKEN")
    if not github_personal_access_token:
        raise ValueError("GitHub token not found")

    github_object = Github(github_personal_access_token)
    repo = github_object.get_repo("nikhilkamuni/Teams_notification")
    merged_prs = check_pr_titles(repo, "nightly_success", "main", ".*")

    if merged_prs:
        print("\n".join(merged_prs))
    else:
        print("No merged PRs found.")

if __name__ == "__main__":
    main()
