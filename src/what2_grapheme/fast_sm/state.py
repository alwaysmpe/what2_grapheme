"""
Grapheme Cluster State Machine.

This state machine implements the boundary rules described
in section 3.1.1 Grapheme Cluster Boundary Rules at
https://unicode.org/reports/tr29/#Grapheme_Cluster_Boundary_Rules
with some minor alterations.

Note - Rule modifications
-------------------------
Rules as explicitly described would fail the associated break
grapheme tests for InCB sequences. The tests contain combinations
that are extended by Extend characters that don't have the InCB
Extend property (ZWJ and Extend). As such, InCB Extend is ignored in
the current implementation and the Extend property is used instead.
InCB Extend characters are a strict subset of those with the Extend
property.

Note - Use of Literal values
----------------------------
This implementation uses literal values instead of those
defined in the Break enum. This makes the code significantly
harder to read but in my benchmarks 10-20% faster to compute
the length of strings containing grapheme clusters. This can
be tested yourself by swapping the import of this to the state
machine from the simple implementation as they are otherwise
approximately the same.

Strings that don't contain grapheme clusters are less impacted
due to the send_default optimization in break_gen, other operations
are less proportionally impacted as they're performing more
operations outside of state machine transitions.
"""

from collections.abc import Callable

type StateRet = tuple[bool, StateFn, bool]
type StateFn = Callable[[int], StateRet]


class StateMachine:
    @classmethod
    def initial_state(cls, next_kind: int) -> StateRet:
        return cls._override_default(next_kind, should_break=False)

    @classmethod
    def default(cls, next_kind: int) -> StateRet:
        match next_kind:
            case 0:
                return True, cls.cr_GB3, False
            case 1:
                return True, cls.lf_or_control_GB4, False
            case 2:
                return True, cls.lf_or_control_GB4, False
            case 3:
                return True, cls.hangul_l_GB6, False
            case 4:
                return True, cls.hangul_lv_or_v_GB7, False
            case 5:
                return True, cls.hangul_lv_or_v_GB7, False
            case 6:
                return True, cls.hangul_lvt_or_t_GB8, False
            case 7:
                return True, cls.hangul_lvt_or_t_GB8, False
            case 8:
                return True, cls.prepend_GB9b, False
            case 9:
                return True, cls.incb_pre_link_GB9c, False
            case 10:
                return True, cls.emoji_pre_linked_GB11, False
            case 11:
                return True, cls.emoji_flag_ri_GB12, False
            case 12:
                return True, cls.default, True
            case _:
                return False, cls.default, True

    @classmethod
    def _override_default(cls, next_kind: int, *, should_break: bool) -> StateRet:
        _, next_state, is_default = cls.default(next_kind)
        return should_break, next_state, is_default

    @classmethod
    def cr_GB3(cls, next_kind: int) -> StateRet:
        if next_kind == 1:
            return False, cls.lf_or_control_GB4, False

        return cls._override_default(next_kind, should_break=True)

    @classmethod
    def lf_or_control_GB4(cls, next_kind: int) -> StateRet:
        return cls._override_default(next_kind, should_break=True)

    @classmethod
    def hangul_l_GB6(cls, next_kind: int) -> StateRet:
        if next_kind == 3:
            return False, cls.hangul_l_GB6, False

        if next_kind in {4, 5}:
            return False, cls.hangul_lv_or_v_GB7, False

        if next_kind == 7:
            return False, cls.hangul_lvt_or_t_GB8, False

        return cls.default(next_kind)

    @classmethod
    def hangul_lv_or_v_GB7(cls, next_kind: int) -> StateRet:
        if next_kind == 4:
            return False, cls.hangul_lv_or_v_GB7, False
        if next_kind == 6:
            return False, cls.hangul_lvt_or_t_GB8, False

        return cls.default(next_kind)

    @classmethod
    def hangul_lvt_or_t_GB8(cls, next_kind: int) -> StateRet:
        if next_kind == 6:
            return False, cls.hangul_lvt_or_t_GB8, False

        return cls.default(next_kind)

    @classmethod
    def prepend_GB9b(cls, next_kind: int) -> StateRet:
        return cls._override_default(next_kind, should_break=next_kind in {0, 1, 2})

    @classmethod
    def incb_pre_link_GB9c(cls, next_kind: int) -> StateRet:
        if next_kind == 16:
            return False, cls.incb_linked_GB9c, False

        if next_kind in {15, 17}:
            return False, cls.incb_pre_link_GB9c, False

        return cls.default(next_kind)

    @classmethod
    def incb_linked_GB9c(cls, next_kind: int) -> StateRet:
        if next_kind == 9:
            return False, cls.incb_pre_link_GB9c, False

        if next_kind in {15, 16, 17}:
            return False, cls.incb_linked_GB9c, False

        return cls.default(next_kind)

    @classmethod
    def emoji_pre_linked_GB11(cls, next_kind: int) -> StateRet:
        if next_kind == 13 or next_kind == 16 or next_kind == 17:
            return False, cls.emoji_pre_linked_GB11, False

        if next_kind == 15:
            return False, cls.emoji_linked_GB11, False

        return cls.default(next_kind)

    @classmethod
    def emoji_linked_GB11(cls, next_kind: int) -> StateRet:
        if next_kind == 10:
            return False, cls.emoji_pre_linked_GB11, False

        return cls.default(next_kind)

    @classmethod
    def emoji_flag_ri_GB12(cls, next_kind: int) -> StateRet:
        if next_kind == 11:
            return False, cls.default, True

        return cls.default(next_kind)
