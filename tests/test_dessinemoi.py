import attrs
import pytest as pytest

import dessinemoi
from dessinemoi import Factory, LazyType


@pytest.fixture
def factory():
    yield Factory()


@attrs.define
class LazyTypeTest:
    # Class for lazy type testing
    pass


def test_factory_instantiate(factory):
    # A Factory instance can be created
    assert isinstance(factory, Factory)


def test_factory_register(factory):
    class Sheep:
        _TYPE_ID = "sheep"

    # Register class based on its built-in ID
    factory.register(Sheep)
    assert "sheep" in factory.registry
    assert factory.registry["sheep"] == dessinemoi.FactoryRegistryEntry(
        cls=Sheep, dict_constructor=None
    )

    # Registering class again fails
    with pytest.raises(ValueError):
        factory.register(Sheep, type_id="mouton")

    # Overwriting existing ID fails if not explicitly allowed
    with pytest.raises(ValueError):
        factory.register(int, type_id="sheep")
    factory.register(int, type_id="sheep", overwrite_id=True)

    # A new class can also be registered with a decorator
    @factory.register  # Optionless form
    class Lamb(Sheep):
        _TYPE_ID = "lamb"

    assert "lamb" in factory.registry
    assert factory.registry["lamb"].cls is Lamb

    @factory.register(type_id="agneau")  # Full form
    class Agneau(Sheep):
        pass

    assert "agneau" in factory.registry
    assert factory.registry["agneau"].cls is Agneau


def test_factory_alias(factory):
    # Registering an alias to a nonexisting type fails
    with pytest.raises(ValueError):
        factory.alias("lamb", "agneau")

    # Aliasing an existing type works as expected
    @factory.register(type_id="lamb")
    class Lamb:
        pass

    factory.alias("lamb", "agneau")
    assert "agneau" in factory.registry
    assert factory.registry["agneau"].cls is Lamb

    # Aliasing a type with an existing type ID fails
    with pytest.raises(ValueError):
        factory.alias("lamb", "agneau")

    # Aliases can be defined upon registration
    factory.registry.clear()
    factory.register(Lamb, type_id="lamb", aliases=["agneau"])
    assert factory.registry["lamb"].cls is Lamb
    assert factory.registry["agneau"].cls is Lamb


def test_factory_lazy(factory):
    # Lazy types must have non-empty names
    with pytest.raises(ValueError):
        LazyType("", "")

    # Eager registration immediately dereferences a lazy type
    factory.register(
        f"{__name__}.LazyTypeTest",
        type_id="lazy",
        allow_lazy=False,
    )
    assert factory.registry["lazy"].cls is LazyTypeTest

    # A LazyType instance can be registered and is resolved upon call to create()
    del factory.registry["lazy"]
    factory.register(
        LazyType(__name__, "LazyTypeTest"),
        type_id="lazy",
    )
    assert isinstance(factory.registry["lazy"].cls, dessinemoi.LazyType)
    assert isinstance(factory.create("lazy"), LazyTypeTest)
    # After dereferencing, the lazy type is replaced by the actual type
    assert factory.registry["lazy"].cls is LazyTypeTest

    # Strings are interpreted as lazy types
    del factory.registry["lazy"]
    factory.register(
        f"{__name__}.LazyTypeTest",
        type_id="lazy",
        overwrite_id=True,
    )
    assert isinstance(factory.create("lazy"), LazyTypeTest)

    del factory.registry["lazy"]
    factory.register(
        f"{__name__}.LazyTypeTest",
        type_id="lazy",
        overwrite_id=True,
    )
    assert isinstance(factory.create("lazy"), LazyTypeTest)

    # Lazy types require an ID
    with pytest.raises(ValueError):
        factory.register(
            f"{__name__}.LazyTypeTest",
            overwrite_id=True,
        )


