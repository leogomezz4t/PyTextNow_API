import time
from datetime import time as dt

from pytextnow.TN_objects.API import ApiHandler
from pytextnow.database.db import DatabaseHandler
from pytextnow.tools.constants import *
from pytextnow.tools.robot import RoboBoi

class CellPhone:
    """
    TODO: Completely move all technical settings to config.py
    Interaction object; Responsible for being the main process
    that controls the database handlers, EventListeners, etc.
    """
    # Allow empty username for choosing which account to use
    def __init__(
            self, username: str = None,
            schema: str = None,
            db_name: str = None,
            debug: bool = False,
            # Enable dev tools
            low_level: bool = False,
            stay_alive: bool = True
        ):
        print("\n\nCreating DatabaseHandler Instance\n\n")
        self.__await_result_timeout = 30
        self.stay_alive = stay_alive
        self.__db_handler = DatabaseHandler(
                schema=schema, db_name=db_name,
                main_handler=True
            )
        # Start event loop
        print("\n\nCreating RoboBoi Instance...\n\n")
        self.__robo_boi = RoboBoi(start=False)
        self.__user = self.__get_user_object(username)
        self.__api_handler = ApiHandler(self.__user)
        self.text_tone = ""
        if stay_alive:
            self.__robo_boi.start()
            #self.start_listening()

    def __get_user_object(self, username):
        user = None
        if username:
            # Try to get the user with the DB Handler
            # This will be None if the user is not found.
            user = self.__db_handler.get_user(self.__user.username)
            # Always get the sid from the login on startup
            user.sid = self.__robo_boi.get_sid(user, True)
        if not user:
            # Have the user choose an account. Log in and assign the sid
            user = self.__robo_boi.choose_account(assign_sid=True)
        return user

    def __reset_sid(self, sid=None, auto_rotating=False, method=None):
        """
        Get the new SID for the user and set user.sid to the new value

        If auto rotating, print out something to show that it changed

        :Args:
            - sid: The value of the connect.sid cookie
            - auto_rotating: If Client noticed an SID change after hitting
                the API, this will be True
            - method: If auto rotating, this will be the method calling
                '__reset_sid' to be used in a debug print. If not auto
                rotating, this should be None

        :Returns:
            None
        """
        # If coming from the API
        if auto_rotating:
            print(
                "\nconnect.sid for user", self.__user.username,
                "has changed!\nOld sid:", self.__user.sid,
                "\nNew sid:", sid,
                f"\nLocation: TNAPI.py -> Client -> {method}"
            )
            self.__user.sid = sid
            # We already have the sid, don't return it
            return
        # No sid was provided, let the robot get it
        self.__user.sid = self.__robo_boi.get_sid(self.__user)
        return None

    def await_result(self, func_name, fail_silently=False):
        result = self.__api_handler.results.get(func_name, None)
        if not result:
            # Threading could have changed the value. check again
            result = self.__api_handler.results.get(func_name, None)
            # Ensure we don't go passed the timeout
            start = time.time()
            while not result:
                result = self._api_handler.results.get(func_name, None)
                if result:
                    return result
                if time.time() - start >= self.__await_result_timeout:
                    if not fail_silently:
                        raise Exception(
                            "\n\nCellPhone timed out while waiting for the ApiHandler to "
                            "finish executing '%s'.\n\n!!!Make sure your internet is connected!!!\n"
                            "If your internet is slow, you may have to raise the timeout limit!" 
                        )
                    else:
                        print(
                            "\n\n!!!WARNING!!! CellPhone timed out while "
                            + "awaiting the result of %s" % (func_name)
                        )

    def send_sms(self, number, text):
        self.__api_handler.send_sms(number, text)

    def send_mms(self, number, file):
        self.__api_handler.send_mms(number, file)
