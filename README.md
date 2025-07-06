# Social Pulse Analytics

Real-time social media analytics platform that tracks sentiment, predicts viral content, and analyzes human behavior patterns across Reddit and news sources.

## Features

- **Live Sentiment Analysis** - Real-time mood tracking
- **Viral Content Predictions** - AI-powered engagement forecasting
- **Behavioral Insights** - Human pattern analysis
- **Interactive Dashboard** - Mobile-responsive analytics interface

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get API Keys

**Reddit API (Free)**
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" → select "script"
3. Copy Client ID and Client Secret

**NewsAPI (Free)**
1. Register at [NewsAPI](https://newsapi.org/register)
2. Copy your API Key

### 3. Configure
Add your API keys to `app/config.py`:
```python
reddit_client_id = "your_reddit_client_id"
reddit_client_secret = "your_reddit_client_secret"
newsapi_key = "your_newsapi_key"
```

### 4. Run
```bash
python run.py
```

The dashboard will open at `http://localhost:8501`

## Architecture

- **Data Collection**: Reddit + NewsAPI → SQLite database
- **Analytics**: VADER sentiment analysis + engagement algorithms
- **Interface**: Streamlit dashboard with real-time updates

## Project Structure

```
social_pulse_analytics/
├── collectors/          # Data gathering from APIs
├── analyzers/          # Sentiment analysis and trend detection
├── dashboard/          # Interactive web interface
├── app/               # Core models and configuration
├── data/              # SQLite database
└── logs/              # Application logs
```

## API Limits

- **Reddit**: 60 requests/minute (unlimited daily)
- **NewsAPI**: 1,000 requests/day (free tier)

Collection runs every 30 minutes with smart rate limiting.

## Use Cases

- **Portfolio Projects** - Demonstrate real-time data processing
- **Market Research** - Track sentiment and trends
- **Social Psychology** - Study information spread patterns
- **Content Strategy** - Predict viral potential

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

Built to understand human nature through data.