from rich.console import Console

from what2_time import Timer
from what2.debug import dbg
import regex as re
# from what2_grapheme import w2
# from what2_grapheme.grapheme_property.cache import default_properties
# from what2_grapheme.grapheme_property.type import Break
import ugrapheme
# props = default_properties()

# dbg(props.ascii_other)

# crlf = w2.esc_ch_set("\r\n")
# dbg(crlf.c())
# assert 0
# import_logger = print
import_logger = None


with Timer("what2 import & warmup time", logger=import_logger):
    from what2_grapheme.grapheme_property.cache import warm_up as w2_warm_up
    from what2_grapheme.fast_sm import api as fast_sm_api
    from what2_grapheme.fast_re import api as fast_api
    # from what2_grapheme.egf import exp_api as fast_api
    w2_warm_up()

with Timer("grapheme import & warmup time", logger=import_logger):
    from grapheme import api
with Timer("pyuegc import & warmup time", logger=import_logger):
    from pyuegc.egc import EGC


# import ctypes.util as cutil

# import ctypes

# py_kind = ctypes.pythonapi["PyUnicode_KIND"]
# dbg(py_kind("fooo"))
# exit()
# import pyuegc.egc as pyegc
# arg = b'\\u2701\\u200d\\u2701\\u200d\\u231a'.decode("raw_unicode_escape")
# print(arg)
# dbg((api.graphemes(arg)))
# dbg(fast_api.graphemes(arg))
# # print(pyegc._BREAK_RULES)
# exit()

from bm import cases, rng, runner
from typing import cast
from collections.abc import Callable
# from what2.debug import dbg
from typing import Protocol

show_detail: bool = False
# show_detail: bool = True
show_summary: bool = True
verify = False
# verify = True
from what2_grapheme.simple_sm import api as simple_api


type LenFn = Callable[[str], int]
type SliceFn = Callable[[str, int, int], str]
type InFn = Callable[[str, str], bool]

class ULenFn(Protocol):
    def __call__(self, data: str, until: int | None = None) -> int:
        ...

console = Console()

bm = runner.Benchmark()

case_count = 10
ascii_len = 100000
iter_count = 100
grapheme_len = cast(LenFn, api.length)  # type: ignore reportUnknownMemberType
ugrapheme_len = cast(ULenFn, api.length)  # type: ignore reportUnknownMemberType

def uegc_len(data: str) -> int:
    return len(EGC(data))
re_pat = re.compile('\\X')
def regex_len(data: str) -> int:
    return len(re_pat.findall(data))
def regex_to_grapheme(data: str) -> list[str]:
    return re_pat.findall(data)


