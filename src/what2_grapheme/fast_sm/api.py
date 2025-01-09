from collections.abc import Iterator
from itertools import accumulate, chain

from what2_grapheme.fast_sm.break_gen import StrBreakGen
from what2_grapheme.grapheme_property.cache import GraphemeBreak, default_properties
from what2_grapheme.util.iter import sliding_window


def iter_grapheme_sizes(data: str, properties: GraphemeBreak | None = None) -> Iterator[int]:
    if len(data) == 0:
        return

    if properties is None:
        properties = default_properties()

    state = StrBreakGen(properties)
    current_size = 0

    for char in data:
        should_break = state.send(char)

        if should_break:
            yield current_size
            current_size = 1
        else:
            current_size += 1
    yield current_size


def is_safe(data: str, properties: GraphemeBreak | None = None, *, skip_crlf: bool = False) -> bool:
    if properties is None:
        properties = default_properties()

    ch_set = set(data)

    if skip_crlf:
        ch_set.discard("\r")

    if ch_set.issubset(properties.never_join_chars):
        return True

    if not skip_crlf:
        return all(size == 1 for size in iter_grapheme_sizes(data, properties))
    return all((len(grapheme) == 1 or grapheme == "\r\n") for grapheme in iter_graphemes(data, properties))


def grapheme_sizes(data: str, properties: GraphemeBreak | None = None) -> list[int]:
    return list(iter_grapheme_sizes(data, properties))


def iter_grapheme_starts(data: str, properties: GraphemeBreak | None = None) -> Iterator[int]:
    if len(data) == 0:
        return

    if properties is None:
        properties = default_properties()

    state = StrBreakGen(properties)
    current_size = 0

    yield current_size

    for char in data:
        should_break = state.send(char)

        if should_break:
            yield current_size

        current_size += 1


def grapheme_starts(data: str, properties: GraphemeBreak | None = None) -> list[int]:
    return list(iter_grapheme_starts(data, properties))


def length(data: str, until: int | None = None, properties: GraphemeBreak | None = None) -> int:
    if len(data) == 0:
        return 0

    if properties is None:
        properties = default_properties()

    # TODO: if is_safe(data, skip_crlf=False, properties=properties): return len(data)

    if until is None:
        return sum(1 for _ in iter_grapheme_sizes(data, properties))

    running_len = 0
    for running_len in accumulate(1 for _ in iter_grapheme_sizes(data, properties)):
        if running_len >= until:
            return running_len
    return running_len


def iter_graphemes(data: str, properties: GraphemeBreak | None = None) -> Iterator[str]:
    if len(data) == 0:
        return

    if properties is None:
        properties = default_properties()

    state = StrBreakGen(properties)
    current_sequence = ""

    for char in data:
        should_break = state.send(char)
        if should_break:
            yield current_sequence
            current_sequence = char
        else:
            current_sequence += char

    yield current_sequence


def graphemes(data: str, properties: GraphemeBreak | None = None) -> list[str]:
    return list(iter_graphemes(data, properties))


def _islice(data: str, start: int | None = None, stop: int | None = None, properties: GraphemeBreak | None = None) -> str:
    idx_lk = grapheme_starts(data, properties)
    d_range = range(len(idx_lk))[start: stop]

    start = d_range.start
    stop = d_range.stop
    if start == stop:
        return ""

    start = idx_lk[start]
    if stop == len(idx_lk):
        stop = None
    else:
        stop = idx_lk[stop]

    return data[start: stop]


def strslice(data: str, start: int | None = None, stop: int | None = None, properties: GraphemeBreak | None = None) -> str:
    i_start = start is not None and start < 0
    i_stop = stop is not None and stop < 0

    if i_start or i_stop:
        return _islice(data, start, stop, properties)

    if (start is not None) and (stop is not None) and (start >= stop):
        return ""

    it = enumerate(accumulate(chain((0, ), iter_grapheme_sizes(data, properties))))
    abs_start: int | None = None
    abs_stop: int | None = None

    idx = None
    csum = None
    if start is not None:
        for idx, csum in it:
            if idx == start:
                abs_start = csum
                break
        else:
            return ""

    if stop is not None:
        for idx, csum in it:
            if idx == stop:
                abs_stop = csum
                break
        else:
            return data[abs_start:]
    return data[abs_start: abs_stop]


def contains(data: str, substring: str, properties: GraphemeBreak | None = None) -> bool:
    if substring not in data:
        return False

    if len(substring) == 0:
        return True

    sub_graphemes = graphemes(substring, properties)

    if len(sub_graphemes) == 1:
        return sub_graphemes[0] in iter_graphemes(data, properties)

    it = iter_graphemes(data, properties)

    return any(
        view == sub_graphemes
        for view in sliding_window(it, len(sub_graphemes))
    )
