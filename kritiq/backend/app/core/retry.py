"""
KRITIQ — Retry utility with exponential backoff.
"""

import asyncio
import logging
import random
from functools import wraps
from typing import Any, Callable, Tuple, Type

logger = logging.getLogger("kritiq.core.retry")


def retry_async(
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
):
    """
    Decorator for retrying async functions with exponential backoff.

    Args:
        exceptions: A tuple of exception classes that trigger a retry.
        max_retries: Maximum number of retry attempts.
        initial_delay: Initial delay in seconds.
        backoff_factor: Multiplier for the delay on subsequent attempts.
        jitter: If True, adds a random amount of delay to avoid thundering herd.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as exc:
                    last_exception = exc
                    if attempt == max_retries:
                        logger.error(
                            "Max retries (%d) reached for function %s. Final error: %s",
                            max_retries,
                            func.__name__,
                            exc,
                        )
                        raise

                    actual_delay = delay
                    if jitter:
                        actual_delay += random.uniform(0, 0.5 * delay)

                    logger.warning(
                        "Attempt %d/%d failed for function %s with error: %s. Retrying in %.2fs...",
                        attempt + 1,
                        max_retries + 1,
                        func.__name__,
                        exc,
                        actual_delay,
                    )
                    await asyncio.sleep(actual_delay)
                    delay *= backoff_factor

            if last_exception:
                raise last_exception

        return wrapper
    return decorator
