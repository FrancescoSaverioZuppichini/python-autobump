# Python Auto Bump

> [!WARNING]  
> This is meant for a single package in the repo

## Motivation

Manually having to change version numbers based on changes is a boring task and very prune to error, this repo aims to give a tempalte to auto bumping your python package to a new version bsaed on the commit history

## How it works

This repos contains [`scripts`](./scripts/) and [`github workflows`](/.github/workflows/) to auto bump to a new version based on the commit history that must follow [gitmoji](https://gitmoji.dev/).

### Getting a new version

The python script [`get_new_version.py`](./scripts/get_new_version.py) computes a new version number based on the commit history from the **last version tag**

```bash
# assuming we are at version 0.0.0 and we have a package user `src/package1`
git commit -m "🐛 Fix weird bug"
python scripts/get_new_version.py src/package1
```

Will give you `0.0.1`, so a patch.

The list of `gitmoji` -> `bump` is the following

```python
new_version_emoji = "🔖"
major = r"^[💥]+"
minor = r"^[✨🏗️♻️⚡️👽️]+"
patch = rf"^[🚑️🔒️🐛🥅🔐📌🔧🌐💬📝{new_version_emoji}]+"
```

### Changing to the new version

Once we have the new version number, we use the [`update_version.py`](./scripts/update_version.py) that changes the `__version__` under a `package/__init__.py` file

```bash
python scripts/update_version.py src/package1 0.0.1
```

Will update the `src/package1/__init__.py` to

```python
__version__ = "0.0.1"
```

### Putting everything together

We have a GitHub [`workflow`](./.github/workflows/version_bump.yml) that on `push` on `main`

- get a new version number
- update the package `__init__.py`
- git add, commit and tag it with the new version number
- creates a new GitHub release with that version number
