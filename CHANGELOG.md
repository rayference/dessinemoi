# Release Notes

[![CalVer](https://img.shields.io/badge/calver-YY.MINOR.MICRO-blue)](https://calver.org/)

## Dessine-moi 25.1.0 (2025-06-25)

- *Dessine-moi* is now on conda-forge.
- The "What's New?" page is now entitled "Release Notes".
- Add Python 3.13 support ({ghpr}`11`).

### Developer-side changes

- Migrate from Rye to uv for project management ({ghpr}`11`).

## Dessine-moi 24.1.0 (2024-02-25)

- Add Python 3.12 support ({ghpr}`8`).

### Developer-side changes

- Move from PDM to Rye for project management ({ghpr}`8`).
- Drop Nox for testing ({ghpr}`8`).
- Drop Conda development environment support ({ghpr}`8`).
- Use the Ruff formatter instead of Black in pre-commit hooks ({ghpr}`8`).
- Drop Copier template ({ghpr}`8`).

## Dessine-moi 23.1.0 (2023-02-22)

- Drop support for Python 3.7, add support for Python 3.11 ({ghpr}`7`).

## Dessine-moi 22.2.0 (2022-07-29)

## Fixes and improvements

- `LazyType.convert()`: Resolve lazy types ({ghpr}`5`).
- `Factory`: New alias system ({ghpr}`6`).
- `Factory.register()`: Rename `allow_id_overwrite` to `overwrite_id` ({ghpr}
  `6`).

## Dessine-moi 22.1.1 (2022-07-28)

### Fixes and improvements

- `LazyType.load()`: Replace `__import__()` with `importlib.import_module()`
  ({ghpr}`4`).

## Dessine-moi 22.1.0 (2022-07-19)

### Features

- `Factory`: Support string-based lazy registration ({ghpr}`2`).

### Developer side

- Switch from Poetry to PDM for project management ({ghpr}`3`).
- Apply Copier template ({ghpr}`3`).
- Restructure code to fit implementation in a dedicated module ({ghpr}`3`).
- Switch to next-generation attrs API ({ghpr}`1`).

## Dessine-moi 21.3.0 (2021-07-19)

### Features

- `Factory`: Make arguments keyword-only when relevant ({ghcommit}`b6c5c6`).
- `Factory`: Support default dict constructor ({ghcommit}`dcd1d4`).

## Dessine-moi 21.2.0 (2021-07-13)

### Features

- `Factory.create()`: Add `construct` keyword argument ({ghcommit}`a2e5874`).

## Dessine-moi 21.1.0 (2021-06-02)

Initial release.
