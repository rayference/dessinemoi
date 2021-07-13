from collections.abc import MutableMapping
from typing import Any, Dict, Optional, Sequence, Tuple, Type, Union

import attr

# -- Version information -------------------------------------------------------

__version__ = "21.2.0"

# -- Sentinel value for unset parameters ---------------------------------------


class _Missing:
    pass


_MISSING = _Missing

# -- Core stuff ----------------------------------------------------------------


@attr.s
class Factory:
    #: Dictionary holding the factory registry
    registry: Dict[str, Type] = attr.ib(factory=dict)

    def _register_impl(
        self,
        cls: Type,
        type_id: Optional[str] = None,
        allow_aliases: bool = False,
        allow_id_overwrite: bool = False,
    ) -> Any:
        if type_id is None:
            type_id = cls._TYPE_ID

        if not allow_aliases and cls in self.registry.values():
            raise ValueError(f"{cls} already registered")

        if not allow_id_overwrite and type_id in self.registry.keys():
            raise ValueError(
                f"'{type_id}' already used to reference {self.registry[type_id]}"
            )

        self.registry[type_id] = cls

    def register(
        self,
        cls: Any = _MISSING,
        type_id: Optional[str] = None,
        allow_aliases: bool = False,
        allow_id_overwrite: bool = False,
    ) -> Any:
        """
        If parameter ``cls`` is passed, register ``cls`` to the factory.
        Otherwise, *i.e.* if this method is used as a decorator, register the
        decorated class to the factory.

        :param cls:
            If set, type to register to the factory. If unset, this function
            returns a callable which can be used to register classes. In
            practice, this parameter is unset when the method is used as a
            class decorator.

        :param type_id:
            Identifier string used to register ``cls``.

        :param allow_aliases:
            If ``True``, a given type can be registered multiple times under
            different IDs.

        :param allow_id_overwrite:
            If ``True``, existing IDs can be overwritten.

        :raises ValueError:
            If ``allow_aliases`` is ``False`` and ``cls`` is already registered.

        :raises ValueError:
            If ``allow_id_overwrite`` is ``False`` and ``type_id`` is already
            used to reference a type in the registry.
        """

        if cls is not _MISSING:
            try:
                self._register_impl(
                    cls,
                    type_id=type_id,
                    allow_aliases=allow_aliases,
                    allow_id_overwrite=allow_id_overwrite,
                )
                return cls
            except ValueError:
                raise

        else:

            def inner_wrapper(wrapped_cls):
                self._register_impl(
                    wrapped_cls,
                    type_id=type_id,
                    allow_aliases=allow_aliases,
                    allow_id_overwrite=allow_id_overwrite,
                )
                return wrapped_cls

            return inner_wrapper

    def create(
        self,
        type_id: str,
        allowed_cls: Optional[Union[Type, Tuple[Type]]] = None,
        construct: Optional[str] = None,
        args: Optional[Sequence] = None,
        kwargs: Optional[MutableMapping] = None,
    ) -> Any:
        """
        Create a new instance of a registered type.

        :param type_id:
            ID of the type to be instantiated.

        :param allowed_cls:
            If not ``None``, one or several types to which creation shall be
            restricted. If ``type_id`` does not reference one of these allowed
            types, an exception will be raised.

        :param construct:
            If not ``None``, attempt instantiation using a class method
            constructor instead of the default constructor.

        :param args:
            A sequence of arguments to pass to the constructor of the created
            type.

        :param kwargs:
            A mapping of keyword arguments to passed to the constructor of the
            created type.

        :return:
            Created object.

        :raises TypeError:
            If the requested type is not allowed.
        """
        try:
            cls = self.registry[type_id]
        except KeyError as e:
            raise ValueError(f"no type registered as '{type_id}'") from e

        if allowed_cls is not None and not issubclass(cls, allowed_cls):
            raise TypeError(
                f"'{type_id}' does not reference allowed type {allowed_cls} or any "
                "of its subtypes"
            )

        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = dict()

        if construct is not None:
            return getattr(cls, construct)(*args, **kwargs)
        else:
            return cls(*args, **kwargs)

    def _convert_impl(
        self,
        value,
        allowed_cls: Optional[Union[Type, Tuple[Type]]] = None,
    ) -> Any:
        if isinstance(value, MutableMapping):
            # Fetch class from registry
            type_id = value.pop("type")
            cls = self.registry[type_id]

            # Check if class is allowed
            if allowed_cls is not None and not issubclass(cls, allowed_cls):
                raise TypeError(
                    f"conversion to object type '{type_id}' ({cls}) is not allowed"
                )

            # Construct object
            return self.create(type_id, kwargs=value)

        else:
            # Check if object has allowed type
            if allowed_cls is not None:
                if not isinstance(value, allowed_cls):
                    raise TypeError("value type is not allowed")

            return value

    def convert(
        self,
        value: MutableMapping = _MISSING,
        allowed_cls: Optional[Union[Type, Tuple[Type]]] = None,
    ) -> Any:
        """
        Convert a dictionary to one of the types supported by the factory.

        :param value:
            Value to attempt conversion of. If ``value`` is a dictionary, the
            method tries to convert it to a registered type based on the
            ``type``. If ``value`` is not a dictionary, it is returned without
            change. If ``value`` is unset, the method returns a callable which
            can later be used for conversion.

        :param allowed_cls:
            Types to restrict conversion to. If set, ``value`` will be checked
            and an exception will be raised if it does not have one of the
            allowed types.

        :return:
            Created object if ``value`` is a dictionary; ``value`` otherwise.

        :raises TypeError:
            If ``allowed_cls`` is specified and ``value.type`` refers to a
            disallowed type or ``type(value)`` is disallowed.
        """
        if value is _MISSING:
            return lambda x: self._convert_impl(value=x, allowed_cls=allowed_cls)

        else:
            return self._convert_impl(value=value, allowed_cls=allowed_cls)


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
