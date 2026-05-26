from collections.abc import Awaitable, Callable
from functools import wraps


def safe_node(fallback: Callable[[dict, Exception], dict]):
    """
    Wraps a node so exceptions become state updates instead of crashes.

    `fallback` receives the input state and the exception, and returns
    the state update the node should emit on failure.
    """

    def decorator(fn: Callable[[dict], Awaitable[dict]]):
        @wraps(fn)
        async def wrapper(state: dict) -> dict:
            try:
                return await fn(state)
            except Exception as exc:
                print(
                    f"node.failed node={fn.__name__} error={type(exc).__name__}: {exc}",
                    flush=True,
                )
                return fallback(state, exc)

        return wrapper

    return decorator
