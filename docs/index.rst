.. dessinemoi documentation master file, created by
   sphinx-quickstart on Tue May 25 18:21:12 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

:hide-toc:

Dessine-moi
===========

*Dessine-moi* v\ |release|.

.. image:: https://img.shields.io/readthedocs/dessinemoi?style=flat-square
   :target: https://dessinemoi.readthedocs.io

.. image:: https://img.shields.io/pypi/v/dessinemoi?color=blue&style=flat-square
   :target: https://pypi.org/project/dessinemoi

.. image:: https://img.shields.io/conda/v/eradiate/dessinemoi?color=blue&style=flat-square
   :target: https://anaconda.org/eradiate/dessinemoi

.. image:: https://img.shields.io/badge/code%20style-black-black?style=flat-square
   :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/%20imports-isort-blue?style=flat-square&labelColor=orange
   :target: https://pycqa.github.io/isort

*S'il vous plaît, dessine-moi un mouton.*

*Dessine-moi* is a simple Python factory.

Motivation
----------

*To do*

Features
--------

- Create factory objects.
- Register arbitrary types to your factory, possibly with aliases, with a simple
  decorator syntax.
- Create objects using your factory, possibly applying type filters.
- Write custom converters to turn values into objects of a registered type.

Getting started
---------------

Install from PyPI in your virtual environment:

.. code-block:: bash

   python -m pip install dessinemoi

Using Conda:

.. code-block:: bash

   conda install -c eradiate dessinemoi

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

   rst/usage

.. toctree::
   :caption: Development
   :hidden:

   rst/dev
   rst/api
   rst/changes
   GitHub repository <https://github.com/leroyvn/dessinemoi>
