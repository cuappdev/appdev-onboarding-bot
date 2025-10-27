from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()

bolt_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

@bolt_app.event("message")
def handle_message_events(body, say):
    user = body["event"].get("user")
    text = body["event"].get("text")
    print(f"💬 Message from {user}: {text}")
    say(f"Hey <@{user}>! 👋 You said: '{text}' — I’m here to help onboard you.")


app = FastAPI()
handler = SlackRequestHandler(bolt_app)

@app.post("/slack/events")
async def slack_events(request: Request):
    body = await request.json()

    if body.get("type") == "url_verification":
        challenge = body.get("challenge")
        return JSONResponse(content={"challenge": challenge})

    return await handler.handle(request)
