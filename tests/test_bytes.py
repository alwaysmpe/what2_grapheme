from what2 import dbg
from collections.abc import Buffer
import random

# import what2_grapheme.cy.to_ord as to_ord
from what2_grapheme.chunk import grapheme_sizes

from what2_time import Timer
# from cy_test import hello
from what2_grapheme.cy import to_ord as cy
from what2_utf_parse.grapheme_cluster.describe import FlatGroupProperties

import cython

def utf8_to_ord(data: bytes | bytearray | memoryview) -> tuple[int, int]:
    if data[0] < 128:
        # single bit utf8/ascii character
        return data[0], 1

    if data[0] < 224:
        # 2 bit utf8
        leading_bits = (data[0] - 192) << 6
        ord = leading_bits + (data[1] - 128)
        return ord, 2

    if data[0] < 240:
        # 3 bit utf8
        leading_bits = (data[0] - 224) << 12
        mid_bits = (data[1] - 128) << 6
        trail_bits = data[2] - 128
        return leading_bits + mid_bits + trail_bits, 3

    # 4 bit utf8
    leading_bits = (data[0] - 240) << 18
    upper_mid_bits = (data[1] - 128) << 12
    lower_mid_bits = (data[2] - 128) << 6
    trail_bits = data[3] - 128
    return (
        leading_bits
        + upper_mid_bits
        + lower_mid_bits
        + trail_bits
    ), 4

from collections.abc import Iterator

def iter_bchars(data: bytes) -> Iterator[int]:
    view = memoryview(data)
    start_idx = 0
    while start_idx < len(data):
        ch_ord, ch_len = utf8_to_ord(view[start_idx:])
        yield ch_ord
        start_idx += ch_len

def printable_ords() -> list[str]:
    return [
        chr(i)
        for i in range(128)
        if chr(i).isprintable()
    ]

def ch_to_ords(data: str) -> list[int]:
    return [
        ord(ch)
        for ch in data
    ]

def b_to_ords(data: bytes) -> list[int]:
    return list(iter_bchars(data))

def gen_printable_sequence(count: int):
    printables = printable_ords()
    selection: list[str] = random.choices(printables, k=count)
    return "".join(
        selection
    )


def test_sb_perf():
    rand_str = gen_printable_sequence(100000)

    with Timer("ch to ord"):
        ords = ch_to_ords(rand_str)

    gprop = FlatGroupProperties.from_files()
    prop_lookup = gprop.data

    print("mk gstr")
    assert cy.is_cythed()
    gstr = cy.GStr(prop_lookup)
    assert gstr.is_cythed()
    print("made")

    with Timer("new cy ch len"):
        gstr.length(rand_str)
    

    grapheme_sizes(rand_str)
    with Timer("mine ch len"):
        grapheme_sizes(rand_str)




    # with Timer("cy ch to ord"):
    #     ords = to_ord.ch_to_ords(rand_str)
    # assert to_ord.is_cython()

    rand_str_bytes = rand_str.encode()

    with Timer("b to ord"):
        b_ords = b_to_ords(rand_str_bytes)

    assert ords == b_ords

    assert 0


def test_single_bit_utf8():
    for i in range(1114111):
        ch = chr(i)
        if not ch.isprintable():
            continue

        ch_bytes = ch.encode()

        byte_ord, byte_len = utf8_to_ord(ch_bytes)

        try:
            assert byte_ord == ord(ch)
            assert byte_len == len(ch_bytes)
        except:
            dbg(i)
            dbg(ch_bytes)
            raise
