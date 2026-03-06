"""AI detection and rewrite agent.

This module provides simple heuristics to identify text that looks
mechanical or AI‑generated and to rewrite it into a more human‑like tone.
In a full deployment these functions would call a strong LLM (GPT-4.1/5) to
perform paraphrasing, but here we demonstrate the control flow with simple
string transformations and a lightweight detector.
"""

import logging
import random
import re
from typing import List

# minimal synonyms map for demo purposes
_SYN_MAP = {
    "utilize": "use",
    "demonstrate": "show",
    "approximately": "about",
    "AI": "artificial intelligence",
}


def rewrite_text(text: str) -> str:
    """Rewrite text by applying simple synonym substitutions.

    Real implementation would call an AI model with instructions to rephrase
    the input.  Here we randomly replace a few words from ``_SYN_MAP``.
    """
    logging.info("Rewriting text for human-like tone")
    def replace(match):
        word = match.group(0)
        return _SYN_MAP.get(word.lower(), word)

    # apply substitutions a few times
    result = re.sub(r"\b(" + "|".join(_SYN_MAP.keys()) + r")\b", replace, text, flags=re.IGNORECASE)
    # occasionally append a connective to break monotonous patterns
    if random.random() < 0.3:
        result += "\nOverall, this section provides useful insights."
    return result


def check_ai_generated(text: str) -> bool:
    """Basic check for AI-generated style.

    Returns True if certain key phrases are present or if the lexical
    diversity is very low.  This is intentionally simplistic; a production
    system would use a specialised detector.
    """
    logging.info("Checking if text looks AI-generated")
    # common disclaimer phrase often seen in AI output
    if "as an ai language model" in text.lower():
        return True
    # check for repeated bigrams
    words = re.findall(r"\w+", text.lower())
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
    freq = {}
    for b in bigrams:
        freq[b] = freq.get(b, 0) + 1
        if freq[b] > 3:
            return True
    return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sample = "As an AI language model, I cannot..." + " test test test test"
    print("detected", check_ai_generated(sample))
    print(rewrite_text("This text will utilize AI to demonstrate functionality."))
