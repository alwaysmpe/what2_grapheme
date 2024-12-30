"""
Grapheme clustering implementation.

Implemented by mapping all characters in input strings
to a character representing their associated break
property then clustering using a regular expression.
"""
from collections.abc import Iterator
import re
from typing import cast

from what2_regex import w2

from what2_grapheme.fast_sm.api import iter_grapheme_sizes
from what2_grapheme.grapheme_property.cache import GraphemeBreak, default_properties
from what2_grapheme.grapheme_property.lookup import MAX_ORD
from what2_grapheme.util.caching import cache, lru_cache
from what2_grapheme.util.iter import sliding_window

CR = "a"
LF = chr(ord(CR) + 1)
Control = chr(ord(LF) + 1)
L = chr(ord(Control) + 1)
V = chr(ord(L) + 1)
LV = chr(ord(V) + 1)
T = chr(ord(LV) + 1)
LVT = chr(ord(T) + 1)
Prepend = chr(ord(LVT) + 1)
InCB_Consonant = chr(ord(Prepend) + 1)
Extended_Pictographic = chr(ord(InCB_Consonant) + 1)
Regional_Indicator = chr(ord(Extended_Pictographic) + 1)
Other = chr(ord(Regional_Indicator) + 1)
Extend = chr(ord(Other) + 1)
SpacingMark = chr(ord(Extend) + 1)
ZWJ = chr(ord(SpacingMark) + 1)
InCB_Linker = chr(ord(ZWJ) + 1)


@cache
def ord_encode_map(properties: GraphemeBreak) -> dict[int, str]:
    """
    Get a mapping from ordinal to break property character.
    """
    return {
        i: chr(ord("a") + int(properties.code_to_cat(i)))
        for i in range(MAX_ORD)
    }


def _fast_safe(data: str, until: int | None, properties: GraphemeBreak) -> tuple[str, bool]: # noqa: ARG001
    """
    Fast but not comprehensive test to see if a string contains graphemes.
    """
    safe_pat = _fast_safe_re_ascii(properties, skip_crlf=False)
    re_match = safe_pat.match(data)

    if (re_match is not None) and (re_match.end() == len(data)):
        return "", True

    str_ch = data.translate(ord_encode_map(properties))

    safe_pat = _fast_safe_re(properties)
    re_match = safe_pat.match(str_ch)

    if re_match is None:
        return str_ch, False

    return str_ch, re_match.end() == len(data)


@cache
def _fast_safe_re(properties: GraphemeBreak) -> re.Pattern[str]:
    """
    A regex to match all non-joining grapheme characters.

    Not a comprehensive test for joining as a character
    may join if only followed by certain other characters.
    """
    codes = properties.never_join_codes
    ch_set = w2.ch_set(
        *(
            chr(ord(CR) + int(chcode))
            for chcode in codes
        ),
    ).repeat
    return ch_set.c()


@lru_cache(maxsize=2)
def _fast_safe_re_ascii(properties: GraphemeBreak, *, skip_crlf: bool) -> re.Pattern[str]:
    """
    A regex to match all non-joining ASCII characters.

    This is not the same as `_fast_safe_re` as regex
    matching only ASCII characters is (noticeably)
    faster than all utf8 characters.
    """
    codes = properties.ascii_other
    if skip_crlf:
        esc_ch_set = w2.ch_set.esc("\r", *codes).repeat
    else:
        esc_ch_set = w2.ch_set.esc(*codes).repeat
    return esc_ch_set.c()


def is_safe(data: str, properties: GraphemeBreak | None = None, *, skip_crlf: bool = False) -> bool:
    """
    Test whether a string contains grapheme clusters.

    If a string is safe no special string handling
    is necessary.
    """
    if properties is None:
        properties = default_properties()

    safe_pat = _fast_safe_re_ascii(properties, skip_crlf=skip_crlf)
    re_match = safe_pat.match(data)

    if (re_match is not None) and (re_match.end() == len(data)):
        return True

    n_j = properties.never_join_chars
    if n_j.issuperset(data):
        return True

    if not skip_crlf:
        return all(size == 1 for size in iter_grapheme_sizes(data, properties))
    return all((len(grapheme) == 1 or grapheme == "\r\n") for grapheme in iter_graphemes(data, properties))


