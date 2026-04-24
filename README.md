
# 🤖 AIPoster – AI-Powered News Aggregator & Auto-Tweeter

## Quick Public Deploy (Fastest)

The easiest way to deploy this app for public use is Render.

1. Push this repository to GitHub.
2. In Render, click New + > Blueprint and select this repo.
3. Render will detect `render.yaml` automatically.
4. Set environment variables in Render:
  - `GNEWS_API_KEY`
  - `OPENROUTER_API_KEY`
  - `SUPABASE_URL`
  - `SUPABASE_KEY`
  - `ENCRYPTION_KEY`
  - Optional: override `APP_BASE_URL` with your real Render URL
5. Deploy and open `https://<your-service>.onrender.com/health` to confirm status `ok`.

Start command used in production:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**AIPoster** is an automated content pipeline that fetches real-time news, generates engaging social media posts using AI, and publishes them to Twitter—all with minimal human intervention. Built for creators, marketers, and developers who want to maintain an active, relevant social presence.

**Experience a beautiful, modern interface featuring:**
- **Stunning purple gradient theme** with glassmorphism effects
- **Intuitive navigation** with smooth animations
- **Responsive design** that works on all devices
- **Clean card-based layout** for easy content viewing
- **Professional aesthetic** with attention to detail

<img width="801" height="808" alt="Screenshot 2025-06-28 162348" src="https://github.com/user-attachments/assets/849cfac0-53e0-4629-a721-3a19d0239579" />

