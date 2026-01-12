from api_routes import get_current_user, router as api_router
from datetime import timedelta
from fastapi import Depends, FastAPI, Form, HTTPException, Body, status
import auth
from config import UserInput, TimeFrame, settings
from auth import User, authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
import requests
import tweepy
from typing import List
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import re
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(api_router, prefix="/api")
logger = logging.getLogger(__name__)

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_twitter_client(api_keys: dict):
    """Initialize Twitter client with user's API keys"""
    required_keys = [
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_SECRET"
    ]
    
    missing_keys = [key for key in required_keys if not api_keys.get(key)]
    if missing_keys:
        logger.warning(f"Missing Twitter keys: {', '.join(missing_keys)}")
        return None
    
    try:
        return tweepy.Client(
            consumer_key=api_keys["TWITTER_API_KEY"],
            consumer_secret=api_keys["TWITTER_API_SECRET"],
            access_token=api_keys["TWITTER_ACCESS_TOKEN"],
            access_token_secret=api_keys["TWITTER_ACCESS_SECRET"]
        )
    except Exception as e:
        logger.error(f"Twitter client initialization failed: {str(e)}")
        return None

def call_openrouter_gemma(prompt: str, max_tokens: int = 150) -> str:
    """Call OpenRouter's API with current working model"""
    try:
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000/",
            "X-Title": "News Aggregator"
        }
        
        payload = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"OpenRouter API error: {str(e)}")
        raise HTTPException(status_code=500, detail="OpenRouter API error")

def clean_tweet_text(tweet: str) -> str:
    """Ensure tweet is text-only and meets Twitter requirements"""
    tweet = re.sub(r'http\S+', '[URL]', tweet)
    tweet = ''.join(char for char in tweet if ord(char) < 128)
    return tweet[:280].strip()

@app.post("/generate-and-post")
async def generate_and_post(
    user_input: UserInput,
    current_user: User = Depends(get_current_user)
):
    """Main endpoint to fetch news, generate tweet, and post to Twitter"""
    try:
        logger.info(f"Processing request for user: {current_user['username']}")
        
        # Get user's API keys
        api_keys = current_user.get("api_keys", {})
        if not api_keys:
            raise HTTPException(status_code=400, detail="No API keys configured")
        
        # Initialize Twitter client with user's keys
        twitter_client = get_twitter_client(api_keys)
        
        # Fetch news articles
        articles = fetch_news(user_input.keywords, user_input.timeframe)
        if not articles:
            raise HTTPException(status_code=404, detail="No articles found")
        
        # Generate tweet
        tweet = generate_tweet_summary(articles, user_input.tone)
        
        # Post to Twitter if client initialized
        tweet_url = None
        if twitter_client:
            try:
                clean_tweet = clean_tweet_text(tweet)
                response = twitter_client.create_tweet(text=clean_tweet)
                
                if response.data:
                    tweet_url = f"https://twitter.com/user/status/{response.data['id']}"
                    logger.info(f"Tweet posted successfully: {tweet_url}")
            except tweepy.TweepyException as e:
                logger.error(f"Twitter post failed: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Twitter error: {str(e)}")
        
        return {
            "articles": [a["title"] for a in articles],
            "tweet": tweet,
            "tweet_url": tweet_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("API processing error")
        raise HTTPException(status_code=500, detail=str(e))

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_news(keywords: List[str], timeframe: str) -> List[dict]:
    """Fetch news articles from GNews API"""
    query = " AND ".join(keywords)
    url = f"https://gnews.io/api/v4/search?q={query}&lang=en&max=3&apikey={settings.GNEWS_API_KEY}"
    
    if timeframe == "24h":
        url += "&from=now-24h"
    elif timeframe == "week":
        url += "&from=now-7d"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        return [a for a in articles[:3] if a.get("title") and a.get("description")]
    except requests.exceptions.RequestException as e:
        logger.error(f"News API failed: {str(e)}")
        return []

def generate_tweet_summary(articles: List[dict], tone: str) -> str:
    """Generate a tweet summary from articles using Gemma"""
    article_texts = "\n\n".join([
        f"Title: {article['title']}\nDescription: {article['description']}"
        for article in articles if article.get('title')
    ])
    
    prompt = f"""Create a Twitter post with these requirements:
    - Tone: {tone}
    - Length: Maximum 280 characters
    - Content: Summary of key points from these articles
    - Include: 2-3 relevant hashtags
    - Links: Replace with [URL]
    - Style: Engaging and informative
    
    Articles:
    {article_texts}
    
    Twitter Post:"""
    
    try:
        return call_openrouter_gemma(prompt)
    except Exception as e:
        logger.error(f"Tweet generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Tweet generation failed")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def form_post(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(user_data: dict = Body(...)):
    try:
        result = auth.create_user(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"]
        )
        return result
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@app.post("/token")
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...)
):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("api_settings.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/instructions", response_class=HTMLResponse)
async def documentation(request: Request):
    return templates.TemplateResponse("docs.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def home_redirect(request: Request):
    return RedirectResponse(url="/")

# Add to main.py

@app.get("/trending-topics")
async def get_trending_topics():
    """Fetch trending news topics from GNews"""
    try:
        url = f"https://gnews.io/api/v4/top-headlines?category=general&lang=en&max=10&apikey={settings.GNEWS_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        
        # Extract common keywords from trending articles
        topics = set()
        for article in articles:
            if article.get("title"):
                title = article["title"].lower()
                # Extract words that might be good keywords (more than 3 letters)
                words = [word for word in title.split() if len(word) > 3 and not word.startswith(('http', 'www'))]
                topics.update(words[:3])  # Add up to 3 keywords per article
                
        return {"topics": sorted(list(topics))[:10]}  # Return top 10 unique topics
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Trending topics fetch failed: {str(e)}")
        return {"topics": []}