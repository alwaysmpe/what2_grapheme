from collections.abc import Callable
from itertools import product

from what2.debug import dbg

from what2_grapheme.fast_re import api as fast_api
from what2_grapheme.fast_sm import api as fast_sm_api

import pytest
import ugrapheme

impls: tuple[Callable[[str, int | None, int | None], str], ...] = (
    fast_api.strslice,
    fast_sm_api.strslice,
)


@pytest.fixture(params=[
    (None, None),
    (None, 1),
    (None, 2),
    (None, 3),
    (None, 10),
    (None, 0),
    (None, 100),
    (None, 1000),
    (0, None),
    (1, None),
    (10, None),
    (1, 10),
    (3, 10),
    (8, 8),
    (16, 18),
    (-1, 10),
    (-10, -2),
    (None, -4),
    (None, -1),
    (-1, None),
])
def slice_pair(request: pytest.FixtureRequest) -> tuple[int | None, int | None]:
    return request.param


@pytest.fixture
def slice_start(slice_pair: tuple[int | None, int | None]) -> int | None:
    return slice_pair[0]


@pytest.fixture
def slice_stop(slice_pair: tuple[int | None, int | None]) -> int | None:
    return slice_pair[1]


def test_short_slice(slice_start: int | None, slice_stop: int | None):

    zwj = "\u200D"

    eg_strs = (
        (eg_str, f"{zwj.join(eg_str)}{zwj}")
        for eg_str in (
            "a",
            "a" * 2,
            "a" * 3,
            "a" * 5,
            "a" * 9,
            "a" * 10,
            "a" * 11,
            "a" * 12,
        )
    )

    for (eg_str, eg_zwj_str), impl in product(eg_strs, impls):
        start = slice_start
        stop = slice_stop

        expected = eg_str[start: stop]
        expected_zwj = zwj.join(expected) + zwj * bool(expected)

        result = "<no value returned>"
        result_zwj = "<no value returned>"

        try:
            result = impl(eg_str, start, stop)
            assert result == expected
        except:
            dbg(eg_str)
            dbg(len(eg_str))
            dbg(start)
            dbg(stop)
            dbg(expected)
            dbg(len(expected))
            dbg(result)
            dbg(len(result))
            raise

        try:
            result_zwj = impl(eg_zwj_str, start, stop)
            assert result_zwj == expected_zwj
        except:
            dbg(eg_zwj_str)
            dbg(len(eg_zwj_str))
            dbg(start)
            dbg(stop)
            dbg(expected_zwj)
            dbg(len(expected_zwj))
            dbg(result_zwj)
            dbg(len(result_zwj))
            raise


def test_slice(slice_start: int | None, slice_stop: int | None):
    eg_str = "abcdefghi" * 10
    zwj = "\u200D"
    eg_zwj_str = zwj.join(eg_str) + zwj
    start = slice_start
    stop = slice_stop
    expected = eg_str[start: stop]
    expected_zwj = zwj.join(expected) + zwj * bool(expected)
    result = "<no value returned>"
    result_zwj = "<no value returned>"

    for impl in impls:
        try:
            result = impl(eg_str, start, stop)
            assert expected == result
        except Exception:
            dbg(eg_str)
            dbg(len(eg_str))
            dbg(start)
            dbg(stop)
            dbg(result)
            dbg(len(result))
            raise
        try:
            result_zwj = impl(eg_zwj_str, start, stop)
            assert result_zwj == expected_zwj
        except Exception:
            dbg(eg_zwj_str)
            dbg(len(eg_zwj_str))
            dbg(start)
            dbg(stop)
            dbg(result_zwj)
            dbg(len(result_zwj))
            raise
