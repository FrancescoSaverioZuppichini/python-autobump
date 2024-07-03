#!/usr/bin/env python3

import argparse
import re
import sys
from pathlib import Path


def is_python_package(src: Path) -> bool:
    return (src / "__init__.py").exists()


def update_version_in_file(file_path: Path, new_version: str) -> bool:
    """
    Update the __version__ variable in the specified file.

    Args:
    file_path (Path): Path to the file to update.
    new_version (str): New version string to set.

    Returns:
    bool: True if the version was updated, False otherwise.
    """
    with file_path.open("r") as file:
        content = file.read()

    pattern = r'__version__\s*=\s*["\']([^"\']+)["\']'

    if re.search(pattern, content):
        updated_content = re.sub(pattern, f'__version__ = "{new_version}"', content)

        with file_path.open("w") as file:
            file.write(updated_content)

        return True
    else:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Update the __version__ in a Python package."
    )
    parser.add_argument("src", type=Path, help="Path to the package directory")
    parser.add_argument("version", type=str, help="New version string")
    args = parser.parse_args()

    src = args.src
    new_version = args.version

    if not src.is_dir():
        raise ValueError(f"{src} is not a valid directory.")
    if not is_python_package(src):
        raise ValueError(f"{src} is not a python package, missing `__init__.py`.")

    init_file = src / "__init__.py"
    if update_version_in_file(init_file, new_version):
        print(f"Successfully updated version to {new_version} in {init_file}")
    else:
        raise ValueError(f"Could not find __version__ in {init_file}")


if __name__ == "__main__":
    main()