<img width="1009" height="773" alt="Screenshot 2025-06-28 162356" src="https://github.com/user-attachments/assets/7c0e8eb8-9180-4ed8-947b-1490011d4330" />
<img width="790" height="617" alt="Screenshot 2025-06-28 162406" src="https://github.com/user-attachments/assets/987a4f55-23e0-431e-a59a-325e6c7023f8" />

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Twitter API](https://img.shields.io/badge/Twitter%20API-v2-1DA1F2.svg)](https://developer.twitter.com)

## 🚀 Key Features


### 🧠 Intelligent Content Generation
- **💬 Natural Language Prompts** – Just describe what you want: *"Write an enthusiastic tweet about AI breakthroughs"*
- **🔍 Smart Keyword Extraction** – AI automatically identifies relevant search terms from your description
- **🤖 Context-Aware AI** – Uses OpenRouter (Mistral 7B) to generate tweets that match your intent and tone
- **🎯 Tone Customization** – Choose from professional, casual, enthusiastic, or neutral tones

### 📰 Real-Time News Integration
- **Live News Fetching** – Pulls latest articles from GNews API based on your keywords or prompt
- **🔥 Trending Topics** – One-click access to what's trending now
- **📅 Timeframe Control** – Filter by today, last week, or last month
- **📊 Article Aggregation** – Combines multiple sources for comprehensive coverage

### 🐦 Automated Twitter Posting
- **One-Click Publishing** – Generate and post tweets instantly
- **⚡ Rate Limit Handling** – Smart retry logic respects Twitter's API limits
- **✅ Quality Validation** – Ensures tweets meet character limits and formatting standards
- **🔗 Direct Links** – Get instant links to your posted tweets

### 🔐 Enterprise-Grade Security
- **JWT Authentication** – Secure 24-hour access tokens with automatic refresh
- **🔄 Token Auto-Refresh** – Stay logged in seamlessly without interruptions
- **🔒 Encrypted Storage** – API keys stored securely in Supabase with Fernet encryption
- **👤 User Management** – Individual accounts with isolated API key storage

### 🎨 Beautiful User Experience
- **Modern UI** – Purple gradient backgrounds with glassmorphism effects
- **📱 Fully Responsive** – Perfect experience on desktop, tablet, and mobile
- **✨ Smooth Animations** – Slide-in effects, hover states, and transitions
- **🎯 Intuitive Forms** – Clear labels, helpful hints, and collapsible sections

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.9+, FastAPI (async/await) |
| **AI/ML** | OpenRouter API (Mistral 7B Instruct) |
| **APIs** | GNews API, Twitter API v2 (Tweepy) |
| **Database** | Supabase (PostgreSQL) |
| **Authentication** | JWT with automatic refresh tokens |
| **Frontend** | Jinja2 templates, Vanilla JavaScript |
| **Styling** | Modern CSS with gradients & glassmorphism |
| **Deployment** | Vercel / Render / Railway ready |

---

## 📦 Quick Start

### Prerequisites
- Python 3.9 or higher
- Twitter Developer Account with API v2 access
- OpenRouter API key ([Get one free](https://openrouter.ai/))
- GNews API key ([Free tier available](https://gnews.io/))
- Supabase account ([Sign up free](https://supabase.com/))


### Installation

```bash
# Clone the repository
git clone https://github.com/satyy2301/AIPoster.git
cd AIPoster

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Configuration
Create a `.env` file:
OPENROUTER_API_KEY=your_openrouter_api_key
GNEWS_API_KEY=your_gnews_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SECRET_KEY=your_jwt_secret_key
ENCRYPTION_KEY=your_fernet_encryption_key
```

**Note**: Store your Twitter API credentials in the app dashboard after login for secure encrypted storage.WS_API_KEY=your_gnews_api_key
```

### Running the Application

```bash
# Start the FastAPI server
uvicorn main:app --reload

# Or with production settings
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🚀 API Endpoints-and-post`
Generate and post a tweet from news articles using natural language or keywords.

**Request:**
```json
{
  "prompt": "Write an enthusiastic tweet about AI breakthroughs this week",
  "timeframe": "week",
  "tone": "enthusiastic"
}
```

**Or with manual keywords:**
```json
{
  "keywords": ["AI", "technology", "breakthrough"],
  "timeframe": "week",
  "tone": "professional"
}
```

**Response:**
```json
{
  "tweet": "🚀 Incredible AI breakthroughs this week! New models pushing boundaries... #AI #TechNews",
  "tweet_url": "https://twitter.com/user/status/123456789",
  "articles": ["Article Title 1", "Article Title 2"],
  "extracted_keywords": ["AI", "breakthrough", "models"]
}
```User Input** → Natural language prompt or manual keywords entry
2. **Keyword Extraction** → AI extracts searchable keywords from natural language (if needed)
3. **News Fetching** → Fetches latest articles based on keywords using GNews API
4. **Content Processing** → Extracts key information and filters relevant content
5. **AI Generation** → Uses OpenRouter (Mistral AI) to generate engaging tweet-length summaries with user's intent
6. **Quality Check** → Validates tweet length, relevance, and formatting
7. **Auto-Posting** → Publishes to Twitter via Tweepy with error handling
8. **Logging** → Comprehensive logging t
User authentication endpoint for login.

### GET `/api/api-keys`
Retrieve stored API keys (requires authentication)
### GET `/health`
Health check endpoint.

## 🔧 How It Works

1. **News Fetching** → Fetches latest articles based on keywords using GNews API
2. **Content Processing** → Extracts key information and filters relevant content
3. **AI Summarization** → Uses DeepSeek AI to generate engaging tweet-length summaries
4. **Quality Check** → Validates tweet length, relevance, and safety
5. **Auto-Posting** → Publishes to Twitter via Tweepy with error handling
6. **Logging** → Tracks all actions for monitoring and debugging

## 📊 Project Structure

```
AIPoster/
├── main.py              # FastAPI application entry point
├── core/
│   ├── news_fetcher.py  # GNews API integration
│   ├── ai_generator.py  # DeepSeek AI integration
│   ├── twitter_client.py # Twitter API wrapper
│   └── pipeline.py      # Main orchestration logic
├── api/
│   └── endpoints.py     # API route definitions
├── utils/
│   ├── helpers.py       # Utility functions
│   └── logger.py        # Logging configuration
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
└── README.md           # This file
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test the generate endpoint
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["tech"], "max_articles": 1, "post_to_twitter": false}'
```

## 🔒 Security & Best Practices

- **Never commit `.env` files** – Use `.env.example` as a template
- **Rotate API keys** regularly and use least-privilege access
- **Implement rate limiting** to respect API quotas
- **Add content moderation** filters to prevent inappropriate posts
- **Monitor logs** for failed attempts or suspicious activity

## 🚀 Deployment

### Vercel
```bash
# Install Vercel CLI
npmx] Natural language prompt support
- [x] Smart keyword extraction
- [x] JWT authentication with auto-refresh
- [x] Trending topics integration
- [ ] Analytics dashboard for tweet performance tracking
- [ ] Scheduled posting with cron jobs
- [ ] A/B testing for multiple tweet variations
- [ ] Thread generation for longer content
- [ ] Multi-platform posting (LinkedIn, Facebook, Instagram)
- [ ] Image generation for visual tweets

### Docker
```bash
# Build image
docker build -t aiposter .

# Run container
docker run -p 8000:8000 --env-file .env aiposter
```

## 📈 Future Enhancements

- [ ] Multi-platform posting (LinkedIn, Facebook, Instagram)
- [ ] Scheduled posting with cron jobs
- [ ] Sentiment analysis for tone optimization
- [ ] Image generation for visual tweets
- [ ] Analytics dashboard for performance tracking
- [ ] Custom AI model fine-tuning
- [ ] RSS feed integration for additional sources

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
OpenRouter](https://openrouter.ai/) for AI model access (Mistral AI)
- [GNews API](https://gnews.io/) for news aggregation
- [Twitter API](https://developer.twitter.com/) for social integration
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Supabase](https://supabase.com/) for database and authentication infrastructure) file for details.

## 🙏 Acknowledgments

- [DeepSeek AI](https://platform.deepseek.com/) for AI capabilities
- [GNews API](https://gnews.io/) for news aggregation
- [Twitter API](https://developer.twitter.com/) for social integration
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework

**⭐ If you find this project useful, please give it a star on GitHub!**
