import google.generativeai as genai
from newspaper import Article
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
else:
    print("Warning: GEMINI_API_KEY not found in environment variables")
    model = None

def extract_article_content(url):
    """Extract article content using newspaper3k"""
    try:
        print(f"Extracting content from: {url}")
        article = Article(url)
        article.download()
        article.parse()
        
        if not article.text or len(article.text.strip()) < 100:
            print(f"Article text too short or empty: {len(article.text) if article.text else 0} chars")
            return None
            
        print(f"Successfully parsed article: {len(article.text)} characters")
        return {
            'title': article.title,
            'text': article.text,
            'summary': article.summary,
            'authors': article.authors,
            'publish_date': article.publish_date,
            'top_image': article.top_image
        }
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None

def condense_with_gemini(title, content, max_chars=4000):
    """Condense article content with Gemini to 350 words max"""
    if not model:
        return "Gemini API key not configured"
    
    try:
        # Limit content to avoid token limits
        content_preview = content[:max_chars] if content else ""
        
        prompt = f"""
        Condense this news article to exactly 350 words or less while preserving all key information:
        
        Title: {title}
        Content: {content_preview}
        
        Requirements:
        - Maximum 350 words
        - Preserve all important facts and details
        - Maintain the original tone and context
        - Focus on the main story and key points
        - Keep it readable and coherent
        - Include any financial data, numbers, or specific details mentioned
        
        Return only the condensed article text.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error with Gemini condensation: {e}")
        return f"Condensation failed: {str(e)}"

def process_articles_with_gemini(articles):
    """Process articles from fetch_news and return condensed versions"""
    if not articles:
        return []
    
    condensed_articles = []
    
    for i, article in enumerate(articles):
        url = article['url']
        title = article['title']
        published_at = article['published_at']
        
        print(f"Processing article {i+1}/{len(articles)}: {title}")
        
        # Extract content
        content_data = extract_article_content(url)
        
        if content_data:
            # Condense with Gemini
            condensed_content = condense_with_gemini(content_data['title'], content_data['text'])
            
            # Add to results
            condensed_articles.append({
                'title': content_data['title'],
                'condensed_content': condensed_content,
                'summary': content_data['summary'],
                'authors': content_data['authors'],
                'publish_date': content_data['publish_date'],
                'top_image': content_data['top_image'],
                'url': url,
                'published_at': published_at
            })
            
            print(f"Successfully processed: {content_data['title']}")
        else:
            print(f"Failed to extract content from: {url}")
    
    return condensed_articles

def generate_market_summary(condensed_articles, ticker):
    """Generate market summary using condensed articles"""
    if not model:
        return "Gemini API key not configured"
    
    if not condensed_articles:
        return "No articles available for analysis"
    
    try:
        # Prepare articles text for analysis
        articles_text = ""
        for i, article in enumerate(condensed_articles):
            articles_text += f"\n--- Article {i+1} ---\n"
            articles_text += f"Title: {article['title']}\n"
            articles_text += f"Content: {article['condensed_content']}\n"
        
        prompt = f"""
        Based on the following news articles about {ticker}, generate a comprehensive market summary:
        
        {articles_text}
        
        Please provide:
        1. **Overall Market Sentiment** (Positive/Negative/Neutral)
        2. **Key Themes** (3-5 main topics driving the news)
        3. **Market Impact** (How these developments might affect {ticker} stock)
        4. **Risk Factors** (Any potential concerns or challenges mentioned)
        5. **Investment Outlook** (Short-term and medium-term perspective)
        
        Format your response clearly with headers for each section. Be concise but comprehensive.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating market summary: {e}")
        return f"Summary generation failed: {str(e)}"

if __name__ == "__main__":
    # Test the functions
    test_articles = [
        {
            'title': 'Test Article',
            'url': 'https://example.com/test',
            'published_at': '2025-01-01'
        }
    ]
    
    condensed = process_articles_with_gemini(test_articles)
    print("Condensed Articles:", condensed)
    
    if condensed:
        summary = generate_market_summary(condensed, "TEST")
        print("Market Summary:", summary)
