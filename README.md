# AI-Powered News Aggregator & Auto-Tweeter

## Features
- Fetches news based on keywords
- Generates engaging tweets using AI
- Ready-to-use API endpoint

## Setup
1. Create `.env` file with your API keys
2. Install requirements: `pip install -r requirements.txt`
3. Run: `uvicorn main:app --reload`

## API Endpoints
- POST `/generate-and-post` - Generate tweet from news
- GET `/` - Health check

## Requirements
- Python 3.8+
- API keys for GNews, OpenAI, and Twitter


-review before posting 
-give 3 varients of each post for review before posting
-schedule deltion if in a certian amount of time engagement is below a certain level
-diversfied posting accross platforms like threads, youtube, insta, fb etc.
-scheduling posts before hand (around 3-5 hours tops)
-allow specific news article to be converted to tweet (pasting link or searching it based on headline)
