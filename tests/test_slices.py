from what2 import dbg

from what2_grapheme.fast_re import api as egf_api
from what2_grapheme.fast_sm import api

import pytest


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


def test_short_gslice_sm(slice_start: int | None, slice_stop: int | None):

    eg_strs = [
        "a",
        "a" * 2,
        "a" * 3,
        "a" * 5,
        "a" * 9,
        "a" * 10,
        "a" * 11,
        "a" * 12,
    ]
    zwj = "\u200D"
    for eg_str in eg_strs:
        print("start " + "-" * 40)
        eg_zwj_str = zwj.join(eg_str) + zwj
        start = slice_start
        stop = slice_stop
        bstr = eg_str[start: stop]
        gstr = "<test not run>"
        try:
            gstr = api.strslice(eg_str, start, stop)
            assert gstr == bstr
        except Exception:
            dbg(eg_str)
            dbg(len(eg_str))
            dbg(start)
            dbg(stop)
            dbg(len(bstr))
            dbg(len(gstr))
            raise

        print("start " + "-" * 40)
        b_zwj_str = zwj.join(bstr) + zwj * bool(bstr)
        bstr = ""
        g_zwj_str = "<test not run>"

        try:
            g_zwj_str = api.strslice(eg_zwj_str, start, stop)
            assert g_zwj_str == b_zwj_str
        except Exception:
            dbg(len(eg_zwj_str))
            dbg(start)
            dbg(stop)
            dbg(len(g_zwj_str))
            dbg(len(b_zwj_str))
            raise


def test_short_gslice_re(slice_start: int | None, slice_stop: int | None):

    eg_strs = [
        "a",
        "a" * 2,
        "a" * 3,
        "a" * 5,
        "a" * 9,
        "a" * 10,
        "a" * 11,
        "a" * 12,
    ]
    zwj = "\u200D"
    for eg_str in eg_strs:
        print("start " + "-" * 40)
        eg_zwj_str = zwj.join(eg_str) + zwj
        start = slice_start
        stop = slice_stop
        bstr = eg_str[start: stop]
        estr = "<test not run>"
        try:
            estr = egf_api.strslice(eg_str, start, stop)
            assert estr == bstr
        except Exception:
            dbg(len(eg_str))
            dbg(start)
            dbg(stop)
            dbg(len(bstr))
            dbg(len(estr))
            raise

        print("start " + "-" * 40)
        b_zwj_str = zwj.join(bstr) + zwj * bool(bstr)
        # bstr = ""
        e_zwj_str = "<test not run>"

        try:
            e_zwj_str = egf_api.strslice(eg_zwj_str, start, stop)
            assert e_zwj_str == b_zwj_str
        except Exception:
            dbg(len(eg_zwj_str))
            dbg(start)
            dbg(stop)
            dbg(len(e_zwj_str))
            dbg(len(b_zwj_str))
            raise


def test_gslice(slice_start: int | None, slice_stop: int | None):

    eg_str = "abcdefghi" * 10
    zwj = "\u200D"
    eg_zwj_str = zwj.join(eg_str) + zwj
    start = slice_start
    stop = slice_stop

    gstr = api.strslice(eg_str, start, stop)
    estr = egf_api.strslice(eg_str, start, stop)
    bstr = eg_str[start: stop]
    try:
        assert gstr == bstr
        assert estr == bstr
    except Exception:
        dbg(len(eg_str))
        dbg(start)
        dbg(stop)
        dbg(len(gstr))
        dbg(len(estr))
        dbg(len(bstr))
        raise

    g_zwj_str = api.strslice(eg_zwj_str, start, stop)
    e_zwj_str = egf_api.strslice(eg_zwj_str, start, stop)
    b_zwj_str = zwj.join(bstr) + zwj * bool(bstr)

    try:
        assert g_zwj_str == b_zwj_str
        assert e_zwj_str == b_zwj_str
    except Exception:
        dbg(len(eg_zwj_str))
        dbg(start)
        dbg(stop)
        dbg(len(g_zwj_str))
        dbg(len(e_zwj_str))
        dbg(len(b_zwj_str))
        raise
