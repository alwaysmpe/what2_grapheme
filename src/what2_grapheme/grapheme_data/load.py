from contextlib import AbstractContextManager
import importlib.resources as impr
from pathlib import Path


def utf_version() -> str:
    return "16.0.0"


def derived_properties() -> AbstractContextManager[Path, bool | None]:
    files = impr.files()
    data = files / "data" / "DerivedCoreProperties.txt"
    return impr.as_file(data)


def break_properties() -> AbstractContextManager[Path, bool | None]:
    files = impr.files()
    data = files / "data" / "GraphemeBreakProperty.txt"
    return impr.as_file(data)


def emoji_data() -> AbstractContextManager[Path, bool | None]:
    files = impr.files()
    data = files / "data" / "emoji-data.txt"
    return impr.as_file(data)


def utf_license() -> AbstractContextManager[Path, bool | None]:
    files = impr.files()
    data = files / "data" / "license.txt"
    return impr.as_file(data)
