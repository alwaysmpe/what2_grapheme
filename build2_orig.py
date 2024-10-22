from pathlib import Path
# from distutils.extension import Extension
# from distutils.dist import Distribution
from setuptools import Extension, Distribution
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
from setuptools._distutils.file_util import copy_file
try:
    from what2 import dbg
except:
    dbg = print
from collections.abc import Iterator
import shutil
from typing import cast
# from Cython.Distutils.build_ext import build_ext
compile_args = [
    "-march=native",
    "-O3",
    "-msse",
    "-msse2",
    "-mfma",
    "-mfpmath=sse"
]



def pk_name():
    return "what2_grapheme"


def sources() -> list[str]:
    root = Path(__file__).absolute().parent
    cy_dir = root / "src" / pk_name() / "cy"
    
    return [
        str(path.relative_to(root))
        for path in cy_dir.glob("*.py")
    ]


def to_pkg_dir(path: Path) -> Path:
    assert not path.is_absolute()
    return path.relative_to("src")


def to_ns_pair(root: Path, path: Path) -> tuple[str, str]:
    rel = path.relative_to(root)
    source = str(rel)
    name = ".".join(to_pkg_dir(rel).parts)[:-3]
    return name, source


def get_cy_dir() -> tuple[Path, Path]:
    root_dir = Path(__file__).absolute().parent
    cy_dir = root_dir / "src" / "what2_grapheme" / "cy"
    return root_dir, cy_dir


def iter_cy_files() -> Iterator[tuple[Path, Path]]:
    root_dir, cy_dir = get_cy_dir()
    for path in iter_py(cy_dir):
        yield root_dir, path


def iter_ext_src() -> Iterator[tuple[str, str]]:
    for root_dir, path in iter_cy_files():
        print(to_ns_pair(root_dir, path))
        yield to_ns_pair(root_dir, path)

def iter_py(path: Path):
    for file in path.iterdir():
        if file.name == "__init__.py":
            continue
        if file.name.startswith("_"):
            continue
        if file.suffix == ".py":
            yield file


def copy_extensions_to_source(build_root: Path) -> Iterator[tuple[Path, Path]]:
    root_dir, cy_dir = get_cy_dir()
    build_path = build_root / to_pkg_dir(cy_dir.relative_to(root_dir))
    for path in iter_py(cy_dir):
        print(path)
        dbg(build_path)
        built_files = build_path.glob(f"{path.stem}.*")
        print(list(built_files))
        built_files = build_path.glob(f"{path.stem}.*")
        for file in built_files:
            shutil.copy(file, cy_dir)


def build():
    extensions = [
        Extension(
            name=name,
            sources=[source],
        )
        for name, source in iter_ext_src()
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
    # ext_n = "what2_grapheme.cy.to_ord"
    cmd.run()
    # dbg(cmd)

    # dbg(cmd.get_outputs())
    # dbg(cmd.get_output_mapping())
    # dbg(cmd.get_ext_fullname(ext_n))
    # dbg(cmd.get_ext_fullpath("what2_grapheme.cy.to_ord"))

    # build_py = cmd.get_finalized_command("build_py")
    build_lib = Path(cmd.build_lib).absolute()

    copy_extensions_to_source(build_lib)

    # for ext in cmd.extensions:
    #     cmd.get
    #     ip_file, reg_file = cmd._get_inplace_equivalent(build_py, ext)
    #     ip_path = Path("src").absolute() / Path(ip_file)
    #     reg_path = Path(reg_file).absolute()
    #     dbg(ip_path)
    #     dbg(reg_path)
    #     # assert 0
    #     print("----------------------------" * 10)
    #     # copy_file(ip_file, reg_file)
    #     # shutil.copy(ip_path, reg_path)
    #     shutil.copy(reg_path, ip_path)
        # copy_file(reg_file, ip_file)
    # cmd.copy_extensions_to_source()




if __name__ == "__main__":
    build()
