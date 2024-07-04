#!/usr/bin/env python3

import logging
import re
import subprocess
from argparse import ArgumentParser
from pathlib import Path
from typing import Tuple


def is_python_package(src: Path) -> bool:
    return (src / "__init__.py").exists()


# Commit regex, based on [gitmoji](https://gitmoji.dev/)
new_version_emoji = "🔖"
major = r"^[💥]+"
minor = r"^[✨🏗️♻️⚡️👽️]+"
patch = rf"^[🚑️🔒️🐛🥅🔐📌🔧🌐💬📝{new_version_emoji}]+"


logging.basicConfig(
    format="%(asctime)s AUTOVERSION_BUMP %(levelname)-4s: %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%dT%H:%M:%S",
)

# Type to represent a verion, [0,0,0]
Version = Tuple[int, int, int]


def format_version(version: Version) -> str:
    return ".".join([str(el) for el in version])


def get_current_version_from_package(src: Path) -> Version:
    package_name = src.name
    logging.info(f"Trying to infer version importing {package_name}")
    with (src / "__init__.py").open("r") as f:
        content = f.read()

    version_match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", content)
    if not version_match:
        raise ValueError(f"__version__ not found in {package_name}")

    version_str = version_match.group(1)
    return [int(el) for el in version_str.split(".")]


def parse_bump_type(src: Path, fail_on_parse: bool = True):
    # Fetch the tags for the function
    tag_command = ["git", "tag", "--list", f"{src}-*", "--sort=-v:refname"]
    tag_result = subprocess.run(tag_command, capture_output=True, text=True)
    logging.info(tag_result)

    if tag_result.returncode != 0:
        raise ValueError(f"Error fetching tags: {tag_result.stderr}")

    tags = tag_result.stdout.strip().splitlines()

    # Fetch the commits that affect the files in src directory since the last tag
    if len(tags) == 0:
        git_command = ["git", "log", "--oneline", "--", str(src / "*")]
    else:
        tag = tags[0]
        git_command = [
            "git",
            "log",
            f"{tag}..HEAD",
            "--oneline",
            "--",
            str(src / "*"),
        ]
    result = subprocess.run(git_command, capture_output=True, text=True)
    logging.info(result)

    if result.returncode != 0:
        raise ValueError(f"Error fetching commits: {result.stderr}")

    commits = result.stdout.splitlines()
    if len(commits) == 0:  # If there are no commits, do not bump
        return ""

    # Parse the commits and check emojis for bump type
    bump_major = False
    bump_minor = False
    bump_patch = False

    for commit in commits:
        commit_message = commit.split(" ", 1)[1]
        if re.match(major, commit_message):
            bump_major = True
        elif re.match(minor, commit_message):
            bump_minor = True
        elif re.match(patch, commit_message):
            bump_patch = True

    if bump_major is True:
        return "major"
    elif bump_minor is True:
        return "minor"
    elif bump_patch is True:
        return "patch"

    elif fail_on_parse is True:
        raise ValueError(
            "There aren't any commit messages with the required emojis to compute the new version number"
        )

    return "patch"


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "src",
        default=Path("src"),
        type=Path,
        help="Path to the package you want autoversion.",
    )
    parser.add_argument(
        "--version",
        default=None,
        type=str,
        help="Current package version, it not provider we will try to infer it.",
    )
    args = parser.parse_args()
    src: Path = args.src
    if not src.is_dir():
        raise ValueError(f"{src} is not a valid directory.")
    if not is_python_package(src):
        raise ValueError(f"{src} is not a python package, missing `__init__.py`.")

    logging.info(f"Getting autoversion for package @{src.absolute()}")
    current_version = args.version
    if current_version is None:
        current_version = get_current_version_from_package(args.src)
    version_bump = parse_bump_type(args.src)
    logging.info(f"Found version bump = {version_bump}")
    log_msg = f"Bumping from {format_version(current_version)} ➡️ "
    # doing the bumping
    match version_bump:
        case "major":
            current_version[0] += 1
        case "minor":
            current_version[1] += 1
        case "patch":
            current_version[2] += 1

    log_msg += f"{format_version(current_version)}"
    logging.info(log_msg)
    print(format_version(current_version))


if __name__ == "__main__":
    main()