with_others = False
# with_others = True
if not with_others:

    len_specs: list[tuple[str, LenFn, rng.Generator]] = [
        # ("len builtin", len, rng.seeded_rng()),
        # ("what2", fast_sm_api.length, rng.seeded_rng()),
        ("what2_api", fast_api.length, rng.seeded_rng()),
        # ("ugrapheme", ugrapheme.grapheme_len, rng.seeded_rng()),

        # ("pyuegc", uegc_len, rng.seeded_rng()),
        # ("what2_simple", simple_api.length, rng.seeded_rng()),
        # ("grapheme", grapheme_len, rng.seeded_rng()),
    ]
    utf_len_specs = (
        # ("what2", fast_sm_api.length, rng.seeded_rng()),
        ("what2_api", fast_api.length, rng.seeded_rng()),
        # ("pyuegc", uegc_len, rng.seeded_rng()),
        # ("what2_simple", simple_api.length, rng.seeded_rng()),
        # ("grapheme", grapheme_len, rng.seeded_rng()),
        # ("ugrapheme", ugrapheme.grapheme_len, rng.seeded_rng()),
    )

    until_len_specs: list[tuple[str, ULenFn, rng.Generator]] = [
        # ("what2", fast_sm_api.length, rng.seeded_rng()),
        # ("what2_simple", simple_api.length, rng.seeded_rng()),
        # ("grapheme", ugrapheme_len, rng.seeded_rng()),
    ]

    to_grapheme_specs = [
        # ("what2", fast_sm_api.graphemes, rng.seeded_rng()),
        ("what2_api", fast_api.graphemes, rng.seeded_rng()),
        # ("pyuegc", EGC, rng.seeded_rng()),
        # ("grapheme", lambda x: list(api.graphemes(x)), rng.seeded_rng()),
    ]

    def str_slice(data: str, start: int | None = None, stop: int | None = None) -> str:
        return data[start: stop]

    grapheme_slice = cast(SliceFn, api.slice)  # type: ignore reportUnknownMemberType
    slice_specs: tuple[tuple[str, SliceFn, rng.Generator], ...] = (
        # ("str slice", str_slice, rng.seeded_rng()),
        # ("what2", fast_sm_api.strslice, rng.seeded_rng()),
        ("what2_api", fast_api.strslice, rng.seeded_rng()),
        # ("pyuegc", lambda x, start, stop: "".join(EGC(x)[start: stop]), rng.seeded_rng()),
        # ("what2_simple", simple_api.strslice, rng.seeded_rng()),
        # ("grapheme", grapheme_slice, rng.seeded_rng()),
    )
    neg_slice_specs: tuple[tuple[str, SliceFn, rng.Generator], ...] = (
        # ("str slice", str_slice, rng.seeded_rng()),
        # ("what2", fast_sm_api.strslice, rng.seeded_rng()),
        ("what2_api", fast_api.strslice, rng.seeded_rng()),
        # ("pyuegc", lambda x, start, stop: "".join(EGC(x)[start: stop]), rng.seeded_rng()),
        # ("what2_simple", simple_api.strslice, rng.seeded_rng()),
        # ("grapheme", grapheme_slice, rng.seeded_rng()),
    )

    grapheme_contains = cast(Callable[[str, str], bool], api.contains)  # type: ignore reportUnknownMemberType
    contains_specs = (
        # ("builtin in", str.__contains__, rng.seeded_rng()),
        # ("what2", fast_sm_api.contains, rng.seeded_rng()),
        ("what2_api", fast_api.contains, rng.seeded_rng()),
        # ("what2_simple", simple_api.contains, rng.seeded_rng()),
        # ("grapheme", grapheme_contains, rng.seeded_rng()),
    )

    is_safe_specs = (
        # ("what2", fast_sm_api.is_safe, rng.seeded_rng()),
        ("what2_api", fast_api.is_safe, rng.seeded_rng()),
    )
