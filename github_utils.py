import requests, os, base64, json

REPO_CACHE_FILE = "repo_cache.json"

def load_repo_cache():
    if os.path.exists(REPO_CACHE_FILE):
        with open(REPO_CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_repo_cache(cache):
    with open(REPO_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def fetch_readme(repo_name: str, team: str = None) -> str:
    """Attempts to fetch README.md from Cornell AppDev repos, with caching."""
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"token {github_token}"} if github_token else {}
    cache_key = f"{repo_name}-{team}" if team else repo_name
    
    cache = load_repo_cache()
    if cache_key in cache:
        cached_repo = cache[cache_key]
        print(f"🧠 Using cached repo: {cached_repo}")
        repo_url = f"https://api.github.com/repos/{cached_repo}/readme"
        response = requests.get(repo_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")

    possible_repos = []
    
    if team:
        team_lower = team.lower()
        if team_lower in ["backend", "ios", "android", "frontend"]:
            possible_repos.append(f"cuappdev/{repo_name}-{team_lower}")
        possible_repos.append(f"cuappdev/{repo_name}")
    else:
        possible_repos = [
            f"cuappdev/{repo_name}",
            f"cuappdev/{repo_name}-backend",
            f"cuappdev/{repo_name}-ios",
            f"cuappdev/{repo_name}-android",
            f"cuappdev/{repo_name}-frontend",
        ]

    for repo in possible_repos:
        repo_url = f"https://api.github.com/repos/{repo}/readme"
        response = requests.get(repo_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
            print(f"✅ Successfully fetched README from {repo}")
            cache[cache_key] = repo
            save_repo_cache(cache)
            return content

    print(f"❌ Error: None of these repos had a README for {repo_name} ({team})")
    return f"README not found for {repo_name} {team or ''}. Tried: {', '.join(possible_repos)}"
