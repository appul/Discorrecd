import logging
import types
from asyncio.coroutines import iscoroutinefunction
from collections import OrderedDict
from typing import Dict, Union, Any, Awaitable, Callable, List

log = logging.getLogger(__name__)

EventId = Union['Event', str]
CorFunc = Callable[[Any], Awaitable[Any]]
Handler = Union['EventHandler', CorFunc]


class EventManager(object):
    """Manager for :class:`Event` objects"""

    def __init__(self):
        self._events = {}  # type: Dict[str, 'Event']

    def __contains__(self, event: EventId) -> bool:
        return str(event) in self._events

    def __getitem__(self, key: EventId) -> 'Event':
        return self.get(key)

    def __iter__(self) -> 'Event':
        yield from self._events.values()

    def __len__(self) -> int:
        return len(self._events)

    def get(self, event: EventId, default: Any = None) -> 'Event':
        """Get an event from the manager.

        :param event: The name of the event
        :param default: The default return value if the event is not registered
        :return: The event or the default value
        """
        return self._events.get(str(event), default)

    async def emit(self, event: EventId, *args: Any, **kwargs: Any):
        """Emit an event and call its registered handlers.

        :param event: The event or name of the event to be added
        :param args: The positional arguments passed to the handlers
        :param kwargs: The keyword arguments passed to the handlers
        """
        await self.get(event).emit(*args, **kwargs)

    def add(self, event: EventId) -> 'Event':
        """Add a new or existing event to the event manager.

        If an existing event (:class:`Event`) is given, it will be added to the
        :class:`EventManager`. If the name (:class:`str`) of the event is given

        :param event: The event or name of the event to be added
        :return: The added event
        """
        if not isinstance(event, Event) and not isinstance(event, str):
            raise TypeError('Parameter \'event\' must be of type Event or str')

        if event in self:
            if isinstance(event, Event):
                raise DuplicateEventError('Event already exists and cannot be added again.')
            return self.get(event)

        self._events[str(event)] = event if isinstance(event, Event) else Event(event)
        return self.get(event)

    def add_handler(self, event: EventId, handler: Handler, call_limit: int = None) -> 'EventHandler':
        """Add a new or existing handler to a new or existing event.

        Add a new handler to the specified :class:`Event`.

        :param event: The event or name of the event to which the handler should be added
        :param handler: The handler
        :param call_limit: Optional limit on the amount of times the handler may be called
        :return: The :class:`EventHandler` object
        """
        if event not in self:
            raise EventNotFoundError(
                'Event \'{0}\' doesn\'t exist or hasn\'t been registered to this EventManager.'.format(event))
        return self.get(event).add(handler, call_limit)


class Event(object):
    """The event object that emits to :class:`EventHandler` objects"""

    def __init__(self, name: str):
        """

        :param name: The name of the event
        """
        self.name = name  # type: str
        self.enabled = True  # type: bool
        self._handlers = OrderedDict()  # type: OrderedDict[str, EventHandler]

    def __str__(self) -> str:
        return self.name

    def __contains__(self, handler: Handler) -> bool:
        return hash(handler) in self._handlers

    def __getitem__(self, handler: Handler) -> 'EventHandler':
        return self.get(handler)

    def __delitem__(self, handler: Handler):
        return self.remove(handler)

    def __iter__(self) -> 'EventHandler':
        yield from self._handlers.values()

    def __len__(self) -> int:
        return len(self._handlers)

    def __hash__(self) -> int:
        return hash(self.name)

    async def emit(self, *args: Any, **kwargs: Any):
        """Emit and call the handlers of the event.

        :param args: The positional arguments passed to the handlers
        :param kwargs: The keyword arguments passed to the handlers
        """
        if self.enabled and len(self):
            log.debug('Emitting event: {}'.format(self.name))
            for handler in self:
                await handler.call(*args, **kwargs)

    def get(self, handler: Handler, default: Any = None) -> 'EventHandler':
        """Get a :class:`EventHandler` object from the event.

        :param handler: The :class:`EventHandler` or method
        :param default: The default return value if the handler is not registered
        :return: The :class:`EventHandler` or the default value
        """
        return self._handlers.get(hash(handler), default)

    def add(self, handler: Handler, call_limit: int = None) -> 'EventHandler':
        """Add a handler to the event.

        :param handler: The :class:`EventHandler` or method
        :param call_limit: Optional limit on the amount of times the handler may be called
        :return: The :class:`EventHandler`
        """
        if not isinstance(handler, EventHandler) and not iscoroutinefunction(handler):
            raise TypeError('Parameter \'handler\' must be coroutine function or of type EventHandler')

        if handler not in self:
            if not isinstance(handler, EventHandler):
                handler = EventHandler(handler)
            self._handlers[hash(handler)] = handler

        self.get(handler).call_limit = call_limit
        return self.get(handler)

    def remove(self, handler: Handler):
        """Remove a handler from the event.

        :param handler: The :class:`EventHandler` or method
        """
        self._handlers[handler] = None

    def clear(self):
        """Remove all the handlers from the event."""
        self._handlers.clear()


