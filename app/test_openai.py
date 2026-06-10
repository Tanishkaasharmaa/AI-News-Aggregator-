import sys
from datetime import datetime, timezone
from app.openai_scraper import OpenAIScraper

def main():
    print("=" * 60)
    print("OpenAI Scraping Test Utility (OpenAIScraper)")
    print("=" * 60)

    # Instantiate the OpenAI Scraper (by default fetches live, falls back to mock XML)
    scraper = OpenAIScraper()

    # We use a broad time range for testing since the mock dates are around June 8-10, 2026.
    # We will fetch articles from the last 7 days (168 hours).
    max_age_hours = 168.0

    print(f"\nFetching OpenAI articles published in the last {max_age_hours} hours...")
    articles = scraper.fetch_latest_articles(max_age_hours=max_age_hours)
    
    print(f"\nFound {len(articles)} articles:")
    print("-" * 60)
    for idx, article in enumerate(articles, start=1):
        print(f"{idx}. {article.title}")
        print(f"   Published: {article.published_at}")
        print(f"   Link:      {article.link}")
        print(f"   Summary:   {article.description}")
        print("-" * 60)
        
    print("\nTest completed.")

if __name__ == "__main__":
    main()
