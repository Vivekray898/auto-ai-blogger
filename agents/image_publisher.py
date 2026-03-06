"""Image fetching and WordPress publishing agent.

Provides helpers to obtain royalty-free images from Unsplash or Pexels and to
create posts using the WordPress REST API.  All network calls are retried a few
times via the ``utils.retry`` decorator.
"""

import logging
from typing import Dict, Any

import requests

from config import (
    UNSPLASH_API_KEY,
    PEXELS_API_KEY,
    WORDPRESS_URL,
    WORDPRESS_USER,
    WORDPRESS_APP_PASSWORD,
)
from utils import retry


@retry(max_attempts=3)
def _unsplash_random(query: str) -> str:
    """Return a random image URL from Unsplash matching the query."""
    if not UNSPLASH_API_KEY:
        raise RuntimeError("Unsplash key not configured")
    url = "https://api.unsplash.com/photos/random"
    params = {"query": query, "orientation": "landscape"}
    headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("urls", {}).get("regular", "")


@retry(max_attempts=3)
def _pexels_search(query: str) -> str:
    """Return first photo URL from Pexels search."""
    if not PEXELS_API_KEY:
        raise RuntimeError("Pexels key not configured")
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 1}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    photos = data.get("photos", [])
    if photos:
        return photos[0].get("src", {}).get("original", "")
    return ""


def fetch_image_for_section(query: str) -> str:
    """Return a URL for an image matching the query.

    Try Unsplash first, fall back to Pexels.  If both APIs fail we return an
    empty string.
    """
    logging.info("Fetching image for section '%s'", query)
    try:
        return _unsplash_random(query)
    except Exception as e:
        logging.warning("Unsplash fetch failed for '%s': %s", query, e)
    try:
        return _pexels_search(query)
    except Exception as e:
        logging.warning("Pexels fetch failed for '%s': %s", query, e)
    return ""


@retry(max_attempts=2)
def publish_to_wordpress(title: str, content: str, seo_meta: Dict[str, Any]) -> Dict[str, Any]:
    """Create or update a WordPress post via REST API.

    ``seo_meta`` should already be formatted for RankMath (focus keyword,
    meta description, slug, internal_links, faq_schema, etc.).
    Throws on HTTP errors.
    """
    logging.info("Publishing post '%s' to WordPress", title)
    data: Dict[str, Any] = {
        "title": title,
        "content": content,
        "status": "publish",
        "rank_math": seo_meta,
    }
    resp = requests.post(
        WORDPRESS_URL,
        auth=(WORDPRESS_USER, WORDPRESS_APP_PASSWORD),
        json=data,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print("image->", fetch_image_for_section("python tutorial"))
    try:
        print(publish_to_wordpress("Test", "<p>hello</p>", {}))
    except Exception as ex:
        print("publish failed (expected if creds invalid):", ex)
