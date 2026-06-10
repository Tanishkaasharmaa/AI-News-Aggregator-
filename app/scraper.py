import re
import os
from datetime import datetime, timezone
from calendar import timegm
import requests
import feedparser
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# --- YouTube Models ---
class YouTubeVideo(BaseModel):
    """
    Pydantic model representing a single YouTube video.
    """
    video_id: str
    title: str
    link: str
    published_at: datetime
    description: str

class VideoTranscript(BaseModel):
    """
    Pydantic model representing a YouTube video transcript.
    """
    text: str

# --- OpenAI Models ---
class OpenAIArticle(BaseModel):
    """
    Pydantic model representing an OpenAI news article.
    """
    title: str
    description: str
    link: str
    published_at: datetime

# --- Scraper Classes ---
class YouTubeScraper:
    """
    Scraper class to handle fetching latest videos and transcripts from YouTube channels.
    """
    def __init__(self):
        # Initialize the API client once for reuse
        self.api = YouTubeTranscriptApi()

    def fetch_latest_videos(self, channel_id: str, max_age_hours: float = 24.0) -> list[YouTubeVideo]:
        """
        Fetches latest videos from a YouTube channel RSS feed using its Channel ID and filters them by time.
        Returns a list of YouTubeVideo Pydantic models.
        """
        if not (channel_id.startswith("UC") and len(channel_id) == 24):
            print(f"Warning: '{channel_id}' does not appear to be a valid YouTube Channel ID (should start with 'UC' and be 24 characters).")

        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        
        try:
            feed = feedparser.parse(feed_url)
            if not feed.entries:
                if hasattr(feed, 'bozo') and feed.bozo:
                    print(f"Feed parsing error for channel {channel_id}: {feed.bozo_exception}")
                return []
            
            now_utc = datetime.now(timezone.utc)
            filtered_videos = []
            
            for entry in feed.entries:
                # Parse publication time
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published_dt = datetime.fromtimestamp(timegm(entry.published_parsed), timezone.utc)
                else:
                    try:
                        published_dt = datetime.fromisoformat(entry.published.replace("Z", "+00:00"))
                    except Exception:
                        continue
                
                # Filter by publication age
                age = now_utc - published_dt
                if age.total_seconds() <= max_age_hours * 3600:
                    video_id = None
                    if hasattr(entry, "id") and entry.id.startswith("yt:video:"):
                        video_id = entry.id.split(":")[-1]
                    else:
                        watch_match = re.search(r"v=([a-zA-Z0-9_-]+)", entry.link)
                        if watch_match:
                            video_id = watch_match.group(1)
                    
                    if not video_id:
                        continue
                    
                    description = ""
                    if hasattr(entry, "media_description"):
                        description = entry.media_description
                    elif hasattr(entry, "summary"):
                        description = entry.summary
                    
                    # Instantiate Pydantic model
                    video_model = YouTubeVideo(
                        video_id=video_id,
                        title=entry.title,
                        link=entry.link,
                        published_at=published_dt,
                        description=description
                    )
                    filtered_videos.append(video_model)
            
            return filtered_videos

        except Exception as e:
            print(f"Error fetching RSS feed for channel {channel_id}: {e}")
            return []

    def get_video_transcript(self, video_id: str) -> VideoTranscript | None:
        """
        Fetches the full transcript text of a YouTube video using the youtube-transcript-api.
        Returns a VideoTranscript Pydantic model, or None if transcripts are unavailable.
        """
        try:
            transcript_list = self.api.fetch(video_id)
            # Join lines with spaces using the text attribute
            text_lines = [item.text for item in transcript_list]
            full_text = " ".join(text_lines)
            
            # Return as VideoTranscript Pydantic model
            return VideoTranscript(text=full_text)
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"Transcript not available for video {video_id}: {e}")
            return None
        except Exception as e:
            print(f"Error retrieving transcript for video {video_id}: {e}")
            return None


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
