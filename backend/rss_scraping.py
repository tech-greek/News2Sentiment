import feedparser
import sys
import pyshorteners

def shorten_url(url):
    s = pyshorteners.Shortener()
    try:
        short_url = s.tinyurl.short(url)
        return short_url
    except Exception as e:
        print(f"Error shortening URL: {e}")
        return url


def clean_title(title):
    return title.rsplit(' - ', 1)[0].strip()

def fetch_news(search_terms):
    articles=[]

    search_terms = search_terms.replace(" ", "+")

    gn_url = f"https://news.google.com/rss/search?q={search_terms}&hl=en-US&gl=US&ceid=US:en"
    gn_feed = feedparser.parse(gn_url)
    if gn_feed.entries:
        for news_item in gn_feed.entries[:5]:
                news_title = clean_title(news_item.title)
                news_link = shorten_url(news_item.link)
                publication_date = news_item.published
                articles.append({"title": news_title, 'url': news_link, 'published_at': publication_date})
        print(articles)
        return articles
    else:
            print(f"No news found for the term: {search_terms}")


if __name__ == "__main__":
    search_terms = "AAPL Stock"
    if not search_terms:
        print("No search terms provided. Exiting.")
        sys.exit()
    fetch_news(search_terms)