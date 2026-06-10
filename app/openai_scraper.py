import os
from datetime import datetime, timezone
from calendar import timegm
import requests
import feedparser
from pydantic import BaseModel

class OpenAIArticle(BaseModel):
    """
    Pydantic model representing an OpenAI news article.
    """
    title: str
    description: str
    link: str
    published_at: datetime

class OpenAIScraper:
    """
    Scraper class to handle fetching latest news from OpenAI's blog RSS feed.
    Supports live fetching with a local mock fallback (to bypass Cloudflare 403 errors).
    """
    def __init__(self, source: str = "https://openai.com/news/rss"):
        self.source = source

    def fetch_latest_articles(self, max_age_hours: float = 24.0) -> list[OpenAIArticle]:
        """
        Fetches the latest OpenAI articles from the RSS source and filters them by publication time.
        """
        xml_data = None
        
        # Try fetching from web if it looks like a URL
        if self.source.startswith("http"):
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/xml, text/xml, */*",
            }
            try:
                response = requests.get(self.source, headers=headers, timeout=10)
                if response.status_code == 200:
                    xml_data = response.content
                else:
                    print(f"Failed to fetch live OpenAI feed (HTTP {response.status_code}). Falling back to mock XML.")
            except Exception as e:
                print(f"Error fetching live OpenAI feed: {e}. Falling back to mock XML.")
        
        # Fallback to local mock XML file if live fetch failed or if source is a local path
        if not xml_data:
            mock_path = self.source if not self.source.startswith("http") else os.path.join(os.path.dirname(__file__), "mock_openai_rss.xml")
            try:
                if os.path.exists(mock_path):
                    with open(mock_path, "r", encoding="utf-8") as f:
                        xml_data = f.read()
                else:
                    print(f"Mock file not found at {mock_path}.")
                    return []
            except Exception as e:
                print(f"Error reading mock file: {e}")
                return []

        # Parse XML using feedparser
        try:
            feed = feedparser.parse(xml_data)
            if not feed.entries:
                if hasattr(feed, 'bozo') and feed.bozo:
                    print(f"OpenAI feed parsing error: {feed.bozo_exception}")
                return []
                
            now_utc = datetime.now(timezone.utc)
            filtered_articles = []
            
            for entry in feed.entries:
                # Parse publication time
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published_dt = datetime.fromtimestamp(timegm(entry.published_parsed), timezone.utc)
                else:
                    try:
                        published_dt = datetime.fromisoformat(entry.published.replace("Z", "+00:00"))
                    except Exception:
                        continue
                
                # Filter by age
                age = now_utc - published_dt
                if age.total_seconds() <= max_age_hours * 3600:
                    title = entry.title if hasattr(entry, "title") else ""
                    description = entry.summary if hasattr(entry, "summary") else ""
                    link = entry.link if hasattr(entry, "link") else ""
                    
                    article = OpenAIArticle(
                        title=title,
                        description=description,
                        link=link,
                        published_at=published_dt
                    )
                    filtered_articles.append(article)
                    
            return filtered_articles
            
        except Exception as e:
            print(f"Error parsing OpenAI feed data: {e}")
            return []
