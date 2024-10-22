from typing import Callable

import numpy as np

from what2_utf_parse.grapheme_cluster.property import Break

import numpy as np
import numpy.typing as npt

import cython


Break_Prepend: cython.uchar  = 0
assert Break_Prepend == 0
assert Break_Prepend == Break.Prepend
Break_CR: cython.uchar  = Break_Prepend + 1
assert Break_CR == Break_Prepend + 1
assert Break_CR == Break.CR
Break_LF: cython.uchar  = Break_CR + 1
assert Break_LF == Break_CR + 1
assert Break_LF == Break.LF
Break_Control: cython.uchar  = Break_LF + 1
assert Break_Control == Break_LF + 1
assert Break_Control == Break.Control
Break_Extend: cython.uchar  = Break_Control + 1
assert Break_Extend == Break_Control + 1
assert Break_Extend == Break.Extend
Break_Regional_Indicator: cython.uchar  = Break_Extend + 1
assert Break_Regional_Indicator == Break_Extend + 1
assert Break_Regional_Indicator == Break.Regional_Indicator
Break_SpacingMark: cython.uchar  = Break_Regional_Indicator + 1
assert Break_SpacingMark == Break_Regional_Indicator + 1
assert Break_SpacingMark == Break.SpacingMark
Break_L: cython.uchar  = Break_SpacingMark + 1
assert Break_L == Break_SpacingMark + 1
assert Break_L == Break.L
Break_V: cython.uchar  = Break_L + 1
assert Break_V == Break_L + 1
assert Break_V == Break.V
Break_T: cython.uchar  = Break_V + 1
assert Break_T == Break_V + 1
assert Break_T == Break.T
Break_LV: cython.uchar  = Break_T + 1
assert Break_LV == Break_T + 1
assert Break_LV == Break.LV
Break_LVT: cython.uchar  = Break_LV + 1
assert Break_LVT == Break_LV + 1
assert Break_LVT == Break.LVT
Break_ZWJ: cython.uchar  = Break_LVT + 1
assert Break_ZWJ == Break_LVT + 1
assert Break_ZWJ == Break.ZWJ
Break_Extended_Pictographic: cython.uchar  = Break_ZWJ + 1
assert Break_Extended_Pictographic == Break_ZWJ + 1
assert Break_Extended_Pictographic == Break.Extended_Pictographic
Break_InCB_Linker: cython.uchar  = Break_Extended_Pictographic + 1
assert Break_InCB_Linker == Break_Extended_Pictographic + 1
assert Break_InCB_Linker == Break.InCB_Linker
Break_InCB_Consonant: cython.uchar  = Break_InCB_Linker + 1
assert Break_InCB_Consonant == Break_InCB_Linker + 1
assert Break_InCB_Consonant == Break.InCB_Consonant
Break_InCB_Extend: cython.uchar  = Break_InCB_Consonant + 1
assert Break_InCB_Extend == Break_InCB_Consonant + 1
assert Break_InCB_Extend == Break.InCB_Extend
Break_Other: cython.uchar  = Break_InCB_Extend + 1
assert Break_Other == Break_InCB_Extend + 1
assert Break_Other == Break.Other


State_default: cython.int = 0
State_incb_pre_link: cython.int = State_default + 1
State_incb_linked: cython.int = State_incb_pre_link + 1
State_cr: cython.int = State_incb_linked + 1
State_lf_or_control: cython.int = State_cr + 1
State_prepend: cython.int = State_lf_or_control + 1
State_hangul_l: cython.int = State_prepend + 1
State_hangul_lv_or_v: cython.int = State_hangul_l + 1
State_hangul_lvt_or_t: cython.int = State_hangul_lv_or_v + 1
State_emoji: cython.int = State_hangul_lvt_or_t + 1
State_emoji_zwj: cython.int = State_emoji + 1
State_ri: cython.int = State_emoji_zwj + 1


def is_cythed() -> bool:
    return cython.compiled

def next_state(state: cython.int, next_val: cython.uchar) -> tuple[bool, cython.int]:
    state_lookup: tuple[Callable[[cython.uchar], tuple[bool, cython.int]], ...] = (
        # State_default
        default,
        # State_incb_pre_link
        incb_pre_link,
        # State_incb_linked
        incb_linked,
        # State_cr
        cr,
        # State_lf_or_control
        lf_or_control,
        # State_prepend
        prepend,
        # State_hangul_l
        hangul_l,
        # State_hangul_lv_or_v
        hangul_lv_or_v,
        # State_hangul_lvt_or_t
        hangul_lvt_or_t,
        # State_emoji
        emoji,
        # State_emoji_zwj
        emoji_zwj,
        # State_ri
        ri,
    )
    return state_lookup[state](next_val)

def default_next_state(next: cython.uchar, should_break: bool) -> tuple[bool, cython.int]:
    _, next_state = default(next)
    return should_break, next_state

