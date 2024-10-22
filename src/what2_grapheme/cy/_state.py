from typing import Callable

import numpy as np

from what2_utf_parse.grapheme_cluster.property import Break

import cython

Break_Prepend: np.uint8  = np.uint8(0)
assert Break_Prepend == 0
assert Break_Prepend == Break.Prepend
Break_CR: np.uint8  = Break_Prepend + 1
assert Break_CR == Break_Prepend + 1
assert Break_CR == Break.CR
Break_LF: np.uint8  = Break_CR + 1
assert Break_LF == Break_CR + 1
assert Break_LF == Break.LF
Break_Control: np.uint8  = Break_LF + 1
assert Break_Control == Break_LF + 1
assert Break_Control == Break.Control
Break_Extend: np.uint8  = Break_Control + 1
assert Break_Extend == Break_Control + 1
assert Break_Extend == Break.Extend
Break_Regional_Indicator: np.uint8  = Break_Extend + 1
assert Break_Regional_Indicator == Break_Extend + 1
assert Break_Regional_Indicator == Break.Regional_Indicator
Break_SpacingMark: np.uint8  = Break_Regional_Indicator + 1
assert Break_SpacingMark == Break_Regional_Indicator + 1
assert Break_SpacingMark == Break.SpacingMark
Break_L: np.uint8  = Break_SpacingMark + 1
assert Break_L == Break_SpacingMark + 1
assert Break_L == Break.L
Break_V: np.uint8  = Break_L + 1
assert Break_V == Break_L + 1
assert Break_V == Break.V
Break_T: np.uint8  = Break_V + 1
assert Break_T == Break_V + 1
assert Break_T == Break.T
Break_LV: np.uint8  = Break_T + 1
assert Break_LV == Break_T + 1
assert Break_LV == Break.LV
Break_LVT: np.uint8  = Break_LV + 1
assert Break_LVT == Break_LV + 1
assert Break_LVT == Break.LVT
Break_ZWJ: np.uint8  = Break_LVT + 1
assert Break_ZWJ == Break_LVT + 1
assert Break_ZWJ == Break.ZWJ
Break_Extended_Pictographic: np.uint8  = Break_ZWJ + 1
assert Break_Extended_Pictographic == Break_ZWJ + 1
assert Break_Extended_Pictographic == Break.Extended_Pictographic
Break_InCB_Linker: np.uint8  = Break_Extended_Pictographic + 1
assert Break_InCB_Linker == Break_Extended_Pictographic + 1
assert Break_InCB_Linker == Break.InCB_Linker
Break_InCB_Consonant: np.uint8  = Break_InCB_Linker + 1
assert Break_InCB_Consonant == Break_InCB_Linker + 1
assert Break_InCB_Consonant == Break.InCB_Consonant
Break_InCB_Extend: np.uint8  = Break_InCB_Consonant + 1
assert Break_InCB_Extend == Break_InCB_Consonant + 1
assert Break_InCB_Extend == Break.InCB_Extend
Break_Other: np.uint8  = Break_InCB_Extend + 1
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


class CyStateMachine:
    @staticmethod
    def is_cythed() -> bool:
        return cython.compiled

    @classmethod
    def next_state(cls, state: cython.int, next_val: np.uint8) -> tuple[bool, cython.int]:
        state_lookup: tuple[Callable[[np.uint8], tuple[bool, cython.int]], ...] = (
            # State_default
            cls.default,
            # State_incb_pre_link
            cls.incb_pre_link,
            # State_incb_linked
            cls.incb_linked,
            # State_cr
            cls.cr,
            # State_lf_or_control
            cls.lf_or_control,
            # State_prepend
            cls.prepend,
            # State_hangul_l
            cls.hangul_l,
            # State_hangul_lv_or_v
            cls.hangul_lv_or_v,
            # State_hangul_lvt_or_t
            cls.hangul_lvt_or_t,
            # State_emoji
            cls.emoji,
            # State_emoji_zwj
            cls.emoji_zwj,
            # State_ri
            cls.ri,
        )
        return state_lookup[state](next_val)

    @classmethod
    def default_next_state(cls, next: np.uint8, should_break: bool) -> tuple[bool, cython.int]:
        _, next_state = cls.default(next)
        return should_break, next_state

    @classmethod
    def default(cls, next: np.uint8) -> tuple[bool, cython.int]:
        # default_next: tuple[bool, cython.int] = True, State_default

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

    @classmethod
    def incb_pre_link(cls, next: np.uint8) -> tuple[bool, cython.int]:
        if next == Break_InCB_Linker:
            return False, State_incb_linked
        
        is_incb_extend = next = Break_InCB_Extend
        is_extend = next == Break_Extend
        is_zwj = next == Break_ZWJ
        if is_incb_extend or is_extend or is_zwj:
            return False, State_incb_pre_link
        
        return cls.default(next)


    @classmethod
    def incb_linked(cls, next: np.uint8) -> tuple[bool, cython.int]:
        if next == Break_InCB_Consonant:
            return False, State_incb_pre_link

        is_incb_extend = next == Break_InCB_Extend
        is_extend = next == Break_Extend
        is_zwj = next == Break_ZWJ
        is_incb_link = next == Break_InCB_Linker
        if is_incb_extend or is_extend or is_zwj or is_incb_link:
            return False, State_incb_pre_link
        
        return cls.default_next_state(next, True)


    @classmethod
    def cr(cls, next: np.uint8) -> tuple[bool, cython.int]:
        if next == Break_LF:
            return False, State_lf_or_control
        return cls.default_next_state(next, True)

    @classmethod
    def lf_or_control(cls, next: np.uint8) -> tuple[bool, cython.int]:
        return cls.default_next_state(next, True)

    @classmethod
    def prepend(cls, next: np.uint8) -> tuple[bool, cython.int]:
        if next == Break_CR:
            return True, State_cr
        
        is_control = next == Break_Control
        is_lf = next == Break_LF
        if is_control or is_lf:
            return True, State_default

        return cls.default_next_state(next, False)

    @classmethod
    def hangul_l(cls, next: np.uint8) -> tuple[bool, cython.int]:
        if next == Break_L:
            return False, State_hangul_l

        is_v = next == Break_V
        is_lv = next == Break_LV
        if is_v or is_lv:
            return False, State_hangul_lv_or_v

        if next == Break_LVT:
            return False, State_hangul_lvt_or_t

        return cls.default(next)

    @classmethod
    def hangul_lv_or_v(cls, next: np.uint8) -> tuple[bool, cython.int]:
        if next == Break_V:
            return False, State_hangul_lv_or_v
        
        if next == Break_T:
            return False, State_hangul_lvt_or_t
        
        return cls.default(next)


    @classmethod
    def hangul_lvt_or_t(cls, next: np.uint8) -> tuple[bool, cython.int]:
        if next == Break_T:
            return False, State_hangul_lvt_or_t
    
        return cls.default(next)

    @classmethod
    def emoji(cls, next: np.uint8) -> tuple[bool, cython.int]:
        is_extend = next == Break_Extend
        is_incb_extend = next == Break_InCB_Extend
        
        if is_extend or is_incb_extend:
            return False, State_emoji
        if next == Break_ZWJ:
            return False, State_emoji_zwj
        return cls.default(next)

    @classmethod
    def emoji_zwj(cls, next: np.uint8) -> tuple[bool, cython.int]:
        if next == Break_Extended_Pictographic:
            return False, State_emoji
        
        return cls.default(next)

    @classmethod
    def ri(cls, next: np.uint8) -> tuple[bool, cython.int]:
        if next == Break_Regional_Indicator:
            return False, State_default
        return cls.default(next)
