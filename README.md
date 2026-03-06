# Auto AI Blogger

A modular, distributed multi-agent blogging system written in Python 3.11+.
It is designed for SEO-driven content automation using free/low-cost AI
models, free image services, and automatic WordPress publishing.

## Folder Structure
```
auto_ai_blogger/
│
├── agents/               # independent modules for each AI agent
│   ├── scraper_outline.py
│   ├── writer_agent.py
│   ├── content_gap_seo.py
│   ├── rewrite_agent.py
│   ├── image_publisher.py
│
├── orchestrator.py       # coordinates the full pipeline
├── config.py             # user-editable settings and API keys
├── utils.py              # shared helpers (logging, retry decorator)
├── requirements.txt      # Python dependencies
└── README.md             # this document
```

## Features Demonstrated

* **Scraper & Outline Agent** – scrapes DuckDuckGo/Reddit/Quora for
  competitor URLs, extracts headings and bullets, builds a clean outline.
* **Writer Agent** – generates long-form content by section. Supports
  distributed models with fallbacks and parallelism.
* **Content Gap & SEO Agent** – uses sentence-transformers embeddings to
  identify missing points and heuristics to populate RankMath SEO fields.
* **Rewrite Agent** – detects AI-like text and rewrites it with a simple
  synonym substitution fallback.
* **Image & Publisher Agent** – fetches contextual images (Unsplash/Pexels)
  and publishes posts to WordPress with RankMath metadata.
* **Resilience** – retry decorators, fallback models, error logging.
* **Parallelism** – section-based generation with asyncio semaphores.

## Getting Started

1. **Install dependencies**:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. **Configure** `config.py`:
   * Set `SEED_KEYWORDS` to your initial topic list.
   * Populate API keys (`UNSPLASH_API_KEY`, `PEXELS_API_KEY`), WordPress
     credentials, and adjust `MAX_POSTS_PER_DAY` / `SECTION_PARALLELISM`.
3. **Run the orchestrator**:
   ```bash
   python orchestrator.py
   ```
   The script will log each step and print a snippet of the generated HTML
   along with the WordPress API response (or error).

## Sample HTML Output

The orchestrator produces HTML like the following for a topic:

```html
<h1>Example Topic</h1>
<h2>Introduction</h2>
<img src="https://source.unsplash.com/featured/?Introduction" alt="Introduction" />
<p>[gemini-1.5-pro] Generated content for...</p>
...
```

SEO meta is built automatically and attached to the WordPress post under the
`rank_math` field.

## Extending the System

* Replace stubbed model calls in `writer_agent` and `rewrite_agent` with real
  API/SDK integrations (OpenAI, Gemini, etc.).
* Improve scraping heuristics or add caching.
* Enhance SEO optimization with more sophisticated NLP models.
* Add monitoring/metrics and database persistence for production use.

## Notes

All modules are self-contained and can be run individually for testing. The
pipeline is designed to scale to dozens of posts per day; add orchestration
(e.g. Airflow, Celery) or containerization as needed.

---

This repository is a proof-of-concept; treat it as a starting point for a
full production-grade SEO content automation platform.
