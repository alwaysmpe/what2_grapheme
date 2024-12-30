from collections.abc import Iterable, Iterator
from itertools import islice


def sliding_window[T](iterable: Iterable[T], size: int) -> Iterator[list[T]]:
    iterator = iter(iterable)
    if (size - 1) < 0:
        raise ValueError
    window = list(islice(iterator, size - 1))

    for x in iterator:
        window.append(x)
        yield window
        window.pop(0)
