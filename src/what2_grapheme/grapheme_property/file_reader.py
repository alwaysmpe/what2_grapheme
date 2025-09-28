from collections.abc import Generator, Iterable
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import final, override

from what2_grapheme.grapheme_property.type import Break


@dataclass
class CodeBreak:
    code_start: int
    code_end: int
    break_class: Break


@final
@dataclass
class UTFFilter(Iterable[str]):
    data: Iterable[str]

    @override
    def __iter__(self) -> Generator[str]:
        for raw_line in self.data:
            line = raw_line.strip().replace(" ", "")
            if len(line) == 0 or line.startswith("#"):
                continue
            if "#" in line:
                line, _comment = line.split("#", maxsplit=1)
            yield line.strip()


def parse_file(path: Path) -> Generator[CodeBreak]:
    with path.open() as data:
        reader = csv.reader(UTFFilter(data), delimiter=";")
        for char_code, *break_classes in reader:
            break_class = "_".join(break_classes)
            if break_class not in Break._member_names_:
                continue
            if ".." in char_code:
                code_start, code_end = char_code.split("..")
            else:
                code_start = code_end = char_code
            code_start = int(code_start, base=16)
            code_end = int(code_end, base=16)
            yield CodeBreak(
                code_start,
                code_end,
                Break[break_class],
            )