class EventHandler(object):
    """The handler object that handles event calls and finally passes on the event arguments to the method"""

    def __init__(self, method: CorFunc, call_limit: int = None):
        self._method = None  # type: CorFunc
        self._enabled = True  # type: bool
        self.call_limit = call_limit  # type: int

        self.method = method  # type: CorFunc

    def __hash__(self) -> int:
        """Get a hash by hashing the handler."""
        return hash(self._method)

    async def call(self, *args: Any, **kwargs: Any) -> Any:
        """Call the handler.

        :param args: The positional arguments passed to the method
        :param kwargs: The keyword arguments passed to the method
        """
        if self.enabled:
            if self.call_limit:
                self.call_limit -= 1
            return await self._method(*args, **kwargs)
        return None

    def limit(self, limit: int = 1):
        """Set a limit for the amount of times this handler may be called.

        :param limit: The amount of times
        """
        self.call_limit = int(limit)

    @property
    def enabled(self) -> bool:
        """Enabled status."""
        return self._enabled and (self.call_limit is None or self.call_limit > 0)

    @enabled.setter
    def enabled(self, enabled: bool):
        if not isinstance(enabled, bool):
            raise TypeError('expected bool '
                            'for enabled, got {0}'.format(type(enabled)))
        self._enabled = enabled

    @property
    def method(self) -> CorFunc:
        """The method of the handler that's called."""
        return self._method

    @method.setter
    def method(self, method: CorFunc):
        if not iscoroutinefunction(method):
            raise TypeError('Parameter \'handler\' must be a coroutine function')
        self._method = method


class EventMethod(object):
    """A decorator base class for event methods

    :cvar category: Indicates what category of events this handler belongs to.
        Implementations can use this indication to assign the handler to the correct
        :class:`EventManager`.
    """
    category = 'events'

    def __init__(self, events: List[str], call_limit: int = None, bind=True):
        """

        :param events: List of event names to which the method should be registered
        :param call_limit: Optional limit on the amount of times the handler may be called
        :param bind: Whether the method should be bound to the holding instance. If False,
            the method is used as an unbound method.
        """
        self.method = None  # type: CorFunc
        self.events = events  # type: List[str]
        self.call_limit = call_limit  # type: int
        self.bind = bind  # type: bool

    def __call__(self, method: CorFunc) -> 'EventMethod':
        """The decorator that takes the method

        :param method: The handler method
        """
        self.method = method
        return self

    def register(self, manager: EventManager, holder: object = None):
        """Register the method to the :class:`EventManager`

        :param manager: The manager to which the handler should be registered
        :param holder: The instance that holds the method if the method should be
            bound to the instance. The method is used as an unbound method if omitted
        """
        method = self._prepare_method(holder)
        for event in self.events:
            manager.add_handler(event, method)

    def _prepare_method(self, holder: object) -> CorFunc:
        """Binds the method if necessary and returns a method ready to be registered

        :param holder: An instance of the holding instance for binding the method if necessary"""
        if holder is not None and self.bind:
            return types.MethodType(self.method, holder)
        return self.method

    @classmethod
    def register_methods(cls, manager: EventManager, holder: object):
        """Registers all event methods of an object to the specified :class:`EventManager`

        All attributes matching this class are registered to the specified :class:`EventManager`


        :param manager: The manager to which the handlers should be registered
        :param holder: The instance that holds the methods if the methods should be
            bound to the instance. The methods are used as unbound methods if omitted
        """
        for name in dir(holder):
            obj = getattr(holder, name)
            log.debug(' | '.join(str(o) for o in [name, obj]))
            if isinstance(obj, cls):
                obj.register(manager, holder)


class EventNotFoundError(Exception):
    """Raised when an event cannot be found."""


class DuplicateEventError(Exception):
    """Raised when an event already exists"""
