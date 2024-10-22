from pathlib import Path
from setuptools import Extension, Distribution
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
from collections.abc import Iterator
import shutil
from typing import cast

def pkg_name() -> str:
    return "what2_grapheme"

def ext_name() -> str:
    return f"{pkg_name()}.cy"

def cy_rel_pkg_dir() -> Path:
    return Path(pkg_name()) / "cy"

def root() -> Path:
    return Path(__file__).absolute().parent

def cy_sources() -> Iterator[str]:
    root_dir = root()
    cy_dir = root_dir / "src" / cy_rel_pkg_dir()

    for path in cy_dir.iterdir():
        if path.suffix != ".py":
            continue

        if path.name == "__init__.py":
            continue

        yield str(path.relative_to(root_dir))


def build():
    extensions = [
        Extension(
            name=ext_name(),
            sources=list(cy_sources()),
        )
    ]
    ext_modules: list[Extension] = cast(list[Extension], cythonize(
        extensions,
        compiler_directives={"language_level": 3},
    ))

    dist = Distribution({
        "name": "extended",
        "ext_modules": ext_modules,
    })

    print("running build")

    cmd = build_ext(dist)

    cmd.ensure_finalized()

    cmd.run()

    build_lib = Path(cmd.build_lib).absolute()
    print(build_lib)


if __name__ == "__main__":
    build()
