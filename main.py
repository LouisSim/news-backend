import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from getNews import get_news
import requests
from bs4 import BeautifulSoup

biasPrompt = (
    "Evaluate the following article for reliability and potential bias. Respond in under 50 words, focusing only on bias indicators such as language, perspective, or omissions. Do not include any prefatory text or framing like 'this is the bias report.' Provide your evaluation directly. Here is the article: "
)

summaryPrompt = (
    "Imagine you are an excellent reporter with advanced knowledge of the news. Do not give a prefaces, explanation, or introductory phrase before the summary. Without any preface, summarize the following article briefly, focusing solely on unbiased factual content. DO NOT WRITE 'here is a summary of the article' or anything simular. Highlight key points like names, dates, events, and outcomes without opinions, speculation, or charged language.  Here is the article: "
)

app = FastAPI()
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://louissim.github.io"],  # Update to match your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NewsQuery(BaseModel):
    topic: str
    date_range: str

def extract_descriptions_and_urls(articles):
    extracted_data = []
    for article in articles:
        title = article.get('title', 'No title available')
        if title == '[Removed]':
            continue
        description = article.get('description', 'No description available')
        url = article.get('url', 'No URL available')
        source = article.get('source', {}).get('name', 'No source available')
        extracted_data.append({'title': title, 'description': description, 'url': url, 'source': source})
    return extracted_data

def scrape_article_content(article_url):
    try:
        response = requests.get(article_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([para.get_text() for para in paragraphs])
        return content
    except requests.RequestException as e:
        print(f"Error scraping article content: {e}")
        return "Content not available"

@app.get("/facts")
async def get_facts(topic: str = Query(...), date_range: str = Query(...), reputable: bool = False):
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="News API Key missing")
        if(reputable):
            print("Reputable news sources only")
        # Log the received parameters
        print(f"Received topic: {topic}, date_range: {date_range}")
        news_stories = get_news(api_key, topic, date_range, reputable)
        
        # Extract descriptions and URLs
        extracted_data = extract_descriptions_and_urls(news_stories)
        
        return {"topic": topic, "articles": extracted_data}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/additional-data")
async def get_additional_data(articleId: int, articleUrl: str):
    try:
        # Scrape the article content
        article_content = scrape_article_content(articleUrl)
        
        # Ensure the article content is not too long for the API request
        max_content_length = 4000  # Adjust based on API limits
        if len(article_content) > max_content_length:
            article_content = article_content[:max_content_length] + "..."

        # Prepare the request payload for groq API
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ API Key missing")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {groq_api_key}"
        }
        
        data = {
            "model": "llama3-8b-8192",
            "messages": [{
                "role": "user",
                "content": summaryPrompt + article_content
            }]
        }
        
        bias_data =  {
            "model": "llama3-8b-8192",
            "messages": [{
                "role": "user",
                "content": biasPrompt + article_content
            }]
        }
        
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        groq_response = response.json()
        
        bias_response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=bias_data)
        bias_response.raise_for_status()
        groq_bias_response = bias_response.json()
        
        # Extract the summary from the groq response
        summary = groq_response.get("choices", [{}])[0].get("message", {}).get("content", "Summary not available")
        bias_report = groq_bias_response.get("choices", [{}])[0].get("message", {}).get("content", "Bias report not available")
        additional_data = {
            "summary": summary,
            "biasRating": bias_report  # Placeholder for bias rating
        }
        return additional_data
    except requests.HTTPError as e:
        if e.response.status_code == 400:
            print(f"Error fetching additional data: {e.response.content}")
        else:
            print(f"Error fetching additional data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching additional data")
    except Exception as e:
        print(f"Error fetching additional data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching additional data")