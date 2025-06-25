# Dessine-moi, a simple Python factory

> S'il vous plaît, dessine-moi un mouton.

The narrator of Antoine de Saint-Exupéry's Little Prince probably dreamt of a
factory like this one...

[![PyPI version](https://img.shields.io/pypi/v/dessinemoi?color=blue)](https://pypi.org/project/dessinemoi)
[![Conda version](https://img.shields.io/conda/v/conda-forge/dessinemoi?color=blue)](https://anaconda.org/conda-forge/dessinemoi)

[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/leroyvn/dessinemoi/ci.yml?branch=main)](https://github.com/leroyvn/dessinemoi/actions/workflows/ci.yml)
[![Documentation Status](https://img.shields.io/readthedocs/dessinemoi)](https://dessinemoi.readthedocs.io)

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Motivation

*Dessine-moi* is a simple Python implementation of the factory pattern. It was
born from the need to create dynamically object trees from nested dictionaries
(*e.g.* a JSON document).

## Features

- Create a `Factory` object and register types to it
- Use dictionaries to create objects from the factory
- Create *attrs*-compatible converters to automatically convert dictionaries to
  instances of registered types
- Customize factories to your needs

Check the [documentation](https://dessinemoi.readthedocs.io) for more detail.

## License

*Dessine-moi* is distributed under the terms of the
[MIT license](https://choosealicense.com/licenses/mit/).

## About

*Dessine-moi* is written and maintained by [Vincent Leroy](https://github.com/leroyvn).

The development is supported by [Rayference](https://www.rayference.eu).

*Dessine-moi* is a component of the
[Eradiate radiative transfer model](https://www.eradiate.eu).
