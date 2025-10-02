# 📰 News2Sentiment

An AI-powered stock sentiment analysis application that combines real-time news scraping, content extraction, and advanced AI analysis to provide comprehensive market insights.

## 🚀 Features

### 📊 **Real-Time Market Analysis**
- **Stock Data Integration**: Live stock prices, market cap, and volume from Yahoo Finance
- **Interactive Charts**: Price trends and technical indicators using Plotly
- **Sentiment Scoring**: AI-powered sentiment analysis on a 0-100 scale

### 🔍 **Advanced News Integration**
- **Google News Scraping**: Beautiful Soup-based web scraping for real article URLs
- **Content Extraction**: Full article content parsing from major news sources
- **Source Diversity**: Articles from Investopedia, CNN, CNBC, Yahoo Finance, and more

### 🤖 **AI-Powered Analysis**
- **Gemini Integration**: Google's Gemini AI for content condensation and market summaries
- **FinBERT Sentiment**: Financial sentiment analysis using specialized BERT models
- **Comprehensive Summaries**: Structured market analysis with themes, risks, and outlook

### 💻 **Modern Web Interface**
- **Streamlit Dashboard**: Clean, responsive web interface
- **Real-Time Updates**: Live data refresh and analysis
- **Professional UI**: Dark theme with gradient styling and interactive components

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd News2Sentiment
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run the application**
   ```bash
   streamlit run frontend/app.py
   ```

## 📁 Project Structure

```
News2Sentiment/
├── backend/
│   ├── rss_scraping.py      # Google News scraping with Beautiful Soup
│   ├── gemini_analysis.py   # AI content processing and market summaries
│   └── sentiment.py         # FinBERT sentiment analysis
├── frontend/
│   └── app.py              # Streamlit web application
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Core Components

### 1. **News Integration (`backend/rss_scraping.py`)**
- **Google News Scraping**: Beautiful Soup-based web scraping for real article URLs
- **Content Extraction**: Parses full article content from news sources
- **Fallback System**: RSS feed backup if scraping fails
- **Source Diversity**: Handles multiple news sources and formats

### 2. **AI Analysis (`backend/gemini_analysis.py`)**
- **Content Condensation**: Reduces articles to 350 words while preserving key information
- **Market Summary Generation**: Creates comprehensive market analysis
- **Error Handling**: Graceful fallbacks and retry mechanisms
- **API Integration**: Google Gemini API for advanced text processing

### 3. **Sentiment Analysis (`backend/sentiment.py`)**
- **FinBERT Model**: Specialized financial sentiment analysis
- **Score Calculation**: 0-100 sentiment scale with confidence weighting
- **Multi-Article Analysis**: Aggregates sentiment from multiple sources
- **Visual Indicators**: Color-coded sentiment display

### 4. **Web Interface (`frontend/app.py`)**
- **Stock Dashboard**: Real-time stock data and charts
- **News Cards**: Interactive news display with direct article links
- **Market Summary**: AI-generated market analysis and insights
- **Responsive Design**: Mobile-friendly interface

## 🎯 Usage

### Basic Workflow

1. **Launch the Application**
   ```bash
   streamlit run frontend/app.py
   ```

2. **Enter Stock Ticker**
   - Input stock symbol (e.g., AAPL, TSLA, MSFT)
   - Select date range for analysis
   - Click "Analyze"

3. **View Results**
   - **Stock Overview**: Price, market cap, volume
   - **Price Charts**: Interactive price trends
   - **Market Summary**: AI-generated analysis
   - **News Articles**: Recent news with direct links

## 🔑 API Keys Setup

### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` file: `GEMINI_API_KEY=your_key_here`


## 🚨 Troubleshooting

### Common Issues

1. **API Quota Exceeded**
   - **Issue**: Gemini API free tier limit (50 requests/day)
   - **Solution**: Wait for quota reset or upgrade to paid plan

2. **Content Extraction Fails**
   - **Issue**: Some news sources block automated access
   - **Solution**: App automatically falls back to alternative sources

3. **Import Errors**
   - **Issue**: Missing dependencies
   - **Solution**: Run `pip install -r requirements.txt`

## 🔄 Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **Beautiful Soup**: Web scraping and HTML parsing
- **Requests**: HTTP library for API calls
- **YFinance**: Yahoo Finance data integration
- **Plotly**: Interactive charts and visualizations

### AI/ML Libraries
- **Google Generative AI**: Gemini API integration
- **Transformers**: Hugging Face FinBERT model
- **Newspaper3k**: Article content extraction
- **NumPy**: Numerical computations

### Utility Libraries
- **Python-dotenv**: Environment variable management
- **Feedparser**: RSS feed parsing (fallback)

## 🛠️ Technical Skills Demonstrated

- **Web Scraping**: Beautiful Soup for Google News scraping
- **API Integration**: Google Gemini API
- **Machine Learning**: FinBERT for financial sentiment analysis
- **Data Visualization**: Plotly and Streamlit for interactive dashboards
- **Web Development**: Streamlit for responsive web applications
- **Error Handling**: Robust fallback systems and retry mechanisms
- **Environment Management**: Secure API key handling with python-dotenv

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini**: AI content analysis and summarization
- **Hugging Face**: FinBERT financial sentiment model
- **Yahoo Finance**: Real-time stock data
- **Streamlit**: Web application framework
- **Beautiful Soup**: Web scraping capabilities

---

**Built with ❤️ for financial analysis and market insights**