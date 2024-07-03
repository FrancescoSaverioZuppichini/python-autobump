"""Simple script that parses the commits since the last tag and, using the emojis in the messages,
returns the type of version bump that should be performed"""

from pathlib import Path
import sys
import re
import subprocess
import logging
from argparse import ArgumentParser

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


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "src",
        default=Path("src"),
        type=Path,
        help="Path to the package you want autoversion.",
    )
    args = parser.parse_args()
    src: Path = args.src
    logging.info(f"Getting autoversion for package @{src.absolute()}")
    version_bump = parseBumpType(args.src)
    print(version_bump)


def parseBumpType(src: Path, fail_on_parse: bool = True):
    # Fetch the tags for the function
    tag_command = ["git", "tag", "--list", f"{src}-*", "--sort=-v:refname"]
    tag_result = subprocess.run(tag_command, capture_output=True, text=True)
    logging.info(tag_result)

    if tag_result.returncode != 0:
        raise ValueError(f"Error fetching tags: {tag_result.stderr}")

    tags = tag_result.stdout.strip().splitlines()

    # Fetch the commits that affect the function code since the last tag
    if len(tags) == 0:
        git_command = ["git", "log", "--oneline", "--", str(src)]
    else:
        tag = tags[0]
        git_command = [
            "git",
            "log",
            f"{tag}..HEAD",
            "--oneline",
            "--",
            f"{src}",
        ]
    result = subprocess.run(git_command, capture_output=True, text=True)
    logging.info(result)

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
        print(commit)
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