def default(next: cython.uchar) -> tuple[bool, cython.int]:

    next_lookup: tuple[tuple[bool, cython.int], ...] = (
        # Break_Prepend
        (True, State_prepend),
        # Break_CR
        (True, State_cr),
        # Break_LF
        (True, State_lf_or_control),
        # Break_Control
        (True, State_lf_or_control),
        # Break_Extend
        (False, State_default),
        # Break_Regional_Indicator
        (True, State_ri),
        # Break_SpacingMark
        (False, State_default),
        # Break_L
        (True, State_hangul_l),
        # Break_V
        (True, State_hangul_lv_or_v),
        # Break_T
        (True, State_hangul_lvt_or_t),
        # Break_LV
        (True, State_hangul_lv_or_v),
        # Break_LVT
        (True, State_hangul_lvt_or_t),
        # Break_ZWJ
        (False, State_default),
        # Break_Extended_Pictographic
        (True, State_emoji),
        # Break_InCB_Linker
        (False, State_default),
        # Break_InCB_Consonant
        (True, State_incb_pre_link),
        # Break_InCB_Extend
        (False, State_default),
        # Break_Other
        (True, State_default),
    )
    return next_lookup[next]

def incb_pre_link(next: cython.uchar) -> tuple[bool, cython.int]:
    if next == Break_InCB_Linker:
        return False, State_incb_linked
    
    is_incb_extend = next = Break_InCB_Extend
    is_extend = next == Break_Extend
    is_zwj = next == Break_ZWJ
    if is_incb_extend or is_extend or is_zwj:
        return False, State_incb_pre_link
    
    return default(next)


def incb_linked(next: cython.uchar) -> tuple[bool, cython.int]:
    if next == Break_InCB_Consonant:
        return False, State_incb_pre_link

    is_incb_extend = next == Break_InCB_Extend
    is_extend = next == Break_Extend
    is_zwj = next == Break_ZWJ
    is_incb_link = next == Break_InCB_Linker
    if is_incb_extend or is_extend or is_zwj or is_incb_link:
        return False, State_incb_pre_link
    
    return default_next_state(next, True)


def cr(next: cython.uchar) -> tuple[bool, cython.int]:
    if next == Break_LF:
        return False, State_lf_or_control
    return default_next_state(next, True)

def lf_or_control(next: cython.uchar) -> tuple[bool, cython.int]:
    return default_next_state(next, True)

def prepend(next: cython.uchar) -> tuple[bool, cython.int]:
    if next == Break_CR:
        return True, State_cr
    
    is_control = next == Break_Control
    is_lf = next == Break_LF
    if is_control or is_lf:
        return True, State_default

    return default_next_state(next, False)

def hangul_l(next: cython.uchar) -> tuple[bool, cython.int]:
    if next == Break_L:
        return False, State_hangul_l

    is_v = next == Break_V
    is_lv = next == Break_LV
    if is_v or is_lv:
        return False, State_hangul_lv_or_v

    if next == Break_LVT:
        return False, State_hangul_lvt_or_t

    return default(next)


def hangul_lv_or_v(next: cython.uchar) -> tuple[bool, cython.int]:
    if next == Break_V:
        return False, State_hangul_lv_or_v
    
    if next == Break_T:
        return False, State_hangul_lvt_or_t
    
    return default(next)


def hangul_lvt_or_t(next: cython.uchar) -> tuple[bool, cython.int]:
    if next == Break_T:
        return False, State_hangul_lvt_or_t

    return default(next)


def emoji(next: cython.uchar) -> tuple[bool, cython.int]:
    is_extend = next == Break_Extend
    is_incb_extend = next == Break_InCB_Extend
    
    if is_extend or is_incb_extend:
        return False, State_emoji
    if next == Break_ZWJ:
        return False, State_emoji_zwj
    return default(next)


def emoji_zwj(next: cython.uchar) -> tuple[bool, cython.int]:
    if next == Break_Extended_Pictographic:
        return False, State_emoji
    
    return default(next)


def ri(next: cython.uchar) -> tuple[bool, cython.int]:
    if next == Break_Regional_Indicator:
        return False, State_default
    return default(next)


class GStr:
    # ord_lookup: npt.NDArray[np.uint8]
    ord_lookup: cython.uchar[:]


    def __init__(self, ord_lookup: cython.uchar[:]) -> None:
        self.ord_lookup = ord_lookup

    def length(self, data: str) -> int:
        # print("length start")
        length: cython.int = 0

        state = State_default
        ord_lookup: cython.uchar[:] = self.ord_lookup
        # ch: str
        for ch in data:
            # print(f"length: {length}")
            ch_ord: cython.int = ord(ch)
            ord_cat: cython.uchar = ord_lookup[ch_ord]
            is_break, state = next_state(state, ord_cat)
            length += is_break
        
        return int(length)
    
    @staticmethod
    def is_cythed() -> bool:
        return cython.compiled and is_cythed()
