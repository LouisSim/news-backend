from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta
from domains import reputable_domains

def get_news(api_key, query, date_range, reputable, language='en', page_size=15):
    """
    Query the NewsAPI for articles.
    
    :param api_key: Your NewsAPI key
    :param query: Topic to search for
    :param date_range: Date range for the search (e.g., 'last_3_days', 'last_week', 'last_month')
    :param language: Language of the articles (default is English)
    :param page_size: Number of results per page (max 100)
    :return: List of articles
    """
    
    # Calculate from_date and to_date based on date_range
    to_date = datetime.now()
    if date_range == 'last_3_days':
        from_date = to_date - timedelta(days=3)
    elif date_range == 'last_week':
        from_date = to_date - timedelta(weeks=1)
    elif date_range == 'last_month':
        from_date = to_date - timedelta(days=30)
    else:
        raise ValueError("Invalid date_range. Use 'last_3_days', 'last_week', or 'last_month'.")

    # Format dates as strings
    to_date_str = to_date.strftime('%Y-%m-%d')
    from_date_str = from_date.strftime('%Y-%m-%d')
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_date_str,
        "to": to_date_str,
        "language": language,
        "pageSize": page_size,
        "sortBy": "relevancy",
        "apiKey": api_key
    }
    
    if reputable:

        params["domains"] = reputable_domains
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('articles', [])
    else:
        print(f"News Error: {response.status_code}, {response.json().get('message', 'No details available')}")
        return []