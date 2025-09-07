import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timedelta, time, date
import altair as alt
import plotly.express as px
from backend import rss_scraping
import yfinance as yf
import streamlit as st
import streamlit.components.v1 as components

def render_news_card(title, url, pub_date):
    html_code = f"""
    <div style="
        border-radius: 36px;
        padding: 18px;
        margin-bottom: 18px;
        padding-bottom: 30px;
        background: #1e1e1e;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        font-family: 'Segoe UI', sans-serif;
        overflow: hidden;
        background-clip: padding-box;
    ">
        <h4 style="
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 8px;">
            <a href="{url}" target="_blank" style="
                text-decoration: none;
                background: linear-gradient(90deg, #4DA3FF, #00FFC6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;">
                {title}
            </a>
        </h4>
        <span style="font-size: 0.8em; color: #999;">🗓 {pub_date}</span>
    </div>
    """
    components.html(html_code, height=130, scrolling=False)


st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            min-width: 250px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(
    page_title = "AI Finance Dashboard",
    page_icon= "💰",
    layout="wide",
    initial_sidebar_state = "expanded"
)

alt.themes.enable("dark")

end_date_default = datetime.today()
start_date_default = end_date_default - timedelta(days=20)
with st.sidebar:
    st.title("News2Sentiment")
    tickers_input = st.sidebar.text_input("Enter Stock Tickers (comma-separated):", "AAPL")
    tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]
    start_date = st.sidebar.date_input("Start Date", value=start_date_default)
    end_date = st.sidebar.date_input("End Date", value=end_date_default,max_value=datetime.today())

start_date = datetime.combine(start_date, time.min)
end_date = datetime.combine(end_date, time.max)

print(f"Start: {start_date} ({type(start_date)}), End: {end_date} ({type(end_date)})")



if st.sidebar.button("Analyze"):
    for ticker in tickers:
        try:
            ticker_obj = yf.Ticker(ticker)

            # Historical data for charts
            hist = ticker_obj.history(start=start_date, end=end_date)
            hist.reset_index(inplace=True)

            # Last price from historical data
            last_price = hist['Close'].iloc[-1] if not hist.empty else None

            # Try fast_info first
            fast_info = ticker_obj.fast_info
            market_cap = getattr(fast_info, "market_cap", None)
            volume = getattr(fast_info, "last_volume", None) or getattr(fast_info, "volume", None)

            # Fallback: try .info if still missing
            if market_cap is None or volume is None:
                info = ticker_obj.info
                market_cap = market_cap or info.get("marketCap", None)
                volume = volume or info.get("volume", None)

            # Final fallback: if volume missing, use historical data
            if volume is None and not hist.empty:
                volume = hist['Volume'].iloc[-1]

            # Formatting for display
            last_price_display = f"${last_price:,.2f}" if last_price is not None else "N/A"
            market_cap_display = f"${market_cap:,.0f}" if market_cap is not None else "N/A"
            volume_display = f"{volume:,}" if volume is not None else "N/A"

        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")
            continue




        # Row 1: Stock Overview & Sentiment
        st.subheader(f"{ticker} - Stock Overview")
        col1, col2 = st.columns([2, 1])

        with col1:
            st.metric(
                label="Last Price",
                value=f"${last_price:,.2f}" if last_price else "N/A"
            )
            st.metric(
                label="Market Cap",
                value=f"{market_cap / 1e12:.2f}T" if market_cap and market_cap >= 1e12 else
                f"{market_cap / 1e9:.2f}B" if market_cap and market_cap >= 1e9 else
                f"{market_cap / 1e6:.2f}M" if market_cap else "N/A"
            )
            st.metric(
                label="Volume",
                value=f"{volume:,}" if volume else "N/A"
            )

        with col2:
            sentiment_score = 0.72  # still placeholder until we integrate Gemini
            gauge_html = f"""
                    <div style="width:150px;height:150px;border-radius:50%;border:8px solid {'#4CAF50' if sentiment_score > 0.3 else '#F44336'};display:flex;align-items:center;justify-content:center;font-size:24px;color:white;">
                        {int(sentiment_score * 100)}%
                    </div>
                    <p style="text-align:center;color:gray;font-size:0.9em;">Market Sentiment</p>
                    """
            st.markdown(gauge_html, unsafe_allow_html=True)

        st.markdown("---")

        # Row 2: Price & Sentiment Charts
        st.subheader("Price Trends")

        st.markdown("**Price Chart**")
        if not hist.empty:
                fig_price = px.line(hist, x="Date", y="Close", title=f"{ticker} Stock Price Over Time")
                st.plotly_chart(fig_price, use_container_width=True)
        else:
                st.warning("No price data available.")


        st.markdown("---")

        # Row 3: AI-Generated Summary
        st.subheader("Market Mood Summary")
        st.write(
            "Overall sentiment is positive. Recent news highlights strong quarterly earnings and optimistic guidance for the next quarter.")  # Placeholder

        st.markdown("---")

        # Row 4: News Cards
        st.subheader("Recent News")
        with st.spinner(f"Fetching news for {ticker}..."):
            articles = rss_scraping.fetch_news(ticker)
            if not articles:
                st.warning(f"No articles found for {ticker}.")
            else:
                for article in articles:

                    render_news_card(
                        title=article.get("title", "No Title"),
                        url=article.get("url", "#"),
                        pub_date=article.get("published_at", "No Published Date"),
                    )