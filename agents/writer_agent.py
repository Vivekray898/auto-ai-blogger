"""Writer Agent: produces long-form content for each section."""

import asyncio
import logging
from typing import Dict, List

from config import PRIMARY_WRITER_MODEL, SECONDARY_WRITER_MODEL


async def generate_section(section: Dict[str, str], model: str) -> str:
    """Generate text for a single section using the chosen model.

    In a production pipeline this would call an AI service. Here we just
    simulate latency and echo the title.
    """
    logging.info("Generating content for section '%s' with model %s", section["title"], model)
    await asyncio.sleep(0.1)  # simulate network delay
    return f"Content for {section['title']} (model: {model})\n"


async def generate_article(outline: Dict[str, any]) -> Dict[str, str]:
    """Generate content for every section in the outline with fallbacks.

    Returns a mapping from section title to generated text.
    """
    sections = outline.get("sections", [])
    results: Dict[str, str] = {}

    async def generate_with_fallback(sec):
        try:
            return await generate_section(sec, PRIMARY_WRITER_MODEL)
        except Exception as e:
            logging.warning("Primary model failed: %s", e)
            try:
                return await generate_section(sec, SECONDARY_WRITER_MODEL)
            except Exception as e2:
                logging.error("Secondary model also failed: %s", e2)
                return f"[Failed to generate section {sec['title']}]"

    tasks = [generate_with_fallback(sec) for sec in sections]
    contents = await asyncio.gather(*tasks)
    for sec, text in zip(sections, contents):
        results[sec["title"]] = text
    return results


# quick test when run directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sample_outline = {"sections": [{"title": "Intro"}, {"title": "Body"}]}
    article = asyncio.run(generate_article(sample_outline))
    print(article)
