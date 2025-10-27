# AppDev Onboarding Bot

An interactive **Slack onboarding bot** for Cornell AppDev that guides new members through setup, team intros, and repo onboarding.

## Features
- **Smart Conversation Flow:** Natural language extraction of app, team, and experience level
- **Technical Onboarding:** Step-by-step setup guides for Android, iOS, Backend, and Frontend teams
- **Experience-Aware:** Tailored instructions for beginners, intermediate, and experienced developers
- **GitHub Integration:** Automatic README fetching from Cornell AppDev repos
- **AI-Powered:** Gemini-based summarization and follow-up question handling
- **Caching:** Smart caching for faster responses and reduced API calls
- **Built with:** FastAPI + Slack Bolt for Python + Google Gemini AI

## Tech Stack
- **Backend:** FastAPI, Uvicorn  
- **Slack SDK:** Bolt for Python  
- **AI:** Google Gemini 2.5 Flash
- **GitHub:** REST API for README fetching
- **Local Tunnel:** ngrok  
- **Env Mgmt:** python-dotenv  

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
GEMINI_API_KEY=your-gemini-api-key
GITHUB_TOKEN=your-github-token  # Optional, for higher API rate limits
```

## Run locally
```bash
# Start the FastAPI server
uvicorn main:api --reload --port 3000

# In another terminal, start ngrok
ngrok http 3000

# Update your Slack app's Event Subscriptions URL to:
# https://your-ngrok-url.ngrok.io/slack/events
```

## Usage

### Quick Onboarding
Users can provide all information at once:
```
"onboard me to Resell Backend as a new developer"
"help me start with Eatery iOS, I'm experienced"
```

### Step-by-Step Onboarding
Or follow the guided conversation:
```
User: onboard me
Bot: Which AppDev project are you joining?

User: Resell
Bot: Which team are you on? (Android, iOS, Backend, Frontend, Design, Marketing)

User: Backend
Bot: Are you new to Backend development, or do you have experience?

User: I'm new
Bot: [Delivers personalized setup guide]
```

### Follow-up Questions
After onboarding, ask questions about the codebase:
```
"What environment variables do I need?"
"How do I run the server?"
"Where's the Figma link?"
```

See [CONVERSATION_FLOW.md](./CONVERSATION_FLOW.md) for detailed conversation examples.

## Project Structure
```
├── main.py                  # FastAPI + Slack Bolt integration
├── github_utils.py          # GitHub README fetching with caching
├── summarize_repo.py        # Gemini-powered summarization
├── conversation.py          # (Optional) Advanced conversation planner
├── summaries_cache.json     # Cached AI summaries
├── repo_cache.json          # Cached repo mappings
└── CONVERSATION_FLOW.md     # Detailed conversation flow documentation
```