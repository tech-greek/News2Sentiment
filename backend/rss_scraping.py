import feedparser
import requests
from bs4 import BeautifulSoup


def clean_title(title):
    return title.rsplit(' - ', 1)[0].strip()

def scrape_google_news_search(search_terms):
    """Scrape Google News search results to get actual article URLs"""
    try:
        # Construct Google News search URL
        search_query = f"{search_terms} stock"
        encoded_query = requests.utils.quote(search_query)
        url = f"https://www.google.com/search?q={encoded_query}&gl=us&tbm=nws&num=100"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        news_results = []
        
        # Try multiple selectors in case Google changes their HTML structure
        selectors_to_try = [
            "div.SoaBEf",  # Original selector
            "div[data-ved]",  # Alternative selector
            "div.g",  # Generic Google result selector
        ]
        
        for selector in selectors_to_try:
            elements = soup.select(selector)
            
            if elements:
                for el in elements[:5]:  # Limit to 5 articles
                    try:
                        # Extract link
                        link_element = el.find("a")
                        if not link_element or not link_element.get("href"):
                            continue
                            
                        link = link_element["href"]
                        
                        # Extract title
                        title_selectors = ["div.MBeuO", "h3", "div[role='heading']", "a h3"]
                        title = None
                        for title_sel in title_selectors:
                            title_elem = el.select_one(title_sel)
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                break
                        
                        if not title:
                            continue
                        
                        # Extract snippet
                        snippet_selectors = [".GI74Re", ".s3v9rd", "span"]
                        snippet = ""
                        for snippet_sel in snippet_selectors:
                            snippet_elem = el.select_one(snippet_sel)
                            if snippet_elem:
                                snippet = snippet_elem.get_text(strip=True)
                                break
                        
                        # Extract date
                        date_selectors = [".LfVVr", ".LEwnzc", ".f"]
                        date = ""
                        for date_sel in date_selectors:
                            date_elem = el.select_one(date_sel)
                            if date_elem:
                                date = date_elem.get_text(strip=True)
                                break
                        
                        # Extract source
                        source_selectors = [".NUnG9d span", ".CEMjEf", ".WfABme"]
                        source = ""
                        for source_sel in source_selectors:
                            source_elem = el.select_one(source_sel)
                            if source_elem:
                                source = source_elem.get_text(strip=True)
                                break
                        
                        news_results.append({
                            "title": clean_title(title),
                            "url": link,
                            "snippet": snippet,
                            "published_at": date,
                            "source": source
                        })
                        
                    except Exception as e:
                        continue
                
                if news_results:
                    break  # If we found results with this selector, stop trying others
        
        return news_results
        
    except Exception as e:
        return []

def fetch_news_rss_fallback(search_terms):
    """Fallback to RSS feed if search scraping doesn't work"""
    articles = []
    search_terms = search_terms.replace(" ", "+")

    gn_url = f"https://news.google.com/rss/search?q={search_terms}&hl=en-US&gl=US&ceid=US:en"
    gn_feed = feedparser.parse(gn_url)
    if gn_feed.entries:
        for news_item in gn_feed.entries[:5]:
            news_title = clean_title(news_item.title)
            news_link = news_item.link
            publication_date = news_item.published
            articles.append({"title": news_title, 'url': news_link, 'published_at': publication_date})
        return articles
    else:
        return []

def fetch_news(search_terms):
    """
    Fetch news using Google News search scraping (with RSS fallback)
    """
    # Try Google News search scraping first
    articles = scrape_google_news_search(search_terms)
    
    # If search scraping doesn't work well, fall back to RSS
    if not articles:
        articles = fetch_news_rss_fallback(search_terms)
    
    return articles