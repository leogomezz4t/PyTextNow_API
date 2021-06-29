import threading
import time
import typing


# Why would you run this for hours unless you made a desktop app
# In Minutes < 60 seconds times 60 minutes >
class ThreadManager(object):
    """
    Communicate things between threads

    If using a function not provided by this manager,
    pass your function with its args in a tuple to ThreadManager.to_async()
    If you want the thread to start, pass start=True.
    After the initial call to to_async() you can instead call ThreadManager.start_thread(thread_name)
    as this manager will store any methods not already stored for use in threads.

    TODO: Create StateMachineMixins that will take the place of the dictionaries
    of states. Then make a BaseManager object this class will subclass then
    make a Worker object that will take care of the thread states
    BaseManager will have shared attributes and be used mainly for event loops.

    TODO: Add database functionality to make this 'remember' methods that it doesn't
    have by default. If we get an exception when we try to call the method, that either
    means it's gone or 

    TODO: Add signal kill for individual threads. Accomplished by using something like a uuid1 assigned
    to thread names in a dictionary and we have a list of threads to be terminated. Do a simple check
    if thread_name in self.must_terminate: break
    """

    def __init__(
            self, max_threads=5,
    ) -> None:
        # Give the manager its own connection to the database
        # This will NOT recreate nor effect the existing tables/db
        # created by client instantiation. only a seperate connection
        # Used for the @on decorator
        # Management
        # Basically a sigkill for all responsive threads
        self.__stop = False
        # Tell all threads to wait
        self.__wait = False
        # The thread, if any, that won't stop working if a wait is started
        self.__wont_wait = None
        # Which threads are currently wanting everyone to wait
        self.__requesting_waits = []
        self.__max_threads = max_threads
        # Example of self.__thread_results contents
        # self.__thread_results = {
        #       table_exists: {
        #           started_at: perf_counter object
        #           ended_at: perf_counter object
        #           completed_in: 160, <-- MiliSeconds
        #           result: True,
        #           args: (table_name,)
        #       },
        #       sms_sent: {
        #           completed_in: 5264,
        #           result: None or Message(),
        #           args: ('contacts', updated_contact_list),
        #       }
        #   }
        self.__thread_results = {}
        self.default_jobs = {
            'initial_check': self.initial_db_check,
            'check_and_update': self.check_and_update,
            'please_wait': self.please_wait
        }
        self.__registered_threads = {
            'sms_sent': "Corresponding database function thread (uncalled)",
            'sms_received': "Corresponding database function thread (uncalled)",
            'sms_deleted': "Corresponding database function thread (uncalled)",

            'mms_sent': "Corresponding database function thread (uncalled)",
            'mms_received': "Corresponding database function thread (uncalled)",
            'mms_deleted': "Corresponding database function thread (uncalled)",

            'user_updated': "Corresponding database function thread (uncalled)",
            'user_created': "Corresponding database function thread (uncalled)",
            'user_deleted': "Corresponding database function thread (uncalled)",

            'contact_created': "Corresponding database function thread (uncalled)",
            'contact_deleted': "Corresponding database function thread (uncalled)",
            'contact_updated': "Corresponding database function thread (uncalled)",
        }
        self.__active_threads = []
        self.__inactive_threads = {}
        # Store what the threads were doing, their args,
        # where they were in their operation etc.
        # on wait request to release resources
        self.__default_thread_state = {
            "started_at": time.perf_counter,
            "ended_at": time.perf_counter,
            "completed_in": 0.0,
            "exit_callback": {
                # uncalled function
                'func': "",
                'args': ""
            }
        }

        self.__registered_callbacks = {}
        self.__thread_states = {}
        # Match event names with the threads they start

        self.__setup()

    # Management

    def __setup(self):
        self.__set_thread_states()

    def start_thread(self, thread_name, callback_info=None):
        """
        Start an existing thread
        """
        if len(self.__active_threads) >= len(self.__max_threads):
            # Add thread to queue, no threads currently available
            return self.__add_to_queue(thread_name)

        #########################################
        # Change this to allow easier access to #
        # create your own event threads         #
        #########################################
        # Mainly to ensure all events are properly registered and paired to
        # their respective threads
        if thread_name not in self.__event_threads:
            raise Exception(
                f"{thread_name} tried to start a thread but is not a registered event thread. "
                f"Please register {thread_name} with the ThreadManager and try again"
            )
        # Got an unrecognized thread target. add it to the thread states
        # This can happen if something is registered but not hard coded in
        # __thread_states
        if thread_name not in self.__thread_states.keys():
            self.__thread_states[thread_name] = self.__default_thread_state.copy()
        # Add if to the event threads

        print("Attempting to Start Thread:", thread_name)
        if thread_name in self.__active_threads:
            print(
                "\n\n!!!WARNING!!!\nA thread named {thread_name} attempted to start "
                "but was already started. Please check your callbacks and any "
                "calls to 'to_async', 'as_async' or 'start_thread' to make sure "
                "you're not starting the same thread more than once before it has "
                "a chance to finish."
            )
            return
        self.__active_threads.append(thread_name)

        desired_thread = self.__inactive_threads.pop(thread_name)
        self.__thread_states[thread_name]['started_at'] = \
            self.__thread_states[thread_name]['started_at']()
        started_thread = desired_thread.start()

        self.__thread_results[thread_name] = started_thread.results

    def __add_to_queue(self, thread_name):
        """
        Add a thread to the queue if there are no available
        threads left
        """
        # FIFO
        self.__waiting_threads.append(thread_name)

    def request_wait(self, requester_name, release_resources=False):
        """
        Request a wait.
        :param requester_name: The name of the thread requesting a wait
        """
        if release_resources:
            raise NotImplementedError("Releasing resources and storing state is not yet implemented!")
        if not self.wait:
            self.wait = True
            self.__wont_wait = requester_name
            return
        self.__requesting_waits.append(requester_name)

    def stop(self):
        """
        Stop all threads
        """
        if not self.__stop:
            self.__stop = True

    def on_exit(self, thread_name):
        """
        Do something on job finish
        """
        thread_state = self.__thread_states[thread_name]
        thread = self.__active_threads.pop(thread_name)
        self.__set_completed_in(thread_name)
        args = thread_state.get('args')
        return thread_state.get('func')(args)

    # Thread Targets

    def initial_db_check(self, schema):
        """
        Check the database to see if there are any records
        if not, start some threads to get and insert records into the datbase
        """
        pass

    def check_and_update(
            self, table_name, objects_or_data: typing.Union[typing.Any, typing.Dict[str, str]]
    ) -> None:
        """
        Check if all objects (or the first N) are in the database already
        if not, update the table
        """

        pass

    def please_wait(self, message="Please Wait"):
        """
        For a long running process or to be run during
        sigkill (KeyBoardInterrupt) while threads are being killed
        """
        last_dot_amount = 0
        min_dots = 0
        max_dots = 25
        going_down = False
        going_up = True
        print(message)
        while self.working:
            if last_dot_amount % 5 == 0:
                print("Phew, this is taking a while eh?\n\nWe're still going though...")
            # Are we going up or down?
            if last_dot_amount >= max_dots:
                going_down = True
                going_up = False
            elif last_dot_amount <= min_dots:
                going_down = False
                going_up = True
            # Actually go up or down
            if going_down:
                print("." * last_dot_amount)
                last_dot_amount -= 1
            elif going_up:
                print("." * last_dot_amount)
                last_dot_amount += 1
            if not self.working:
                break
            # Don't bury the messages from the program
            time.sleep(0.5)
        return None

    # Utilities
    def set_completed_in(self, thread_name):
        """
        Get the time it took to finish the thread
        """
        thread_info = self.__thread_states.get(thread_name)
        started_at = thread_info['started_at']
        completion_counter = thread_info['ended_at']()
        # Modify the original
        thread_info['completed_in'] = started_at - completion_counter

    def get_result(self, thread_name):
        """
        Get the result of the thread name,
        """
        return self.__thread_results.get(thread_name)()

    def await_results(self, thread_name):
        waiting = True
        while waiting:
            result = self.__thread_results.get(thread_name)()
            if result:
                return result

    def calculate_worker_count(self):
        """
        Figure out how many threads we can use without slowing the pc down
        """
        return 5

    @staticmethod
    def to_async(self, func, name=None, for_event=None, start=False, *args, **kwargs):
        """
        Start an asynchronous task, whatever the function
        """
        name = None if not name else name
        # Create thread
        new_thread = threading.Thread(target=func, args=args, name=name, daemon=True)
        # Register with thread states
        self.__thread_states[name] = self.__default_thread_state.copy()
        # Register the thread with events
        if for_event:
            self.__event_threads[name] = new_thread
        # Start if required
        if start:
            print("Starting Job: ", func.func_name)
            self.active_jobs.append(new_thread.name)
            new_thread.start()

        else:
            self.__inactive_threads[func.func_name] = new_thread

    def as_async(self, func, *args, **kwargs):
        def __to_async(func, *args, **kwargs):
            self.to_async(func, start=False, *args, **kwargs)
            return func

        return __to_async(func, *args, **kwargs)

    def get_active_thread_index(self, thread_name):
        # Assign the thread name to its index in case we need n
        for index in range(len(self.active_jobs)):
            if self.active_jobs[index] == thread_name:
                return index
        raise Exception(f"No active job found with thread name {thread_name}")

    def has_active(self):
        return len(self.__active_threads) > 0

    def __set_thread_states(self, threads=None):
        if not threads:
            threads = self.__inactive_threads.copy()
        for thread_name in threads.keys():
            self.__thread_states[thread_name] = self.default_thread_state.copy()

    def stop_thread(self, thread_name):
        del self.__active_threads[self.get_active_thread_index(thread_name)]
        self.__thread_states.get(thread_name)['running'] = False

    def still_running(self, thread_name):
        """
        Return True if a thread is still running, return the time it's been running
        if running_time is longer than wait time with no end time, stop thread,
        request a wait, warn about unresponsive thread, try to give hints, resume
        running after a three second wait
        """
        if self.get_active_thread_index(thread_name):
            pass
