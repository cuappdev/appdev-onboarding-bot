from slack_bolt import App
from fastapi import FastAPI, Request
from slack_bolt.adapter.fastapi import SlackRequestHandler
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

# --- Load environment variables ---
load_dotenv()

# --- Initialize Slack + FastAPI ---
app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)
api = FastAPI()
handler = SlackRequestHandler(app)

# --- Allowed AppDev apps for onboarding ---
allowed_apps = [
    "eatery", "resell", "uplift", "score", "navi",
    "hustle", "coursegrab", "volume", "scooped", "all-in"
]

# --- In-memory user state storage (temporary) ---
user_states = {}

# --- Slack event handlers ---
@app.event("app_mention")
def handle_app_mention(body, say):
    say("👋 Hi there! To get started, just type `onboard me`.")

@app.event("message")
def handle_message_events(event, say):
    user_id = event.get("user")
    text = event.get("text", "").strip().lower()

    if not user_id or "bot_id" in event:
        return

    state = user_states.get(user_id, {"step": None})

    if text in ["onboard me", "start onboarding"]:
        say(f"Welcome to Cornell AppDev! 🎉\n\nAvailable apps:\n{', '.join(allowed_apps)}\n\nWhich app would you like to onboard to?")
        user_states[user_id] = {"step": "choose_app"}
        return
    if state["step"] == "choose_app":
        if text in allowed_apps:
            state["app"] = text
            say(f"Cool — which subteam are you on? (Android, iOS, Backend, Design, Marketing)")
            state["step"] = "choose_team"
        else:
            say("Hmm, I didn’t recognize that app. Please pick from:\n" + ", ".join(allowed_apps))
        user_states[user_id] = state
        return
    if state["step"] == "choose_team":
        state["team"] = text
        app_name = state["app"]
        team = state["team"]
        say(f"Got it! You’re onboarding to *{app_name} ({team})*! 🚀")
        say(f"Fetching setup info for {app_name} {team} team...")
        state["step"] = "done"
        user_states[user_id] = state
        return
    if state["step"] == "done":
        say("🎉 You're all set! Type `onboard me` anytime to restart.")
        return

# --- FastAPI endpoint for Slack events ---
@api.post("/slack/events")
async def slack_events(request: Request):
    return await handler.handle(request)
