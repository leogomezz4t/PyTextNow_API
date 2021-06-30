"""
Start integrating state management
"""
from copy import deepcopy
from queue import Queue
from functools import wraps
from .workers import ThreadManager


class EventManager(object):
    """
    Manage sending events to ThreadManager or wherever

    Starts event dispatcher on instantiation
    """
    def __init__(self, max_threads=5, start_dispatcher=True) -> None:
        self.__threads = ThreadManager(max_threads)
        self.__working = True
        # Max of 10 tasks can be queued by default, if more gets pushed raise a StackOverflowError
        # because it shouldn't take that long to finish the existing threads
        self.__event_queue = []
        self.__registered_events = {}
        self.__registered_callbacks = {}
        self.__default_callback_info = {
                'func': None,
                'args': None,
                'kwargs': None,
                'assigned_to': None
            }
        if start_dispatcher:
            self.__threads.start_thread('event_dispatcher')



    def start(self, event_name):
        """
        Send a signal
        """
        if len(self.__event_queue) >= self.__max_q_size:
            raise Exception(
                f"The event {event_name} attempted to fire but the event "
                "queue is full! Please increase the maximum size or "
                "modify the execution flow of the program!"
            )
        self.__event_queue.append(event_name)

# Decorators

    def register_target(self, name=None):
        """
        Register a function as a thread target to be started when
        the event(s) it's bound to executes
        """
        def wrap(func):
            def wrapper(*args, **kwargs):
                self.__threads._register(func, name, *args, **kwargs)
                return func
            return wrapper
        return wrap

    def register_event(self, fire=False, name=None, target={}):
        """
        Register a function as an event and listen for its
        signal. Don't execute on function call and return an
        unchanged function
        """
        def wrap(func):
            def decorated(*args, **kwargs):
                event_name = func.func_name
                if name:
                    event_name = name
                self.__registered_events[event_name] = {
                    'func': func,
                    'args': args,
                    'kwargs': kwargs,
                    'target': {
                        'func': target['func'],
                        'args': target['args'],
                        'kwargs': target['kwargs'],
                        'callback': target['callback']
                    }
                }
                if fire:
                    if len(target) == 0:
                        raise Exception("The target dictionary of an event cannot be empty!")
                    
                    self.__add_to_queue(self.__registered_events[event_name])
                return func
            return decorated
        return wrap

    def register_callback(self, name=None):
        """
        Decorator to indicate that the decorated function is for
        on_exit purposes. if provided a for_event arg, the decorated
        function will be called when the thread finishes.
        """
        def decorated(func):
            def wrapped(*args, **kwargs):
                callback_name = func.func_name
                if name:
                    callback_name = name
                self.__registered_callbacks[callback_name] = self.__default_callback_info.copy()
                return func
            return wrapped
        return decorated

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
                f"{callback_name} with the decorator or use the managers method and try again!"
            )

    def __get_event_bound_callback(self, event_name):
        for callback_name, info in self.__registered_callbacks.items():
            if info.get('assigned_to') == event_name:
                return callback_name
        raise Exception(f"Failed to get callback bound to event {event_name}")

    def register_target(self, func, target_name, *args, **kwargs):
        """

        Tell the thread manager to register a function for use
        as the target of a thread when the event it's bound to
        is fired. This is required to run custom functions in the
        background. If not registered you get an Exception

        ANYTHING bound with this will become the target
        of a thread/will be able to be used in a direct call to
        EventManager.emit('name of the method you bound or the name you passed')
        """ 
        pass

    def bind_target_to_event(self, func, name=None, *args, **kwargs):
        """
        Allow function decoration to register the function as a thread
        target
        """
        pass

    def await_results(self, event_name):
        return self.__threads.await_results(event_name)

    def event_dispatcher(self):
        """
        Dispatch the events
        """
        while self.__working:
            # Prevent race conditions by deep copying
            # the queue list and its dictionaries
            q_copy = deepcopy(self.__event_queue)
            q_has_events = True if len(q_copy) > 0 else False
            # Continue trying to start threads until
            # some are available
            if not self.__working:
                if (
                        not self.__finish_before_stop
                        or not q_has_events
                    ):
                    break
            if q_has_events:
                # Make it first in first out by iterating
                # backwards
                for event_index in range(
                        len(q_copy) - 1,
                        -1, -1, -1
                    ):
                    if not self.__threads._all_threads_used():
                        event_name = q_copy[event_index]['name']
                        self.__threads._start_thread(
                            q_copy[event_index]
                        )
                        # Ensure we delete the right event in case the list
                        # was updated before getting here
                        self.__remove_from_queue(event_name)

    def __remove_from_queue(self, event_name):
        for event_idx in range(len(self.__event_queue)-1):
            if self.__event_queue['name'] == event_name:
                del self.__event_queue[event_idx]

    def __get_event_idx(self, event_name):
        for event_idx in range(len(self.__event_queue)-1):
            if self.__event_queue['name'] == event_name:
                return event_idx

    def __add_to_queue(self, event_name, event_dict):
        """
        Add an event dictionary to the queue
        """
        # Is registered event?
        if event_dict['name'] not in list(self.__registered_events.keys()):
            raise Exception(
                f"Cannot add event {event_dict['name']} to queue "
                f"because {event_dict['name']} is not a registered event. "
                f"Register {event_dict['name']} as an event and try again!"
            )
        # Add
        self.__event_queue.append(event_dict)
