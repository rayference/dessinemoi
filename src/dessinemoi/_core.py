from __future__ import annotations

import importlib
from collections.abc import MutableMapping
from copy import copy
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union

import attrs

# -- Sentinel value for unset parameters ---------------------------------------


class _Missing:
    pass


_MISSING = _Missing


# -- Utilities -----------------------------------------------------------------


def _fullname(cls):
    """
    Easily get fully qualified name of a class.
    """
    if isinstance(cls, LazyType):
        return cls.fullname

    else:
        mod = cls.__module__
        if mod == "builtins":
            return cls.__qualname__  # avoid outputs like 'builtins.str'
        return f"{mod}.{cls.__qualname__}"


# -- Core components -----------------------------------------------------------


@attrs.frozen
class LazyType:
    """
    A lightweight data class specifying a lazily loaded type.

    .. versionadded:: 22.1.0
    """

    mod: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    Module where the imported object will be looked up.
    """

    attr: str = attrs.field(validator=attrs.validators.instance_of(str))
    """
    Name of the imported object.
    """

    @attr.validator
    @mod.validator
    def _validator(self, attribute, value):
        if value == "":
            raise ValueError(
                f"while validating '{attribute.name}': got '{value}', "
                "must be non-empty"
            )

    @property
    def fullname(self):
        """
        Fully qualified name of the object.
        """
        return f"{self.mod}.{self.attr}"

    @classmethod
    def from_str(cls, value: str) -> LazyType:
        """
        Initialise a :class:`LazyType` from a string representing its fully
        qualified name.

        :param value:
            String representing an absolute import path to the target type.

        :return:
            Created lazy type specification.

        :raises ValueError:
            If the ``value`` cannot be interpreted as a fully qualified name
            and, therefore, is suspected to be a relative import path.
        """
        decomposed = value.split(".")
        if len(decomposed) < 2 or value.startswith("."):
            raise ValueError(
                f"'{value}' seems to specify a relative import path, "
                "please use a fully qualified name"
            )

        mod = ".".join(decomposed[:-1])
        attr = decomposed[-1]
        return cls(mod, attr)

    def load(self) -> Type:
        """
        Import the specified lazy type.

        :return:
            Imported type.
        """
        mod = importlib.import_module(self.mod)
        return getattr(mod, self.attr)


@attrs.define
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

    cls: Union[None, Type, LazyType] = attrs.field()
    dict_constructor: Optional[str] = attrs.field()


@attrs.define
class Factory:
    registry: Dict[str, FactoryRegistryEntry] = attrs.field(factory=dict)
    """
    Dictionary holding the factory registry.

    .. versionchanged:: 21.3.0
       Changed type from ``Dict[str, Type]`` to
       ``Dict[str, FactoryRegistryEntry]``.
    """

    @property
    def registered_types(self) -> List[str]:
        """
        List of currently registered types, without duplicates.

        .. versionadded:: 21.3.0
        """
        return list({_fullname(x.cls) for x in self.registry.values()})

    def _register_impl(
        self,
        cls: Union[Type, LazyType, str],
        type_id: Optional[str] = None,
        dict_constructor: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        overwrite_id: bool = False,
        allow_lazy: bool = True,
    ) -> Any:
        if isinstance(cls, str):
            cls = LazyType.from_str(cls)

        # Upon request, force eager loading of lazy type declarations
        if isinstance(cls, LazyType) and not allow_lazy:
            cls = cls.load()

        # If no ID is specified and the type declares one, use it
        if type_id is None:
            try:
                type_id = cls._TYPE_ID
            except AttributeError as e:
                raise ValueError(
                    f"while registering {cls}: please declare a type ID"
                ) from e

        # Check if type is already registered
        cls_fullname = _fullname(cls)
        if not aliases and cls_fullname in self.registered_types:
            raise ValueError(f"'{cls_fullname}' is already registered")

        # Check if ID is already used
        if not overwrite_id and type_id in self.registry.keys():
            raise ValueError(
                f"'{type_id}' is already used to reference "
                f"'{_fullname(self.registry[type_id].cls)}'"
            )

        # Check that dict constructor exists (skipped with lazy types)
        if isinstance(cls, type) and dict_constructor is not None:
            try:
                getattr(cls, dict_constructor)
            except AttributeError as e:
                raise ValueError(
                    f"class method '{cls.__name__}.{dict_constructor}()' does not exist"
                ) from e

        # All checks done: perform actual registration
        self.registry[type_id] = FactoryRegistryEntry(
            cls=cls,
            dict_constructor=dict_constructor,
        )

        # Add aliases
        if aliases is None:
            aliases = []

        for alias_id in aliases:
            self.alias(type_id, alias_id)

        return cls

    def register(
        self,
        cls: Any = _MISSING,
        *,
        type_id: Optional[str] = None,
        dict_constructor: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        overwrite_id: bool = False,
        allow_lazy: bool = True,
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
            class decorator. A :class:`LazyType` instance or a string
            convertible to :class:`LazyType` may also be passed.

        :param type_id:
            Identifier string used to register ``cls``. Required if ``cls`` is a
            lazy type or if it does not specify its identifier itself.

        :param dict_constructor:
            Class method to be used for dictionary-based construction. If
            ``None``, the default constructor is used.

        :param aliases:
            If ``True``, a given type can be registered multiple times under
            different IDs.

        :param overwrite_id:
            If ``True``, existing IDs can be overwritten.

        :param allow_lazy:
            If ``False``, force eager loading of lazy types.

        :raises ValueError:
            If ``allow_aliases`` is ``False`` and ``cls`` is already registered.

        :raises ValueError:
            If ``allow_id_overwrite`` is ``False`` and ``type_id`` is already
            used to reference a type in the registry.

        .. versionchanged:: 21.3.0
           Made keyword-only.

        .. versionchanged:: 21.3.0
           Added ``dict_constructor`` argument.

        .. versionchanged:: 22.1.0
           Added ``allow_lazy`` argument. Accept :class:`LazyType` and strings
           for ``cls``.

        .. versionchanged:: 22.2.0
           Renamed ``allow_id_overwrite`` to ``overwrite_id``.
           Removed ``allow_aliases``, replaced by ``aliases``.
        """

        if cls is not _MISSING:
            try:
                return self._register_impl(
                    cls,
                    type_id=type_id,
                    dict_constructor=dict_constructor,
                    aliases=aliases,
                    overwrite_id=overwrite_id,
                    allow_lazy=allow_lazy,
                )
            except ValueError:
                raise

        else:

            def inner_wrapper(wrapped_cls):
                return self._register_impl(
                    wrapped_cls,
                    type_id=type_id,
                    dict_constructor=dict_constructor,
                    aliases=aliases,
                    overwrite_id=overwrite_id,
                )

            return inner_wrapper

    def alias(self, type_id: str, alias_id: str, overwrite_id: bool = False) -> None:
        """
        Register a new alias to a registered type.

        :param type_id:
            ID of the aliased type.

        :param alias_id:
            Created alias ID.

        :raises ValueError:


        .. versionadded:: 22.2.0
        """
        if type_id in self.registry:
            if not overwrite_id and alias_id in self.registry.keys():
                raise ValueError(
                    f"'{type_id}' is already used to reference "
                    f"'{_fullname(self.registry[type_id].cls)}'"
                )

            else:
                self.registry[alias_id] = self.registry[type_id]

        else:
            raise ValueError(f"cannot alias unregistered type '{type_id}'")

    def get_type(self, type_id: str) -> Type:
        """
        Return the type corresponding to the requested type ID. Lazy types will
        be loaded.

        :param type_id:
            ID of a registered type.

        :returns:
            Corresponding type.

        .. versionadded:: 22.1.1
        """
        entry = self.registry[type_id]

        if isinstance(entry.cls, LazyType):
            cls = entry.cls.load()
            self.registry[type_id].cls = cls
        else:
            cls = entry.cls

        return cls

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

        :raises ValueError:
            If ``type_id`` does not reference a registered type.

        :raises TypeError:
            If the requested type is not allowed.

        .. versionchanged:: 21.2.0
           Added ``construct`` keyword argument.
        """
        try:
            cls = self.get_type(type_id)
        except KeyError as e:
            raise ValueError(f"no type registered as '{type_id}'") from e

        if allowed_cls is not None and not issubclass(cls, allowed_cls):
            raise TypeError(
                f"'{type_id}' does not reference allowed type {allowed_cls} or "
                "any of its subtypes"
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

            try:
                entry = self.registry[type_id]
            except KeyError as e:
                raise ValueError(f"no type registered as '{type_id}'") from e

            # Resolve lazy type if necessary
            cls = entry.cls.load() if isinstance(entry.cls, LazyType) else entry.cls

            # Check if class is allowed
            if allowed_cls is not None and not issubclass(cls, allowed_cls):
                raise TypeError(
                    f"conversion to object type '{type_id}' ({cls}) is not allowed"
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
