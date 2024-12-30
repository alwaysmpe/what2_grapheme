from what2_grapheme.grapheme_data.load import break_test
from what2_grapheme.grapheme_property.parse import parse_utf_delimited
import pandas as pd
import re
from bm.rng import mk_rng, Generator

from what2_grapheme.util.caching import cache

parse_utf_delimited = cache(parse_utf_delimited)

__break_test_data: list[str] | None = None
def load_break_test_data() -> list[str]:
    global __break_test_data
    if __break_test_data is not None:
        return list(__break_test_data)

    with break_test() as path:
        data_df = parse_utf_delimited(path, ("break_eg",))
    
    data: pd.Series[str] = data_df["break_eg"].str.strip() # type: ignore
    data = data.str.strip("÷ ") # type: ignore
    return list(data)

def case_count() -> int:
    return len(load_break_test_data())

def break_str_case(break_idx: int) -> str:
    return load_break_test_data()[break_idx]

@cache
def case_str_size(break_idx: int) -> int:

    chunks = break_str_case(break_idx).split(" ÷ ")

    return len(chunks)


break_pat: re.Pattern[str] = re.compile(f" [×÷] ")


@cache
def case_str(break_idx: int) -> str:
    return "".join(
        chr(int(chunk, base=16))
        for chunk in break_pat.split(break_str_case(break_idx))
    )


@cache
def all_case_strs() -> list[str]:
    return [
        case_str(i)
        for i in range(case_count())
    ]

def random_utf_string(chunk_count: int, rng: Generator | None = None) -> str:
    if rng is None:
        rng = mk_rng()

    all_chs = all_case_strs()
    
    return "".join(rng.choice(all_chs, size=chunk_count))
