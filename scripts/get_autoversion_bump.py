"""Simple script that parses the commits since the last tag and, using the emojis in the messages,
returns the type of version bump that should be performed"""

from pathlib import Path
import sys
import re
import subprocess
import logging
from argparse import ArgumentParser
from typing import Tuple

# Commit regex
new_version_emoji = "🔖"
major = r"^[💥]+"
minor = r"^[✨🏗️♻️⚡️👽️]+"
patch = rf"^[🚑️🔒️🐛🥅🔐📌🔧🌐💬📝{new_version_emoji}]+"


logging.basicConfig(
    format="%(asctime)s AUTOVERSION_BUMP %(levelname)-4s: %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%dT%H:%M:%S",
)


Version = Tuple[int, int, int]


def format_version(version: Version) -> str:
    return ".".join([str(el) for el in version])


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
    logging.info(f"Getting autoversion for package @{src.absolute()}")
    current_version = args.version
    if current_version is None:
        current_version = get_current_version_from_package(args.src)
    version_bump = parse_bump_type(args.src)
    logging.info(f"Found version bump = {version_bump}")
    log_msg = f"Bumping from {format_version(current_version)} ➡️ "

    match version_bump:
        case "major":
            current_version[0] += 1
        case "minor":
            current_version[1] += 1
        case "patch":
            current_version[2] += 1

    log_msg += f"{format_version(current_version)}"
    logging.info(log_msg)


def get_current_version_from_package(src: Path) -> Version:
    package_name = src.name
    logging.info(f"Trying to infer version importing {package_name}")
    result = subprocess.run(
        f'cd {src.parent} && python -c "import {package_name};print({package_name}.__version__)"',
        shell=True,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Error getting version: {result.stderr}")

    return [int(el) for el in result.stdout.strip().split(".")]


def parse_bump_type(src: Path, fail_on_parse: bool = True):
    # Fetch the tags for the function
    tag_command = ["git", "tag", "--list", f"{src.name}-*", "--sort=-v:refname"]
    tag_result = subprocess.run(tag_command, capture_output=True, text=True)
    logging.info(tag_result)

    if tag_result.returncode != 0:
        raise ValueError(f"Error fetching tags: {tag_result.stderr}")

    tags = tag_result.stdout.strip().splitlines()

    # Fetch the commits that affect the files in src directory since the last tag
    if len(tags) == 0:
        git_command = ["git", "log", "--oneline", "--", f"{src}/**"]
    else:
        tag = tags[0]
        git_command = [
            "git",
            "log",
            f"{tag}..HEAD",
            "--oneline",
            "--",
            f"{src}/**",
        ]

    logging.info(f"Executing git command: {' '.join(git_command)}")
    result = subprocess.run(git_command, capture_output=True, text=True)
    logging.info(f"Git command output: {result.stdout}")

    if result.returncode != 0:
        raise ValueError(f"Error fetching commits: {result.stderr}")

    commits = result.stdout.splitlines()
    if len(commits) == 0:  # If there are no commits, do not bump
        return ""

    # Parse the commits and check emojis for bump type
    bumpMajor = False
    bumpMinor = False
    bumpPatch = False

    for commit in commits:
        commit_message = commit.split(" ", 1)[1]
        if re.match(major, commit_message):
            bumpMajor = True
        elif re.match(minor, commit_message):
            bumpMinor = True
        elif re.match(patch, commit_message):
            bumpPatch = True

    if bumpMajor is True:
        return "major"
    elif bumpMinor is True:
        return "minor"
    elif bumpPatch is True:
        return "patch"

    elif fail_on_parse is True:
        raise ValueError(
            "There aren't any commit messages with the required emojis to compute the new version number"
        )

    return "patch"


if __name__ == "__main__":
    main()
