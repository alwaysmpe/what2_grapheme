from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import get_type_hints

import pandas as pd

from what2_grapheme.grapheme_property.type import Break


@dataclass
class CodeBreak:
    code_start: int
    code_end: int
    break_class: pd.CategoricalDtype


def parse_utf_delimited(path: Path, names: Sequence[str]) -> pd.DataFrame:
    return pd.read_table( # type: ignore reportUnknownMemberTypes
        path,
        comment="#",
        delimiter=";",
        skip_blank_lines=True,
        names=list(names),
    )


def parse_data_file(path: Path, names: list[str]) -> pd.DataFrame:
    assert names[0] == "char_codes"

    utf_df = parse_utf_delimited(path, names)

    for col in utf_df:
        utf_df[col] = utf_df[col].str.strip() # type: ignore reportUnknownMemberType

    utf_df["is_range"] = utf_df["char_codes"].str.contains(r"\.\.") # type: ignore reportUnknownMemberType

    range_groups = utf_df.groupby("is_range") # type: ignore reportUnknownMemberType

    single = pd.DataFrame(range_groups.get_group(name=False)) # type: ignore reportUnknownMemberType
    single["code_start"] = single["char_codes"].apply(int, base=16) # type: ignore reportUnknownMemberType
    single["code_end"] = single["code_start"]

    ranges = pd.DataFrame(range_groups.get_group(name=True)) # type: ignore reportUnknownMemberType
    endings = ranges["char_codes"].str.split(r"\.\.", expand=True) # type: ignore reportUnknownMemberType
    ranges["code_start"] = endings[0].apply(int, base=16) # type: ignore reportUnknownMemberType
    ranges["code_end"] = endings[1].apply(int, base=16) # type: ignore reportUnknownMemberType

    return pd.concat([single, ranges])


def mk_break_cat() -> pd.CategoricalDtype:
    return pd.CategoricalDtype(
        categories=[*Break._member_names_],
        ordered=False,
    )


def _parse_property_class(path: Path) -> pd.DataFrame: # CodeBreak format
    names = [
        "char_codes",
        "break_class",
    ]

    break_df = parse_data_file(path, names)

    break_df["break_class"] = break_df["break_class"].astype(mk_break_cat())

    ret_cols = list(get_type_hints(CodeBreak).keys())

    return break_df[ret_cols]


def parse_break_properties(path: Path) -> pd.DataFrame: # CodeBreak format

    break_df = _parse_property_class(path)

    if break_df["break_class"].hasnans:
        message = "Unrecognised break category in input data"
        raise ValueError(message)

    return break_df


def parse_emoji_data(path: Path) -> pd.DataFrame: # CodeBreak format
    break_df = _parse_property_class(path)

    return break_df.dropna() # type: ignore reportUnknownMemberType


def parse_incb_properties(path: Path) -> pd.DataFrame: # CodeBreak format
    names = [
        "char_codes",
        "property_kind",
        "property_value",
    ]
    prop_df = parse_data_file(path, names)

    prop_df = prop_df.dropna() # type: ignore reportUnknownMemberType
    prop_df = prop_df[[
        "code_start",
        "code_end",
        "property_kind",
        "property_value",
    ]]

    prop_df = prop_df.groupby("property_kind").get_group("InCB") # type: ignore reportUnknownMemberType

    prop_df["break_class"] = (prop_df["property_kind"] + "_" + prop_df["property_value"]).astype(mk_break_cat())

    result_vals = [
        "code_start",
        "code_end",
        "break_class",
    ]

    return prop_df[result_vals]
