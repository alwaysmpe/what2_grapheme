from collections.abc import Callable

from what2_grapheme.grapheme_property.type import Break

type StateRet = tuple[bool, StateFn, bool]
type StateFn = Callable[[int], StateRet]


class StateMachine:
    @classmethod
    def initial_state(cls, next_kind: int) -> StateRet:
        return cls._override_default(next_kind, should_break=False)

    @classmethod
    def default(cls, next_kind: int) -> StateRet:
        match next_kind:
            case Break.CR:
                return True, cls.cr_GB3, False
            case Break.LF:
                return True, cls.lf_or_control_GB4, False
            case Break.Control:
                return True, cls.lf_or_control_GB4, False
            case Break.L:
                return True, cls.hangul_l_GB6, False
            case Break.V:
                return True, cls.hangul_lv_or_v_GB7, False
            case Break.LV:
                return True, cls.hangul_lv_or_v_GB7, False
            case Break.T:
                return True, cls.hangul_lvt_or_t_GB8, False
            case Break.LVT:
                return True, cls.hangul_lvt_or_t_GB8, False
            case Break.Prepend:
                return True, cls.prepend_GB9b, False
            case Break.InCB_Consonant:
                return True, cls.incb_pre_link_GB9c, False
            case Break.Extended_Pictographic:
                return True, cls.emoji_pre_linked_GB11, False
            case Break.Regional_Indicator:
                return True, cls.emoji_flag_ri_GB12, False
            case Break.Other:
                return True, cls.default, True
            case _:
                return False, cls.default, True

    @classmethod
    def _override_default(cls, next_kind: int, *, should_break: bool) -> StateRet:
        return should_break, *cls.default(next_kind)[1:]

    @classmethod
    def cr_GB3(cls, next_kind: int) -> StateRet:
        if next_kind == Break.LF:
            return False, cls.lf_or_control_GB4, False

        return cls._override_default(next_kind, should_break=True)

    @classmethod
    def lf_or_control_GB4(cls, next_kind: int) -> StateRet:
        return cls._override_default(next_kind, should_break=True)

    @classmethod
    def hangul_l_GB6(cls, next_kind: int) -> StateRet:
        if next_kind == Break.L:
            return False, cls.hangul_l_GB6, False

        if next_kind == Break.LV or next_kind == Break.V:
            return False, cls.hangul_lv_or_v_GB7, False

        if next_kind == Break.LVT:
            return False, cls.hangul_lvt_or_t_GB8, False

        return cls.default(next_kind)

    @classmethod
    def hangul_lv_or_v_GB7(cls, next_kind: int) -> StateRet:
        if next_kind == Break.V:
            return False, cls.hangul_lv_or_v_GB7, False
        if next_kind == Break.T:
            return False, cls.hangul_lvt_or_t_GB8, False

        return cls.default(next_kind)

    @classmethod
    def hangul_lvt_or_t_GB8(cls, next_kind: int) -> StateRet:
        if next_kind == Break.T:
            return False, cls.hangul_lvt_or_t_GB8, False

        return cls.default(next_kind)

    @classmethod
    def prepend_GB9b(cls, next_kind: int) -> StateRet:
        is_cr = next_kind == Break.CR
        is_lf = next_kind == Break.LF
        is_ctrl = next_kind == Break.Control
        is_ctl_code = is_cr or is_lf or is_ctrl

        return cls._override_default(next_kind, should_break=is_ctl_code)

    @classmethod
    def incb_pre_link_GB9c(cls, next_kind: int) -> StateRet:
        if next_kind == Break.InCB_Linker:
            return False, cls.incb_linked_GB9c, False

        is_extend = next_kind == Break.InCB_Extend
        is_zwj = next_kind == Break.ZWJ

        if is_extend or is_zwj:
            return False, cls.incb_pre_link_GB9c, False

        return cls.default(next_kind)

    @classmethod
    def incb_linked_GB9c(cls, next_kind: int) -> StateRet:
        if next_kind == Break.InCB_Consonant:
            return False, cls.incb_pre_link_GB9c, False

        is_incb_link = next_kind == Break.InCB_Linker
        is_incb_extend = next_kind == Break.InCB_Extend
        is_zwj = next_kind == Break.ZWJ

        if is_incb_link or is_incb_extend or is_zwj:
            return False, cls.incb_linked_GB9c, False

        return cls.default(next_kind)

    @classmethod
    def emoji_pre_linked_GB11(cls, next_kind: int) -> StateRet:
        is_extend = (next_kind == Break.Extend or next_kind == Break.InCB_Extend or next_kind == Break.InCB_Linker)
        is_zwj = next_kind == Break.ZWJ
        if is_extend:
            return False, cls.emoji_pre_linked_GB11, False

        if is_zwj:
            return False, cls.emoji_linked_GB11, False

        return cls.default(next_kind)

    @classmethod
    def emoji_linked_GB11(cls, next_kind: int) -> StateRet:
        if next_kind == Break.Extended_Pictographic:
            return False, cls.emoji_pre_linked_GB11, False

        return cls.default(next_kind)

    @classmethod
    def emoji_flag_ri_GB12(cls, next_kind: int) -> StateRet:
        if next_kind == Break.Regional_Indicator:
            return False, cls.default, True

        return cls.default(next_kind)
