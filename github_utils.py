from github import Github
import os
from dotenv import load_dotenv

load_dotenv()

g = Github(os.getenv("GITHUB_TOKEN"))

def fetch_readme(repo_name: str) -> str:
    """
    Fetches the README.md content from a Cornell AppDev repo.
    Example: fetch_readme("resell-backend")
    """
    try:
        repo_full_name = f"cuappdev/{repo_name}"
        repo = g.get_repo(repo_full_name)
        readme_file = repo.get_readme()
        return readme_file.decoded_content.decode("utf-8")
    except Exception as e:
        print(f"❌ Error fetching README for {repo_name}: {e}")
        return "No README found or could not fetch repository."
