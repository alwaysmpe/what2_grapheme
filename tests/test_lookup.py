from typing import cast

from grapheme.grapheme_property_group import GraphemePropertyGroup, get_group_ord
from what2 import dbg

from what2_grapheme.grapheme_property.cache import default_properties
from what2_grapheme.grapheme_property.type import Break


def test_match_grapheme():
    for val in Break:
        assert val == val.value

    props = default_properties()
    failed = False
    for i in range(1114111):
        g_gr: GraphemePropertyGroup = cast(GraphemePropertyGroup, get_group_ord(i))

        break_code = props.code_to_cat(i)
        break_enum = Break(break_code)
        ref_name = g_gr.name.lower().replace("_", "")
        val_name = break_enum.name.lower().replace("_", "")
        if val_name.startswith("incb"):
            if val_name.endswith("consonant"):
                assert ref_name == "other"
                continue
            if val_name.endswith("linker"):
                assert ref_name == "extend"
                continue

        if ref_name != val_name:
            dbg(ref_name)
            dbg(val_name)
            dbg(i)
            dbg(hex(i))

            failed = True
        assert ref_name == val_name
    assert not failed
