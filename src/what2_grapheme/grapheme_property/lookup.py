from collections.abc import Iterator
from contextlib import ExitStack
from dataclasses import dataclass
from functools import cached_property
from itertools import chain, pairwise
from pathlib import Path
from typing import Self, cast, overload, override

import numpy as np
import numpy.typing as npt
import pandas as pd

from what2_grapheme.grapheme_data import load
from what2_grapheme.grapheme_property.parse import parse_break_properties, parse_emoji_data, parse_incb_properties
from what2_grapheme.grapheme_property.type import Break

type PrevT = tuple[int, int, str]
type NextT = PrevT | None
type PairIter = Iterator[tuple[PrevT, NextT]]

MAX_ORD = 1114111


@dataclass
class GraphemeBreak:
    data: npt.NDArray[np.uint8]
    version: str

    @override
    def __eq__(self, value: object) -> bool:
        match value:
            case GraphemeBreak():
                return self.version == value.version
            case _:
                return False

    @override
    def __hash__(self) -> int:
        return hash(self.__class__.__name__ + self.version)

    def char_to_cat(self, char: str) -> np.uint8:
        return self.code_to_cat(ord(char))

    def char_to_enum(self, char: str) -> Break:
        code = self.code_to_cat(ord(char))
        return Break(code)

    def code_to_cat(self, code: int) -> np.uint8:
        return self.data[code]

    def ch_cat(self, cat: int) -> str:
        return "".join(
            chr(i)
            for i in range(MAX_ORD)
            if self.code_to_cat(i) == cat
        )

    @cached_property
    def ascii_other(self) -> set[str]:
        return {
            chr(i)
            for i in range(128)
            if self.code_to_cat(i) == Break.Other.value
        }

    @cached_property
    def ascii_other_codes(self) -> set[int]:
        return {
            i
            for i in range(128)
            if self.code_to_cat(i) == Break.Other.value
        }

    @cached_property
    def all_other(self) -> set[str]:
        return set(self.all_other_list)

    @cached_property
    def all_other_codes(self) -> set[int]:
        other = Break.Other.value
        return {
            i
            for i in range(MAX_ORD)
            if self.code_to_cat(i) == other
        }

    @cached_property
    def never_join_chars(self) -> frozenset[str]:
        """
        A set of characters which on their own never form grapheme clusters of size > 1.
        """
        codes = self.never_join_codes
        return frozenset({
            chr(i)
            for i in range(MAX_ORD)
            if self.code_to_cat(i) in codes
        })

    @cached_property
    def never_join_codes(self) -> frozenset[np.uint8]:
        """
        A common set of codes which on their own never form grapheme clusters of size > 1.
        """
        return frozenset({
            Break.LF.value,
            Break.Control.value,
            Break.Other.value,
        })

    @cached_property
    def all_other_list(self) -> tuple[str, ...]:
        other = Break.Other.value
        return tuple(
            chr(i)
            for i in range(MAX_ORD)
            if self.code_to_cat(i) == other
        )

    @cached_property
    def str_prop_map(self) -> dict[str, int]:

        return {
            chr(i): int(self.code_to_cat(i))
            for i in range(MAX_ORD)
        }

    @cached_property
    def code_prop_map(self) -> dict[int, int]:

        return {
            i: int(self.code_to_cat(i))
            for i in range(MAX_ORD)
        }

    @classmethod
    @overload
    def from_files(cls, property_path: Path, emoji_path: Path, incb_path: Path, version: str) -> Self:
        ...

    @classmethod
    @overload
    def from_files(cls, property_path: None = None, emoji_path: None = None, incb_path: None = None, version: None = None) -> Self:
        ...

    @classmethod
    def _load_break_properties(cls, property_path: Path | None) -> pd.DataFrame:
        with ExitStack() as stack:
            if property_path is None:
                property_path = stack.enter_context(load.break_properties())

            return parse_break_properties(property_path)

    @classmethod
    def _load_emoji_data(cls, emoji_path: Path | None) -> pd.DataFrame:
        with ExitStack() as stack:
            if emoji_path is None:
                emoji_path = stack.enter_context(load.emoji_data())

            return parse_emoji_data(emoji_path)

    @classmethod
    def _load_incb_properties(cls, incb_path: Path | None) -> pd.DataFrame:
        with ExitStack() as stack:
            if incb_path is None:
                incb_path = stack.enter_context(load.derived_properties())

            return parse_incb_properties(incb_path)

    @classmethod
    def _combine_data(cls, break_data: pd.DataFrame, emoji_data: pd.DataFrame, incb_data: pd.DataFrame) -> npt.NDArray[np.uint8]:
        data = pd.concat([break_data, emoji_data])

        data = data.sort_values(by="code_start").reset_index(drop=True) # type: ignore reportUnknownMemberType

        break_cat_dtype: pd.CategoricalDtype = data["break_class"].dtype # type: ignore reportUnknownMemberType

        dtype_series: dict[str, pd.Series[pd.CategoricalDtype]] = {
            cat: pd.Series(
                [cat],
                dtype=break_cat_dtype,
            )

            for cat in break_cat_dtype.categories # type: ignore reportUnknownMemberType
        }

        results: list[pd.Series[pd.CategoricalDtype]] = []

        start: int = cast(int, data["code_start"][0])

        if start != 0:
            other_s: pd.Series[pd.CategoricalDtype] = dtype_series[Break.Other.name].repeat(start)
            results.append(other_s)

        prev_row: PrevT
        next_row: NextT

        pair_row_iter: Iterator[tuple[PrevT, NextT]] = cast(PairIter, pairwise(chain(data.itertuples(index=False, name=None), (None,))))

        for prev_row, next_row in pair_row_iter:
            code_start, code_end, break_class = prev_row
            cat_series = dtype_series[break_class]
            count = code_end - code_start + 1
            cat_series = cat_series.repeat(count)
            results.append(cat_series)

            if next_row is None:
                gap_end = MAX_ORD + 1
            else:
                gap_end = next_row[0]

            gap_count = gap_end - code_end - 1

            assert gap_count >= 0

            if gap_count == 0:
                continue

            gap_series = dtype_series[Break.Other.name]
            gap_series = gap_series.repeat(gap_count)

            results.append(gap_series)

        cat_data: pd.Series[pd.CategoricalDtype] = pd.concat(results)
        # from collections import defaultdict # noqa: ERA001
        # code_desc = defaultdict(set) # noqa: ERA001

        row_iter: Iterator[PrevT] = cast(Iterator[PrevT], incb_data.itertuples(index=False, name=None))
        for code_start, code_end, break_class in row_iter:
            # for code in cat_data[code_start: code_end + 1]:
            #     code_desc[break_class].add(code) # noqa: ERA001

            if break_class == "InCB_Extend":
                code_slice = cat_data[code_start: code_end + 1]
                assert np.all(np.logical_or(code_slice == Break.Extend.name, code_slice == Break.ZWJ.name))
                # InCB_Extend doesn't modify behaviour.
                # According to UTF break tests, non-incb
                # extend/zwj characters must have same extending effect.
                # Slightly underspecified by standard.
                continue

            if break_class == Break.InCB_Consonant.name:
                code_slice = cat_data[code_start: code_end + 1]
                assert np.all(code_slice == Break.Other.name)

            if break_class == Break.InCB_Linker.name:
                code_slice = cat_data[code_start: code_end + 1]
                assert np.all(code_slice == Break.Extend.name)

            cat_data[code_start: code_end + 1] = break_class
        # print(code_desc) # noqa: ERA001
        # assert 0 # noqa: ERA001

        break_map: dict[str, np.uint8] = {
            val.name: val.value
            for val in Break
        }

        np_data: npt.NDArray[np.uint8] = cast(npt.NDArray[np.uint8], cat_data.map(break_map).to_numpy(dtype=np.uint8)) # type: ignore reportUnknownMemberType
        return np_data

    @classmethod
    def from_files(cls, property_path: Path | None = None, emoji_path: Path | None = None, incb_path: Path | None = None, version: str | None = None) -> Self:
        attrs = property_path, emoji_path, version
        any_none = any(
            attr is None
            for attr in attrs
        )

        all_none = all(
            attr is None
            for attr in attrs
        )

        if any_none and not all_none:
            raise ValueError

        break_data = cls._load_break_properties(property_path)
        emoji_data = cls._load_emoji_data(emoji_path)
        incb_data = cls._load_incb_properties(incb_path)

        if version is None:
            version = load.utf_version()

        np_data = cls._combine_data(break_data, emoji_data, incb_data)

        if len(np_data) != MAX_ORD + 1:
            raise ValueError

        return cls(
            np_data,
            version,
        )
