

from collections.abc import Generator, Iterator
from dataclasses import dataclass, field
from typing import override, cast, Any
from functools import partial
import numpy as np

from what2_grapheme.state import StateTransform, StateMachine
from what2 import dbg
from what2_utf_parse.grapheme_cluster.describe import FlatGroupProperties
from what2_utf_parse.grapheme_cluster.property import Break

__default_properties: FlatGroupProperties | None = None
def default_properties() -> FlatGroupProperties:
    global __default_properties
    if __default_properties is None:
        __default_properties = FlatGroupProperties.from_files()
    return __default_properties


class BreakGenerator(Generator[bool, np.uint8]):
    state_transform: StateTransform = partial(StateMachine.default_next_state, should_break=False)

    @override
    def send(self, value: np.uint8) -> bool:
        should_break, self.state_transform = self.state_transform(value)
        return should_break
    
    @override
    def throw(
        self, typ: Any, val: Any = None, tb: Any = None, /
    ) -> bool:
        if isinstance(val, BaseException):
            raise val
        raise StopIteration


@dataclass
class StrBreakGen(Generator[bool, str]):
    ch_props: FlatGroupProperties
    state: BreakGenerator = field(default_factory=BreakGenerator)

    @override
    def send(self, value: str) -> bool:
        if value in self.ch_props.ascii_other:
            # ascii short circuit for performance
            self.state.state_transform = StateMachine.default
            return True
        break_kind = self.ch_props.char_to_cat(value)
        # dbg(break_kind)
        # dbg(Break._value2member_map_[break_kind])
        ret = self.state.send(break_kind)
        # dbg(ret)
        return ret
    @override
    def throw(
        self, typ: Any, val: Any = None, tb: Any = None, /
    ) -> bool:
        if isinstance(val, BaseException):
            raise val
        raise StopIteration


def length(data: str, properties: FlatGroupProperties | None = None) -> int:
    return sum(1 for _ in iter_grapheme_sizes(data, properties))

def grapheme_sizes(data: str, properties: FlatGroupProperties | None = None) -> list[int]:
    return list(iter_grapheme_sizes(data, properties))


def iter_grapheme_sizes(data: str, properties: FlatGroupProperties | None = None) -> Iterator[int]:
    if len(data) == 0:
        return

    if properties is None:
        properties = default_properties()

    state = StrBreakGen(properties)
    current_size = 0

    for char in data:
        should_break = state.send(char)

        if should_break:
            yield current_size
            current_size = 1
        else:
            current_size += 1
    
    yield current_size


def graphemes(data: str, properties: FlatGroupProperties = __default_properties) -> list[str]:
    return list(iter_graphemes(data, properties))


def iter_graphemes(data: str, properties: FlatGroupProperties | None = None) -> Iterator[str]:
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
