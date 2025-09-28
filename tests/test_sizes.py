from collections.abc import Callable
from itertools import product
import string

import what2_grapheme.fast_re.api as fast_api

impls: tuple[Callable[[str], list[int]], ...] = (
    fast_api.grapheme_sizes,
)


def test_simple():
    case_sizes: tuple[tuple[str, list[int]], ...] = (
        ("", []),
        ("a", [1]),
        ("abc", [1, 1, 1]),
    )

    for (case, sizes), impl in product(case_sizes, impls):
        assert impl(case) == sizes


def test_crlf():
    for impl in impls:
        assert impl("\r\n") == [2]


def test_ascii_sizes():
    for impl in impls:
        sizes = impl(string.ascii_letters)
        assert len(sizes) == len(string.ascii_letters)
        assert set(sizes) == {1}


def test_emoji_zwj():
    woman = "\U0001F469"
    zwj = "\u200D"
    rocket = "\U0001F680"
    woman_astronaut = woman + zwj + rocket

    for impl in impls:
        assert impl(woman_astronaut) == [3]


def test_emoji_zwj_compound():
    woman = "\U0001F469"
    zwj = "\u200D"
    rocket = "\U0001F680"
    woman_astronaut = woman + zwj + rocket

    compound_strs = [
        (f"abc{woman_astronaut}abc", [1, 1, 1, 3, 1, 1, 1]),
        (f"{woman_astronaut}abc", [3, 1, 1, 1]),
        (f"abc{woman_astronaut}", [1, 1, 1, 3]),
    ]
    for (data, data_sizes), impl in product(compound_strs, impls):
        assert impl(data) == data_sizes
