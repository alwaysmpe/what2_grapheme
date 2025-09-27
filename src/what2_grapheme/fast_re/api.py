"""
Grapheme clustering implementation.

Implemented by mapping all characters in input strings
to a character representing their associated break
property then clustering using a regular expression.
"""
from collections.abc import Iterator
from typing import cast as _cast

from what2_grapheme.fast_re.internal import (
    build_re as _build_re,
)
from what2_grapheme.fast_re.internal import (
    fast_safe as _fast_safe,
)
from what2_grapheme.fast_re.internal import (
    fast_safe_re_ascii as _fast_safe_re_ascii,
)
from what2_grapheme.fast_re.internal import (
    neg_idx_slice as _neg_idx_slice,
)
from what2_grapheme.fast_re.internal import (
    ord_encode_map as _ord_encode_map,
)
from what2_grapheme.fast_re.internal import (
    slice_from as _slice_from,
)
from what2_grapheme.fast_re.internal import (
    slice_from_to as _slice_from_to,
)
from what2_grapheme.fast_re.internal import (
    slice_to as _slice_to,
)
from what2_grapheme.grapheme_property.cache import GraphemeBreak
from what2_grapheme.grapheme_property.cache import default_properties as _default_properties
from what2_grapheme.util.iter import sliding_window as _sliding_window


def iter_grapheme_sizes(data: str, properties: GraphemeBreak | None = None) -> Iterator[int]:
    if properties is None:
        properties = _default_properties()

    str_ch, is_fast_safe = _fast_safe(data, None, properties)
    if is_fast_safe:
        yield from (1 for _ in range(len(data)))
        return

    re_pat = _build_re()

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
        properties = _default_properties()

    safe_pat = _fast_safe_re_ascii(properties, skip_crlf=skip_crlf)
    re_match = safe_pat.match(data)

    if (re_match is not None) and (re_match.end() == len(data)):
        return True

    n_j = properties.never_join_chars
    if n_j.issuperset(data):
        return True

    str_ch = data.translate(_ord_encode_map(properties))
    re_pat = _build_re()

    if not skip_crlf:
        return all(
            ((match.end() - match.start()) == 1)
            for match in re_pat.finditer(str_ch)
        )
    return all(
        ((match.end() - match.start()) == 1) or ()
        for match in re_pat.finditer(str_ch)
    )
    return all((len(grapheme) == 1 or grapheme == "\r\n") for grapheme in iter_graphemes(data, properties))


def iter_graphemes(data: str, properties: GraphemeBreak | None = None) -> Iterator[str]:
    """
    Iterate through all graphemes in a string.
    """
    if properties is None:
        properties = _default_properties()

    str_ch, is_fast_safe = _fast_safe(data, None, properties)
    if is_fast_safe:
        yield from iter(data)
        return
    re_pat = _build_re()

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
        properties = _default_properties()

    str_ch, is_fast_safe = _fast_safe(data, until, properties)
    if is_fast_safe:
        return until or len(data)

    re_pat = _build_re()
    return len(re_pat.findall(str_ch))


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
        properties = _default_properties()

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
        stop = _cast("int", stop)
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
        properties = _default_properties()

    str_ch, is_fast_safe = _fast_safe(data, None, properties)
    if is_fast_safe:
        return True

    sub_graphemes = graphemes(substring, properties)

    re_pat = _build_re()
    grapheme_it = iter(data[match.start(): match.end()] for match in re_pat.finditer(str_ch))

    if len(sub_graphemes) == 1:
        return sub_graphemes[0] in grapheme_it

    return any(
        view == sub_graphemes
        for view in _sliding_window(grapheme_it, len(sub_graphemes))
    )
