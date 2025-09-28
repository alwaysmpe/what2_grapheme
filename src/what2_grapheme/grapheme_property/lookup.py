from collections.abc import Generator
from contextlib import ExitStack
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Self, overload, override

from what2_grapheme.grapheme_data import load
from what2_grapheme.grapheme_property.file_reader import CodeBreak, parse_file
from what2_grapheme.grapheme_property.type import Break

MAX_ORD = 1114111


@dataclass
class GraphemeBreak:
    data: tuple[str, ...]
    version: str

    @override
    def __eq__(self, value: object, /) -> bool:
        match value:
            case GraphemeBreak():
                return self.version == value.version
            case _:
                return False

    @override
    def __hash__(self) -> int:
        return hash(self.__class__.__name__ + self.version)

    def char_to_enum(self, char: str) -> Break:
        return Break(self.data[ord(char)])

    def code_to_enum(self, code: int) -> Break:
        return self.char_to_enum(chr(code))

    @cached_property
    def never_join_codes(self) -> frozenset[str]:
        """
        A common set of codes which on their own never form grapheme clusters of size > 1.
        """
        return frozenset({
            Break.LF.value,
            Break.Control.value,
            Break.Other.value,
        })

    @cached_property
    def ascii_other(self) -> set[str]:
        return {
            chr(i)
            for i in range(128)
            if self.data[i] == Break.Other.value
        }

    @cached_property
    def never_join_chars(self) -> frozenset[str]:
        """
        A set of characters which on their own never form grapheme clusters of size > 1.
        """
        codes = self.never_join_codes
        return frozenset({
            chr(i)
            for i in range(MAX_ORD + 1)
            if self.data[i] in codes
        })

    @cached_property
    def all_other_list(self) -> tuple[str, ...]:
        other = Break.Other.value
        return tuple(
            chr(i)
            for i in range(MAX_ORD)
            if self.data[i] == other
        )

    @classmethod
    @overload
    def from_files(cls, property_path: Path, emoji_path: Path, incb_path: Path, version: str) -> Self:
        ...

    @classmethod
    @overload
    def from_files(cls, property_path: None = None, emoji_path: None = None, incb_path: None = None, version: None = None) -> Self:
        ...

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

        default_data = [
            Break.Other.value
            for _ord in range(MAX_ORD + 1)
        ]

        for code_break in cls._load_break_properties(property_path):
            for code in range(code_break.code_start, code_break.code_end + 1):
                default_data[code] = code_break.break_class.value

        for code_break in cls._load_emoji_data(emoji_path):
            for code in range(code_break.code_start, code_break.code_end + 1):
                default_data[code] = code_break.break_class.value

        for code_break in cls._load_incb_properties(incb_path):
            for code in range(code_break.code_start, code_break.code_end + 1):
                if default_data[code] == Break.ZWJ.value:
                    continue
                default_data[code] = code_break.break_class.value

        if version is None:
            version = load.utf_version()

        return cls(tuple(default_data), version)

    @classmethod
    def _load_break_properties(cls, property_path: Path | None) -> Generator[CodeBreak]:
        with ExitStack() as stack:
            if property_path is None:
                property_path = stack.enter_context(load.break_properties())

            yield from parse_file(property_path)

    @classmethod
    def _load_emoji_data(cls, emoji_path: Path | None) -> Generator[CodeBreak]:
        with ExitStack() as stack:
            if emoji_path is None:
                emoji_path = stack.enter_context(load.emoji_data())

            yield from parse_file(emoji_path)

    @classmethod
    def _load_incb_properties(cls, incb_path: Path | None) -> Generator[CodeBreak]:
        with ExitStack() as stack:
            if incb_path is None:
                incb_path = stack.enter_context(load.derived_properties())

            yield from parse_file(incb_path)
