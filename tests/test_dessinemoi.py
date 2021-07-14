import attr
import pytest as pytest

import dessinemoi
from dessinemoi import Factory


@pytest.fixture
def factory():
    yield Factory()


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

    # Registering class again fails if aliases are not allowed
    with pytest.raises(ValueError):
        factory.register(Sheep, type_id="mouton")
    factory.register(Sheep, type_id="mouton", allow_aliases=True)
    assert factory.registry["mouton"] == dessinemoi.FactoryRegistryEntry(
        cls=Sheep, dict_constructor=None
    )

    # Overwriting existing ID fails if not explicitly allowed
    with pytest.raises(ValueError):
        factory.register(int, type_id="sheep")
    factory.register(int, type_id="sheep", allow_id_overwrite=True)

    # A new class can also be registered with a decorator
    # Decorator uses can also be chained
    @factory.register(type_id="agneau", allow_aliases=True)  # Full function call form
    @factory.register  # Optionless form
    class Lamb(Sheep):
        _TYPE_ID = "lamb"

    assert "lamb" in factory.registry
    assert "agneau" in factory.registry
    assert factory.registry["lamb"].cls is Lamb
    assert factory.registry["agneau"].cls is Lamb


def test_factory_create(factory):
    @factory.register
    @attr.s(frozen=True)
    class Sheep:
        _TYPE_ID = "sheep"
        age = attr.ib()
        name = attr.ib()

    @factory.register
    @attr.s(frozen=True)
    class Ram(Sheep):
        _TYPE_ID = "ram"
        name = attr.ib(default="Gorki")

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
    @attr.s(frozen=True)
    class Sheep:
        _TYPE_ID = "sheep"
        age = attr.ib()
        name = attr.ib()

        @classmethod
        def old(cls, name):
            return cls(15, name)

    # The construct parameter allows for the selection of a class method constructor
    s = factory.create("sheep", construct="old", kwargs={"name": "Romuald"})
    assert s.age == 15


def test_convert(factory):
    @factory.register
    @attr.s(frozen=True)
    class Sheep:
        _TYPE_ID = "sheep"
        wool = attr.ib(default="some")

    @factory.register
    @attr.s(frozen=True)
    class Lamb(Sheep):
        _TYPE_ID = "lamb"

    # We can construct keyword-only classes from a dictionary using a converter
    merino = factory.convert({"type": "sheep", "wool": "a_lot"})
    assert merino == Sheep(wool="a_lot")

    # Objects other than dictionaries are not modified
    assert factory.convert(merino) is merino

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
    @attr.s(frozen=True)
    class Sheep:
        _TYPE_ID = "sheep"
        wool = attr.ib(default="some")

    assert dessinemoi.create("sheep") == Sheep()
    assert dessinemoi.convert({"type": "sheep"}) == Sheep()


def test_factory_dict_constructor(factory):
    @attr.s
    class Sheep:
        wool = attr.ib()

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
