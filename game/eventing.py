# -*- coding: utf-8 -*-
import logging
from types import MethodType as _MethodType
from weakref import ref as _ref
from weakref import WeakMethod as _WeakMethod

logger = logging.getLogger(__name__)
logger.debug("importing...")


class EventDispatcher:
    """
    For dispatching events. Based on the dispatcher build into the library 'esper'.
    """

    def __init__(self):
        self.event_registry: dict = {}

    def dispatch_event(self, name: str, *args) -> None:
        """Dispatch an event by name, with optional arguments.

        Any handlers set with the :py:func:`esper.set_handler` function
        will receive the event. If no handlers have been set, this
        function call will pass silently. The name will be passed
        as first argument, potentially followed by optional arguments.

        :note:: If optional arguments are provided, but set handlers
                do not account for them, it will likely result in a
                TypeError or other undefined crash.
        """
        for func in self.event_registry.get(name, []):
            func()(name, *args)

    def _make_callback(self, name: str):
        """Create an internal callback to remove dead handlers."""

        def callback(weak_method):
            self.event_registry[name].remove(weak_method)
            if not self.event_registry[name]:
                del self.event_registry[name]

        return callback

    def set_handler(self, name: str, func) -> None:
        """Register a function to handle the named event type.

        After registering a function (or method), it will receive all
        events that are dispatched by the specified name.

        :note:: Only a weak reference is kept to the passed function,
        """
        if name not in self.event_registry:
            self.event_registry[name] = set()

        if isinstance(func, _MethodType):
            self.event_registry[name].add(_WeakMethod(func, self._make_callback(name)))
        else:
            self.event_registry[name].add(_ref(func, self._make_callback(name)))

    def remove_handler(self, name: str, func) -> None:
        """Unregister a handler from receiving events of this name.

        If the passed function/method is not registered to
        receive the named event, or if the named event does
        not exist, this function call will pass silently.
        """
        if func not in self.event_registry.get(name, []):
            return

        self.event_registry[name].remove(func)
        if not self.event_registry[name]:
            del self.event_registry[name]


logger.debug("imported")
