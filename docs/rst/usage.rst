.. _usage:

Usage
=====

Create a factory object
^^^^^^^^^^^^^^^^^^^^^^^

To start using *Dessine-moi*'s factories, the first thing to do is to instantiate
the :class:`.Factory` class:


.. doctest::

   >>> import dessinemoi
   >>> factory = dessinemoi.Factory()

Our factory holds a *registry*, which maps *identifiers* (IDs), consisting of
strings, to Python types. Our factory has currently an empty registry:

.. doctest::

    >>> factory
    Factory(registry={})

Register types to the factory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's define a new Python type. For convenience, we will work with the ``attrs``
library, but *Dessine-moi* does not require you to use it. Let's define a simple
class:

.. doctest::

   >>> import attr
   >>> @attr.s
   ... class Sheep:
   ...     wool = attr.ib(default="some")

We can now register this class to the factory using the
:meth:`~.Factory.register` method:

.. doctest::

   >>> factory.register(Sheep, type_id="sheep")
   <class '__main__.Sheep'>
   >>> factory
   Factory(registry={'sheep': FactoryRegistryEntry(cls=<class '__main__.Sheep'>, dict_constructor=None)})

Classes can also be registered upon declaration using :meth:`~.Factory.register`
as a decorator. In that case, the ``cls`` positional argument is omitted. If the
``type_id`` keyword argument is omitted, *Dessine-moi* looks for a ``_TYPE_ID``
class attribute to set the class's ID in the registry:

.. doctest::

   >>> @factory.register
   ... @attr.s
   ... class Lamb(Sheep):
   ...     _TYPE_ID = "lamb"
   >>> factory
   Factory(registry={'sheep': FactoryRegistryEntry(cls=<class '__main__.Sheep'>, dict_constructor=None), 'lamb': FactoryRegistryEntry(cls=<class '__main__.Lamb'>, dict_constructor=None)})

.. note:: As can be seen from the previous code snippet, the call operator ``()``
   can be omitted if all arguments are omitted.

.. note:: When used as a decorator, :meth:`~.Factory.register` is best used
   last (*i.e.* at the top of the sequence).

The :meth:`~.Factory.register` method implements safeguards which can be
bypassed with dedicated keyword arguments:

* if ``allow_aliases`` is ``True``, a type can be registered multiple times with
  different IDs (the default value is ``False``):

  .. doctest::

     >>> factory.register(Sheep, "mouton", allow_aliases=True)
     <class '__main__.Sheep'>
     >>> factory
     Factory(registry={'sheep': FactoryRegistryEntry(cls=<class '__main__.Sheep'>, dict_constructor=None), 'lamb': FactoryRegistryEntry(cls=<class '__main__.Lamb'>, dict_constructor=None), 'mouton': FactoryRegistryEntry(cls=<class '__main__.Sheep'>, dict_constructor=None)})

* if ``allow_id_overwrite`` is ``True``, registering a type with an existing ID
  will succeed and overwrite the existing entry (the default value is ``False``).

Finally, :meth:`~.Factory.register` features an optional ``dict_constructor``
argument which, when set, associates a class method constructor to be called
upon attempting dictionary conversion. See `Convert objects`_ for more detail.

Instantiate registered types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once a type is registered, it can be instantiated using the :meth:`~.Factory.new`
method. If constructed class's constructor expects arguments, the ``args`` and
``kwargs`` arguments will forward them appropriately:

.. doctest::

   >>> merino = factory.create("sheep", kwargs={"wool": "lots"})
   >>> merino
   Sheep(wool='lots')

If you want to restrict the set of allowed types, the ``allowed_cls`` argument is
here:

.. doctest::

   >>> factory.create("sheep", allowed_cls=Lamb)
   Traceback (most recent call last):
   ...
   TypeError: 'sheep' does not reference allowed type <class '__main__.Lamb'> or any of its subtypes

.. note:: Under the hood, ``allowed_cls`` is passed to a call to
   :func:`isinstance`: it can therefore be a single type or a tuple of allowed
   types.

Any subtype of an allowed type is allowed:

.. doctest::

    >>> factory.create("lamb", allowed_cls=Sheep)
    Lamb(wool='some')

.. note::

   A very common and Pythonic design pattern consists in defining special
   constructors using class methods. If you use this approach, *Dessine-moi*
   lets you select a constructor using the ``construct`` argument. For
   demonstrative purposes, let us attach a class method constructor to our
   ``Sheep`` class:

   .. doctest::

      >>> @classmethod
      ... def unsheavable(cls):
      ...     return cls(wool="none")
      >>> Sheep.unsheavable = unsheavable

   We can now route object creation to this function using the ``construct``
   keyword argument. Since the ``unsheavable()`` class method takes no argument,
   we do not pass the ``args`` and ``kwargs`` arguments:

   .. doctest::

      >>> factory.create("sheep", construct="unsheavable")
      Sheep(wool='none')


Convert objects
^^^^^^^^^^^^^^^

*Dessine-moi*'s factories implement converters which can be used as part of the
``attrs`` conversion step. In its most straightforward form, the
:meth:`~.Factory.convert` method operates on a ``value`` argument.

* If ``value`` is not a dictionary, :meth:`~.Factory.convert` returns it
  unchanged.
* If ``value`` is a dictionary, :meth:`~.Factory.convert` queries its ``type``
  entry for a type ID and uses it to call :meth:`~.Factory.new`.

  .. doctest::

     >>> factory.convert({"type": "sheep", "wool": "lots"})
     Sheep(wool='lots')

.. admonition:: Notes
   :class: note

   * :meth:`~.Factory.convert` takes a ``allowed_cls`` argument and uses it
     exactly as :meth:`~.Factory.new` does.
   * Dictionary conversion won't work with classes expected non kw-only fields.
   * If a ``dict_constructor`` is associated to the registered type, it will be
     used to create the object instead of the default constructor.

     .. doctest::

        >>> factory.registry.clear()
        >>> factory.register(Sheep, type_id="sheep", dict_constructor="unsheavable")
        <class '__main__.Sheep'>
        >>> factory.convert({"type": "sheep"})
        Sheep(wool='none')

Extend factories
^^^^^^^^^^^^^^^^

Arguably, :meth:`~.Factory.convert` is rather limited. For instance, it works
only for classes whose constructors only take keyword arguments and reserves the
``type`` entry for factory ID specification. One could wish to change some of
that.

Fortunately, implementing custom conversion methods is simple: subclass
:class:`.Factory` and reimplement its :meth:`~.Factory.convert` method!
