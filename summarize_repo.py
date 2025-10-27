import os
import google.generativeai as genai
from dotenv import load_dotenv
from github_utils import fetch_readme
import json
import re

CACHE_FILE = "summaries_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-flash")

FIGMA_LINK = "https://www.figma.com/files/team/642125268638133075/all-projects?fuid=1419832257768926711"

def clean_markdown_artifacts(text: str) -> str:
    """Clean up markdown formatting for Slack compatibility and improve readability."""
    code_blocks = []
    def save_code(match):
        code_blocks.append(match.group(0))
        return f"___CODE_BLOCK_{len(code_blocks)-1}___"
    
    text = re.sub(r'`[^`]+`', save_code, text)
    text = re.sub(r'\*\*([^\*]+?)\*\*', r'*\1*', text)
    text = re.sub(r'\*\*\s+', ' ', text)
    text = re.sub(r'\s+\*\*', ' ', text)
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'([^\n])\n(\*[📱🛠️🔑▶️📚🎨🔗👥])', r'\1\n\n\2', text)
    text = re.sub(r'(\*[📱🛠️🔑▶️📚🎨🔗👥][^\n]+\*)\n([^\n])', r'\1\n\n\2', text)
    text = re.sub(r'([^\n])\n(\d+\.)', r'\1\n\n\2', text)
    text = re.sub(r'(\d+\.[^\n]+)\n([^\d\n•])', r'\1\n\n\2', text)
    text = re.sub(r'([^\n•])\n(•)', r'\1\n\n\2', text)
    text = re.sub(r'(•[^\n]+)\n([^\n•\d])', r'\1\n\n\2', text)
    text = re.sub(r'([^\n`])\n(`[^`]+`)\n', r'\1\n\n\2\n\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    for i, code in enumerate(code_blocks):
        text = text.replace(f"___CODE_BLOCK_{i}___", code)
    
    return text.strip()

def summarize_repo(repo_name: str, role: str, experience: str = "beginner") -> str:
    cache = load_cache()
    cache_key = f"{repo_name}-{role}-{experience}"
    if cache_key in cache:
        return cache[cache_key]

    readme = fetch_readme(repo_name, role)
    role_lower = role.lower()

    if any(x in role_lower for x in ["backend", "android", "ios", "frontend"]):
        if experience == "beginner":
            experience_context = "This is their first time with {role} development, so be extra clear and include prerequisites."
        elif experience == "intermediate":
            experience_context = "They have some {role} experience, so focus on project-specific setup."
        else:
            experience_context = "They are experienced with {role}, so be concise and focus on unique project requirements."
        
        prompt = f"""
You are an onboarding assistant for Cornell AppDev.
The user is joining the {repo_name} project as a {role} developer ({experience} level).
{experience_context.format(role=role)}

Create a clear, step-by-step technical onboarding guide from the README.

IMPORTANT FORMATTING RULES:
- Use *text* for bold (single asterisks, not double)
- Use `code` for commands and file names (backticks)
- Use simple bullet points with •
- Keep formatting minimal and clean

Format your response as follows:

*📱 About {repo_name.title()}*
[1-2 sentence description of what the app does]

*🛠️ Setup Instructions*
1. [First step with specific commands in `backticks`]
2. [Second step...]
3. [Continue with all setup steps]

*🔑 Required Configuration*
• [List any API keys, environment variables, or credentials needed]
• [Be specific about where to get them or who to ask]

*▶️ Running the Project*
• [Command to start the development server/build in `backticks`]
• [Where to view the running app]

*📚 Key Resources*
• [Link to documentation if mentioned]
• [Any important files or directories to know about]

Be specific with commands (e.g., `npm install`, `pod install`, `python manage.py runserver`).
If the README mentions dependencies, list them clearly.
If setup steps are unclear in the README, note what information is missing.

README:
{readme}
"""
    else:
        prompt = f"""
You are an onboarding assistant for Cornell AppDev.
The user is joining the {repo_name} project as a {role} member ({experience} level).

Create a friendly onboarding message that includes:

IMPORTANT FORMATTING RULES:
- Use *text* for bold (single asterisks, not double)
- Use simple bullet points with •
- Keep formatting minimal and clean

*📱 About {repo_name.title()}*
[Brief description of what the app does and its purpose]

*🎨 Your Role as {role.title()}*
[How {role} contributes to this project]
[What they'll typically work on]

*🔗 Design Resources*
Figma: {FIGMA_LINK}

*👥 Getting Started*
• [Any setup or access they need]
• [Who to reach out to on the team]
• [First steps they should take]

Keep it warm, welcoming, and actionable.

README:
{readme}
"""
    try:
        response = model.generate_content(prompt)
        summary = response.text.strip()
        summary = clean_markdown_artifacts(summary)
        cache[cache_key] = summary
        save_cache(cache)
        return summary
    except Exception as e:
        return f"Error summarizing repo: {e}"

def answer_followup(user_query: str, repo_name: str, role: str, readme: str) -> str:
    """Handles follow-up questions using repo context."""
    
    prompt = f"""
You are Cornell AppDev's onboarding assistant helping a {role} member on the {repo_name} project.
Answer their question conversationally and concisely using the README context.

Guidelines:
- For technical questions, provide specific commands, file paths, or configuration details
- If the answer isn't in the README, acknowledge that and suggest who they should ask (e.g., "Check with your team lead")
- Keep responses focused and actionable
- Use code formatting for commands (e.g., `npm install`)

Special responses:
- If they ask for Figma/design: Share {FIGMA_LINK}
- If they ask about dependencies: List them clearly from the README
- If they ask about environment variables: Specify which ones and where to get them
- If they're stuck on setup: Break down the problematic step

User's question:
{user_query}

README context:
{readme}
"""
    try:
        response = model.generate_content(prompt)
        answer = response.text.strip()
        answer = clean_markdown_artifacts(answer)
        return answer
    except Exception as e:
        return f"⚠️ Error answering your question: {e}\nTry rephrasing or reach out to your team lead."
