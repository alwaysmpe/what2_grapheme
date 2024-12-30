import numpy as np
from numpy.random import Generator

def __mk_seed() -> int:
    return int(np.pi * 10 ** 10)


def seeded_rng() -> Generator:
    """
    A random generator seeded with the same seed every call.

    Useful for tests and other operations where order independence is ideal.
    """
    return np.random.default_rng(__mk_seed())


__rng = seeded_rng()


def mk_rng() -> Generator:
    """
    A random generator with a deterministic but random seed.

    Will produce the same result every time the same program is run,
    but different results for each call to the function.
    """
    return __rng.spawn(1)[0]
