from collections.abc import Generator, Iterator
from dataclasses import dataclass, field
from itertools import accumulate
from typing import Any, NoReturn, cast, override

from what2_grapheme.grapheme_property.cache import default_properties
from what2_grapheme.grapheme_property.lookup import GraphemeBreak
from what2_grapheme.simple_sm.state import StateFn, StateMachine
from what2_grapheme.util.iter import sliding_window


class BreakGenerator(Generator[bool, int]):
    state_transform: StateFn = StateMachine.initial_state

    @override
    def send(self, value: int) -> bool:
        should_break, self.state_transform, _ = self.state_transform(value)
        return should_break

    @override
    def throw(
        self, typ: Any, val: Any = None, tb: Any = None, /,
    ) -> NoReturn:
        if isinstance(val, BaseException):
            raise val
        raise StopIteration


@dataclass
class StrBreakGen(Generator[bool, str]):
    ch_props: GraphemeBreak
    state: BreakGenerator = field(default_factory=BreakGenerator)

    @override
    def send(self, value: str) -> bool:
        break_kind = cast("int", self.ch_props.char_to_cat(value))
        return self.state.send(break_kind)

    @override
    def throw(
        self, typ: Any, val: Any = None, tb: Any = None, /,
    ) -> NoReturn:
        if isinstance(val, BaseException):
            raise val
        raise StopIteration


def length(data: str, until: int | None = None, properties: GraphemeBreak | None = None) -> int:
    if len(data) == 0:
        return 0

    if until is None:
        return sum(1 for _ in iter_grapheme_sizes(data, properties))

    running_len = 0
    for running_len in accumulate(1 for _ in iter_grapheme_sizes(data, properties)):
        if running_len >= until:
            return running_len
    return running_len


def grapheme_sizes(data: str, properties: GraphemeBreak | None = None) -> list[int]:
    return list(iter_grapheme_sizes(data, properties))


def iter_grapheme_sizes(data: str, properties: GraphemeBreak | None = None) -> Iterator[int]:
    if len(data) == 0:
        return

    if properties is None:
        properties = default_properties()

    state = StrBreakGen(properties)
    current_size = 0

    for char in data:
        should_break = state.send(char)

        if should_break and current_size:
            yield current_size
            current_size = 1
        else:
            current_size += 1

    yield current_size


def graphemes(data: str, properties: GraphemeBreak | None = None) -> list[str]:
    return list(iter_graphemes(data, properties))


def iter_graphemes(data: str, properties: GraphemeBreak | None = None) -> Iterator[str]:
    if len(data) == 0:
        return

    if properties is None:
        properties = default_properties()

    state = StrBreakGen(properties)
    current_sequence = ""

    for char in data:
        should_break = state.send(char)
        if should_break:
            yield current_sequence
            current_sequence = char
        else:
            current_sequence += char

    yield current_sequence


def strslice(data: str, start: int | None = None, stop: int | None = None, properties: GraphemeBreak | None = None) -> str:
    slice_graphemes = graphemes(data, properties)[start: stop]
    return "".join(slice_graphemes)


def contains(data: str, substring: str, properties: GraphemeBreak | None = None) -> bool:
    if substring not in data:
        return False

    if len(substring) == 0:
        return True

    sub_graphemes = graphemes(substring, properties)

    it = iter_graphemes(data, properties)

    return any(
        view == sub_graphemes
        for view in sliding_window(it, len(sub_graphemes))
    )
