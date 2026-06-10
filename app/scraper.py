import re
from datetime import datetime, timezone
from calendar import timegm
import feedparser
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

class YouTubeScraper:
    """
    Scraper class to handle fetching latest videos and transcripts from YouTube channels.
    """
    def __init__(self):
        # Initialize the API client once for reuse
        self.api = YouTubeTranscriptApi()

    def fetch_latest_videos(self, channel_id: str, max_age_hours: float = 24.0) -> list[dict]:
        """
        Fetches latest videos from a YouTube channel RSS feed using its Channel ID and filters them by time.
        Returns a list of videos:
          [
            {
              "video_id": "...",
              "title": "...",
              "link": "...",
              "published_at": datetime,
              "description": "..."
            },
            ...
          ]
        """
        # Channel ID validation
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
                    
                    filtered_videos.append({
                        "video_id": video_id,
                        "title": entry.title,
                        "link": entry.link,
                        "published_at": published_dt,
                        "description": description
                    })
            
            return filtered_videos

        except Exception as e:
            print(f"Error fetching RSS feed for channel {channel_id}: {e}")
            return []

    def get_video_transcript(self, video_id: str) -> str | None:
        """
        Fetches the full transcript text of a YouTube video using the youtube-transcript-api.
        Returns the transcript as a single unified string, or None if transcripts are unavailable.
        """
        try:
            transcript_list = self.api.fetch(video_id)
            text_lines = [item.text for item in transcript_list]
            return " ".join(text_lines)
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"Transcript not available for video {video_id}: {e}")
            return None
        except Exception as e:
            print(f"Error retrieving transcript for video {video_id}: {e}")
            return None
