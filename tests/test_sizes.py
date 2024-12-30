import string

import what2_grapheme.fast_sm.api as fast_api
import what2_grapheme.simple_sm.api as simple_api


def test_simple():
    sizes = list(fast_api.grapheme_sizes(""))
    assert sizes == []
    sizes = list(fast_api.grapheme_sizes("a"))
    assert sizes == [1]
    sizes = list(fast_api.grapheme_sizes("abc"))
    assert sizes == [1, 1, 1]
    sizes = list(simple_api.grapheme_sizes(""))
    assert sizes == []
    sizes = list(simple_api.grapheme_sizes("a"))
    assert sizes == [1]
    sizes = list(simple_api.grapheme_sizes("abc"))
    assert sizes == [1, 1, 1]


def test_crlf():
    sizes = list(fast_api.grapheme_sizes("\r\n"))
    assert sizes == [2]
    sizes = list(simple_api.grapheme_sizes("\r\n"))
    assert sizes == [2]


def test_ascii_sizes():
    sizes = list(fast_api.grapheme_sizes(string.ascii_letters))
    assert len(sizes) == len(string.ascii_letters)
    assert set(sizes) == {1}
    sizes = list(simple_api.grapheme_sizes(string.ascii_letters))
    assert len(sizes) == len(string.ascii_letters)
    assert set(sizes) == {1}


def test_emoji_zwj():
    woman = "\U0001F469"
    zwj = "\u200D"
    rocket = "\U0001F680"
    woman_astronaut = woman + zwj + rocket

    sizes = list(fast_api.grapheme_sizes(woman_astronaut))
    assert sizes == [3]
    sizes = list(simple_api.grapheme_sizes(woman_astronaut))
    assert sizes == [3]


def test_emoji_zwj_compound():
    woman = "\U0001F469"
    zwj = "\u200D"
    rocket = "\U0001F680"
    woman_astronaut = woman + zwj + rocket

    compound_strs = [
        (f"abc{woman_astronaut}abc", [1, 1, 1, 3, 1, 1, 1]),
        (f"{woman_astronaut}abc", [3, 1, 1, 1]),
        (f"abc{woman_astronaut}", [1, 1, 1, 3]),
    ]
    for data, data_sizes in compound_strs:

        sizes = list(fast_api.grapheme_sizes(data))
        assert sizes == data_sizes
        sizes = list(simple_api.grapheme_sizes(data))
        assert sizes == data_sizes
