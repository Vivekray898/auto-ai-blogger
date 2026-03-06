"""Writer Agent: produces long-form content for each section.

This module handles section-by-section generation using distributed AI models.
A semaphore limits concurrent calls (section parallelism) and fallback logic
ensures that if a primary model fails the code will transparently try a
secondary. The actual ``_call_model`` function is a stub which should be
replaced with real API/SDK invocations in a production deployment.
"""

import asyncio
import logging
import random
from typing import Dict, List

from config import (
    PRIMARY_WRITER_MODEL,
    SECONDARY_WRITER_MODEL,
    SECTION_PARALLELISM,
)


async def _call_model(prompt: str, model: str) -> str:
    """Simulated network call to an AI model.

    Raises an exception randomly to emulate an unreliable external service.
    In production you would invoke the real HTTP/SDK API here.
    """
    logging.debug("calling model %s for prompt length %d", model, len(prompt))
    await asyncio.sleep(random.uniform(0.1, 0.5))
    # simulate occasional failure
    if random.random() < 0.1:
        raise RuntimeError(f"simulated failure from {model}")
    # echo the prompt as 'generated' text
    return f"[{model}] Generated content for: {prompt[:60]}...\n"


async def generate_section(
    section: Dict[str, str], model: str, notes: str = ""
) -> str:
    """Produce text for a single section using ``model``.

    ``notes`` can contain research or competitor excerpts to condition on.
    """
    prompt = f"Write an in-depth article section for the heading '{section['title']}'.\n"
    if notes:
        prompt += f"\nResearch notes:\n{notes}\n"
    return await _call_model(prompt, model)


async def generate_article(
    outline: Dict[str, any], notes_map: Dict[str, str] = None
) -> Dict[str, str]:
    """Generate all section texts in parallel with throttling and fallbacks.

    Args:
        outline: dictionary containing ``sections`` list of ``{'title':...}``.
        notes_map: optional dict mapping section title to supporting notes.
    Returns:
        mapping from section title to generated string.
    """
    if notes_map is None:
        notes_map = {}
    sections = outline.get("sections", [])
    results: Dict[str, str] = {}
    sem = asyncio.Semaphore(SECTION_PARALLELISM)

    async def worker(sec):
        async with sem:
            title = sec["title"]
            for model in (PRIMARY_WRITER_MODEL, SECONDARY_WRITER_MODEL):
                try:
                    return await generate_section(sec, model, notes_map.get(title, ""))
                except Exception as e:
                    logging.warning("section '%s' failed on %s: %s", title, model, e)
            logging.error("all writer models failed for section %s", title)
            return f"[could not generate content for {title}]"

    tasks = [worker(sec) for sec in sections]
    outputs = await asyncio.gather(*tasks)
    for sec, out in zip(sections, outputs):
        results[sec["title"]] = out
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sample_outline = {"sections": [{"title": "Intro"}, {"title": "Body"}]}
    article = asyncio.run(generate_article(sample_outline))
    for k, v in article.items():
        print(k, "->", v)

