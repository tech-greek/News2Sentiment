from transformers import pipeline

# Initialize the FinBERT model for financial sentiment analysis
pipe = pipeline("text-classification", model="ProsusAI/finbert")

def analyze_single_article(article_text):
    """
    Analyze sentiment of a single condensed article using FinBERT
    
    Args:
        article_text (str): Condensed article text from Gemini
        
    Returns:
        dict: Sentiment analysis result with label, confidence, and score
    """
    if not article_text or len(article_text.strip()) < 10:
        raise ValueError("Article text is too short or empty")
    
    result = pipe(article_text)
    
    # FinBERT returns a list with one result
    if isinstance(result, list) and len(result) > 0:
        result = result[0]
    
    # Extract label and confidence - NO FALLBACKS
    label = result['label']
    confidence = result['score']
    
    # Convert to numerical score (-1 to 1)
    # FinBERT returns lowercase labels: 'positive', 'negative', 'neutral'
    if label == 'positive':
        raw_score = confidence  # 0.5 to 1.0
    elif label == 'negative':
        raw_score = -confidence  # -0.5 to -1.0
    else:  # neutral
        raw_score = 0.0
        
    return {
        "label": label.upper(),  # Convert to uppercase for consistency
        "confidence": confidence,
        "raw_score": raw_score
    }

def calculate_final_sentiment_score(condensed_articles):
    """
    Calculate final sentiment score (0-100) from multiple condensed articles
    
    Args:
        condensed_articles (list): List of condensed articles from Gemini analysis
        
    Returns:
        dict: Final sentiment analysis with score (0-100) and breakdown
    """
    if not condensed_articles:
        raise ValueError("No condensed articles provided for sentiment analysis")
    
    # Analyze each condensed article
    sentiment_results = []
    for article in condensed_articles:
        if isinstance(article, dict) and 'condensed_content' in article:
            article_text = article['condensed_content']
        elif isinstance(article, str):
            article_text = article
        else:
            continue
            
        result = analyze_single_article(article_text)
        sentiment_results.append(result)
    
    if not sentiment_results:
        raise ValueError("No valid articles could be analyzed for sentiment")
    
    # Calculate weighted average score
    raw_scores = [result['raw_score'] for result in sentiment_results]
    confidences = [result['confidence'] for result in sentiment_results]
    labels = [result['label'] for result in sentiment_results]
    
    # Weight by confidence
    weighted_score = sum(score * conf for score, conf in zip(raw_scores, confidences)) / sum(confidences)
    
    # Convert from (-1, 1) to (0, 100) scale
    # -1 maps to 0, 0 maps to 50, 1 maps to 100
    final_score = ((weighted_score + 1) / 2) * 100
    
    # Determine sentiment label
    if final_score >= 70:
        sentiment_label = "BULLISH"
    elif final_score >= 60:
        sentiment_label = "SLIGHTLY BULLISH"
    elif final_score >= 40:
        sentiment_label = "NEUTRAL"
    elif final_score >= 30:
        sentiment_label = "SLIGHTLY BEARISH"
    else:
        sentiment_label = "BEARISH"
    
    # Count sentiment distribution
    positive_count = labels.count('POSITIVE')
    negative_count = labels.count('NEGATIVE')
    neutral_count = labels.count('NEUTRAL')
    
    # Calculate overall confidence
    overall_confidence = sum(confidences) / len(confidences)
    
    return {
        "final_score": round(final_score, 1),
        "sentiment_label": sentiment_label,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
        "total_articles": len(sentiment_results),
        "confidence": round(overall_confidence, 3)
    }

def get_sentiment_color(score):
    """
    Get color based on sentiment score (0-100)
    
    Args:
        score (float): Sentiment score (0-100)
        
    Returns:
        str: Color code for UI display
    """
    if score >= 70:
        return "#4CAF50"  # Green for bullish
    elif score >= 60:
        return "#8BC34A"  # Light green for slightly bullish
    elif score >= 40:
        return "#FF9800"  # Orange for neutral
    elif score >= 30:
        return "#FF5722"  # Light red for slightly bearish
    else:
        return "#F44336"  # Red for bearish

def get_sentiment_emoji(score):
    """
    Get emoji based on sentiment score (0-100)
    
    Args:
        score (float): Sentiment score (0-100)
        
    Returns:
        str: Emoji for UI display
    """
    if score >= 70:
        return "🚀"  # Rocket for bullish
    elif score >= 60:
        return "📈"  # Trending up for slightly bullish
    elif score >= 40:
        return "➡️"  # Right arrow for neutral
    elif score >= 30:
        return "📉"  # Trending down for slightly bearish
    else:
        return "📉"  # Trending down for bearish
