"""
Start integrating state management
"""
from queue import Queue
from functools import wraps
from .workers import ThreadManager


class EventManager(object):
    """
    Manage sending events to ThreadManager or wherever

    Starts event dispatcher on instantiation
    """

    def __init__(self, max_threads=None) -> None:
        self.threads = ThreadManager(max_threads)
        self.__working = True
        # Max size of 10, if more gets pushed raise a StackOverflowError
        # because it shouldn't take that long to finish the existing threads
        self.event_queue = Queue(maxsize=10)
        # Actual threads in thread manager to be started on event fire
        self.__event_threads = {}
        self.registered_events = {

        }
        self.registered_callbacks = {}

    def as_event(self, func, name=None, for_event=None, auto_start=False, *args, **kwargs):
        """
        Emit a signal to the ThreadManager to trigger
        a thread to start or be added to the queue
        if no available threads
        """

        @wraps(func)
        def wrap(func, name, *args, **kwargs):
            name = func.func_name if not name else name
            try:
                callback_info = kwargs.pop('callback')
                callback_info[name] = func
            except KeyError:
                callback_info = {"func": func}
            callback_info['assigned_to'] = None if not for_event else for_event
            if auto_start:
                self.emit_event(name)
            # callback info looks like this

        return wrap(
            func, name,
            for_event, auto_start,
            *args, **kwargs
        )

    def emit(self, event_name):
        """
        Send a signal
        """
        self.event_queue.put(event_name)

    def register_event(self, func, name=None, *args, **kwargs):
        """
        Register a function as an event and listen for its
        signal
        """

        @wraps(func)
        def decorated(func, name=None, *args, **kwargs):
            name = func.func_name if not name else name
            self.registered_events[name] = {
                'func': func,
                'args': args,
                'kwargs': kwargs
            }

        return decorated(func, name, *args, **kwargs)

    def register_callback(self, func, name=None, for_event=None, *args, **kwargs):
        """
        Decorator to indicate that the decorated function is for
        on_exit purposes. if provided a for_event arg, the decorated
        function will be called when the thread finishes.

        Pass 
        {
            "name": name you'll reference in @register_event,
            "for_event": thread_name,
        }

        :param callback_info: Dictionary of three elements. one is the
        """

        @wraps(func)
        def decorated(func, name=None, for_event=None, *args, **kwargs):
            name = func.func_name if not name else name
            try:
                callback_info = kwargs.pop('callback')
                callback_info[name] = func
            except KeyError:
                callback_info = {"func": func}
            callback_info['for_event'] = None if not for_event else for_event
            self.__registered_callbacks[name] = callback_info
            # callback info looks like this
            return func(*args, **kwargs)

        return decorated()

    def bind_callback(self, callback_name, event_name):
        """
        bind a callback to an event
        """
        try:
            self.registered_callbacks[callback_name]['assigned_to'] = event_name
        except KeyError:
            raise Exception(
                f"You attemmpted to bind {callback_name} to the event {event_name} "
                f"but {callback_name} is not a registered callback, please register "
                f"{callback_name} with the decorator or method and try again!"
            )

    def await_results(self, event_name):
        return self.threads.await_results(event_name)

    def event_dispatcher(self):
        """
        Dispatch the events
        """
        while self.__working:
            if not self.event_queue.empty():
                for event_name in self.event_queue:
                    self.threads.start_thread(event_name)

    def __starting_what(self, event_name, greeting=None):
        greeting = None if not greeting else f"Starting event...{event_name}"
        print("\n\ngreeting\n\n")

    def __enter__(self, *args, **kwargs):
        """
        Start doing things on instantiation
        """
        # for event in self.registered_events.items()
        # if current
        self.threads.start_thread('event_dispatcher')

    def __exit__(self, *args, **kwargs):
        """
        Perform a cleanup
        """
        pass

    @staticmethod
    def can_add_thread(self):
        pass
