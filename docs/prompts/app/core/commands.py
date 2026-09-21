"""Shared command bus for the application.

Defines the building blocks for a lightweight, in-process command bus:

- :class:`Command` — a plain data container describing an intent.
- :class:`CommandHandler` — the protocol every handler must satisfy.
- :func:`command_handler` — registers a callable as the handler for a
  given :class:`Command` subtype.
- :class:`CommandBus` — a synchronous in-process registry + dispatcher
  that looks up the registered handler for a command and executes it.

This module intentionally does **not** import anything from
``app.modules`` so that every module can depend on it without creating
a circular import. Modules wire their handlers through the
``@command_handler`` decorator (or by registering directly on a bus
instance).
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable, Protocol, Type, TypeVar

TCommand = TypeVar("TCommand", bound="Command")
TResult = TypeVar("TResult")


class Command:
    """Base class for all commands.

    A command is an immutable-ish description of an intent to perform
    some action. Commands carry data, never behaviour. Concrete
    commands should subclass this class and declare their fields as
    dataclass attributes.

    Example::

        @dataclass
        class CreateUser(Command):
            email: str
            password: str
    """

    __slots__ = ()


class CommandHandler(Protocol[TCommand, TResult]):
    """Protocol describing a command handler callable.

    A handler receives the command instance and returns whatever the
    use case produces (often ``None`` for fire-and-forget commands, or
    a result object for commands that return data).
    """

    def __call__(self, command: TCommand) -> TResult:  # pragma: no cover
        ...


HandlerFactory = Callable[[], CommandHandler]

_registry: dict[Type[Command], HandlerFactory] = {}


def command_handler(command_type: Type[TCommand]) -> Callable[[HandlerFactory], HandlerFactory]:
    """Register a callable as the handler for ``command_type``.

    Can be used as a plain decorator on a handler function::

        @command_handler(CreateUser)
        def handle_create_user(command: CreateUser) -> UserId:
            ...

    Or on a factory that lazily constructs a handler instance::

        @command_handler(CreateUser)
        def _create_user_handler() -> CreateUserHandler:
            return CreateUserHandler()

    The decorated callable must accept exactly one positional argument
    (the command). Registered handlers are resolved lazily by the bus
    on each dispatch, so handler instances are created per execution.
    """

    def decorator(factory: HandlerFactory) -> HandlerFactory:
        _registry[command_type] = factory
        return factory

    return decorator


def get_handler(command_type: Type[TCommand]) -> HandlerFactory:
    """Return the registered handler factory for ``command_type``.

    Raises :class:`ValueError` when no handler has been registered for
    the command type. Only exact type matches are supported; there is
    no inheritance-based fallback.
    """

    try:
        return _registry[command_type]
    except KeyError:
        raise ValueError(f"No handler registered for command {command_type.__name__}") from None


class CommandBus:
    """A synchronous, in-process command registry and dispatcher.

    Handlers are looked up by their exact command type and invoked
    immediately. This is intentionally kept simple: it is the building
    block modules use internally, and can be swapped later for a more
    sophisticated (async / outbox / queue-backed) implementation
    without callers noticing.
    """

    def __init__(self) -> None:
        self._handlers: dict[Type[Command], HandlerFactory] = {}

    def register(self, command_type: Type[TCommand], factory: HandlerFactory) -> None:
        """Register ``factory`` as the handler for ``command_type``.

        Registering a second handler for the same command type
        overwrites the previous one.
        """

        self._handlers[command_type] = factory

    def register_from_global_registry(self) -> None:
        """Pull every handler registered via ``@command_handler``.

        Copies the module-level ``_registry`` into this bus instance so
        a single bus can dispatch all commands declared across the
        application.
        """

        self._handlers.update(_registry)

    def dispatch(self, command: TCommand) -> Any:
        """Execute the handler registered for ``command`` and return its result.

        Raises :class:`ValueError` when no handler is registered for the
        command's exact type.
        """

        command_type = type(command)
        try:
            factory = self._handlers[command_type]
        except KeyError:
            raise ValueError(
                f"No handler registered for command {command_type.__name__}"
            ) from None

        handler = factory()
        return handler(command)


def ensure_handler_signature(factory: HandlerFactory, command_type: Type[TCommand]) -> None:
    """Validate that ``factory`` produces a single-argument callable.

    Lightweight guard used when registering handlers programmatically,
    to catch a common wiring mistake (handler taking zero or multiple
    positional parameters). Raises :class:`TypeError` on mismatch.
    """

    signature = inspect.signature(factory)
    parameters = [
        parameter
        for parameter in signature.parameters.values()
        if parameter.kind
        in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD)
    ]
    if len(parameters) != 1:
        raise TypeError(
            f"Handler for {command_type.__name__} must accept exactly one "
            f"positional argument (the command), got {len(parameters)}"
        )


@dataclass(frozen=True)
class BusConfig:
    """Immutable configuration for a :class:`CommandBus`.

    Currently a placeholder to keep the public API stable as the bus
    evolves (e.g. adding async dispatch or middleware later).
    """

    preload_global_handlers: bool = True