def iter_graphemes(data: str, properties: GraphemeBreak | None = None) -> Iterator[str]:
    """
    Iterate through all graphemes in a string.
    """
    if properties is None:
        properties = default_properties()

    str_ch, is_fast_safe = _fast_safe(data, None, properties)
    if is_fast_safe:
        return iter(data)
    re_pat = _build_re()

    return iter(match.string for match in re_pat.finditer(str_ch))


def graphemes(data: str, properties: GraphemeBreak | None = None) -> list[str]:
    """
    Get a list of all graphemes in a string.
    """
    return list(iter_graphemes(data, properties))


def length(data: str, until: int | None = None, properties: GraphemeBreak | None = None) -> int:
    """
    Get the grapheme-aware length of a string.
    """
    if properties is None:
        properties = default_properties()

    str_ch, is_fast_safe = _fast_safe(data, until, properties)
    if is_fast_safe:
        return until or len(data)

    re_pat = _build_re()
    return sum(1 for _ in re_pat.finditer(str_ch))


def _neg_idx_slice(data: str, str_ch: str, start: int | None, stop: int | None) -> str:
    re_pat = _build_re()
    re_matches: list[re.Match[str]] = list(re_pat.finditer(str_ch))

    if len(re_matches) == 0:
        return ""

    d_range = range(len(re_matches))[start: stop]

    start = d_range.start
    stop = d_range.stop
    if start == stop:
        return ""

    start_match = re_matches[start].start()
    if stop == len(re_matches):
        stop_match = None
    else:
        stop_match = re_matches[stop].start()

    return data[start_match: stop_match]


def _slice_to(data: str, str_ch: str, idx: int) -> str:
    expr = _pos_re(idx)
    re_match = expr.match(str_ch)
    if re_match is None:
        return data

    return data[:re_match.start("idx")]


def _slice_from(data: str, str_ch: str, idx: int) -> str:
    expr = _pos_re(idx)
    re_match = expr.match(str_ch)
    if re_match is None:
        return ""

    return data[re_match.start("idx"):]


def _slice_from_to(data: str, str_ch: str, start: int, stop: int) -> str:
    pat = _range_re(start, stop)

    re_match = pat.match(str_ch)

    if re_match is None:
        return ""

    start_sl = re_match.start("start")
    end_sl = re_match.start("stop")
    if end_sl == -1:
        end_sl = None

    return data[start_sl: end_sl]


def strslice(data: str, start: int | None = None, stop: int | None = None, properties: GraphemeBreak | None = None) -> str:
    """
    Perform a grapheme-aware slice of the string.

    Indexing is done by graphemes instead of code
    points. Negative values are supported but
    may be slower than positive values.
    """
    i_start = start is not None and start < 0
    i_stop = stop is not None and stop < 0

    if properties is None:
        properties = default_properties()

    if stop is not None and stop >= 0:
        until = stop
    elif start is not None and start >= 0:
        until = start
    else:
        until = None

    str_ch, is_fast_safe = _fast_safe(data, until, properties)

    if is_fast_safe:
        return data[start: stop]

    if i_start or i_stop:
        return _neg_idx_slice(data, str_ch, start, stop)

    if start is None and stop is None:
        return data[:]

    if start is None:
        stop = cast(int, stop)
        return _slice_to(data, str_ch, stop)

    if stop is None:
        return _slice_from(data, str_ch, start)

    if start >= stop:
        return ""

    return _slice_from_to(data, str_ch, start, stop)


