from what2_grapheme.grapheme_property.lookup import GraphemeBreak
from what2_grapheme.util.caching import lru_cache


@lru_cache(maxsize=1)
def default_properties() -> GraphemeBreak:
    return GraphemeBreak.from_files()


def warm_up() -> None:
    default_properties()
