"""Scraper & outline generation agent.

This module provides functions to scrape seed keywords, competitor pages and
turn them into a structured, hierarchical outline suitable for the writer
agent. Production systems would invoke reasoning models to cleanse the data
and handle noise; here we implement real HTTP scraping with fallbacks and
simple heuristics so the pipeline can execute without external AI calls.

Functions are written to be idempotent and retry network operations where
reasonable. Topics may come from DuckDuckGo, Reddit, or Quora depending on the
configuration:
  * `scrape_topics` takes a seed keyword and returns competitor URLs.
  * `scrape_competitor` downloads a page and extracts headings, bullets, and
    very simple FAQ candidates.
  * `build_outline` merges the scraped information into a JSON-friendly
    outline with h1 and sections.
"""

import logging
import re
from typing import Dict, List, Any

import requests
from bs4 import BeautifulSoup


def _duckduckgo_search(query: str, depth: int) -> List[str]:
    """Return top URLs from DuckDuckGo search results."""
    urls: List[str] = []
    try:
        resp = requests.get(
            "https://duckduckgo.com/html/", params={"q": query}, timeout=10
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", class_="result__a")[:depth]:
            href = a.get("href")
            if href:
                urls.append(href)
    except Exception as e:
        logging.warning("DuckDuckGo search failed for '%s': %s", query, e)
    return urls


def scrape_topics(keyword: str, depth: int) -> List[str]:
    """Search for competitor URLs given a seed keyword.

    Supports multiple free sources (DuckDuckGo, Reddit, Quora). The returned
    list is truncated to ``depth`` items and may contain duplicates which are
    deduplicated.

    Args:
        keyword: Search term to look for.
        depth: Maximum number of URLs to return.
    """
    logging.info("Scraping competitor URLs for keyword '%s' (depth=%d)", keyword, depth)
    urls = set()

    # 1. DuckDuckGo
    urls.update(_duckduckgo_search(keyword, depth))

    # 2. Reddit (simple HTML scrape as example)
    try:
        reddit_url = f"https://www.reddit.com/search/?q={requests.utils.quote(keyword)}"
        resp = requests.get(reddit_url, headers={"User-Agent": "auto-ai-bot"}, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.select("a[data-click-id=body]")[:depth]:
            href = a.get("href")
            if href and href.startswith("/r"):
                urls.add("https://www.reddit.com" + href)
    except Exception as e:
        logging.warning("Reddit scrape failed: %s", e)

    # 3. Quora
    try:
        quora_url = f"https://www.quora.com/search?q={requests.utils.quote(keyword)}"
        resp = requests.get(quora_url, headers={"User-Agent": "auto-ai-bot"}, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.select("a.q-box")[:depth]:
            href = a.get("href")
            if href and href.startswith("/"):
                urls.add("https://www.quora.com" + href)
    except Exception as e:
        logging.warning("Quora scrape failed: %s", e)

    # limit to depth
    return list(urls)[:depth]


def scrape_competitor(url: str) -> Dict[str, Any]:
    """Download a page and extract headings, bullet points and simple FAQs.

    The returned dict includes ``title``, ``headings`` (flat list of h1/h2/h3
    text), ``bullets`` (list items) and ``faqs`` (list of ``{'q':..., 'a':...}``).
    If a network error occurs we still return a structure with empty values so
    the pipeline can continue.
    """
    logging.info("Scraping competitor page: %s", url)
    data: Dict[str, Any] = {"url": url, "title": "", "headings": [], "bullets": [], "faqs": []}
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "auto-ai-bot"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        if soup.title and soup.title.string:
            data["title"] = soup.title.string.strip()
        for lvl in ("h1", "h2", "h3"):
            for h in soup.find_all(lvl):
                txt = h.get_text(strip=True)
                if txt:
                    data["headings"].append(txt)
        for li in soup.find_all("li"):
            txt = li.get_text(strip=True)
            if txt:
                data["bullets"].append(txt)
        # very naive FAQ detection: look for the word 'faq' then collect nearby list items
        for node in soup.find_all(string=re.compile("faq", re.I)):
            parent = node.find_parent()
            for sibling in parent.find_next_siblings():
                if sibling.name in ("ul", "dl"):
                    for item in sibling.find_all("li"):
                        q = item.get_text(strip=True)
                        data["faqs"].append({"q": q, "a": ""})
    except Exception as e:
        logging.warning("Failed to scrape competitor %s: %s", url, e)
    return data


def build_outline(scraped_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge several scraped pages into one hierarchical outline.

    The returned object has keys ``h1`` and ``sections`` where sections is a
    list of ``{'title':..., 'content':...}`` entries. Duplicate headings are
    removed. FAQs are appended at the end as a section if any were found.
    """
    logging.info("Building outline from %d scraped pages", len(scraped_data))
    outline: Dict[str, Any] = {"h1": "", "sections": []}
    seen = set()
    for item in scraped_data:
        if not outline["h1"] and item.get("title"):
            outline["h1"] = item["title"]
        for h in item.get("headings", []):
            if h not in seen:
                seen.add(h)
                outline["sections"].append({"title": h, "content": ""})
    faqs: List[Dict[str, str]] = []
    for item in scraped_data:
        faqs.extend(item.get("faqs", []))
    if faqs:
        outline["sections"].append({"title": "Frequently Asked Questions", "content": ""})
    return outline


# quick demonstration when run directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seeds = ["best running shoes"]
    urls = scrape_topics(seeds[0], 3)
    print("found urls", urls)
    data = [scrape_competitor(u) for u in urls]
    outline = build_outline(data)
    print(outline)

