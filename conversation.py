import google.generativeai as genai
from summarize_repo import summarize_repo

def conversation_planner(user_message: str, state: dict, model) -> tuple[str, dict]:
    """Dynamically plan next response using Gemini."""
    app = state.get("app")
    team = state.get("team")
    level = state.get("level")
    phase = state.get("phase", "overview")

    history = state.get("history", [])
    history_text = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in history[-5:]])

    prompt = f"""
You are Cornell AppDev’s friendly onboarding assistant living in Slack.
You help new members onboard conversationally — one message at a time.

Your memory of the conversation so far:
{history_text}

The user just said:
"{user_message}"

You know this context:
- app: {app}
- team: {team}
- level: {level}
- phase: {phase}

Your goals:
1. Figure out what information the user has already given (app, team, experience level, etc.).
2. Decide the next best conversational step naturally.
3. If enough info is known, generate an appropriate summary or setup help
   by clearly instructing the system to call summarize_repo(app, team, phase, level).
4. Always respond warmly, casually, and in 1–3 sentences.
5. Ask questions only when context is missing.

If the user mentions a valid Cornell AppDev app name (like Resell, Uplift, Eatery, etc.), 
immediately acknowledge and move to the next logical onboarding step 
(e.g., asking for their subteam or level) instead of re-confirming.


Return your reasoning and desired action in this JSON format:
{{
  "response": "text you want the bot to say",
  "updates": {{
     "app": "...",
     "team": "...",
     "level": "...",
     "phase": "...",
     "action": "summarize" | "setup" | "contribution" | "none"
  }}
}}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        import json
        parsed = json.loads(text[text.find("{"):text.rfind("}") + 1])
        reply = parsed.get("response", "")
        updates = parsed.get("updates", {})
        for k, v in updates.items():
            if v:
                state[k] = v
        history.append({"user": user_message, "bot": reply})
        state["history"] = history
        action = updates.get("action", "none")
        if action in ["summarize", "setup", "contribution"] and state.get("app") and state.get("team"):
            summary = summarize_repo(
                state["app"], state["team"], phase=action if action != "summarize" else "overview"
            )
            reply += f"\n\n{summary}"
        
        action = updates.get("action", "none")
        if action in ["summarize", "setup", "contribution"] and state.get("app") and state.get("team"):
            summary = summarize_repo(
                state["app"], state["team"], phase=action if action != "summarize" else "overview"
            )
            reply += f"\n\n{summary}"

        elif state.get("app") and not state.get("team"):
            if not any(word in reply.lower() for word in ["subteam", "team"]):
                reply += "\n\nWhich subteam are you joining for this project? (e.g., Android, iOS, Backend, Design, Marketing)"
            state["phase"] = "setup"

        elif state.get("app") and state.get("team") and not state.get("level"):
            if not any(word in reply.lower() for word in ["experience", "new member", "returning", "newbie", "level"]):
                reply += "\n\nGot it! Are you a new member or a returning one?"
            state["phase"] = "experience"

        elif state.get("app") and state.get("team") and state.get("level"):
            if not any(word in reply.lower() for word in ["welcome", "summary", "overview", "project", "team", "get started", "appdev"]):
                reply += "\n\nAwesome — let me summarize everything for you! 🚀"
                summary = summarize_repo(state["app"], state["team"], "overview")
                reply += f"\n\n{summary}"
            state["phase"] = "done"

        return reply, state

    except Exception as e:
        return f"⚠️ Error understanding the conversation: {e}", state
