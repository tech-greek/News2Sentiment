import os
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()
api_key = os.environ.get('NEWS_API_KEY')


def fetch_news(ticker, company_name=None, from_date=None, to_date=None, language="en", sort_by="publishedAt",
               page_size=10, page=1):
    """
    Fetch stock-related news for a given ticker/company using NewsAPI.

    Args:
        ticker (str): Stock ticker symbol (e.g., "AMD").
        company_name (str, optional): Full company name for better relevance.
        from_date (str, optional): "YYYY-MM-DD"
        to_date (str, optional): "YYYY-MM-DD"
    """

    # Build search query to reduce irrelevant results
    if company_name:
        query = f'"{company_name}" OR {ticker} stock OR {ticker} share OR {ticker} earnings'
    else:
        query = f'{ticker} stock OR {ticker} share OR {ticker} earnings'

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "from": from_date,
        "to": to_date,
        "language": language,
        "sortBy": sort_by,
        "pageSize": page_size,
        "page": page,
        "domains": "reuters.com,bloomberg.com,cnbc.com,finance.yahoo.com,marketwatch.com",  # Only finance sites
        # "excludeDomains": "ozbargain.com.au",  # Example: exclude irrelevant sites
    }

    headers = {
        "X-Api-Key": api_key
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        articles = response.json().get("articles", [])

        # Add a publication date in readable format
        for a in articles:
            try:
                pub_time = datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00"))
                a["published_date"] = pub_time.strftime("%Y-%m-%d %H:%M")
            except:
                a["published_date"] = a["publishedAt"]
        return articles
    else:
        print("Error:", response.status_code, response.text)
        return []


# Example usage
if __name__ == "__main__":
    articles = fetch_news("AMD", company_name="Advanced Micro Devices", from_date="2025-08-01", to_date="2025-08-07")
    for i, article in enumerate(articles):
        print(f"\nArticle {i + 1}")
        print("Title:", article["title"])
        print("Description:", article["description"])
        print("URL:", article["url"])

