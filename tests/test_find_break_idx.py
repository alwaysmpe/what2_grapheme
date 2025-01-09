from what2_grapheme.fast_re import internal as re_internal
from what2_grapheme.fast_sm.break_gen import is_definite_break
from what2_grapheme.fast_sm.state import StateFn, StateMachine
from what2_grapheme.grapheme_property.type import Break

# from what2 import dbg
import pytest


@pytest.fixture(params=list(Break))
def prev_break(request: pytest.FixtureRequest) -> Break:
    # prev_break = request.param
    # dbg(prev_break)
    # dbg(prev_break.value)
    return request.param


@pytest.fixture(params=list(Break))
def next_break(request: pytest.FixtureRequest) -> Break:
    # next_break = request.param
    # dbg(next_break)
    # dbg(next_break.value)
    return request.param


def test_breakable(prev_break: Break, next_break: Break):
    state_fns: list[StateFn] = [
        getattr(StateMachine, fn)
        for fn in dir(StateMachine)
        if not fn.startswith("_")
    ]

    can_break = True
    for state_fn in state_fns:
        next_state_fn = state_fn(prev_break.value)[1]
        should_break = next_state_fn(next_break.value)[0]
        # dbg(state_fn.__name__)
        # dbg(next_state_fn.__name__)
        # dbg(should_break)
        can_break = bool(should_break and can_break)

    is_inferred_break = is_definite_break(prev_break, next_break)

    assert is_inferred_break is can_break

    re_ir_str = f"{getattr(re_internal, prev_break.name)}{getattr(re_internal, next_break.name)}"

    re_pat = re_internal.definite_break_re()

    re_match = re_pat.match(re_ir_str)

    if can_break:
        assert re_match is not None
