import os
import google.generativeai as genai # type: ignore
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
        # PR의 코드 변경 내용(diff)을 가져와 요약에 포함합니다.
        diff_content = pull_request.get_patch()
        if diff_content:
            content_to_summarize += "\n--- Code Changes (Diff) ---\n"
            content_to_summarize += diff_content
        else:
            content_to_summarize += "\nNo code changes (diff) found for this PR.\n"
    except Exception as e:
        # diff 가져오는 도중 오류 발생 시 로그 출력
        print(f"Error fetching PR diff: {e}")
        content_to_summarize += "\nError fetching code changes (diff).\n"
        
    return content_to_summarize

def summarize_with_gemini(api_key, text_to_summarize):
    genai.configure(api_key=api_key)
    # Gemini Pro 모델 사용
    # 만약 긴 텍스트 처리에 문제가 있다면 'gemini-1.5-pro'와 같은 더 큰 컨텍스트 모델 고려 (비용 증가)
    model = genai.GenerativeModel('gemini-pro') 

    try:
        response = model.generate_content(
            f"You are a helpful assistant that summarizes GitHub Pull Request changes.\n"
            f"Summarize the following pull request details concisely, highlighting the main changes, purpose, and potential impact.\n"
            f"Provide the summary in a clear and easy-to-read markdown format with bullet points if applicable.\n\n"
            f"Pull Request Details:\n{text_to_summarize}\n\n"
            f"Concise Summary:"
        )
        return response.text.strip() 
    except Exception as e:
        print(f"Error summarizing with Gemini: {e}")
        # 오류 발생 시 오류 메시지 반환
        return f"Failed to generate summary due to an AI error: {e}"

def main():
    # GitHub Actions 환경 변수 가져오기
    github_token = os.environ.get("GITHUB_TOKEN")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    pr_number = int(os.environ.get("PR_NUMBER"))
    repo_owner = os.environ.get("REPO_OWNER")
    repo_name = os.environ.get("REPO_NAME")

    # 필수 환경 변수 확인
    if not github_token:
        print("GITHUB_TOKEN environment variable not set. Exiting.")
        exit(1)
    if not gemini_api_key:
        print("GEMINI_API_KEY environment variable not set. Please add it to GitHub Secrets. Exiting.")
        exit(1)

    # PyGithub 초기화
    g = Github(github_token)
    repo = g.get_user(repo_owner).get_repo(repo_name)
    pull_request = repo.get_pull(pr_number) # PR 객체 가져오기

    # 기존 PR 본문 저장 (AI 요약 아래에 표시하기 위함)
    original_pr_body = pull_request.body or ""
    # 자동 생성 PR의 경우 본문에 특정 표식이 있을 수 있으므로 필터링 (선택 사항)
    # 예: if "이 Pull Request는 AI 요약 기능을 테스트하기 위해" in original_pr_body:
    #         original_pr_body = "" # 이런 경우 기존 본문은 무시

    # PR 상세 정보 가져와 요약 준비
    pr_details_for_summary = get_pr_details_for_summary(repo, pr_number)

    # Gemini 모델의 토큰 제한 고려 (대략적인 바이트 길이로 제한)
    MAX_BYTES_FOR_GEMINI_PRO = 30000 * 4 # 대략 30k 토큰 * 4바이트/토큰
    if len(pr_details_for_summary.encode('utf-8')) > MAX_BYTES_FOR_GEMINI_PRO:
        print(f"PR details too long ({len(pr_details_for_summary.encode('utf-8'))} bytes), truncating for summary.")
        # 너무 길면 잘라내고, 잘라냈다는 표시 추가
        pr_details_for_summary = pr_details_for_summary[:MAX_BYTES_FOR_GEMINI_PRO // 2] + "\n... (트랜케이트됨 - 내용이 너무 길어 잘렸습니다)"
    
    # Gemini로 요약 생성
    ai_generated_summary = summarize_with_gemini(gemini_api_key, pr_details_for_summary)

    # PR 본문을 업데이트할 내용 구성
    updated_pr_body = f"## ✨ AI 생성 Pull Request 요약 ✨\n\n"
    updated_pr_body += f"{ai_generated_summary}\n\n"
    updated_pr_body += f"---\n"
    updated_pr_body += f"*이 요약은 Google Gemini를 사용하는 AI 비서에 의해 자동으로 생성되어 PR 본문을 업데이트했습니다.*\n\n"
    
    if original_pr_body.strip(): # 기존 본문이 비어있지 않다면 추가
        updated_pr_body += f"## 📝 기존 Pull Request 본문\n\n"
        updated_pr_body += original_pr_body

    # GitHub API를 통해 PR 본문 업데이트 시도
    try:
        pull_request.edit(body=updated_pr_body)
        print(f"✅ AI 요약으로 PR #{pr_number}의 본문을 성공적으로 업데이트했습니다.")
    except Exception as e:
        print(f"❌ AI 요약으로 PR #{pr_number} 본문 업데이트 실패: {e}")
        # 본문 업데이트 실패 시, 대신 댓글로 요약을 게시
        comment_body_on_failure = f"## ⚠️ AI 생성 Pull Request 요약 (본문 업데이트 실패)\n\n"
        comment_body_on_failure += f"{ai_generated_summary}\n\n"
        comment_body_on_failure += f"---\n*이 요약은 본문 업데이트에 실패하여 댓글로 게시되었습니다.*\n"
        pull_request.create_issue_comment(comment_body_on_failure)
        print(f"⚠️ AI 요약이 PR #{pr_number}에 댓글로 대신 게시되었습니다.")

if __name__ == "__main__":
    main()