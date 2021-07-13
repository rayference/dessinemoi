# Dessine-moi, a simple Python factory

> S'il vous plaît, dessine-moi un mouton.

The narrator of Antoine de Saint-Exupéry's Little Prince probably dreamt of a factory like this one...

[![PyPI version](https://img.shields.io/pypi/v/dessinemoi?color=blue&style=flat-square)](https://pypi.org/project/dessinemoi)
[![Conda version](https://img.shields.io/conda/v/eradiate/dessinemoi?color=blue&style=flat-square)](https://anaconda.org/eradiate/dessinemoi)

[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/leroyvn/dessinemoi/Tests/main?style=flat-square)](https://github.com/leroyvn/dessinemoi/actions/workflows/tests.yml)
[![Codecov](https://codecov.io/gh/leroyvn/dessinemoi/branch/main/graph/badge.svg)](https://codecov.io/gh/leroyvn/dessinemoi)
[![Documentation Status](https://img.shields.io/readthedocs/dessinemoi?style=flat-square)](https://dessinemoi.readthedocs.io)

[![Code style: black](https://img.shields.io/badge/code%20style-black-black?style=flat-square)](https://black.readthedocs.io)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-blue?style=flat-square&labelColor=orange)](https://pycqa.github.io/isort)

## Motivation

*Dessine-moi* is a simple Python implementation of the factory pattern. It was 
born from the need to create dynamically object trees from nested dictionaries 
(*e.g.* a JSON document).

## Features

- Create a `Factory` object and register types to it
- Use dictionaries to create objects from the factory
- Create `attrs`-compatible converters to automatically convert dictionaries to 
  instances of registered types
- Customise factories to your needs

Check the [documentation](https://dessinemoi.readthedocs.io) for more detail.

## License

*Dessine-moi* is distributed under the terms of the
[MIT license](https://choosealicense.com/licenses/mit/).

## About

*Dessine-moi* is written and maintained by [Vincent Leroy](https://github.com/leroyvn).

The development is supported by [Rayference](https://www.rayference.eu).

*Dessine-moi* is a component of the
[Eradiate radiative transfer model](https://www.eradiate.eu).
