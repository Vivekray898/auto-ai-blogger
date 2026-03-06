"""Utility functions used across agents."""

import logging


def setup_logging():
    """Configure basic logging for the pipeline."""
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=logging.DEBUG,
    )


def retry(max_attempts=3):
    """Simple retry decorator for IO-bound functions."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    logging.warning(
                        "Attempt %d/%d failed for %s: %s",
                        attempt,
                        max_attempts,
                        func.__name__,
                        e,
                    )
            logging.error("All retries failed for %s", func.__name__)
            raise last_exc

        return wrapper

    return decorator
