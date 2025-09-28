from string import ascii_lowercase as ascii_lowercase_str
from bm.rng import mk_rng, Generator
ascii_lowercase = list(ascii_lowercase_str)
from what2_grapheme.py_property.cache import default_properties

def random_utf_string(length: int, rng: Generator | None = None) -> str:
    if rng is None:
        rng = mk_rng()
    codes: tuple[str, ...] = default_properties().all_other_list

    codes_used = max(1, int(length ** 0.5))

    selected_codes = rng.choice(codes, size=codes_used)

    return "".join(
        rng.choice(selected_codes, size=length)
    )


def random_ascii_string(length: int, rng: Generator | None = None) -> str:
    if rng is None:
        rng = mk_rng()

    return "".join(rng.choice(ascii_lowercase) for _ in range(length))
