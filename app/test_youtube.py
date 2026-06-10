import sys
from datetime import datetime, timezone
from app.youtube_scraper import YouTubeScraper, YouTubeVideo

def main():
    print("=" * 60)
    print("YouTube Scraping & Transcript Test Utility (YouTubeScraper + Pydantic)")
    print("=" * 60)

    # Dictionary of test channels: Name -> Channel ID
    test_channels = {
        "OpenAI": "UCXZCJLdBC09xxGZ6gcdrc6A",
        "3Blue1Brown": "UCYO_jab_esuFRV4b17AJtAw",
    }

    # Instantiate the scraper class
    scraper = YouTubeScraper()

    print("\n--- TEST 1: Fetching Latest Videos (Last 7 Days / 168 Hours for testing) ---")
    max_age_hours = 168.0  # Use 7 days to make sure we find at least one video
    
    first_video_found = None
    for name, channel_id in test_channels.items():
        print(f"Fetching videos for {name} (ID: {channel_id}) from the last {max_age_hours} hours...")
        videos = scraper.fetch_latest_videos(channel_id, max_age_hours=max_age_hours)
        print(f"  Found {len(videos)} videos:")
        for idx, video in enumerate(videos, start=1):
            print(f"    {idx}. [{video.published_at}] {video.title}")
            print(f"       URL: {video.link} (ID: {video.video_id})")
            if not first_video_found:
                first_video_found = video
        print()

    # Fallback if no videos found in the last 7 days
    if not first_video_found:
        print("No videos found in the last 7 days. Trying with a default video ID for transcript test...")
        first_video_found = YouTubeVideo(
            video_id="d2ixUSNCv1A",
            title="Default Test Video (3Blue1Brown)",
            link="https://www.youtube.com/watch?v=d2ixUSNCv1A",
            published_at=datetime.now(timezone.utc),
            description="Fallback video for testing transcripts."
        )

    print("--- TEST 2: Transcript Fetching ---")
    print(f"Fetching transcript for: '{first_video_found.title}'")
    print(f"Video ID: {first_video_found.video_id}")
    print("Retrieving...")
    
    transcript = scraper.get_video_transcript(first_video_found.video_id)
    if transcript:
        print("  SUCCESS!")
        print("-" * 50)
        # Show first 500 characters of the transcript text property
        text = transcript.text
        preview = text[:500] + "..." if len(text) > 500 else text
        print(preview)
        print("-" * 50)
        print(f"Total transcript length: {len(text)} characters.")
    else:
        print("  FAILED to fetch transcript (e.g., transcripts disabled, or video has no subtitles).")
    
    print("\nTest completed.")

if __name__ == "__main__":
    main()
