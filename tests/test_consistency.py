from collections import defaultdict as defaultdict
import re

from grapheme import api as gr_api
import regex
import ugrapheme
from what2.debug import dbg

from what2_grapheme import api
from what2_grapheme.grapheme_property.cache import default_properties as default_properties

from tests.data import break_test, segmenter_test
from tests.data.parse import parse_utf_delimited

import pytest


def load_break_test_data() -> list[str]:
    with break_test() as path:
        data_df = parse_utf_delimited(path, ["break_eg"])

    data = data_df["break_eg"].str.strip() # type: ignore reportUnknownMemberType
    data = data.str.strip("÷ ") # type: ignore reportUnknownMemberType
    return list(data)


def load_break_cases() -> list[str]:
    data = load_break_test_data()
    break_pat: re.Pattern[str] = re.compile(r" [×÷] ")

    return [
        "".join(
            chr(int(chunk, base=16))
            for chunk in break_pat.split(reference_case_spec)
        )
        for reference_case_spec in data
    ]


def load_segmenter_test_data() -> list[tuple[str, str, str]]:
    all_lines: list[tuple[str, str]] = []
    for file in segmenter_test():
        with file() as path:
            all_lines.extend(
                (f"{path.name}_{idx}", line)
                for idx, line in enumerate(path.read_text().splitlines())
            )

    all_lines = [
        line
        for line in all_lines
        if (len(line[1]) > 0)
        and not line[1].startswith("#")
    ]

    name_case_and_chunks: list[tuple[str, str, str]] = [
        (name, case.strip().strip("\ufeff"), chunks.strip())
        for name, (case, chunks) in (
            (name, line.split(";")[-2:])
            for (name, line) in all_lines
        )
    ]

    return name_case_and_chunks


def load_segmenter_cases() -> list[str]:
    return [
        case
        for _name, case, _chunks in load_segmenter_test_data()
    ]


def all_cases() -> list[str]:
    return load_segmenter_cases() + load_break_cases()


CASE_DATA = all_cases()


@pytest.fixture(params=range(len(CASE_DATA)))
def reference_idx_a(request: pytest.FixtureRequest) -> int:
    return request.param


@pytest.fixture(params=range(len(CASE_DATA)))
def reference_idx_b(request: pytest.FixtureRequest) -> int:
    return request.param


re_pat = regex.compile(r"\X")


def regex_to_grapheme(data: str) -> list[str]:
    return re_pat.findall(data)


def ugrapheme_to_grapheme(data: str) -> list[str]:
    return ugrapheme.grapheme_split(data)


def graphemeu_to_grapheme(data: str) -> list[str]:
    return list(gr_api.graphemes(data))


def test_consistency(reference_idx_a: int) -> None:
    for reference_idx_b in range(len(CASE_DATA)):
        gen_case_str = f"{CASE_DATA[reference_idx_a]}{CASE_DATA[reference_idx_b]}"

        w2_split = tuple(api.graphemes(data=gen_case_str))
        gu_split = tuple(graphemeu_to_grapheme(data=gen_case_str))
        if w2_split != gu_split:
            dbg(reference_idx_a)
            dbg(reference_idx_b)
            props = default_properties()
            dbg(w2_split)
            dbg(gu_split)
            dbg([ch.encode("raw_unicode_escape") for ch in w2_split])
            dbg([[props.char_to_enum(char).name for char in chunk] for chunk in w2_split])

        assert w2_split == gu_split

        # # unicode 17 not yet supported for these implementations.
        # ug_split = tuple(ugrapheme_to_grapheme(gen_case_str))
        # re_split = tuple(regex_to_grapheme(gen_case_str))

        # results = defaultdict[tuple[str, ...], int](int)

        # results[w2_split] += 1
        # results[ug_split] += 1
        # results[re_split] += 1

        # if len(results) == 1:
        #     continue

        # dbg(reference_idx_a)
        # dbg(reference_idx_b)

        # if len(results) == sum(results.values()):
        #     raise Exception("no agreement")

        # if results[re_split] == 1:
        #     raise Exception("regex disagrees")
        # if results[ug_split] == 1:
        #     raise Exception("ugrapheme disagrees")
        # if results[w2_split] == 1:
        #     raise Exception("what2 disagrees")
