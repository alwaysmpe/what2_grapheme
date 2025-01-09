import re

from what2_regex import w2

from what2_grapheme.grapheme_property.cache import GraphemeBreak
from what2_grapheme.grapheme_property.lookup import MAX_ORD
from what2_grapheme.util.caching import cache, lru_cache

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


def neg_idx_slice(data: str, str_ch: str, start: int | None, stop: int | None) -> str:
    re_pat = build_re()
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


def slice_to(data: str, str_ch: str, idx: int) -> str:
    expr = pos_re(idx)
    re_match = expr.match(str_ch)
    if re_match is None:
        return data

    return data[:re_match.start("idx")]


def slice_from(data: str, str_ch: str, idx: int) -> str:
    expr = pos_re(idx)
    re_match = expr.match(str_ch)
    if re_match is None:
        return ""

    return data[re_match.start("idx"):]


def slice_from_to(data: str, str_ch: str, start: int, stop: int) -> str:
    pat = range_re(start, stop)

    re_match = pat.match(str_ch)

    if re_match is None:
        return ""

    start_sl = re_match.start("start")
    end_sl = re_match.start("stop")
    if end_sl == -1:
        end_sl = None

    return data[start_sl: end_sl]


def fast_safe(data: str, until: int | None, properties: GraphemeBreak) -> tuple[str, bool]: # noqa: ARG001
    """
    Fast but not comprehensive test to see if a string contains graphemes.
    """
    safe_pat = fast_safe_re_ascii(properties, skip_crlf=False)
    re_match = safe_pat.match(data)

    if (re_match is not None) and (re_match.end() == len(data)):
        return "", True

    str_ch = data.translate(ord_encode_map(properties))

    safe_pat = fast_safe_re(properties)
    re_match = safe_pat.match(str_ch)

    if re_match is None:
        return str_ch, False

    return str_ch, re_match.end() == len(data)


@cache
def fast_safe_re(properties: GraphemeBreak) -> re.Pattern[str]:
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
def fast_safe_re_ascii(properties: GraphemeBreak, *, skip_crlf: bool) -> re.Pattern[str]:
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


@cache
def definite_break_re() -> re.Pattern[str]:
    """
    Get a regex to match a pair of grapheme properties that definitely form a grapheme break.
    """

    return w2.seq(
        w2.ng(
            w2.or_seq(
                w2.seq(Prepend, w2.ch_xset(CR, LF, Control)),
                w2.seq(w2.ch_xset(CR, LF, Control), w2.ch_set(Extend, SpacingMark, ZWJ, InCB_Linker)),
                w2.seq(L, w2.ch_set(L, V, LV, LVT)),
                w2.seq(w2.ch_set(V, LV), w2.ch_set(V, T)),
                w2.seq(w2.ch_set(T, LVT), T),
                w2.seq(Regional_Indicator, Regional_Indicator),
                w2.seq(InCB_Consonant, w2.ch_set(Extend, ZWJ, InCB_Linker)),
                w2.seq(w2.ch_set(Extend, ZWJ, InCB_Linker), InCB_Consonant),
                w2.seq(w2.ch_set(Extend, ZWJ), Extended_Pictographic),
                w2.seq(CR, LF),
                w2.seq(".", w2.line_end),
            ),
        ),
        ".",
    ).c()


@cache
def pos_re(idx: int) -> re.Pattern[str]:
    """
    Get a regex to match the grapheme at the given position.

    The returned pattern contains a group called "idx" that
    matches the chosen grapheme.
    """
    nc_or = build_raw_re()
    nc_g = nc_or
    named_re_pat = w2.n_cg("idx", nc_g)

    if idx < 0:
        raise NotImplementedError

    idx_pat = w2.seq(w2.str_start, w2.ag(nc_g).count(idx), named_re_pat)

    return idx_pat.c()


@lru_cache
def range_re(start: int, stop: int) -> re.Pattern[str]:
    """
    Get a regex to match the graphemes at the given start/stop position.

    The returned pattern contains groups called "start" and "stop"
    that match the chosen graphemes.
    """
    nc_or = build_raw_re()
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
def build_re() -> re.Pattern[str]:
    """
    Build and compile a RegEx to match grapheme clusters.
    """
    return build_raw_re().c()


@cache
def build_raw_re() -> w2.or_seq:
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