def contains(data: str, substring: str, properties: GraphemeBreak | None = None) -> bool:
    """
    Test whether one string contains a grapheme cluster sequence.

    Grapheme break boundaries must match in both strings.
    """
    if substring not in data:
        return False

    if len(substring) in {0, len(data)}:
        return True

    if properties is None:
        properties = default_properties()

    str_ch, is_fast_safe = _fast_safe(data, None, properties)
    if is_fast_safe:
        return True

    sub_graphemes = graphemes(substring, properties)

    re_pat = _build_re()
    grapheme_it = iter(match.string for match in re_pat.finditer(str_ch))

    if len(sub_graphemes) == 1:
        return sub_graphemes[0] in grapheme_it

    return any(
        view == sub_graphemes
        for view in sliding_window(grapheme_it, len(sub_graphemes))
    )


@cache
def _pos_re(idx: int) -> re.Pattern[str]:
    """
    Get a regex to match the grapheme at the given position.

    The returned pattern contains a group called "idx" that
    matches the chosen grapheme.
    """
    nc_or = _build_raw_re()
    nc_g = nc_or
    named_re_pat = w2.n_cg("idx", nc_g)

    if idx < 0:
        raise NotImplementedError

    idx_pat = w2.seq(w2.str_start, w2.ag(nc_g).count(idx), named_re_pat)

    return idx_pat.c()


@lru_cache
def _range_re(start: int, stop: int) -> re.Pattern[str]:
    """
    Get a regex to match the graphemes at the given start/stop position.

    The returned pattern contains groups called "start" and "stop"
    that match the chosen graphemes.
    """
    nc_or = _build_raw_re()
    re_pat_start = w2.n_cg("start", nc_or)
    re_pat_end = w2.n_cg("stop", nc_or)

    range_pat = w2.seq(w2.str_start, w2.ag(w2.ag(nc_or).count(start)), w2.ag(re_pat_start))

    gap = stop - start - 1

    if gap > 0:
        range_pat += w2.g(w2.ag(nc_or).count(gap) + re_pat_end.optional).optional
    else:
        range_pat += w2.g(re_pat_end).optional

    return range_pat.c()


@cache
def _build_re() -> re.Pattern[str]:
    """
    Build and compile a RegEx to match grapheme clusters.
    """
    return _build_raw_re().c()


@cache
def _build_raw_re() -> w2.or_seq:
    """
    Build a RegEx to match grapheme clusters.

    implements the rules described in tr29:
    https://unicode.org/reports/tr29/#Regex_Definitions
    """
    cr_lf = w2.seq(CR, LF)
    any_ctl = w2.ch_set(CR, LF, Control)
    non_ctl = ~any_ctl

    hangul_inner = w2.seq(
        w2.ch(L).repeat,
        w2.or_g(
            w2.ch(V).req_repeat,
            w2.seq(LV, w2.ch(V).repeat),
            LVT,
        ),
        w2.ch(T).repeat,
    )

    hangul = w2.or_seq(
        hangul_inner,
        w2.ch(L).req_repeat,
        w2.ch(T).req_repeat,
    )

    ri_ri = w2.seq(Regional_Indicator, Regional_Indicator)
    xpicto = w2.seq(
        Extended_Pictographic,
        w2.g(
            w2.ch(Extend).repeat,
            ZWJ,
            Extended_Pictographic,
        ).repeat,
    )

    incb = w2.seq(
        InCB_Consonant,
        w2.g(
            w2.ch_set(
                Extend,
                ZWJ,
            ).repeat,
            InCB_Linker,
            w2.ch_set(
                Extend,
                InCB_Linker,
                ZWJ,
            ).repeat,
            InCB_Consonant,
        ).req_repeat,
    )

    pre_core = w2.ch(Prepend)
    core = w2.or_g(
        hangul,
        ri_ri,
        xpicto,
        incb,
        non_ctl,
    )

    post_core = w2.ch_set(
        Extend,
        ZWJ,
        SpacingMark,
        InCB_Linker,
    )

    op_egc_re = w2.or_seq(
        cr_lf,
        any_ctl,
        w2.seq(
            pre_core.repeat,
            core,
            post_core.repeat,
        ),
    )

    op_egc_re.check_redundance()

    return op_egc_re