else:
    len_specs: list[tuple[str, LenFn, rng.Generator]] = [
        ("str builtin", len, rng.seeded_rng()),
        ("what2", fast_sm_api.length, rng.seeded_rng()),
        ("what2_api", fast_api.length, rng.seeded_rng()),
        ("pyuegc", uegc_len, rng.seeded_rng()),
        # ("what2_simple", simple_api.length, rng.seeded_rng()),
        ("grapheme", grapheme_len, rng.seeded_rng()),
        ("ugrapheme", ugrapheme.grapheme_len, rng.seeded_rng()),
        ("regex", regex_len, rng.seeded_rng()),

    ]
    utf_len_specs = (
        ("what2", fast_sm_api.length, rng.seeded_rng()),
        ("what2_api", fast_api.length, rng.seeded_rng()),
        ("pyuegc", uegc_len, rng.seeded_rng()),
        # ("what2_simple", simple_api.length, rng.seeded_rng()),
        ("grapheme", grapheme_len, rng.seeded_rng()),
        ("ugrapheme", ugrapheme.grapheme_len, rng.seeded_rng()),
        ("regex", regex_len, rng.seeded_rng()),
    )

    until_len_specs: list[tuple[str, ULenFn, rng.Generator]] = [
        ("what2", fast_sm_api.length, rng.seeded_rng()),
        ("what2_api", fast_api.length, rng.seeded_rng()),
        # ("what2_simple", simple_api.length, rng.seeded_rng()),
        ("grapheme", ugrapheme_len, rng.seeded_rng()),
    ]

    to_grapheme_specs = [
        ("what2", fast_sm_api.graphemes, rng.seeded_rng()),
        ("what2_api", fast_api.graphemes, rng.seeded_rng()),
        ("pyuegc", EGC, rng.seeded_rng()),
        ("grapheme", lambda x: list(api.graphemes(x)), rng.seeded_rng()),
        ("ugrapheme", ugrapheme.grapheme_split, rng.seeded_rng()),
        ("regex", regex_to_grapheme, rng.seeded_rng()),
    ]

    def str_slice(data: str, start: int | None = None, stop: int | None = None) -> str:
        return data[start: stop]

    grapheme_slice = cast(SliceFn, api.slice)  # type: ignore reportUnknownMemberType
    slice_specs: tuple[tuple[str, SliceFn, rng.Generator], ...] = (
        ("str builtin", str_slice, rng.seeded_rng()),
        ("what2", fast_sm_api.strslice, rng.seeded_rng()),
        ("what2_api", fast_api.strslice, rng.seeded_rng()),
        ("pyuegc", lambda x, start, stop: "".join(EGC(x)[start: stop]), rng.seeded_rng()),
        # ("what2_simple", simple_api.strslice, rng.seeded_rng()),
        ("grapheme", grapheme_slice, rng.seeded_rng()),
        ("ugrapheme", ugrapheme.grapheme_slice, rng.seeded_rng()),
    )
    neg_grapheme_slice = cast(SliceFn, api.slice)  # type: ignore reportUnknownMemberType
    neg_slice_specs: tuple[tuple[str, SliceFn, rng.Generator], ...] = (
        ("str builtin", str_slice, rng.seeded_rng()),
        ("what2", fast_sm_api.strslice, rng.seeded_rng()),
        ("what2_api", fast_api.strslice, rng.seeded_rng()),
        ("pyuegc", lambda x, start, stop: "".join(EGC(x)[start: stop]), rng.seeded_rng()),
        # ("what2_simple", simple_api.strslice, rng.seeded_rng()),
        ("grapheme", grapheme_slice, rng.seeded_rng()),
        ("ugrapheme", lambda x, s, e: ugrapheme.graphemes(x).gslice(s, e), rng.seeded_rng()),
    )

    grapheme_contains = cast(Callable[[str, str], bool], api.contains)  # type: ignore reportUnknownMemberType
    contains_specs = (
        ("str builtin", str.__contains__, rng.seeded_rng()),
        ("what2", fast_sm_api.contains, rng.seeded_rng()),
        ("what2_api", fast_api.contains, rng.seeded_rng()),
        # ("what2_simple", simple_api.contains, rng.seeded_rng()),
        ("grapheme", grapheme_contains, rng.seeded_rng()),
        ("ugrapheme", lambda st, sub: sub in ugrapheme.graphemes(st), rng.seeded_rng()),
    )

    is_safe_specs = (
        ("what2", fast_sm_api.is_safe, rng.seeded_rng()),
        ("what2_api", fast_api.is_safe, rng.seeded_rng()),
        # ("what2_api_alt", fast_api.alt_is_safe, rng.seeded_rng()),
        # ("what2_api_alt2", fast_api.set_is_safe, rng.seeded_rng()),
        # ("what2_api_xalt", fast_api.xset_is_safe, rng.seeded_rng()),
    )


