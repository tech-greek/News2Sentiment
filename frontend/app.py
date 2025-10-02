import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timedelta, time
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
from backend import rss_scraping
from backend.gemini_analysis import process_articles_with_gemini, generate_market_summary
from backend.sentiment import calculate_final_sentiment_score, get_sentiment_color, get_sentiment_emoji
import yfinance as yf

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
    page_title = "News2Sentiment",
    page_icon= "💰",
    layout="wide",
    initial_sidebar_state = "expanded"
)


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


        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")
            continue




        # Row 1: Stock Overview & Sentiment
        st.subheader(f"{ticker} - Stock Overview")

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

        # Row 3: News Cards
        st.subheader("Recent News")
        with st.spinner(f"Fetching news for {ticker}..."):
            # Fetch news once
            articles = rss_scraping.fetch_news(ticker)
            
            if not articles:
                st.warning(f"No articles found for {ticker}.")
            else:
                # Display news cards
                for article in articles:
                    render_news_card(
                        title=article.get("title", "No Title"),
                        url=article.get("url", "#"),
                        pub_date=article.get("published_at", "No Published Date"),
                    )

        st.markdown("---")

        # Row 4: AI Analysis (Gemini + FinBERT)
        st.subheader("AI Analysis")
        
        if articles:
            # Process all 5 articles for comprehensive analysis
            limited_articles = articles[:5]
            st.info(f"🚀 Processing {len(limited_articles)} articles for comprehensive analysis...")
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Process articles with Gemini
                status_text.text("🤖 Condensing articles with Gemini...")
                progress_bar.progress(20)
                
                condensed_articles = process_articles_with_gemini(limited_articles)
                progress_bar.progress(40)
                
                if condensed_articles:
                    # Step 2: Run FinBERT analysis
                    status_text.text("🧠 Analyzing sentiment with FinBERT...")
                    progress_bar.progress(60)
                    
                    sentiment_result = calculate_final_sentiment_score(condensed_articles)
                    progress_bar.progress(80)
                    
                    # Step 3: Generate market summary
                    status_text.text("📊 Generating market summary...")
                    market_summary = generate_market_summary(condensed_articles, ticker)
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    
                    # Display results
                    st.success(f"✅ Analyzed {len(condensed_articles)} articles successfully!")
                    
                    # Enhanced Visual Sentiment Display
                    st.subheader("📊 Market Sentiment Analysis")
                    
                    # Main sentiment display with multiple visual elements
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        # Large circular gauge with dynamic colors and emojis
                        score = sentiment_result['final_score']
                        color = get_sentiment_color(score)
                        emoji = get_sentiment_emoji(score)
                        
                        # Create a more sophisticated gauge
                        gauge_html = f"""
                        <div style="
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            padding: 20px;
                            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
                            border-radius: 20px;
                            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                            border: 2px solid {color};
                        ">
                            <div style="
                                width: 200px;
                                height: 200px;
                                border-radius: 50%;
                                background: conic-gradient({color} 0deg, {color} {score * 3.6}deg, #333 {score * 3.6}deg, #333 360deg);
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                position: relative;
                                margin-bottom: 15px;
                            ">
                                <div style="
                                    width: 160px;
                                    height: 160px;
                                    border-radius: 50%;
                                    background: #1e1e1e;
                                    display: flex;
                                    flex-direction: column;
                                    align-items: center;
                                    justify-content: center;
                                    font-family: 'Segoe UI', sans-serif;
                                ">
                                    <div style="font-size: 48px; margin-bottom: 5px;">{emoji}</div>
                                    <div style="font-size: 32px; font-weight: bold; color: {color};">{score:.0f}</div>
                                    <div style="font-size: 14px; color: #999;">/ 100</div>
                                </div>
                            </div>
                            <div style="
                                text-align: center;
                                color: {color};
                                font-size: 18px;
                                font-weight: bold;
                                margin-bottom: 5px;
                            ">{sentiment_result['sentiment_label']}</div>
                            <div style="
                                text-align: center;
                                color: #999;
                                font-size: 14px;
                            ">Market Sentiment Score</div>
                        </div>
                        """
                        st.markdown(gauge_html, unsafe_allow_html=True)
                    
                    with col2:
                        # Article breakdown with visual indicators
                        st.markdown("### 📈 Article Breakdown")
                        
                        # Positive articles
                        pos_color = "#4CAF50" if sentiment_result['positive_count'] > 0 else "#666"
                        st.markdown(f"""
                        <div style="
                            background: {pos_color}20;
                            border-left: 4px solid {pos_color};
                            padding: 10px;
                            margin: 5px 0;
                            border-radius: 5px;
                        ">
                            <div style="color: {pos_color}; font-weight: bold;">📈 {sentiment_result['positive_count']} Positive</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Negative articles
                        neg_color = "#F44336" if sentiment_result['negative_count'] > 0 else "#666"
                        st.markdown(f"""
                        <div style="
                            background: {neg_color}20;
                            border-left: 4px solid {neg_color};
                            padding: 10px;
                            margin: 5px 0;
                            border-radius: 5px;
                        ">
                            <div style="color: {neg_color}; font-weight: bold;">📉 {sentiment_result['negative_count']} Negative</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Neutral articles
                        neu_color = "#FF9800" if sentiment_result['neutral_count'] > 0 else "#666"
                        st.markdown(f"""
                        <div style="
                            background: {neu_color}20;
                            border-left: 4px solid {neu_color};
                            padding: 10px;
                            margin: 5px 0;
                            border-radius: 5px;
                        ">
                            <div style="color: {neu_color}; font-weight: bold;">➡️ {sentiment_result['neutral_count']} Neutral</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        # Confidence and analysis metrics
                        st.markdown("### 🎯 Analysis Confidence")
                        
                        # Confidence progress bar
                        confidence_pct = sentiment_result['confidence'] * 100
                        conf_color = "#4CAF50" if confidence_pct >= 80 else "#FF9800" if confidence_pct >= 60 else "#F44336"
                        
                        st.markdown(f"""
                        <div style="
                            background: #333;
                            border-radius: 10px;
                            padding: 15px;
                            margin: 10px 0;
                        ">
                            <div style="color: {conf_color}; font-size: 24px; font-weight: bold; text-align: center;">
                                {confidence_pct:.1f}%
                            </div>
                            <div style="
                                background: #555;
                                border-radius: 5px;
                                height: 8px;
                                margin: 10px 0;
                                overflow: hidden;
                            ">
                                <div style="
                                    background: {conf_color};
                                    height: 100%;
                                    width: {confidence_pct}%;
                                    transition: width 0.3s ease;
                                "></div>
                            </div>
                            <div style="color: #999; font-size: 12px; text-align: center;">
                                Analysis Confidence
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Total articles processed
                        st.metric(
                            label="Articles Analyzed",
                            value=sentiment_result['total_articles'],
                            delta="Total Processed"
                        )
                    
                    # Display market summary
                    st.subheader("Market Mood Summary")
                    st.markdown(market_summary)
                    
                else:
                    st.warning("⚠️ Could not condense articles for analysis")
                    
            except Exception as e:
                st.error(f"Error in AI analysis: {e}")
            finally:
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
        else:
            st.warning("No articles available for AI analysis.")