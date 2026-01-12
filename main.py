from api_routes import get_current_user, router as api_router
from datetime import timedelta
from fastapi import Depends, FastAPI, Form, HTTPException, Body, status
import auth
from config import UserInput, TimeFrame, settings
from auth import User, authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, create_refresh_token, verify_token
import requests
import tweepy
from typing import List
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import re
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt
import time

app = FastAPI()
app.include_router(api_router, prefix="/api")
logger = logging.getLogger(__name__)

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class TokenRefreshMiddleware(BaseHTTPMiddleware):
    """Auto-refresh token if it's expiring soon"""
    async def dispatch(self, request: Request, call_next):
        # Skip for public routes
        public_routes = ["/", "/login", "/register", "/token", "/health", "/trending-topics", "/instructions", "/refresh-token"]
        if request.url.path in public_routes or request.url.path.startswith("/static"):
            return await call_next(request)
        
        logger.debug(f"[MIDDLEWARE] Processing {request.method} {request.url.path}")
        
        # Check access token
        access_token = request.cookies.get("access_token")
        if not access_token:
            logger.warning(f"[MIDDLEWARE] NO ACCESS TOKEN for {request.url.path}")
        else:
            try:
                payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
                exp = payload.get("exp")
                username = payload.get("sub")
                time_remaining = exp - time.time() if exp else 0
                logger.info(f"[MIDDLEWARE] Token valid for user {username}, expires in {time_remaining:.0f}s")
                
                # If token expires in less than 5 minutes, refresh it
                if exp and time_remaining < 300:
                    logger.warning(f"[MIDDLEWARE] Token expiring soon ({time_remaining:.0f}s), auto-refreshing...")
                    if username:
                        new_access_token = create_access_token({"sub": username})
                        request.state.new_access_token = new_access_token
                        logger.info(f"[MIDDLEWARE] Token refreshed for {username}")
            except Exception as e:
                logger.error(f"[MIDDLEWARE] Token verification failed: {e}")
        
        try:
            response = await call_next(request)
            logger.debug(f"[MIDDLEWARE] Response status: {response.status_code} for {request.url.path}")
        except Exception as e:
            logger.error(f"[MIDDLEWARE] Exception during processing: {e}", exc_info=True)
            raise
        
        # Set new token in cookie if middleware refreshed it
        if hasattr(request.state, "new_access_token"):
            response.set_cookie("access_token", request.state.new_access_token, httponly=True, max_age=86400)
            logger.info(f"[MIDDLEWARE] New token set in response cookie")
        
        return response

