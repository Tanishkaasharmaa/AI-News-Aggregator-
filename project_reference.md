# Project Reference - AI News Aggregator

This document serves as a persistent, living reference for the AI News Aggregator project. It will be updated as the implementation progresses and is intended for future reference, deployment guidance, and onboarding.

---

## 📂 Project Structure

Currently, the basic directory layout is established:

```text
GenAI/
├── agent/                  # Agent logic and prompts
│   └── .gitkeep
├── app/                    # Application logic (Python backend)
│   ├── .gitkeep
│   ├── scraper.py          # Contains YouTubeScraper class (and later blog scraping logic)
│   ├── test_youtube.py     # CLI utility to test YouTube channel scraper and transcript retrieval
├── docker/                 # Container files (PostgreSQL)
│   └── .gitkeep
├── project_reference.md    # This reference document
├── pyproject.toml          # Project configuration & python dependencies
├── requirements.txt        # python dependencies for pip
└── README.md               # User-facing project documentation
```

---

## 🛠️ Tech Stack & Dependencies

- **Language**: Python >= 3.10
- **Database**: PostgreSQL (containerized for local dev, Render Postgres for production)
- **Database ORM**: SQLAlchemy 2.0+
- **LLM Engine**: Gemini API (`gemini-2.5-flash` default / `gemini-2.5-pro` configurable)
- **Email Service**: Resend API (primary) & standard SMTP (fallback)
- **Deployment & Scheduler**: Render Web Service/Cron Jobs

### Python Packages (configured in `pyproject.toml` and `requirements.txt`):
- `sqlalchemy` (ORM and connection management)
- `psycopg2-binary` (PostgreSQL driver)
- `google-genai` (Gemini API integration)
- `requests` (Web page downloading)
- `beautifulsoup4` (HTML parsing & content extraction)
- `feedparser` (YouTube RSS XML parsing)
- `youtube-transcript-api` (YouTube video transcripts)
- `python-dotenv` (Environment config management)
- `resend` (Email client)

---

## 🚀 Getting Started

### 1. Install Dependencies
You can install the dependencies specified in [requirements.txt](file:///d:/Projects/GenAI/requirements.txt) or [pyproject.toml](file:///d:/Projects/GenAI/pyproject.toml) using `pip`:

```bash
# Using standard pip (recommended):
pip install -r requirements.txt

# Or install editable project package:
pip install -e .
```

*Note: The manual `pip install` commands for these libraries are documented below for reference:*
```bash
pip install sqlalchemy psycopg2-binary google-genai requests beautifulsoup4 feedparser youtube-transcript-api python-dotenv resend
```

---

## 📋 Development Roadmap

1. [x] **Project Scaffolding**: Setup folder structure, dependencies (`pyproject.toml`, `requirements.txt`).
2. [ ] **Docker Database**: Create minimal local PostgreSQL container environment.
3. [ ] **DB Models**: Define SQLAlchemy models (`Source`, `Article`, `DailyDigest`).
4. [ ] **Scrapers**: Implement YouTube RSS parser and web content scrapers.
5. [ ] **Gemini Agent Integration**: Establish agent system prompt and LLM digest compiler.
6. [ ] **Notifier**: Implement email dispatching (Resend & SMTP).
7. [ ] **Orchestrator**: Create CLI commands to run the jobs.
8. [ ] **Deployment Guide**: Write instructions for deploying as a Render Cron Job.
