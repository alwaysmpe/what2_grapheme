import re

import grapheme.api as api
from what2_utf_data.load import break_test
from what2_utf_parse.parse import parse_utf_delimited
from what2_grapheme import chunk

import pandas as pd
from what2 import dbg
import pytest

type StrTestCase = tuple[str, list[str]]
type SizeTestCase = tuple[str, list[int]]


def load_break_test_data() -> list[str]:
    with break_test() as path:
        data_df = parse_utf_delimited(path, ["break_eg"])
    
    data: pd.Series[str] = data_df["break_eg"].str.strip()
    data = data.str.strip("÷ ")
    return list(data)


break_test_data = load_break_test_data()


@pytest.fixture(params=range(len(break_test_data)))
def break_idx(request: pytest.FixtureRequest) -> int:
    return request.param


@pytest.fixture
def break_str_case(break_idx: int) -> str:
    return break_test_data[break_idx]


break_pat: re.Pattern[str] = re.compile(f" [×÷] ")
@pytest.fixture
def case_str(break_str_case: str) -> str:
    return "".join(
        chr(int(chunk, base=16))
        for chunk in break_pat.split(break_str_case)
    )


@pytest.fixture
def case_str_chunks(break_str_case: str) -> list[str]:
    str_chunks: list[str] = []
    
    chunks = break_str_case.split(" ÷ ")

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


def test_grapheme_sizes(case_str: str, case_str_sizes: list[int], break_str_case: str):
    sizes = chunk.grapheme_sizes(case_str)
    if sizes != case_str_sizes:
        props = chunk.default_properties()
        # dbg(case_str)
        dbg(break_str_case)
        for char in case_str:
            dbg(props.char_to_enum(char))

    assert sizes == case_str_sizes


def test_grapheme_chunks(case_str: str, case_str_chunks: list[int]):
    chunks = chunk.graphemes(case_str)
    assert chunks == case_str_chunks



# def load_break_tests():
#     with break_test() as path:
#         data_df = parse_utf_delimited(path, ["break_eg"])
    
#     data: pd.Series[str] = data_df["break_eg"].str.strip()
#     data = data.str.strip("÷ ")
#     str_test_egs: list[StrTestCase] = []
#     size_test_egs: list[SizeTestCase] = []

#     print(data)
#     for row in data:
#         str_case: list[str] = []
#         size_case: list[int] = []
#         chunks = row.split(" ÷ ")
        
#         for chunk in chunks:
#             chunk_codes = chunk.split(" ÷ ")
#             size_case.append(len(chunk_codes))
#             str_case.append("".join(
#                 chr(int(code, base=16))
#                 for code in chunk_codes
#             ))
        
#         test_str = "".join(str_case)

#         str_test_egs.append((test_str, str_case))
#         size_test_egs.append((test_str, size_case))




# def test_breaks():
#     data = load_break_tests()


