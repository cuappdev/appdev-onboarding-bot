from github import Github
import os
from dotenv import load_dotenv

load_dotenv()
g = Github(os.getenv("GITHUB_TOKEN"))

def fetch_readme(repo_name: str) -> str:
    repo = g.get_repo(repo_name)
    try:
        readme = repo.get_readme()
        return readme.decoded_content.decode("utf-8")
    except Exception:
        return "README not found for this repository."
