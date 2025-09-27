from collections.abc import Generator
from dataclasses import dataclass, field
from typing import Any, overload, override

import numpy as np

from what2_grapheme.fast_sm.state import StateFn, StateMachine
from what2_grapheme.grapheme_property.lookup import GraphemeBreak
from what2_grapheme.grapheme_property.type import Break

type BreakT = np.uint8 | int | Break


class BreakGenerator(Generator[tuple[bool, bool], int]):
    state_transform: StateFn = StateMachine.initial_state

    @override
    def send(self, value: int) -> tuple[bool, bool]:
        should_break, state_tsfm, is_default = self.state_transform(value)
        self.state_transform = state_tsfm
        return should_break, is_default

    @override
    def throw(
        self, typ: Any, val: Any = None, tb: Any = None, /,
    ) -> tuple[bool, bool]:
        if isinstance(val, BaseException):
            raise val
        raise StopIteration


@dataclass
class StrBreakGen(Generator[bool, str]):
    ch_props: GraphemeBreak
    state: BreakGenerator = field(default_factory=BreakGenerator)

    def send_default(self, value: str) -> bool:
        if value in self.ch_props.all_other:
            return True

        break_kind = self.ch_props.char_to_cat(value)
        ret, is_default = self.state.send(break_kind) # type: ignore reportArgumentType

        if not is_default:
            self.send = self.send_dynamic

        return ret

    def send_dynamic(self, value: str) -> bool:
        if value in self.ch_props.ascii_other:
            break_kind = 12
        else:
            break_kind = self.ch_props.char_to_cat(value)

        ret, is_default = self.state.send(break_kind) # type: ignore reportArgumentType

        if is_default:
            self.send = self.send_default

        return ret

    send = send_dynamic

    @override
    def throw(
        self, typ: Any, val: Any = None, tb: Any = None, /,
    ) -> bool:
        if isinstance(val, BaseException):
            raise val
        raise StopIteration


@overload
def is_definite_break(prev_kind: np.uint8, next_kind: np.uint8) -> bool:
    ...


@overload
def is_definite_break(prev_kind: int, next_kind: int) -> bool:
    ...


def is_definite_break(prev_kind: BreakT, next_kind: BreakT) -> bool:
    prev_kind = np.uint8(prev_kind)
    next_kind = np.uint8(next_kind)
    return _is_definite_break_impl(prev_kind, next_kind) # type: ignore reportArgumentType


def _is_definite_break_impl(prev_kind: int, next_kind: int) -> bool:

    if prev_kind == 12 and next_kind == 12:
        return True

    ctl_chs = {
        0,
        1,
        2,
    }

    if prev_kind in ctl_chs or next_kind in ctl_chs:
        is_cr = prev_kind == 0
        is_lf = next_kind == 1
        is_crlf = is_cr and is_lf
        return not is_crlf

    if prev_kind == 8:
        return False

    join_suffixes = {
        13,
        16,
        17,
        15,
        14,
    }

    if next_kind in join_suffixes:
        return False

    hangul_l_join_suffixes = {
        3,
        4,
        5,
        7,
    }

    if prev_kind == 3 and next_kind in hangul_l_join_suffixes:
        return False

    hangul_v_prefixes = {
        5,
        4,
    }
    hangul_v_join_suffixes = {
        4,
        6,
    }

    if prev_kind in hangul_v_prefixes and next_kind in hangul_v_join_suffixes:
        return False

    hangul_t_prefixes = {
        6,
        7,
    }
    hangul_t_join_suffixes = {
        6,
    }

    if prev_kind in hangul_t_prefixes and next_kind in hangul_t_join_suffixes:
        return False

    if prev_kind == 11 and next_kind == 11:
        return False

    incb_extender = {
        15,
        16,
        17,
    }

    if prev_kind == 9 and next_kind in incb_extender:
        return False

    if prev_kind in incb_extender and next_kind == 9:
        return False

    if prev_kind == 15 and next_kind == 10:
        return False

    return True


def safe_split_idx(data: str, upper_limit: int, ch_props: GraphemeBreak) -> int:
    if upper_limit > len(data):
        return len(data)

    def break_kind(value: str) -> np.uint8:
        if value in ch_props.all_other:
            # performance short circuit
            return np.uint8(17)

        return ch_props.char_to_cat(value)

    next_kind = break_kind(data[upper_limit])

    for idx, prev_ch in enumerate(data[upper_limit - 1:: -1]):
        prev_kind = break_kind(prev_ch)

        if _is_definite_break_impl(prev_kind, next_kind): # type: ignore reportArgumentType
            return upper_limit - idx - 1

        next_kind = prev_kind

    return 0
