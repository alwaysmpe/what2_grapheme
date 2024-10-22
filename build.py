from pathlib import Path
from setuptools import Extension, Distribution
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
from typing import cast, Any
import shutil
from what2 import dbg

def pkg_name() -> str:
    return "what2_grapheme"

def get_root() -> Path:
    return Path(__file__).absolute().parent

def get_src() -> Path:
    return get_root() / "src"

def pkg_path() -> Path:
    return get_src() / pkg_name()

def to_py(path: Path) -> str:
    pkg = path.relative_to(get_src())
    parts = list(pkg.parent.parts)
    parts.append(path.stem)
    return ".".join(parts)

def cpp_exts() -> list[Extension]:
    root = get_root()
    name = f"{pkg_name()}.cpp"
    path = pkg_path() / "cpp"

    exts: list[Extension] = []

    for file in path.iterdir():
        if file.suffix != ".pyx":
            continue

        dbg(to_py(file))
        dbg(str(file.relative_to(root)))

        exts.append(Extension(
            name=to_py(file),
            sources=[str(file.relative_to(root))],
        ))

    return exts


def cython_extensions() -> list[Extension]:

    extensions = cpp_exts()
    ext_modules: list[Extension] = cast(list[Extension], cythonize(
        extensions,
        compiler_directives={"language_level": 3},
    ))
    return ext_modules


def build_inplace():

    dist = Distribution({
        "name": "extended",
        "ext_modules": cython_extensions(),
    })

    print("running build")

    cmd = build_ext(dist)
    cmd.ensure_finalized()
    cmd.run()

    build_lib = Path(cmd.build_lib).absolute()

    for out in cmd.get_outputs():
        out_str: str = cast(str, out)
        out_path = Path(out_str).absolute()
        rel_path = out_path.relative_to(build_lib)
        inplace_path = get_src() / rel_path
        dbg(inplace_path)
        dbg(out_path)
        shutil.copy(out_path, inplace_path)





    pass

def build(setup_kwargs: dict[str, Any]):
    setup_kwargs.update({
        "ext_modules": cython_extensions()
    })


if __name__ == "__main__":
    build_inplace()
