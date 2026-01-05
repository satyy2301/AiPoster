Here's a polished, professional README for your AIPoster project:

---

# 🤖 AIPoster – AI-Powered News Aggregator & Auto-Tweeter

**AIPoster** is an automated content pipeline that fetches real-time news, generates engaging social media posts using AI, and publishes them to Twitter—all with minimal human intervention. Built for creators, marketers, and developers who want to maintain an active, relevant social presence.

<img width="801" height="808" alt="Screenshot 2025-06-28 162348" src="https://github.com/user-attachments/assets/849cfac0-53e0-4629-a721-3a19d0239579" />

<img width="1009" height="773" alt="Screenshot 2025-06-28 162356" src="https://github.com/user-attachments/assets/7c0e8eb8-9180-4ed8-947b-1490011d4330" />
<img width="790" height="617" alt="Screenshot 2025-06-28 162406" src="https://github.com/user-attachments/assets/987a4f55-23e0-431e-a59a-325e6c7023f8" />

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Twitter API](https://img.shields.io/badge/Twitter%20API-v2-1DA1F2.svg)](https://developer.twitter.com)

## 🚀 Features

- **📰 Real-Time News Fetching** – Pulls current news articles using GNews API with keyword-based filtering
- **🤖 AI-Powered Summarization** – Generates concise, engaging tweets (up to 280 characters) using DeepSeek AI (OpenAI alternative)
- **🐦 Automated Twitter Posting** – Publishes tweets automatically via Twitter API with intelligent rate limit handling
- **🌐 Ready-to-Use API** – Fully documented REST endpoints for integration into other systems
- **⚡ Async Architecture** – High-reliability pipeline using Python async/await for concurrent API calls
- **🔒 Secure & Configurable** – Environment-based configuration with no hardcoded secrets

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **AI Integration**: DeepSeek AI (OpenAI-compatible)
- **APIs**: GNews API, Twitter API v2 (Tweepy)
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Vercel / Render / Railway ready

## 📦 Quick Start

### Prerequisites
- Python 3.9+
- Twitter Developer Account & API keys
- DeepSeek AI API key (or OpenAI key)
- GNews API key

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
```env
DEEPSEEK_API_KEY=your_deepseek_api_key
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
GNEWS_API_KEY=your_gnews_api_key
```

### Running the Application

```bash
# Start the FastAPI server
uvicorn main:app --reload

# Or with production settings
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🚀 API Endpoints

### POST `/generate`
Generate and post a tweet from news articles.

**Request:**
```json
{
  "keywords": ["technology", "AI"],
  "max_articles": 3,
  "post_to_twitter": true
}
```

**Response:**
```json
{
  "success": true,
  "tweet": "OpenAI releases new multimodal model... #AI #TechNews",
  "tweet_id": "162879315234567",
  "source_articles": ["Article 1 URL", "Article 2 URL"]
}
```

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
npm i -g vercel

# Deploy
vercel --prod
```

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [DeepSeek AI](https://platform.deepseek.com/) for AI capabilities
- [GNews API](https://gnews.io/) for news aggregation
- [Twitter API](https://developer.twitter.com/) for social integration
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework

**⭐ If you find this project useful, please give it a star on GitHub!**
