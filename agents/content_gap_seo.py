"""Content gap detection and SEO optimization agent.

This module performs both content-gap analysis and RankMath metadata
generation.  Content gaps are computed via sentence embeddings using
sentence-transformers; SEO fields are generated with simple heuristics that
can be replaced with model calls in a production system.
"""

import logging
import re
from typing import Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer, util

# load the embedding model once
_EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
_SIM_THRESHOLD = 0.75


def _sentences(text: str) -> List[str]:
    # naive sentence splitter; replace with spaCy/NLTK if needed
    return [s.strip() for s in re.split(r"(?<=[.!?]) +", text) if s.strip()]


def detect_gaps(draft: str, competitors: List[str]) -> List[str]:
    """Compare ``draft`` to ``competitors`` and return sentences that appear
under‑covered in the draft.

    Args:
        draft: full text produced by writer agent.
        competitors: list of competitor page texts (e.g. scraped content).
    """
    logging.info("Detecting content gaps in draft (length %d)", len(draft))
    if not draft:
        return []
    draft_sents = _sentences(draft)
    if not draft_sents:
        return []
    draft_emb = _EMBED_MODEL.encode(draft_sents, convert_to_tensor=True)

    gaps: List[str] = []
    for comp in competitors:
        for sent in _sentences(comp):
            emb = _EMBED_MODEL.encode(sent, convert_to_tensor=True)
            sims = util.pytorch_cos_sim(emb, draft_emb)
            if float(sims.max()) < _SIM_THRESHOLD:
                gaps.append(sent)
    logging.debug("found %d potential gaps", len(gaps))
    return gaps


def optimize_seo(meta: Dict[str, str], draft: str = "") -> Dict[str, str]:
    """Generate/complete RankMath SEO metadata from given inputs.

    ``meta`` may already contain some fields (title, focus_keyword,
    meta_description, slug, internal_links, faq_schema).  We fill missing
    values based on ``draft``.
    """
    logging.info("Optimizing SEO metadata")
    result = meta.copy()
    title = result.get("title", "")
    # focus keyword heuristic: most frequent non-stopword word
    if "focus_keyword" not in result:
        source = title or draft.split(".\n")[0]
        words = re.findall(r"\w+", source.lower())
        freq = {}
        for w in words:
            if w in ("the", "and", "for", "with", "a", "an", "to"):
                continue
            freq[w] = freq.get(w, 0) + 1
        if freq:
            result["focus_keyword"] = max(freq, key=freq.get)
    if "meta_description" not in result:
        if draft:
            result["meta_description"] = draft[:157] + ("..." if len(draft) > 160 else "")
        else:
            result["meta_description"] = ""
    if "slug" not in result:
        base = title or draft.split(".\n")[0]
        slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
        result["slug"] = slug or "post"
    result.setdefault("internal_links", [])
    result.setdefault("faq_schema", [])
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    draft = "This is a short draft. It covers some points but not everything."
    comps = ["Competitor article mentions an extra feature."]
    print("gaps", detect_gaps(draft, comps))
    seo = optimize_seo({"title": "Sample Post"}, draft)
    print("seo", seo)
