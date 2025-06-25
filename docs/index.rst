:hide-toc:

Dessine-moi
===========

*Dessine-moi* v\ |release|.

.. image:: https://img.shields.io/pypi/v/dessinemoi?color=blue
   :target: https://pypi.org/project/dessinemoi

.. image:: https://img.shields.io/conda/v/conda-forge/dessinemoi?color=blue
   :target: https://anaconda.org/conda-forge/dessinemoi

.. image:: https://img.shields.io/github/actions/workflow/status/rayference/dessinemoi/ci.yml?branch=main
   :target: https://github.com/rayference/dessinemoi/actions/workflows/ci.yml

.. image:: https://img.shields.io/readthedocs/dessinemoi
   :target: https://dessinemoi.readthedocs.io

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json
    :target: https://github.com/astral-sh/uv
    :alt: uv

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

*S'il vous plaît, dessine-moi un mouton.*

Motivation
----------

*Dessine-moi* is a simple Python implementation of the factory pattern. It was
born from the need to create dynamically object trees from nested dictionaries
(*e.g.* a JSON document).

Features
--------

- Create a :class:`.Factory` object and register types to it.
- Use dictionaries to create objects from the factory.
- Create *attrs*-compatible converters to automatically convert dictionaries
  to instances of registered types.
- Customise factories to your needs.

Getting started
---------------

*Dessine-moi* requires Python 3.8+ and depends on *attrs*. It is tested with
Pytest.

Install from PyPI in your virtual environment:

.. code-block:: bash

   python -m pip install dessinemoi

Using Conda:

.. code-block:: bash

   conda install -c conda-forge dessinemoi

The :ref:`usage` section presents *Dessine-moi*'s features and how to use them.

License
-------

*Dessine-moi* is distributed under the terms of the
`MIT license <https://choosealicense.com/licenses/mit/>`_.

About
-----

*Dessine-moi* is written and maintained by `Vincent Leroy <https://github.com/leroyvn>`_.

The development is supported by `Rayference <https://www.rayference.eu>`_.

*Dessine-moi* is a component of the
`Eradiate radiative transfer model <https://www.eradiate.eu>`_.

.. toctree::
   :hidden:
   :caption: Use

   usage

.. toctree::
   :hidden:
   :caption: Reference

   api
   release_notes.md


.. toctree::
   :caption: Develop
   :hidden:

   contributing.md
   GitHub repository <https://github.com/rayference/dessinemoi>
