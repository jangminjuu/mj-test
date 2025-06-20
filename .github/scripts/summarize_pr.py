import os
import google.generativeai as genai
from github import Github

def get_pr_details_for_summary(repo, pr_number):
    pull_request = repo.get_pull(pr_number)
    content_to_summarize = f"PR Title: {pull_request.title}\n"
    content_to_summarize += f"PR Body: {pull_request.body or 'No description provided.'}\n\n"
    content_to_summarize += "Recent Commits:\n"
    for i, commit in enumerate(pull_request.get_commits()):
        if i >= 5:
            break
        content_to_summarize += f"- {commit.commit.message}\n"

    try:
        diff_content = pull_request.get_patch()
        if diff_content:
            content_to_summarize += "\n--- Code Changes (Diff) ---\n"
            content_to_summarize += diff_content
        else:
            content_to_summarize += "\nNo code changes (diff) found for this PR.\n"
    except Exception as e:
        print(f"Error fetching PR diff: {e}")
        content_to_summarize += "\nError fetching code changes (diff).\n"

    return content_to_summarize

def summarize_with_gemini(api_key, text_to_summarize):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro') 

    try:
        response = model.generate_content(
            f"You are a helpful assistant that summarizes GitHub Pull Request changes.\n"
            f"Summarize the following pull request details concisely, highlighting the main changes, purpose and potential impact.\n"
            f"Provide the summary in a clear and easy-to-read markdown format with bullet points if applicable.\n\n"
            f"Pull Request Details:\n{text_to_summarize}\n\n"
            f"Concise Summary:"
        )
        return response.text.strip() 
    except Exception as e:
        print(f"Error summarizing with Gemini: {e}")
        return f"Failed to generate summary due to an AI error: {e}"

def main():
    github_token = os.environ.get("GITHUB_TOKEN")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    pr_number = int(os.environ.get("PR_NUMBER"))
    repo_owner = os.environ.get("REPO_OWNER")
    repo_name = os.environ.get("REPO_NAME")

    if not github_token:
        print("GITHUB_TOKEN environment variable not set. Exiting.")
        exit(1)
    if not gemini_api_key:
        print("GEMINI_API_KEY environment variable not set. Please add it to GitHub Secrets. Exiting.")
        exit(1)

    g = Github(github_token)
    repo = g.get_user(repo_owner).get_repo(repo_name)
    pull_request = repo.get_pull(pr_number)

    original_pr_body = pull_request.body or ""
    pr_details_for_summary = get_pr_details_for_summary(repo, pr_number)

    MAX_BYTES_FOR_GEMINI_PRO = 30000 * 4 # 30k token context window
    if len(pr_details_for_summary.encode('utf-8')) > MAX_BYTES_FOR_GEMINI_PRO:
        print(f"PR details too long ({len(pr_details_for_summary.encode('utf-8'))} bytes), truncating for summary.")
        pr_details_for_summary = pr_details_for_summary[:MAX_BYTES_FOR_GEMINI_PRO // 2] + "\n... (truncated - content too long)"

    ai_generated_summary = summarize_with_gemini(gemini_api_key, pr_details_for_summary)

    updated_pr_body = f"## ✨ AI 생성 Pull Request 요약 ✨\n\n"
    updated_pr_body += f"{ai_generated_summary}\n\n"
    updated_pr_body += f"---\n"
    updated_pr_body += f"*이 요약은 Google Gemini를 사용하는 AI 비서에 의해 자동으로 생성되어 PR 본문을 업데이트했습니다.*\n\n"

    if original_pr_body.strip():
        updated_pr_body += f"## 📝 기존 Pull Request 본문\n\n"
        updated_pr_body += original_pr_body

    try:
        pull_request.edit(body=updated_pr_body)
        print(f"✅ AI 요약으로 PR #{pr_number}의 본문을 성공적으로 업데이트했습니다.")
    except Exception as e:
        print(f"❌ AI 요약으로 PR #{pr_number} 본문 업데이트 실패: {e}")
        comment_body_on_failure = f"## ⚠️ AI 생성 Pull Request 요약 (본문 업데이트 실패)\n\n"
        comment_body_on_failure += f"{ai_generated_summary}\n\n"
        comment_body_on_failure += f"---\n*이 요약은 본문 업데이트에 실패하여 댓글로 게시되었습니다.*\n"
        pull_request.create_issue_comment(comment_body_on_failure)
        print(f"⚠️ AI 요약이 PR #{pr_number}에 댓글로 대신 게시되었습니다.")

if __name__ == "__main__":
    main()