def test_factory_create(factory):
    @factory.register
    @attrs.frozen
    class Sheep:
        _TYPE_ID = "sheep"
        age = attrs.field()
        name = attrs.field()

    @factory.register
    @attrs.frozen
    class Ram(Sheep):
        _TYPE_ID = "ram"
        name = attrs.field(default="Gorki")

    # We can use the factory to instantiate new objects with positional arguments only
    assert factory.create("sheep", args=(5, "Dolly")) == Sheep(5, "Dolly")

    # Keyword arguments are supported as well
    assert factory.create("ram", args=(7,)) == Ram(7, name="Gorki")
    assert factory.create("ram", args=(7,), kwargs=dict(name="Romuald")) == Ram(
        7, name="Romuald"
    )

    # Unregistered type IDs raise
    with pytest.raises(ValueError):
        factory.create("mouton")

    # We can restrict accepted types to a certain type
    assert factory.create("ram", args=(7,), allowed_cls=Ram) == Ram(7, name="Gorki")
    with pytest.raises(TypeError):
        factory.create("sheep", args=(5, "Dolly"), allowed_cls=Ram)


def test_factory_classmethod(factory):
    @factory.register
    @attrs.frozen
    class Sheep:
        _TYPE_ID = "sheep"
        age = attrs.field()
        name = attrs.field()

        @classmethod
        def old(cls, name):
            return cls(15, name)

    # The construct parameter allows for the selection of a class method constructor
    s = factory.create("sheep", construct="old", kwargs={"name": "Romuald"})
    assert s.age == 15


def test_convert(factory):
    @factory.register
    @attrs.frozen
    class Sheep:
        _TYPE_ID = "sheep"
        wool = attrs.field(default="some")

    @factory.register
    @attrs.frozen
    class Lamb(Sheep):
        _TYPE_ID = "lamb"

    # We can construct keyword-only classes from a dictionary using a converter
    merino = factory.convert({"type": "sheep", "wool": "a_lot"})
    assert merino == Sheep(wool="a_lot")

    # Objects other than dictionaries are not modified
    assert factory.convert(merino) is merino

    # Requesting a non-existing type raises a ValueError
    with pytest.raises(ValueError):
        factory.convert({"type": "bull"})

    # Conversion can be restricted to a specific type
    with pytest.raises(TypeError):
        assert factory.convert(Sheep(), allowed_cls=Lamb)
    assert factory.convert(Lamb(), allowed_cls=Lamb) == Lamb()

    with pytest.raises(TypeError):
        assert factory.convert({"type": "sheep"}, allowed_cls=Lamb)
    assert factory.convert({"type": "lamb"}, allowed_cls=Lamb) == Lamb()

    # The convert method can be turned into a converter (in the sense of attrs)
    converter = factory.convert(allowed_cls=Lamb)
    with pytest.raises(TypeError):
        assert converter({"type": "sheep"})
    assert converter({"type": "lamb"}) == Lamb()


def test_module_api():
    # Module has a default Factory instance
    assert isinstance(dessinemoi.factory, Factory)

    # Module allows direct access to factory instance API
    @dessinemoi.register
    @attrs.frozen
    class Sheep:
        _TYPE_ID = "sheep"
        wool = attrs.field(default="some")

    assert dessinemoi.create("sheep") == Sheep()
    assert dessinemoi.convert({"type": "sheep"}) == Sheep()


def test_factory_dict_constructor(factory):
    @attrs.define
    class Sheep:
        wool = attrs.field()

        @classmethod
        def merino(cls):
            return cls(wool="lots")

    # A non-existing dict constructor will raise
    with pytest.raises(ValueError):
        factory.register(Sheep, type_id="sheep", dict_constructor="foo")

    # The dict constructor is correctly registered
    factory.register(Sheep, type_id="sheep", dict_constructor="merino")

    # The registered constructor is called as expected upon dict conversion
    assert factory.registry["sheep"].dict_constructor == "merino"
    s = factory.convert({"type": "sheep"})
    assert s == Sheep(wool="lots")


def test_lazy_type():
    from datetime import datetime

    # Lazy types are dereferenced upon call to load()
    lazy_datetime = dessinemoi.LazyType("datetime", "datetime")
    assert lazy_datetime.load() is datetime

    # String-based constructor tests
    # -- Standard pattern: absolute path
    assert dessinemoi.LazyType.from_str("foo.bar") == dessinemoi.LazyType(
        mod="foo", attr="bar"
    )
    # -- Absolute path with nested submodules
    assert dessinemoi.LazyType.from_str("foo.bar.baz") == dessinemoi.LazyType(
        mod="foo.bar", attr="baz"
    )
    # -- Relative imports are not allowed
    with pytest.raises(ValueError):
        dessinemoi.LazyType.from_str("foo")
    with pytest.raises(ValueError):
        dessinemoi.LazyType.from_str(".foo")
