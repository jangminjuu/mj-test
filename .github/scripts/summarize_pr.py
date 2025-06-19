# .github/scripts/summarize_pr.py

import os
import google.generativeai as genai
from github import Github

def get_commit_messages(repo, branch_name):
    branch = repo.get_branch(branch_name)
    sha = branch.commit.sha
    commit = repo.get_commit(sha)

    messages = []
    for c in repo.get_commits(sha=sha)[:5]:
        messages.append(f"- {c.commit.message.strip()}")
    return "\n".join(messages)

def summarize_with_gemini(api_key, content):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    try:
        response = model.generate_content(
            f"You are an assistant summarizing GitHub commits for a PR description.\n\n"
            f"Commits and context:\n{content}\n\n"
            f"Generate a concise summary for a PR body in markdown with bullet points."
        )
        return response.text.strip()
    except Exception as e:
        print(f"AI Error: {e}")
        return "⚠️ Failed to generate summary."

def main():
    github_token = os.environ.get("GITHUB_TOKEN")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    repo_full_name = os.environ.get("REPO_FULL_NAME")
    branch_name = os.environ.get("BRANCH_NAME")  # new

    g = Github(github_token)
    repo = g.get_repo(repo_full_name)

    commit_messages = get_commit_messages(repo, branch_name)
    summary = summarize_with_gemini(gemini_api_key, commit_messages)

    # 요약만 출력 (stdout → GitHub Actions에서 사용)
    print(summary)

if __name__ == "__main__":
    main()
