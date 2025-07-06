# 🧠 Social Pulse Analytics

**Understanding Human Nature Through Social Media Patterns**

A beautiful, interactive analytics dashboard that analyzes social media trends, sentiment patterns, and human behavior across Reddit and news platforms. Built with Streamlit and optimized for cloud deployment.

![Dashboard Preview](https://img.shields.io/badge/Status-Production%20Ready-brightgreen) ![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B) ![Python](https://img.shields.io/badge/Python-3.10-blue) ![Cloud](https://img.shields.io/badge/Deploy-Streamlit%20Cloud-red)

## 🚀 Quick Deploy

**One-click deployment to Streamlit Cloud:**

[![Deploy to Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/new?repository=https://github.com/YOUR_USERNAME/social_pulse_analytics)

**Or deploy manually in 3 steps:**

1. **Fork this repository** to your GitHub account
2. **Go to [share.streamlit.io](https://share.streamlit.io)** and create a new app
3. **Configure your repository** and add API keys in secrets (see [deployment guide](STREAMLIT_DEPLOYMENT.md))

> **Note**: Replace `YOUR_USERNAME` in the deploy badge URL with your actual GitHub username after forking.

### 🔧 **Deployment Requirements**
- Python 3.10 (automatically configured)
- Reddit API credentials (optional for full functionality)
- News API credentials (optional for full functionality)

## ✨ Features

### 📊 **Real-Time Analytics Dashboard**
- **Overview Tab**: Social media pulse with engagement patterns
- **Sentiment Analysis**: Platform-wide emotion tracking
- **Behavioral Insights**: Human behavior pattern analysis  
- **Viral Predictions**: Content virality forecasting

### 🎨 **Beautiful UI**
- Mobile-responsive design with gradient styling
- Color-coded sections (Orange/Red, Blue, Green themes)
- Interactive charts and visualizations
- Real-time data updates every 30 minutes

### 🤖 **Advanced Analytics**
- Cross-platform sentiment comparison
- Behavioral pattern detection
- Trending topic identification
- Content performance prediction
- Human psychology insights

### 📈 **Data Export**
- Download analytics data as CSV
- Export for machine learning models
- Integration with Google Colab
- Academic research ready

## 🚀 Quick Deploy to Streamlit Cloud

### Option 1: One-Click Deploy
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

1. Click the button above
2. Connect your GitHub account  
3. Fork this repository
4. Set main file path: `streamlit_app.py`
5. Configure your API keys in secrets
6. Deploy! 🎉

### Option 2: Manual Setup
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 🔑 Required API Keys

You'll need these free API keys:

| Service | Purpose | Get Key |
|---------|---------|---------|
| **Reddit API** | Social media data | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) |
| **NewsAPI** | News article data | [newsapi.org](https://newsapi.org/) |

```bash
# Clone the repository
git clone <your-repo-url>
cd social_pulse_analytics

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
cp .env.example .env
# Edit .env with your API keys

# Run the dashboard
streamlit run streamlit_app.py
```

## 📁 Project Structure

```
social_pulse_analytics/
├── streamlit_app.py          # Main entry point for Streamlit Cloud
├── dashboard/
│   └── streamlit_app.py      # Enhanced dashboard with all features
├── app/
│   ├── config.py             # Configuration management
│   ├── database.py           # SQLite database operations
│   └── models.py             # Data models
├── analyzers/
│   ├── sentiment_analyzer.py # Sentiment analysis engine
│   ├── trend_detector.py     # Trend detection algorithms
│   ├── behaviour_analyzer.py # Human behavior analysis
│   └── content_analyzer.py   # Content insights
├── collectors/
│   ├── reddit_collector.py   # Reddit API integration
│   ├── news_collector.py     # News API integration
│   └── scheduler.py          # Data collection scheduling
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml.example # Example secrets file
├── requirements.txt         # Python dependencies
└── DEPLOYMENT.md           # Deployment guide
```

## 🎯 Dashboard Tabs

### 1. 🎯 Overview
- Real-time social media pulse
- Top trending content with color-coded engagement
- Platform analytics and community insights
- Hourly engagement patterns

### 2. 💭 Sentiment Analysis  
- Platform sentiment comparison (Reddit vs News)
- Sentiment over time visualization
- Community sentiment rankings
- Behavioral sentiment insights

### 3. 🧠 Behavioral Insights
- Human behavior pattern analysis
- Content optimization insights
- Community behavior rankings
- Advanced psychological metrics

### 4. 🔮 Viral Predictions
- Viral content forecasting
- Real-time viral indicators (Blue section)
- Viral content timeline (Green section)
- Machine learning data export

## 🎨 Color Scheme

- **🔥 Trending/Viral Sections**: Orange-Red gradient theme
- **⚡ Real-Time Indicators**: Blue gradient theme  
- **📈 Timeline Sections**: Green gradient theme
- **🎯 Overview Elements**: Purple-Blue gradient theme

## 📊 Analytics Capabilities

### Data Collection
- **Reddit**: 40+ subreddits covering technology, politics, finance, entertainment
- **News**: Real-time news from major publishers via NewsAPI
- **Refresh**: Auto-updates every 30 minutes

### Analysis Features
- **Sentiment Analysis**: VADER + TextBlob sentiment scoring
- **Trend Detection**: Cross-platform trending topic identification
- **Behavioral Analysis**: Human psychology pattern detection
- **Virality Prediction**: Machine learning-based content scoring

## 🔧 Configuration

Customize the app by editing `app/config.py`:

```python
# Add your favorite subreddits
REDDIT_SUBREDDITS = [
    "technology", "science", "worldnews", 
    "your_custom_subreddit"
]

# Customize news topics
NEWS_TOPICS = [
    "artificial intelligence", "climate change",
    "your_custom_topic"
]
```

## 🚀 Performance Features

- **Caching**: 30-minute data cache for optimal performance
- **Lazy Loading**: Progressive data loading for faster startup
- **Auto-Refresh**: Background data collection
- **Mobile Optimized**: Responsive design for all devices

## 📈 Use Cases

- **Social Media Marketing**: Track sentiment and viral content
- **Academic Research**: Export data for behavioral studies  
- **Content Strategy**: Identify trending topics and optimal posting times
- **Market Analysis**: Monitor public sentiment on topics/brands
- **Journalism**: Track breaking news and public reactions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



