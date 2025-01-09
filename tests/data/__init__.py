from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager
from functools import partial
import importlib.resources as impr
from pathlib import Path


def break_test() -> AbstractContextManager[Path, bool | None]:
    files = impr.files()
    data = files / "GraphemeBreakTest.txt"
    return impr.as_file(data)


def segmenter_test() -> Iterator[Callable[[], AbstractContextManager[Path, bool | None]]]:
    files = impr.files()
    count = 0
    for file in files.iterdir():
        if not file.name.startswith("TestSegmenter"):
            continue

        yield partial(impr.as_file, file)
        count += 1
    expected_case_count = 6
    assert count == expected_case_count
