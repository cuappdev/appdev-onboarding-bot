from slack_bolt import App
from fastapi import FastAPI, Request
from slack_bolt.adapter.fastapi import SlackRequestHandler
from dotenv import load_dotenv
from summarize_repo import summarize_repo, answer_followup
from github_utils import fetch_readme
import os
import re

load_dotenv()

slack_app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)
api = FastAPI()
handler = SlackRequestHandler(slack_app)

# App and team configurations
user_states = {}
ALLOWED_APPS = ["eatery", "resell", "uplift", "score", "navi", "hustle",
                "coursegrab", "volume", "scooped", "all-in"]
ALLOWED_TEAMS = ["android", "ios", "backend", "frontend", "design", "marketing"]
TECH_TEAMS = ["android", "ios", "backend", "frontend"]
EXPERIENCE_MAP = {
    "new": "beginner",
    "newbie": "beginner",
    "beginner": "beginner",
    "first time": "beginner",
    "first-time": "beginner",
    "no experience": "beginner",
    "never done": "beginner",
    "returning": "intermediate",
    "intermediate": "intermediate",
    "some experience": "intermediate",
    "have experience": "experienced",
    "experienced": "experienced",
    "advanced": "experienced",
    "veteran": "experienced",
    "expert": "experienced",
}

user_states = {}

def extract_app(text: str) -> str | None:
    """Extract app name from user message with fuzzy matching."""
    text_lower = text.lower()
    for app in ALLOWED_APPS:
        if app in text_lower:
            return app
    return None


def extract_team(text: str) -> str | None:
    """Extract team name from user message."""
    text_lower = text.lower()
    for team in ALLOWED_TEAMS:
        if team in text_lower:
            return team
    if "back-end" in text_lower or "back end" in text_lower:
        return "backend"
    if "front-end" in text_lower or "front end" in text_lower:
        return "frontend"
    return None


def extract_experience(text: str) -> str | None:
    """Extract experience level from user message."""
    text_lower = text.lower()
    for keyword, level in EXPERIENCE_MAP.items():
        if keyword in text_lower:
            return level
    return None


def is_tech_team(team: str) -> bool:
    return team in TECH_TEAMS

