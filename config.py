"""Configuration module for auto_ai_blogger.

Place API keys and adjustable parameters here. Import this module from other
agents; update values either directly or by using environment variables in
a production setup.
"""

from typing import List

# -------- AI MODEL CONFIGURATION --------
PRIMARY_WRITER_MODEL = "gemini-1.5-pro"        # free/low-cost reasoning model
SECONDARY_WRITER_MODEL = "cerebrium-gpt-oss-120b"  # fallback distributed model
SCRAPER_MODEL = "o3-mini"
SEO_MODEL = "llama-3.3-70b"
REWRITE_MODEL = "gpt-4.1"
IMAGE_MODEL = "llama-3.1-8b"

# -------- API KEYS / ENDPOINTS --------
WORDPRESS_URL = "https://your-wordpress-site.com/wp-json/wp/v2/posts"
WORDPRESS_USER = "user"
WORDPRESS_APP_PASSWORD = "password"
UNSPLASH_API_KEY = "your_unsplash_key"
PEXELS_API_KEY = "your_pexels_key"

# -------- SCRAPING SETTINGS --------
SCRAPE_DEPTH = 3  # number of competitor pages per topic
# seeds used to bootstrap the pipeline; replace with real keywords
SEED_KEYWORDS: List[str] = ["example topic"]

# -------- RANKMATH SEO SETTINGS --------
DEFAULT_FOCUS_KEYWORD = ""
DEFAULT_META_DESCRIPTION = ""

# -------- PIPELINE SETTINGS --------
MAX_POSTS_PER_DAY = 10
SECTION_PARALLELISM = 4

# the list of topic sources is illustrative; scrape_topics handles the logic
TOPIC_SOURCE = ["duckduckgo", "reddit", "quora"]

# Add additional configuration as needed, e.g. timeouts, logging levels
