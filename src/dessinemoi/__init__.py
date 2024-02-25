from typing import Any

# -- Version information -------------------------------------------------------

from ._version import version as __version__  # noqa: F401

# -- Public API ----------------------------------------------------------------

from ._core import Factory, FactoryRegistryEntry, LazyType  # noqa: F401

# -- API to built-in factory instance ------------------------------------------

factory = Factory()


def __getattr__(name: str) -> Any:
    try:
        return {
            "registry": factory.registry,
            "register": factory.register,
            "create": factory.create,
            "convert": factory.convert,
        }[name]
    except KeyError:
        raise AttributeError(name)


__all__ = [
    "Factory",
    "FactoryRegistryEntry",
    "LazyType",
    "factory",
]
