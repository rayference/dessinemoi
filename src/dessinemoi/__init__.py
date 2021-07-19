from collections.abc import MutableMapping
from copy import copy
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Type, Union

import attr

# -- Version information -------------------------------------------------------

__version__ = "21.3.0"

# -- Sentinel value for unset parameters ---------------------------------------


class _Missing:
    pass


_MISSING = _Missing

# -- Core stuff ----------------------------------------------------------------


@attr.s(frozen=True, slots=True)
class FactoryRegistryEntry:
    """
    Data class holding a ``(cls: Type, dict_constructor: Optional[str])`` pair.

    * ``cls`` is a type registered to a factory;
    * ``dict_constructor`` is a string pointing to the class method constructor
      used by default when :meth:`Factory.convert` attempts dictionary
      conversion.

    If ``dict_constructor`` is set to ``None``, it means that the default
    constructor should be used.

    .. versionadded:: 21.3.0
    """

    cls: Type = attr.ib()
    dict_constructor: Optional[str] = attr.ib()


@attr.s(slots=True)
class Factory:
    registry: Dict[str, FactoryRegistryEntry] = attr.ib(factory=dict)
    """
    Dictionary holding the factory registry.
    
    .. versionchanged:: 21.3.0
       Changed type from ``Dict[str, Type]`` to 
       ``Dict[str, FactoryRegistryEntry]``.
    """

    @property
    def registered_types(self) -> List[Type]:
        """
        List of currently registered types, without duplicates.

        .. versionadded:: 21.3.0
        """
        return list({x.cls for x in self.registry.values()})

    def _register_impl(
        self,
        cls: Type,
        type_id: Optional[str] = None,
        dict_constructor: Optional[str] = None,
        allow_aliases: bool = False,
        allow_id_overwrite: bool = False,
    ) -> Any:
        if type_id is None:
            type_id = cls._TYPE_ID

        if not allow_aliases and cls in self.registered_types:
            raise ValueError(f"{cls} already registered")

        if not allow_id_overwrite and type_id in self.registry.keys():
            raise ValueError(
                f"'{type_id}' already used to reference {self.registry[type_id]}"
            )

        # Check that dict constructor exists
        if dict_constructor is not None:
            try:
                getattr(cls, dict_constructor)
            except AttributeError as e:
                raise ValueError(
                    f"class method '{cls.__name__}.{dict_constructor}()' does not exist"
                ) from e

        self.registry[type_id] = FactoryRegistryEntry(
            cls=cls,
            dict_constructor=dict_constructor,
        )

    def register(
        self,
        cls: Any = _MISSING,
        *,
        type_id: Optional[str] = None,
        dict_constructor: Optional[str] = None,
        allow_aliases: bool = False,
        allow_id_overwrite: bool = False,
    ) -> Any:
        """
        If parameter ``cls`` is passed, register ``cls`` to the factory.
        Otherwise, *i.e.* if this method is used as a decorator, register the
        decorated class to the factory.

        .. note:: All arguments, except ``cls``, are keyword-only.

        :param cls:
            If set, type to register to the factory. If unset, this function
            returns a callable which can be used to register classes. In
            practice, this parameter is unset when the method is used as a
            class decorator.

        :param type_id:
            Identifier string used to register ``cls``.

        :param dict_constructor:
            Class method to be used for dictionary-based construction. If
            ``None``, the default constructor is used.

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

        .. versionchanged:: 21.3.0
           Made keyword-only.

        .. versionchanged:: 21.3.0
           Added ``dict_constructor`` argument.
        """

        if cls is not _MISSING:
            try:
                self._register_impl(
                    cls,
                    type_id=type_id,
                    dict_constructor=dict_constructor,
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
                    dict_constructor=dict_constructor,
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

        .. versionchanged:: 21.2.0
           Added ``construct`` keyword argument.
        """
        try:
            entry = self.registry[type_id]
            cls = entry.cls
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
            # Copy value to avoid unintended mutation
            value_copy = copy(value)

            # Query registry
            type_id = value_copy.pop("type")
            entry = self.registry[type_id]

            # Check if class is allowed
            if allowed_cls is not None and not issubclass(entry.cls, allowed_cls):
                raise TypeError(
                    f"conversion to object type '{type_id}' ({entry.cls}) is not allowed"
                )

            # Construct object
            return self.create(
                type_id, construct=entry.dict_constructor, kwargs=value_copy
            )

        else:
            # Check if object has allowed type
            if allowed_cls is not None:
                if not isinstance(value, allowed_cls):
                    raise TypeError("value type is not allowed")

            return value

    def convert(
        self,
        value: MutableMapping = _MISSING,
        *,
        allowed_cls: Optional[Union[Type, Tuple[Type]]] = None,
    ) -> Any:
        """
        Convert a dictionary to one of the types supported by the factory.

        .. note:: All arguments, except ``self`` and ``value``, are
           keyword-only.

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

        .. versionchanged:: 21.3.0
           Made all args keyword-only except for ``value``.
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
