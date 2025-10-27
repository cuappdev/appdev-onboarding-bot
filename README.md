# AppDev Onboarding Bot

An interactive **Slack onboarding bot** for Cornell AppDev that guides new members through setup, team intros, and repo onboarding.

## Features
- Built with **FastAPI** + **Slack Bolt for Python**
- Supports **DMs** with real replies
- Runs locally using **ngrok** for public Slack event URLs
- Verified Slack app with active App Home + bot presence
- Upcoming: **GitHub integration** (PyGithub) and **LLM summaries** for technical onboarding

## Tech Stack
- **Backend:** FastAPI, Uvicorn  
- **Slack SDK:** Bolt for Python  
- **Local Tunnel:** ngrok  
- **Env Mgmt:** python-dotenv  
- **Planned:** PyGithub + OpenAI API  

## Setup
```bash
git clone https://github.com/<your-username>/appdev-onboarding-bot.git
cd appdev-onboarding-bot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Create .env
```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
```

## Run locally
```bash
uvicorn main:app --reload --port 3000
ngrok http 3000
```