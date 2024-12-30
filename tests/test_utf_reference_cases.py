import re

import pandas as pd
from what2 import dbg

from what2_grapheme.fast_re import api as egf_api
from what2_grapheme.fast_sm import api as fast_api
from what2_grapheme.grapheme_data.load import break_test
from what2_grapheme.grapheme_property.cache import default_properties
from what2_grapheme.grapheme_property.parse import parse_utf_delimited
from what2_grapheme.simple_sm import api as simple_api
from what2_grapheme.util.caching import cache

from tests.conftest import did_fail

import pytest

from _pytest.fixtures import SubRequest


def load_break_test_data() -> list[str]:
    with break_test() as path:
        data_df = parse_utf_delimited(path, ["break_eg"])

    data: pd.Series[str] = data_df["break_eg"].str.strip() # type: ignore reportUnknownMemberType
    data = data.str.strip("÷ ") # type: ignore reportUnknownMemberType
    return list(data)


break_test_data = load_break_test_data()


@pytest.fixture(params=range(len(break_test_data)))
def reference_idx(request: pytest.FixtureRequest) -> int:
    return request.param


@pytest.fixture
def reference_case_spec(reference_idx: int) -> str:
    return break_test_data[reference_idx]


break_pat: re.Pattern[str] = re.compile(" [×÷] ")


@pytest.fixture
def case_str(reference_case_spec: str) -> str:
    return "".join(
        chr(int(chunk, base=16))
        for chunk in break_pat.split(reference_case_spec)
    )


@pytest.fixture
def case_str_chunks(reference_case_spec: str) -> list[str]:
    str_chunks: list[str] = []

    chunks = reference_case_spec.split(" ÷ ")

    for chunk in chunks:
        chunk_codes = chunk.split(" × ")
        str_chunks.append("".join(
            chr(int(code, base=16))
            for code in chunk_codes
        ))

    return str_chunks


@pytest.fixture
def case_str_sizes(case_str_chunks: list[str]) -> list[int]:
    return [
        len(chunk)
        for chunk in case_str_chunks
    ]


@cache
def raw_lines() -> list[str]:
    with break_test() as path, path.open() as f:
        lines = f.readlines()

    return [
        line for line in lines
        if not line.startswith("#")
    ]


@pytest.fixture(autouse=True)
def debug_fail_enum_kind(request: pytest.FixtureRequest, reference_case_spec: str, case_str: str, reference_idx: int):
    assert isinstance(request, SubRequest)
    yield

    if not did_fail(request):
        return

    props = default_properties()

    dbg(reference_idx)
    dbg(reference_case_spec)
    for char in case_str:
        dbg(props.char_to_enum(char))
        dbg(props.char_to_cat(char))

    test_lines = raw_lines()

    dbg(test_lines[reference_idx])


def test_grapheme_length(case_str: str, case_str_sizes: list[int]):
    egf_length = egf_api.length(case_str)
    assert egf_length == len(case_str_sizes)
    fast_length = fast_api.length(case_str)
    assert fast_length == len(case_str_sizes)
    simple_length = simple_api.length(case_str)
    assert simple_length == len(case_str_sizes)
    # assert 0


def test_grapheme_sizes(case_str: str, case_str_sizes: list[int]):
    fast_sizes = fast_api.grapheme_sizes(case_str)
    assert fast_sizes == case_str_sizes
    simple_sizes = simple_api.grapheme_sizes(case_str)
    assert simple_sizes == case_str_sizes


def test_grapheme_chunks(case_str: str, case_str_chunks: list[int]):
    fast_chunks = fast_api.graphemes(case_str)
    assert fast_chunks == case_str_chunks
    simple_chunks = simple_api.graphemes(case_str)
    assert simple_chunks == case_str_chunks


@pytest.fixture
def ref_has_graphemes(case_str_sizes: list[int]) -> bool:
    return set(case_str_sizes) != {1}


def test_is_safe(case_str: str, ref_has_graphemes: bool):
    has_graphemes = not fast_api.is_safe(case_str, skip_crlf=False)
    assert has_graphemes == ref_has_graphemes