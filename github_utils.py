from github import Github
import os
from dotenv import load_dotenv
import json

load_dotenv()
g = Github(os.getenv("GITHUB_TOKEN"))

def fetch_readme(repo_name: str) -> str:
    repo = g.get_repo(repo_name)
    try:
        readme = repo.get_readme()
        return readme.decoded_content.decode("utf-8")
    except Exception:
        return "README not found for this repository."

def build_apps_json():
    """Automatically builds a dictionary of all AppDev repos grouped by app and subteam."""
    org = g.get_organization("cuappdev")
    repos = org.get_repos()
    apps = {}

    for repo in repos:
        name = repo.name.lower()
        # only process repos with dash, like resell-backend
        if "-" in name:
            app_name, subteam = name.split("-", 1)
            if app_name not in apps:
                apps[app_name] = {"name": app_name.capitalize(), "repos": {}}
            apps[app_name]["repos"][subteam] = name
    return apps

def cache_apps_to_file(path="apps.json"):
    apps = build_apps_json()
    with open(path, "w") as f:
        json.dump(apps, f, indent=2)
    print(f"✅ Cached {len(apps)} apps to {path}")
