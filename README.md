# News API and Article Scraper

This project provides an API built with FastAPI that allows users to retrieve news articles, analyze article content for bias, and summarize them. The API uses several external services, including NewsAPI for retrieving articles and Groq for generating summaries and bias evaluations. It also includes a scraping feature that extracts the content of news articles from their URLs using BeautifulSoup.

## Features

- **Get News Articles**: Retrieve articles based on topics and date ranges.
- **Summarize Articles**: Automatically summarize articles without any biased language.
- **Bias Detection**: Analyze articles for potential bias, focusing on language, perspective, and omissions.
- **Scrape Article Content**: Extract full content from articles for detailed analysis.
- **CORS Support**: Middleware to allow specific origins for frontend applications.

## Endpoints

### `/facts`
- **Description**: Get news articles related to a topic within a specified date range.
- **Parameters**:
  - `topic` (string): The news topic to search for.
  - `date_range` (string): Date range to filter articles by (e.g., "last week").
  - `reputable` (boolean, optional): Whether to filter results to reputable sources.
- **Response**:
  - `topic`: The topic of news.
  - `articles`: A list of articles with title, description, URL, and source.

### `/additional-data`
- **Description**: Retrieve additional data for an article, including a summary and bias report.
- **Parameters**:
  - `articleId` (integer): The unique ID of the article.
  - `articleUrl` (string): The URL of the article.
- **Response**:
  - `summary`: A concise summary of the article.
  - `biasRating`: An analysis of the article's bias.

### `/top-headlines`
- **Description**: Get the top headlines from a specific country and category.
- **Parameters**:
  - `country` (string): The country to get headlines from (default: "us").
  - `category` (string, optional): The category of headlines (e.g., "business", "technology").
- **Response**:
  - `country`: The country of the headlines.
  - `category`: The category of the headlines.
  - `headlines`: A list of top headlines with title, description, URL, and source.


### Requirements
- Python 3.8+
- FastAPI
- Requests
- Pydantic
- dotenv
- BeautifulSoup4

###  This project uses https://newsapi.org