def warmup():
    """
    Call some relevent api's at least once.

    Reduces impact from python bytecode compilation, etc.
    """
    import_logger = print
    import_logger = None

    for fn_name, fn, _ in len_specs:
        for arg in cases.rand_utf_joined(6, 100, rng.seeded_rng()):
            # print(fn_name)
            # print(fn.__name__)
            with Timer(fn_name, logger=import_logger):
                fn(arg)

    # fn uses cached sets not necessarily used by other apis
    for _, fn, _ in is_safe_specs:
        for arg in cases.rand_utf_joined(3, 100, rng.seeded_rng()):
            with Timer(fn.__name__, logger=import_logger):
                fn(arg)
                # dbg(fn(f"{arg}\r\n", skip_crlf=False))

    if not verify:
        return

    print("verifying")
    results = {}
    for idx, arg in enumerate(cases.rand_utf_joined(6000, 1000, rng.seeded_rng())):
        # arg = fast_api.strslice(arg, 339, 342)
        # if idx == 50:
        #     continue
        # arg = fast_api.strslice(arg, 16, 17)
        last_name = None
        for fn_name, fn, _ in to_grapheme_specs:
            if fn_name == "grapheme":
                continue
            # is_w2 = fn_name.startswith("what2")
            # is_ug = fn_name == "ugrapheme"
            # if not (is_w2 or is_ug):
            #     continue
            # print(fn_name)

            ret = fn(arg)
            if arg in results:
                if ret != results[arg]:
                    print(last_name)
                    print(fn_name)
                    # print(arg)
                    print(ret)
                    print(results[arg])
                    # print(len(ret))
                    # print(len(results[arg]))

                    from what2_grapheme.grapheme_property.cache import default_properties
                    props = default_properties()

                    dbg([props.char_to_enum(char).name for char in arg])
                    dbg([[props.char_to_enum(char).name for char in chunk] for chunk in ugrapheme.grapheme_split(arg)])
                    dbg([[props.char_to_enum(char).name for char in chunk] for chunk in fast_api.graphemes(arg)])
                    dbg([[props.char_to_enum(char).name for char in chunk] for chunk in fast_sm_api.graphemes(arg)])
                    dbg([[props.char_to_enum(char).name for char in chunk] for chunk in api.graphemes(arg)])
                    dbg(arg.encode("raw_unicode_escape"))
                    for pos, (lhs, rhs) in enumerate(zip(ret, results[arg])):
                        if lhs == rhs:
                            continue
                        dbg(pos)
                        break
                    dbg(idx)
                    # dbg([props.char_to_cat(char) for char in arg])
                    # for char in arg:

                assert ret == results[arg]
            else:
                results[arg] = ret
            last_name = fn_name

    results = {}
    for idx, arg in enumerate(cases.rand_utf_joined(60, 1000, rng.seeded_rng())):
        # if idx == 50:
        #     continue
        for fn_name, fn, _ in neg_slice_specs:
            is_w2 = fn_name.startswith("what2_api")
            is_ug = fn_name == "ugrapheme"
            if not (is_w2 or is_ug):
                continue

            # print(fn_name)
            # print(fn.__name__)
            ret = fn(arg, -300, -100)
            if arg in results:
                if ret != results[arg]:
                    print(fn_name)
                    print(f"{len(ret)=}")
                    print(f"{len(results[arg])=}")
                    # print(arg)
                    # print(ret)
                    # print(results[arg])
                    # print(len(ret))
                    # print(len(results[arg]))

                    from what2_grapheme.grapheme_property.cache import default_properties
                    props = default_properties()

                    # dbg([props.char_to_enum(char) for char in arg])
                    # dbg([[props.char_to_enum(char) for char in chunk] for chunk in ugrapheme.grapheme_split(arg)])
                    # dbg([[props.char_to_enum(char) for char in chunk] for chunk in fast_api.graphemes(arg)])
                    # dbg(arg.encode("raw_unicode_escape"))
                    for pos, (lhs, rhs) in enumerate(zip(ret, results[arg])):
                        if lhs == rhs:
                            continue
                        print(pos)
                        break
                    print(f"{idx=}")
                    # dbg([props.char_to_cat(char) for char in arg])
                    # for char in arg:

                assert ret == results[arg]
            else:
                results[arg] = ret


def main():
    print("starting")
    warmup()
    print("warmed up")
    if verify:
        return

    bm_ascii_len()
    print("done ascii len")
    bm_utf_unjoined_len()
    print("done utf len")
    bm_utf_joined_len()
    print("done utf compound len")
    # bm_to_grapheme()
    # print("done split graphemes")
    # bm_ascii_slice()
    # print("done ascii slice")
    # bm_neg_ascii_slice()
    # print("done neg ascii slice")
    # bm_str_in_str()
    # print("done str in str")
    # bm_contains_graphemes()
    # print("done any graphemes")
    # bm_utf_until_len()
    # print("done utf compound len up to")

    if show_summary:
        for table in bm.summaries():
            console.print(table)


def bm_ascii_len():
    gname = "ASCII String Length"
    short_name = "len(ascii)"
    bm.add_group(runner.Group(gname, short_name))
    for name, fn, fn_rng in len_specs:
        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_ascii(case_count, ascii_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
            )
    if show_detail:
        console.print(bm.table(gname))


def bm_to_grapheme():
    gname = "Split ASCII Graphemes"
    short_name = "api.graphemes(ascii)"
    bm.add_group(runner.Group(gname, short_name))
    for name, fn, fn_rng in to_grapheme_specs:
        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_ascii(case_count, ascii_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
            )
    gname = "Split Grouping Graphemes"
    short_name = "api.graphemes(utf_wgroups)"
    bm.add_group(runner.Group(gname, short_name))
    for name, fn, fn_rng in to_grapheme_specs:
        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_utf_joined(case_count, ascii_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
            )
    if show_detail:
        console.print(bm.table(gname))



