"""Main orchestrator that ties together all agents into a pipeline."""

import asyncio
import logging
from typing import Dict, Any, List

from config import SCRAPE_DEPTH, TOPIC_SOURCE, MAX_POSTS_PER_DAY
from utils import setup_logging, retry

from agents import (
    scraper_outline,
    writer_agent,
    content_gap_seo,
    rewrite_agent,
    image_publisher,
)


async def run_pipeline_for_topic(topic: str) -> Dict[str, Any]:
    """Run the full cycle of scraping, writing, SEO, rewriting, and publishing."""
    logging.info("=== Starting pipeline for topic: %s ===", topic)

    # 1. Scrape competitors
    scraped = []
    for src in TOPIC_SOURCE:
        urls = scraper_outline.scrape_topics(src, SCRAPE_DEPTH)
        for url in urls:
            scraped.append(scraper_outline.scrape_competitor(url))

    # 2. Build outline
    outline = scraper_outline.build_outline(scraped)

    # 3. Write draft
    draft_sections = await writer_agent.generate_article(outline)

    # 4. Combine draft text
    full_draft = "\n".join(draft_sections.values())

    # 5. SEO analysis / content gap detection
    gaps = content_gap_seo.detect_gaps(full_draft, [x.get("title", "") for x in scraped])
    logging.info("Content gaps found: %s", gaps)
    seo_meta = content_gap_seo.optimize_seo({})

    # 6. Rewrite if AI detected
    if rewrite_agent.check_ai_generated(full_draft):
        full_draft = rewrite_agent.rewrite_text(full_draft)

    # 7. Insert images
    final_content = full_draft
    for title, text in draft_sections.items():
        img_url = image_publisher.fetch_image_for_section(title)
        final_content = final_content.replace(text, f"<h2>{title}</h2>\n<p>{text}</p>\n<img src=\"{img_url}\" />")

    # 8. Publish
    try:
        pub_resp = image_publisher.publish_to_wordpress(outline.get("h1", topic), final_content, seo_meta)
        logging.info("Published successfully: %s", pub_resp.get("id"))
    except Exception as e:
        logging.error("Publishing failed: %s", e)
        pub_resp = {"error": str(e)}

    return {
        "topic": topic,
        "outline": outline,
        "draft": full_draft,
        "seo_meta": seo_meta,
        "publish": pub_resp,
    }


def main():
    setup_logging()
    topics = ["Example Topic"]
    results = []

    async def runner():
        for t in topics[:MAX_POSTS_PER_DAY]:
            res = await run_pipeline_for_topic(t)
            results.append(res)

    asyncio.run(runner())
    print("Pipeline finished. Results:")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