app.add_middleware(TokenRefreshMiddleware)

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
        logger.info(f"[OPENROUTER] Calling OpenRouter API...")
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
        
        logger.debug(f"[OPENROUTER] Prompt length: {len(prompt)} chars")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        logger.info(f"[OPENROUTER] Response status: {response.status_code}")
        if response.status_code >= 400:
            logger.error(f"[OPENROUTER] Error {response.status_code}: {response.text}")
        
        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"]
        logger.info(f"[OPENROUTER] Success - Generated {len(result)} chars")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"[OPENROUTER] Request error: {str(e)}")
        raise HTTPException(status_code=502, detail=f"OpenRouter API error: {str(e)}")
    except Exception as e:
        logger.error(f"[OPENROUTER] Unexpected error: {str(e)}", exc_info=True)
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
    start_time = time.time()
    try:
        logger.info(f"[GENERATE] START - User: {current_user['username']}")
        logger.debug(f"[GENERATE] Input - Keywords: {user_input.keywords}, Timeframe: {user_input.timeframe}, Tone: {user_input.tone}")
        
        # Get user's API keys
        api_keys = current_user.get("api_keys", {})
        if not api_keys:
            logger.error(f"[GENERATE] No API keys configured for {current_user['username']}")
            raise HTTPException(status_code=400, detail="No API keys configured")
        logger.info(f"[GENERATE] API keys loaded: {len(api_keys)} keys found")
        
        # Initialize Twitter client with user's keys
        logger.info(f"[GENERATE] Initializing Twitter client...")
        twitter_client = get_twitter_client(api_keys)
        if twitter_client:
            logger.info(f"[GENERATE] Twitter client initialized successfully")
        else:
            logger.warning(f"[GENERATE] Twitter client initialization failed")
        
        # Fetch news articles
        logger.info(f"[GENERATE] Fetching news articles...")
        articles = fetch_news(user_input.keywords, user_input.timeframe)
        if not articles:
            logger.error(f"[GENERATE] No articles found for keywords: {user_input.keywords}")
            raise HTTPException(status_code=404, detail="No articles found")
        logger.info(f"[GENERATE] Found {len(articles)} articles")
        
        # Generate tweet
        logger.info(f"[GENERATE] Generating tweet...")
        tweet = generate_tweet_summary(articles, user_input.tone)
        logger.info(f"[GENERATE] Tweet generated: {tweet[:50]}...")
        
        # Post to Twitter if client initialized
        tweet_url = None
        if twitter_client:
            try:
                logger.info(f"[GENERATE] Posting tweet to Twitter...")
                clean_tweet = clean_tweet_text(tweet)
                logger.debug(f"[GENERATE] Clean tweet: {clean_tweet}")
                response = twitter_client.create_tweet(text=clean_tweet)
                
                if response.data:
                    tweet_url = f"https://twitter.com/user/status/{response.data['id']}"
                    logger.info(f"[GENERATE] Tweet posted successfully: {tweet_url}")
                else:
                    logger.warning(f"[GENERATE] Twitter response has no data: {response}")
            except tweepy.TweepyException as e:
                logger.error(f"[GENERATE] Twitter post failed: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Twitter error: {str(e)}")
            except Exception as e:
                logger.error(f"[GENERATE] Unexpected error during Twitter post: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Tweet posting failed: {str(e)}")
        else:
            logger.warning(f"[GENERATE] Skipping Twitter post - client not initialized")
        
        elapsed = time.time() - start_time
        logger.info(f"[GENERATE] COMPLETED in {elapsed:.2f}s - User: {current_user['username']}")
        
        return {
            "articles": [a["title"] for a in articles],
            "tweet": tweet,
            "tweet_url": tweet_url
        }
        
    except HTTPException as e:
        logger.error(f"[GENERATE] HTTPException: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        logger.exception(f"[GENERATE] FAILED in {elapsed:.2f}s - Unexpected error: {str(e)}")
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
        logger.info(f"[GNEWS] Fetching articles for keywords: {keywords} (timeframe: {timeframe})")
        response = requests.get(url, timeout=10)
        logger.info(f"[GNEWS] Response status: {response.status_code}")
        
        if response.status_code >= 400:
            logger.error(f"[GNEWS] Error {response.status_code}: {response.text}")
        
        response.raise_for_status()
        articles = response.json().get("articles", [])
        filtered = [a for a in articles[:3] if a.get("title") and a.get("description")]
        logger.info(f"[GNEWS] Found {len(filtered)} valid articles")
        return filtered
    except requests.exceptions.RequestException as e:
        logger.error(f"[GNEWS] Request failed: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"[GNEWS] Unexpected error: {str(e)}", exc_info=True)
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
    """Login endpoint - returns both access and refresh tokens"""
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create both tokens
    access_token = create_access_token(data={"sub": user["username"]})
    refresh_token = create_refresh_token(data={"sub": user["username"]})
    
    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie("access_token", access_token, httponly=True, max_age=86400)  # 24 hours
    response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=604800)  # 7 days
    return response

@app.post("/refresh-token")
async def refresh_token_endpoint(request: Request):
    """Auto-refresh access token when it's about to expire"""
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token found")
    
    # Verify refresh token
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Token missing username")
    
    # Create new access token
    new_access_token = create_access_token({"sub": username})
    
    response = JSONResponse({"success": True})
    response.set_cookie("access_token", new_access_token, httponly=True, max_age=86400)
    return response

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