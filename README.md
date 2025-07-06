# 🧠 Social Pulse Analytics

**Understanding Human Nature Through Social Media Patterns**

A data analytics platform that analyzes human behavior by correlating trending topics, sentiment, and engagement patterns across Reddit and news platforms. Built with minimal code for maximum functionality.

## 🎯 Features

### Core Analytics
- **Real-time Sentiment Analysis** - VADER + TextBlob sentiment scoring
- **Trend Detection** - Cross-platform trending topic identification  
- **Engagement Pattern Analysis** - Viral content prediction algorithms
- **Human Behavior Insights** - Correlation between platforms and psychology

### Interactive Dashboard
- **📊 Live Data Visualization** - Interactive Plotly charts
- **🔥 Trending Topics Board** - Real-time trend tracking
- **💭 Sentiment Comparison** - Reddit vs News sentiment analysis
- **🔮 Viral Predictions** - AI-powered content virality scoring
- **📱 Mobile-Friendly** - Responsive Streamlit interface

### Data Engineering
- **Multi-source ETL Pipeline** - Reddit API + NewsAPI integration
- **Automated Scheduling** - 30-minute data collection cycles
- **SQLite Database** - Efficient local data storage
- **Rate Limiting** - API quota management
- **Error Handling** - Robust data collection with fallbacks

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Windows/macOS/Linux
- VS Code (recommended)

### 1. Clone and Setup
```cmd
git clone <repository-url>
cd social_pulse_analytics

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Get API Keys

#### Reddit API (Free)
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" → "script"
3. Copy **Client ID** and **Client Secret**

#### NewsAPI (Free)
1. Go to [NewsAPI](https://newsapi.org/register)
2. Register for free account
3. Copy your **API Key**

### 3. Configure Environment
```cmd
# Copy example environment file
copy .env.example .env

# Edit .env file with your API keys
notepad .env
```

Add your keys to `.env`:
```bash
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
NEWS_API_KEY=your_newsapi_key_here
```

### 4. Run the Application
```cmd
python run.py
```

Choose option:
1. **Collect data once** - Test data collection
2. **Launch dashboard with auto-collection** - Full application
3. **Dashboard only** - View existing data

### 5. View Dashboard
Open browser to: `http://localhost:8501`

## 📊 Dashboard Overview

### 🎯 Overview Tab
- **Social Media Pulse** - Hourly engagement trends
- **Key Metrics** - Sentiment, engagement, cross-platform trends
- **Top Trending** - Real-time trending topics

### 📈 Trends Tab
- **Cross-Platform Analysis** - Topics trending on both platforms
- **Bubble Chart** - Topic coverage visualization
- **Subreddit Rankings** - Sentiment by community

### 💭 Sentiment Tab
- **Platform Comparison** - Reddit vs News sentiment
- **Distribution Charts** - Positive/Negative/Neutral breakdown
- **Sentiment Timeline** - Mood changes over time

### 🔮 Predictions Tab
- **Viral Content Scoring** - AI-powered virality predictions
- **Human Behavior Insights** - Cross-platform patterns
- **Trend Forecasting** - What might go viral next

## 🏗️ Project Structure

```
social_pulse_analytics/
├── app/                    # Core application
│   ├── config.py          # Configuration management
│   ├── database.py        # SQLite operations
│   └── models.py          # Data models
├── collectors/             # Data collection
│   ├── reddit_collector.py # Reddit API integration
│   ├── news_collector.py  # NewsAPI integration
│   └── scheduler.py       # Automated collection
├── analyzers/              # Analytics engines
│   ├── sentiment_analyzer.py # VADER sentiment analysis
│   ├── trend_detector.py     # Trend identification
│   └── correlation_engine.py # Cross-platform analysis
├── dashboard/              # Streamlit dashboard
│   └── streamlit_app.py   # Interactive dashboard
├── data/                   # SQLite database
└── run.py                 # Main entry point
```

## 🔧 Configuration Options

### Environment Variables
```bash
# API Configuration
REDDIT_CLIENT_ID=your_key
REDDIT_CLIENT_SECRET=your_secret
NEWS_API_KEY=your_key

# Collection Settings
UPDATE_INTERVAL=30          # Minutes between collections
REDDIT_POST_LIMIT=25       # Posts per subreddit
NEWS_ARTICLE_LIMIT=50      # Total articles per cycle

# Dashboard Settings
STREAMLIT_PORT=8501        # Dashboard port
```

### Subreddit Configuration
Edit `app/config.py` to modify tracked subreddits:
```python
REDDIT_SUBREDDITS = [
    "technology", "science", "worldnews", 
    "datascience", "artificial", "futurology"
]
```

## 📈 Analytics Capabilities

