from typing import Callable

import numpy as np

from what2_utf_parse.grapheme_cluster.property import Break

type ShouldBreak = bool
type TransformRet = tuple[ShouldBreak, StateTransform]
type StateTransform = Callable[[np.uint8], TransformRet]


class StateMachine:
    @classmethod
    def default(cls, next: np.uint8) -> TransformRet:
        match next:
            case Break.Other.value:
                return True, cls.default
            case Break.CR.value:
                return True, cls.cr
            case Break.LF.value | Break.Control.value:
                return True, cls.lf_or_control
            case Break.Extend.value | Break.InCB_Extend.value | Break.InCB_Linker.value | Break.SpacingMark.value | Break.ZWJ.value:
                return False, cls.default
            case Break.Extended_Pictographic.value:
                return True, cls.emoji
            case Break.Regional_Indicator.value:
                return True, cls.ri
            case Break.L.value:
                return True, cls.hangul_l
            case Break.LV.value | Break.V.value:
                return True, cls.hangul_lv_or_v
            case Break.LVT.value | Break.T.value:
                return True, cls.hangul_lvt_or_t
            case Break.Prepend.value:
                return True, cls.prepend
            case Break.InCB_Consonant.value:
                return True, cls.incb_pre_link
            case _:
                return True, cls.default

    @classmethod
    def default_next_state(cls, next: np.uint8, should_break: bool) -> TransformRet:
        _, next_state = cls.default(next)
        return should_break, next_state

    @classmethod
    def incb_pre_link(cls, next: np.uint8) -> TransformRet:
        match next:
            case Break.InCB_Extend.value | Break.Extend.value | Break.ZWJ.value:
                return False, cls.incb_pre_link
            case Break.InCB_Linker.value:
                return False, cls.incb_linked
            case _:
                return cls.default(next)

    @classmethod
    def incb_linked(cls, next: np.uint8) -> TransformRet:
        match next:
            case Break.InCB_Extend.value | Break.Extend.value | Break.ZWJ.value | Break.InCB_Linker.value:
                return False, cls.incb_linked
            case Break.InCB_Consonant.value:
                return False, cls.incb_pre_link
            case _:
                return cls.default_next_state(next, True)

    @classmethod
    def cr(cls, next: np.uint8) -> TransformRet:
        match next:
            case Break.LF.value:
                return False, cls.lf_or_control
            case _:
                return cls.default_next_state(next, True)

    @classmethod
    def lf_or_control(cls, next: np.uint8) -> TransformRet:
        return cls.default_next_state(next, True)

    @classmethod
    def prepend(cls, next: np.uint8) -> TransformRet:
        match next:
            case Break.Control.value | Break.LF.value:
                return True, cls.default
            case Break.CR.value:
                return True, cls.cr
            case _:
                return cls.default_next_state(next, False)

    @classmethod
    def hangul_l(cls, next: np.uint8) -> TransformRet:
        match next:
            case Break.V.value | Break.LV.value:
                return False, cls.hangul_lv_or_v
            case Break.LVT.value:
                return False, cls.hangul_lvt_or_t
            case Break.L.value:
                return False, cls.hangul_l
            case _:
                return cls.default(next)

    @classmethod
    def hangul_lv_or_v(cls, next: np.uint8) -> TransformRet:
        match next:
            case Break.V.value:
                return False, cls.hangul_lv_or_v
            case Break.T.value:
                return False, cls.hangul_lvt_or_t
            case _:
                return cls.default(next)

    @classmethod
    def hangul_lvt_or_t(cls, next: np.uint8) -> TransformRet:
        match next:
            case Break.T.value:
                return False, cls.hangul_lvt_or_t
            case _:
                return cls.default(next)

    @classmethod
    def emoji(cls, next: np.uint8) -> TransformRet:
        match next:
            case Break.Extend.value | Break.InCB_Extend.value:
                return False, cls.emoji
            case Break.ZWJ.value:
                return False, cls.emoji_zwj
            case _:
                return cls.default(next)

    @classmethod
    def emoji_zwj(cls, next: np.uint8) -> TransformRet:
        match next:
            case Break.Extended_Pictographic.value:
                return False, cls.emoji
            case _:
                return cls.default(next)

    @classmethod
    def ri(cls, next: np.uint8) -> TransformRet:
        match next:
            case Break.Regional_Indicator.value:
                return False, cls.default
            case _:
                return cls.default(next)
