"""Image fetching and WordPress publishing agent."""

import logging
import requests
from typing import Dict, List

from config import UNSPLASH_API_KEY, PEXELS_API_KEY, WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_APP_PASSWORD


def fetch_image_for_section(query: str) -> str:
    """Return a URL for an image matching the query.

    Try Unsplash first, fall back to Pexels. If both fail, return an empty string.
    """
    logging.info("Fetching image for query: %s", query)
    try:
        # unsplash stub
        return f"https://source.unsplash.com/featured/?{query}"
    except Exception as e:
        logging.warning("Unsplash failed: %s", e)
    try:
        # pexels stub
        return f"https://www.pexels.com/search/{query}/"
    except Exception as e:
        logging.warning("Pexels failed: %s", e)
    return ""


def publish_to_wordpress(title: str, content: str, seo_meta: Dict[str, any]) -> Dict[str, any]:
    """Create a WordPress post via REST API.

    Returns the JSON response or raises an exception.
    """
    logging.info("Publishing post to WordPress: %s", title)
    data = {
        "title": title,
        "content": content,
        "status": "publish",
        # RankMath fields could go under "rank_math" or similar depending on plugin
        "rank_math": seo_meta,
    }
    response = requests.post(
        WORDPRESS_URL,
        auth=(WORDPRESS_USER, WORDPRESS_APP_PASSWORD),
        json=data,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    img = fetch_image_for_section("python")
    print("image", img)
    try:
        resp = publish_to_wordpress("Test", "<p>hello</p>", {})
        print(resp)
    except Exception as ex:
        print("publish failed (expected if creds invalid):", ex)
