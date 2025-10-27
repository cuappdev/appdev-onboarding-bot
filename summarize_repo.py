import os
import google.generativeai as genai
from dotenv import load_dotenv
from github_utils import fetch_readme

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.5-flash")

def summarize_repo(repo_name: str, role: str) -> str:
    """Fetches the repo README and returns a Gemini summary tailored for a specific subteam."""
    readme = fetch_readme(repo_name)
    prompt = f"""
    You are an onboarding assistant for Cornell AppDev.
    Summarize this README for someone joining the {role} team.
    Emphasize setup steps, technologies used, key dependencies,
    and how to get started contributing.

    README:
    {readme}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error summarizing repo: {e}"
