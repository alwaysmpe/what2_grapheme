
from collections.abc import Callable
from functools import cache as _cache
from functools import lru_cache as _lru_cache
from functools import wraps as _wraps
from types import NoneType
from typing import cast, overload


def cache[**P, R](fn: Callable[P, R]) -> Callable[P, R]:
    """
    Typed wrapper around `functools.cache`.

    Unlike `functools.cache`, the returned
    function has the same signature as the
    cached function. The callable instead
    isn't constrained to something that
    takes hashables. I think that's a better
    trade off.
    """
    return cast("Callable[P, R]", _wraps(fn)(_cache(fn)))


@overload
def lru_cache[**P, R](
        maxsize: Callable[P, R],
        *,
        typed: bool = False,
) -> Callable[P, R]:
    ...


@overload
def lru_cache[**P, R](
        maxsize: int | None = 128,
        *,
        typed: bool = False,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...


def lru_cache[**P, R](
        maxsize: Callable[P, R] | int | None = 128,
        *,
        typed: bool = False,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Typed wrapper around `functools.lru_cache`.

    Unlike `functools.lru_cache`, the returned
    function has the same signature as the cached
    function.  The callable instead isn't constrained
    to something that takes hashables. I think that's
    a bettertrade off.
    """
    if isinstance(maxsize, int | NoneType):
        def inner(fn: Callable[P, R]) -> Callable[P, R]:
            return cast("Callable[P, R]", _wraps(fn)(_lru_cache(maxsize, typed)(fn)))

        return inner

    return cast("Callable[P, R]", _wraps(maxsize)(_lru_cache(typed=typed)(maxsize)))
