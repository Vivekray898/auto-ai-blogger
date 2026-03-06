"""Main orchestrator tying together all agents.

This script can be run as a standalone process to execute the full pipeline for
one or more seed keywords.  Each agent runs as a separate module; the
orchestrator handles retries, fallbacks, concurrency, and publishes the final
result to WordPress.
"""

import asyncio
import logging
from typing import Dict, Any, List

from config import (
    SCRAPE_DEPTH,
    SEED_KEYWORDS,
    TOPIC_SOURCE,
    MAX_POSTS_PER_DAY,
)
from utils import setup_logging

from agents import (
    scraper_outline,
    writer_agent,
    content_gap_seo,
    rewrite_agent,
    image_publisher,
)


async def run_pipeline_for_topic(topic: str) -> Dict[str, Any]:
    logging.info("=== pipeline start for '%s' ===", topic)

    # 1. gather competitor URLs by scraping each source
    scraped_pages = []
    for src in TOPIC_SOURCE:
        urls = scraper_outline.scrape_topics(topic, SCRAPE_DEPTH)
        for url in urls:
            scraped_pages.append(scraper_outline.scrape_competitor(url))
    logging.debug("scraped %d competitor pages", len(scraped_pages))

    # 2. build a clean outline
    outline = scraper_outline.build_outline(scraped_pages)
    if not outline.get("h1"):
        outline["h1"] = topic
    logging.debug("outline: %s", outline)

    # 3. optionally build notes map from scraped bullets or headings
    notes_map: Dict[str, str] = {}
    for page in scraped_pages:
        for sec in outline.get("sections", []):
            if sec["title"] in page.get("headings", []) or sec["title"] in page.get("bullets", []):
                notes_map.setdefault(sec["title"], "")
                notes_map[sec["title"]] += "\n" + "\n".join(page.get("bullets", []))

    # 4. generate draft using writer agent
    draft_sections = await writer_agent.generate_article(outline, notes_map)
    full_draft = "\n".join(draft_sections.values())

    # 5. run content gap detection against competitor text bodies
    comp_texts = [" ".join(p.get("headings", []) + p.get("bullets", [])) for p in scraped_pages]
    gaps = content_gap_seo.detect_gaps(full_draft, comp_texts)
    if gaps:
        logging.warning("Detected content gaps that may need manual review: %s", gaps)

    # 6. SEO metadata optimization
    seo_meta = content_gap_seo.optimize_seo({"title": outline.get("h1", topic)}, full_draft)

    # 7. rewrite entire draft if flagged
    if rewrite_agent.check_ai_generated(full_draft):
        full_draft = rewrite_agent.rewrite_text(full_draft)
        logging.info("Draft rewritten for human tone")

    # 8. assemble final HTML with images
    html_parts: List[str] = []
    html_parts.append(f"<h1>{outline.get('h1')}</h1>")
    for title, tbody in draft_sections.items():
        img = image_publisher.fetch_image_for_section(title)
        html_parts.append(f"<h2>{title}</h2>")
        if img:
            html_parts.append(f"<img src=\"{img}\" alt=\"{title}\" />")
        html_parts.append(f"<p>{tbody}</p>")
    final_html = "\n".join(html_parts)

    # 9. publish
    publish_resp: Dict[str, Any]
    try:
        publish_resp = image_publisher.publish_to_wordpress(outline.get("h1"), final_html, seo_meta)
        logging.info("published id=%s", publish_resp.get("id"))
    except Exception as exc:
        logging.error("publish failed: %s", exc)
        publish_resp = {"error": str(exc)}

    return {
        "topic": topic,
        "outline": outline,
        "draft": full_draft,
        "seo_meta": seo_meta,
        "publish": publish_resp,
        "html": final_html,
    }


def main():
    setup_logging()
    topics = SEED_KEYWORDS
    results: List[Dict[str, Any]] = []

    async def runner():
        for t in topics[:MAX_POSTS_PER_DAY]:
            res = await run_pipeline_for_topic(t)
            results.append(res)

    asyncio.run(runner())

    print("pipeline finished")
    for r in results:
        print("---")
        print(r["topic"], "-> publish response", r.get("publish"))
        print("HTML snippet:\n", r.get("html")[:500])


if __name__ == "__main__":
    main()