def bm_ascii_slice():

    gname = "Start of ASCII Slice"
    short_name = "ascii[100: 300]"
    bm.add_group(runner.Group(gname, short_name))
    for name, fn, fn_rng in slice_specs:
        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_ascii(case_count, ascii_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
                100,
                300,
            )
    if show_detail:
        console.print(bm.table(gname))

    gname = "End of ASCII Slice"
    short_name = f"ascii[{ascii_len - 300}: {ascii_len - 100}]"
    bm.add_group(runner.Group(gname, short_name))
    for name, fn, fn_rng in slice_specs:
        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_ascii(case_count, ascii_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
                len(arg) - 300,
                len(arg) - 100,
            )
    if show_detail:
        console.print(bm.table(gname))

    gname = "Start of UTF Joining Slice"
    short_name = "utf_wgroups[100: 300]"
    bm.add_group(runner.Group(gname, short_name))
    for name, fn, fn_rng in slice_specs:
        if name == "str builtin":
            continue
        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_utf_joined(case_count, ascii_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
                100,
                300,
            )
    if show_detail:
        console.print(bm.table(gname))

    gname = "End of UTF Joining Slice"
    short_name = f"utf_wgroups[{ascii_len - 300}: {ascii_len - 100}]"
    bm.add_group(runner.Group(gname, short_name))
    for name, fn, fn_rng in slice_specs:
        if name == "str builtin":
            continue

        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_utf_joined(case_count, ascii_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
                len(arg) - 300,
                len(arg) - 100,
            )
    if show_detail:
        console.print(bm.table(gname))


def bm_neg_ascii_slice():

    gname = "Start of ASCII Slice - negative index"
    short_name = "ascii[100 - len(ascii): 300 - len(ascii)]"
    bm.add_group(runner.Group(gname, short_name))
    for name, fn, fn_rng in neg_slice_specs:
        is_w2 = name.startswith("what2")
        is_builtin = "builtin" in name
        is_ug = name == "ugrapheme"
        if not (is_w2 or is_builtin or is_ug):
            continue
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_ascii(case_count, ascii_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
                100 - len(arg),
                300 - len(arg),
            )
    if show_detail:
        console.print(bm.table(gname))

    gname = "End of ASCII Slice - negative index"
    short_name = f"ascii[-300: -100]"
    bm.add_group(runner.Group(gname, short_name))
    for name, fn, fn_rng in neg_slice_specs:
        is_w2 = name.startswith("what2")
        is_builtin = "builtin" in name
        is_ug = name == "ugrapheme"
        if not (is_w2 or is_builtin or is_ug):
            continue
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_ascii(case_count, ascii_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
                -300,
                -100,
            )
    if show_detail:
        console.print(bm.table(gname))

    gname = "Start of UTF Joining Slice - negative index"
    short_name = "utf_wgroups[100 - len(utf_wgroups): 300 - len(utf_wgroups)]"
    bm.add_group(runner.Group(gname, short_name))
    for name, fn, fn_rng in neg_slice_specs:
        is_w2 = name.startswith("what2")
        is_ug = name == "ugrapheme"
        if not (is_w2 or is_ug):
            continue
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_utf_joined(case_count, ascii_len, fn_rng):
            str_len = fast_api.length(arg)
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
                100 - str_len,
                300 - str_len,
            )
    if show_detail:
        console.print(bm.table(gname))

    gname = "End of UTF Joining Slice - negative index"
    short_name = f"utf_wgroups[-300: -100]"
    bm.add_group(runner.Group(gname, short_name))
    for name, fn, fn_rng in neg_slice_specs:
        is_w2 = name.startswith("what2")
        is_ug = name == "ugrapheme"
        if not (is_w2 or is_ug):
            continue

        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_utf_joined(case_count, ascii_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
                -300,
                -100,
            )
    if show_detail:
        console.print(bm.table(gname))


