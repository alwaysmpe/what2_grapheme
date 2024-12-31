"""
Grapheme clustering implementation.

Implemented by mapping all characters in input strings
to a character representing their associated break
property then clustering using a regular expression.
"""
from collections.abc import Iterator
from typing import cast

from what2_grapheme.fast_re.internal import (
    build_re,
    fast_safe,
    fast_safe_re_ascii,
    neg_idx_slice,
    slice_from,
    slice_from_to,
    slice_to,
)
from what2_grapheme.grapheme_property.cache import GraphemeBreak, default_properties
from what2_grapheme.util.iter import sliding_window


def iter_grapheme_sizes(data: str, properties: GraphemeBreak | None = None) -> Iterator[int]:
    if properties is None:
        properties = default_properties()

    str_ch, is_fast_safe = fast_safe(data, None, properties)
    if is_fast_safe:
        yield from (1 for _ in range(len(data)))
        return

    re_pat = build_re()

    for match in re_pat.finditer(str_ch):
        yield match.end() - match.start()


def grapheme_sizes(data: str, properties: GraphemeBreak | None = None) -> list[int]:
    return list(iter_grapheme_sizes(data, properties))


def is_safe(data: str, properties: GraphemeBreak | None = None, *, skip_crlf: bool = False) -> bool:
    """
    Test whether a string contains grapheme clusters.

    If a string is safe no special string handling
    is necessary.
    """
    if properties is None:
        properties = default_properties()

    safe_pat = fast_safe_re_ascii(properties, skip_crlf=skip_crlf)
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

    str_ch, is_fast_safe = fast_safe(data, None, properties)
    if is_fast_safe:
        yield from iter(data)
        return
    re_pat = build_re()

    for match in re_pat.finditer(str_ch):
        yield data[match.start(): match.end()]


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

    str_ch, is_fast_safe = fast_safe(data, until, properties)
    if is_fast_safe:
        return until or len(data)

    re_pat = build_re()
    return sum(1 for _ in re_pat.finditer(str_ch))


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

    str_ch, is_fast_safe = fast_safe(data, until, properties)

    if is_fast_safe:
        return data[start: stop]

    if i_start or i_stop:
        return neg_idx_slice(data, str_ch, start, stop)

    if start is None and stop is None:
        return data[:]

    if start is None:
        stop = cast("int", stop)
        return slice_to(data, str_ch, stop)

    if stop is None:
        return slice_from(data, str_ch, start)

    if start >= stop:
        return ""

    return slice_from_to(data, str_ch, start, stop)


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

    str_ch, is_fast_safe = fast_safe(data, None, properties)
    if is_fast_safe:
        return True

    sub_graphemes = graphemes(substring, properties)

    re_pat = build_re()
    grapheme_it = iter(match.string for match in re_pat.finditer(str_ch))

    if len(sub_graphemes) == 1:
        return sub_graphemes[0] in grapheme_it

    return any(
        view == sub_graphemes
        for view in sliding_window(grapheme_it, len(sub_graphemes))
    )
