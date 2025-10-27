from github import Github
import os
from dotenv import load_dotenv

load_dotenv()
gh = Github(os.getenv("GITHUB_TOKEN"))

user = gh.get_user()
print("✅ Authenticated as:", user.login)