@slack_app.event("message")
def handle_message(event, say):
    user_id = event.get("user")
    text = event.get("text", "").strip()
    if not user_id or "bot_id" in event:
        return

    state = user_states.get(user_id, {})
    text_lower = text.lower()
    found_app = extract_app(text)
    found_team = extract_team(text)
    found_experience = extract_experience(text)
    if "onboard" in text_lower or "help me start" in text_lower or "get started" in text_lower:
        if found_app and found_team and found_experience:
            state.update({
                "app": found_app,
                "team": found_team,
                "experience": found_experience,
                "phase": "confirm"
            })
            user_states[user_id] = state
            say(f"Perfect! Onboarding you to *{found_app.title()} {found_team.title()}* as a *{found_experience}* member.")
            _deliver_onboarding(user_id, state, say)
            return
            
        elif found_app and found_team:
            state.update({"app": found_app, "team": found_team, "phase": "ask_experience"})
            user_states[user_id] = state
            
            if is_tech_team(found_team):
                say(f"Got it — onboarding you to *{found_app.title()} {found_team.title()}*! "
                    f"Are you new to {found_team.title()} development, or do you have experience?")
            else:
                say(f"Got it — onboarding you to *{found_app.title()} {found_team.title()}*! "
                    "Are you a new member or returning member?")
            return
            
        elif found_app:
            state.update({"app": found_app, "phase": "ask_team"})
            user_states[user_id] = state
            say(f"Awesome! Onboarding you to *{found_app.title()}*. Which team are you joining?\n"
                "• *Android* | *iOS* | *Backend* | *Frontend* (dev teams)\n"
                "• *Design* | *Marketing* (non-dev teams)")
            return
        elif found_team:
            state.update({"team": found_team, "phase": "ask_app"})
            user_states[user_id] = state
            say(f"Great! You're joining the *{found_team.title()}* team. Which AppDev project?\n"
                "_(Examples: Eatery, Resell, Uplift, Volume, Coursegrab)_")
            return
        else:
            state.update({"phase": "ask_app"})
            user_states[user_id] = state
            say("Hey there! 👋 Which AppDev project are you joining?\n"
                "_(Examples: Eatery, Resell, Uplift, Volume, Coursegrab)_")
            return
    if state.get("phase") == "ask_app":
        if found_app:
            if state.get("team"):
                state.update({"app": found_app, "phase": "ask_experience"})
                user_states[user_id] = state
                team = state["team"]
                if is_tech_team(team):
                    say(f"Perfect! *{found_app.title()} {team.title()}*. Are you new to {team.title()} development, "
                        "or do you have prior experience?")
                else:
                    say(f"Perfect! *{found_app.title()} {team.title()}*. Are you a new member or returning member?")
                return
            else:
                state.update({"app": found_app, "phase": "ask_team"})
                user_states[user_id] = state
                say(f"Great! *{found_app.title()}* it is. Which team are you on?\n"
                    "• *Android* | *iOS* | *Backend* | *Frontend* (dev teams)\n"
                    "• *Design* | *Marketing* (non-dev teams)")
                return
        else:
            say("I didn't catch that. Can you tell me which app? (e.g., Eatery, Resell, Uplift)")
            return
    if state.get("phase") == "ask_team":
        if found_team:
            state.update({"team": found_team, "phase": "ask_experience"})
            user_states[user_id] = state
            
            if is_tech_team(found_team):
                say(f"Perfect! *{found_team.title()}* team. Are you new to {found_team.title()} development, "
                    "or do you have prior experience?")
            else:
                say(f"Perfect! *{found_team.title()}* team. Are you a new member or returning member?")
            return
        else:
            say("I didn't catch that. Which team? (Android, iOS, Backend, Frontend, Design, or Marketing)")
            return
    if state.get("phase") == "ask_experience":
        if found_experience:
            state.update({"experience": found_experience, "phase": "onboarded"})
            user_states[user_id] = state
            
            app = state["app"]
            team = state["team"]
            say(f"Awesome! Getting your *{app.title()} {team.title()}* onboarding guide ready... 🚀")
            _deliver_onboarding(user_id, state, say)
            return
        else:
            say("Just to clarify — are you new to this, or do you have experience? "
                "(You can say: new, returning, experienced, etc.)")
            return
    if state.get("phase") == "onboarded" and state.get("readme"):
        reply = answer_followup(text, state["app"], state["team"], state["readme"])
        say(reply)
        return
    if not state or state.get("phase") is None:
        if found_app and found_team:
            state.update({"app": found_app, "team": found_team, "phase": "ask_experience"})
            user_states[user_id] = state
            
            if is_tech_team(found_team):
                say(f"Got it — onboarding you to *{found_app.title()} {found_team.title()}*! "
                    f"Are you new to {found_team.title()} development, or do you have experience?")
            else:
                say(f"Got it — onboarding you to *{found_app.title()} {found_team.title()}*! "
                    "Are you a new member or returning member?")
            return
        
        say("Hi! 👋 I'm the AppDev onboarding bot. Say *'onboard me'* to get started, "
            "or tell me which project and team you're joining (e.g., 'Resell Backend').")
        return

def _deliver_onboarding(user_id: str, state: dict, say):
    """Helper function to fetch and deliver onboarding materials."""
    app = state["app"]
    team = state["team"]
    experience = state["experience"]
    
    try:
        readme = fetch_readme(app, team)
        summary = summarize_repo(app, team, experience)
        
        state.update({"phase": "onboarded", "readme": readme})
        user_states[user_id] = state
        
        say(summary)
        if is_tech_team(team):
            say("\n💡 *Next steps:*\n"
                "• Ask me any questions about setup or the codebase\n"
                "• Request the Figma link if you need design references\n"
                "• Let me know if you need help with specific commands or dependencies")
    except Exception as e:
        say(f"⚠️ Sorry, I ran into an issue fetching the onboarding materials: {e}\n"
            "Please try again or reach out to your team lead.")


@api.post("/slack/events")
async def slack_events(request: Request):
    return await handler.handle(request)

@slack_app.event("app_home_opened")
def handle_app_home_opened_events(body, logger):
    logger.info("🪄 Ignored app_home_opened event")
