from collections.abc import Callable

from what2_grapheme.fast_re import api as fast_api
from what2_grapheme.fast_sm import api as fast_sm_api
from what2_grapheme.simple_sm import api as simple_api
import ugrapheme
from tests.data import segmenter_test

import pytest


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


segmenter_test_data = load_segmenter_test_data()


def _idx_to_id(idx: int) -> str:
    return segmenter_test_data[idx][0]


@pytest.fixture(params=range(len(segmenter_test_data)), ids=_idx_to_id)
def reference_idx(request: pytest.FixtureRequest) -> int:
    return request.param


@pytest.fixture
def case_str(reference_idx: int) -> str:
    return segmenter_test_data[reference_idx][1]


@pytest.fixture
def case_chunks(reference_idx: int) -> list[str]:
    chunks = segmenter_test_data[reference_idx][2].strip("÷").split("÷")
    return [
        chunk.strip()
        for chunk in chunks
    ]


def test_grapheme_segmentation(case_str: str, case_chunks: str):
    impls: tuple[Callable[[str], list[str]], ...] = (
        fast_api.graphemes,
        fast_sm_api.graphemes,
        simple_api.graphemes,
        ugrapheme.grapheme_split,
    )

    for impl in impls:
        assert impl(case_str) == case_chunks
