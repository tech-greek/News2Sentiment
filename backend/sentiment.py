import os
from newsapi import NewsApiClient


api = NewsApiClient(api_key=os.environ.get('NEWS_API_KEY'))

def fetch_news(ticker, from_date, to_date):

    print("from_date:", from_date, type(from_date))
    print("to_date:", to_date, type(to_date))

    all_articles = api.get_everything(
        q=ticker,
        from_param=from_date,
        to=to_date,
        language='en',
        sort_by='relevancy',
        page_size=100,
    )

    return all_articles['articles']