### Sentiment Analysis
- **VADER Sentiment** - Social media optimized scoring
- **TextBlob Sentiment** - Traditional text analysis
- **Hybrid Scoring** - Combined approach for accuracy
- **Platform Comparison** - Reddit vs News sentiment trends

### Trend Detection
- **Keyword Extraction** - NLP-based topic identification
- **Cross-platform Correlation** - Topics spanning both platforms
- **Momentum Calculation** - Rising/declining trend detection
- **Viral Prediction** - Engagement velocity algorithms

### Human Behavior Insights
- **Engagement Patterns** - When people are most active
- **Sentiment Contagion** - How emotions spread
- **Platform Prediction** - Reddit predicting news topics
- **Community Psychology** - Subreddit behavior analysis

## 🔄 Data Collection Process

### Automated Pipeline
1. **Reddit Collection** - Hot posts from configured subreddits
2. **News Collection** - Latest articles from major sources
3. **Sentiment Analysis** - VADER + TextBlob scoring
4. **Trend Detection** - Keyword extraction and ranking
5. **Database Storage** - SQLite with 7-day retention
6. **Dashboard Update** - Real-time visualization refresh

### Collection Schedule
- **Every 30 minutes** - Automated data collection
- **Rate Limited** - Respects API quotas
- **Error Handling** - Continues on partial failures
- **Data Cleaning** - Automatic old data removal

## 📱 Mobile Support

The Streamlit dashboard is **mobile-responsive**:
- **Touch-friendly** interface
- **Responsive charts** that adapt to screen size
- **Mobile navigation** optimized for phones
- **Fast loading** on mobile networks

## 🛠️ Development

### Adding New Data Sources
1. Create collector in `collectors/`
2. Add to scheduler in `collectors/scheduler.py`
3. Update models in `app/models.py`
4. Add dashboard components

### Customizing Analytics
1. Modify analyzers in `analyzers/`
2. Add new metrics to dashboard
3. Update database schema if needed

### Extending Dashboard
1. Edit `dashboard/streamlit_app.py`
2. Add new tabs or visualizations
3. Create custom Plotly charts

## 🚀 Deployment Options

### Local Development
- Run directly with `python run.py`
- SQLite database for simplicity
- Perfect for testing and development

### Cloud Deployment
- **Railway** - Deploy with git push
- **Vercel** - Serverless functions
- **VPS** - Full control deployment

### Production Considerations
- Switch to PostgreSQL for scale
- Add Redis for caching
- Implement user authentication
- Set up monitoring and alerts

## 📊 API Quotas & Limits

### Reddit API (Free)
- **60 requests/minute**
- **Unlimited daily requests**
- **OAuth 2.0 authentication**

### NewsAPI (Free Tier)
- **1,000 requests/day**
- **100 articles per request**
- **Developer rate limits**

### Optimization Tips
- Collection runs every 30 minutes
- Smart rate limiting built-in
- Minimal API calls for efficiency

## 🤝 Contributing

### Getting Started
1. Fork the repository
2. Create feature branch
3. Add your improvements
4. Test thoroughly
5. Submit pull request

### Areas for Enhancement
- **Additional APIs** - Twitter, YouTube, TikTok
- **Advanced ML** - Deep learning sentiment models
- **Real-time Streaming** - WebSocket updates
- **User Accounts** - Personal dashboards
- **Alert System** - Trend notifications

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

### Common Issues

**"Missing API keys"**
- Check `.env` file exists and has correct keys
- Verify Reddit app is "script" type
- Ensure NewsAPI key is valid

**"No data collected"**
- Check internet connection
- Verify API keys are working
- Look at console output for errors

**"Dashboard won't load"**
- Ensure port 8501 is available
- Check firewall settings
- Try different browser

### Getting Help
1. Check console output for errors
2. Verify API keys in `.env` file
3. Review database logs in `logs/`
4. Test API connections manually

## 🎯 Use Cases

### Data Science Portfolio
- **Real-world data** processing
- **Machine learning** implementation
- **Visualization** skills demonstration
- **API integration** expertise

### Business Intelligence
- **Market sentiment** tracking
- **Trend forecasting** for products
- **Social media monitoring**
- **Competitive analysis**

### Research Applications
- **Social psychology** studies
- **Information spread** analysis
- **Platform behavior** research
- **Sentiment evolution** tracking

## 🌟 What Makes This Special

### For FAANG Interviews
- **Real-time data processing** at scale
- **Multi-source ETL pipeline** design
- **Human behavior analytics** - unique angle
- **Production-ready code** structure
- **Scalable architecture** patterns

### Technical Highlights
- **Minimal but functional** - Quick setup, immediate results
- **Industry best practices** - Clean code, proper error handling
- **Mobile-first dashboard** - Modern responsive design
- **Automated insights** - AI-powered trend detection
- **Cross-platform correlation** - Unique analytical approach

---

**🧠 Built to understand human nature through data - one trend at a time.**