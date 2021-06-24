"""
Holds all things to do with asynchronous database work
This can be useful if doing bulk updates on multiple tables
with a ridiculous amount of data
"""
import multiprocessing as async_work

class ThreadManager(object):
    """
    Manage all things threads
    """
    def __init__(self):
    # Assign each worker their own table to prevent
    # race conditions
        pass