def bm_str_in_str():

    gname = "ASCII String Contains Start"
    short_name = "ascii[:100] in x"
    bm.add_group(runner.Group(gname, short_name))
    for name, fn, fn_rng in contains_specs:
        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_ascii(case_count, ascii_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
                arg[:100]
            )
    if show_detail:
        console.print(bm.table(gname))


    gname = "ASCII String Contains End"
    short_name = "ascii[-100:] in x"
    bm.add_group(runner.Group(gname, short_name))
    for name, fn, fn_rng in contains_specs:
        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_ascii(case_count, ascii_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
                arg[-100:]
            )
    gname = "UTF Joining String Contains Start"
    short_name = "utf_wgroups[:100] in utf_wgroups"
    bm.add_group(runner.Group(gname, short_name))
    for name, fn, fn_rng in contains_specs:
        if name == "str builtin":
            continue
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_utf_joined(case_count, ascii_len, fn_rng):
            sliced_data = fast_api.strslice(arg, None, 100)
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
                sliced_data,
            )
    if show_detail:
        console.print(bm.table(gname))

    gname = "UTF Joining String Contains End"
    short_name = "utf_wgroups[-100:] in utf_wgroups"
    bm.add_group(runner.Group(gname, short_name))
    is_first = True
    result_map: dict[bool, set[str]] = {
        True: set(),
        False: set(),
    }
    for name, fn, fn_rng in contains_specs:
        if name == "str builtin":
            continue
        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_utf_joined(case_count, ascii_len, fn_rng):
            utf_len = fast_api.length(arg)
            sliced_data = fast_api.strslice(arg, utf_len - 100, None)
            assert sliced_data in arg
            result = fn(
                arg,
                sliced_data
            )
            # if is_first:
            #     result_map[result].add(arg)
            # else:
            #     if arg not in result_map[result]:
            #         # dbg(arg)
            #         # dbg(sliced_data)
            #         dbg(name)
            #         dbg(fn(arg, sliced_data))
            #     assert arg in result_map[result]


            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
                sliced_data,
            )
        is_first = False
    if show_detail:
        console.print(bm.table(gname))


def bm_contains_graphemes():
    gname = "ASCII String contains graphemes"
    short_name = "api.is_safe(ascii)"
    bm.add_group(runner.Group(gname, short_name))
    utf_nj_len = ascii_len
    for name, fn, fn_rng in is_safe_specs:
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_ascii(case_count, utf_nj_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
            )
    if show_detail:
        console.print(bm.table(gname))

    gname = "UTF Distinct String contains graphemes"
    short_name = "api.is_safe(utf_wogroups)"
    bm.add_group(runner.Group(gname, short_name))
    utf_nj_len = ascii_len
    for name, fn, fn_rng in is_safe_specs:
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_utf_unjoined(case_count, utf_nj_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
            )
    if show_detail:
        console.print(bm.table(gname))

    gname = "UTF Joining String contains graphemes"
    short_name = "api.is_safe(utf_wgroups)"
    bm.add_group(runner.Group(gname, short_name))
    utf_j_len = ascii_len
    is_first = True
    result_map: dict[bool, set[str]] = {
        True: set(),
        False: set(),
    }

    for name, fn, fn_rng in is_safe_specs:
        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_utf_joined(case_count, utf_j_len, fn_rng):
            result = fn(
                arg,
            )
            # dbg(name)
            if is_first:
                result_map[result].add(arg)
            else:
                assert arg in result_map[result]

            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
            )
        is_first = False
    if show_detail:
        console.print(bm.table(gname))


def bm_utf_unjoined_len():
    gname = "UTF Distinct String Length"
    short_name = "len(utf_wogroups)"
    bm.add_group(runner.Group(gname, short_name))
    utf_nj_len = ascii_len
    for name, fn, fn_rng in len_specs:
        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_utf_unjoined(case_count, utf_nj_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
            )
    if show_detail:
        console.print(bm.table(gname))

def bm_utf_joined_len():
    gname = "UTF Joining String Length"
    short_name = "len(utf_wgroups)"
    bm.add_group(runner.Group(gname, short_name))
    utf_j_len = ascii_len
    for name, fn, fn_rng in utf_len_specs:
        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_utf_joined(case_count, utf_j_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
            )
    if show_detail:
        console.print(bm.table(gname))

def bm_utf_until_len():
    gname = "Limited UTF Joining String Length"
    short_name = "api.length(utf_wgroups, 500)"
    bm.add_group(runner.Group(gname, short_name))
    utf_j_len = ascii_len
    for name, fn, fn_rng in until_len_specs:
        # dbg(name)
        bm.add_run(gname, name, iterations=iter_count)
        for arg in cases.rand_utf_joined(case_count, utf_j_len, fn_rng):
            bm.extra_runs(
                gname,
                name,
                1,
                fn,
                arg,
                utf_j_len // 4,
            )
    if show_detail:
        console.print(bm.table(gname))

def profile_len():
    from cProfile import Profile
    from pstats import SortKey
    import io, pstats
    utf_len = ascii_len
    pr = Profile()
    for arg in cases.rand_utf_joined(case_count, utf_len, rng.seeded_rng()):
        pr.enable()
        fast_sm_api.length(arg)
        pr.disable()

    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

if __name__ == "__main__":
    main()
