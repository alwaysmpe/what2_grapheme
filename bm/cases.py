from bm.rng import Generator, seeded_rng
from bm import gen
from bm import ref
from collections.abc import Iterator


def rand_ascii(count: int, length: int, rng: Generator | None = None) -> Iterator[str]:
    if rng is None:
        rng = seeded_rng()

    for _ in range(count):
        yield gen.random_ascii_string(length, rng)



def rand_utf_joined(count: int, approx_length: int, rng: Generator | None = None) -> Iterator[str]:
    if rng is None:
        rng = seeded_rng()

    for _ in range(count):
        yield ref.random_utf_string(approx_length // 3, rng)

def rand_utf_unjoined(count: int, length: int, rng: Generator | None = None) -> Iterator[str]:
    if rng is None:
        rng = seeded_rng()

    for _ in range(count):
        yield gen.random_utf_string(length, rng)
