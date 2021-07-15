
import random
import getpass
import typing
import threading
import time
from undetected_chromedriver.v2 import ChromeOptions, Chrome

from pytextnow.database.db import DatabaseHandler
from pytextnow.TN_objects.user import User
from pytextnow.server.app import Listener
from pytextnow.tools.constants import *
import pytextnow.settings

class RoboBoi(object):

    def __init__(self, proxy=None, start=True) -> None:
        self.__proxy = proxy
        # What table needs updated
        self.to_be_updated = []
        self.__server = None
        self.__wait_thread_running = False
        self.__wait_msg = "Please wait..."
        self.__debug = settings.DEBUG

        self.__start_time = time.time()
        self.__last_refresh = 0
        self.__working = False
        print("\n\nCreating DatabaseHandler for RoboBoi...\n\n")
        self.__db_handler = DatabaseHandler(main_handler=False)
        self.__driving = False
        self.__driver = self.__configure()
        self.__r_lock = threading.RLock()
        # Start the browser and keep it running
        self.__feedback_wait = False
        # Not using it, don't waste the resources
        #self.__plz_wait = threading.Thread(
         #   target=self.__please_wait,
          #  daemon=True
        #)
        if start:
            self.start()
    
    def start(self):
        # Start the thread to keep chrome open
        threading.Thread(target=self.__drive, daemon=True).start()
        # Start the server thread
        self.__server = Listener()
        self.__server.start()

    def __drive(self):
        self.__driving = True
        print("\n\nStarting to drive the robot...")
        with self.__driver:
            next_refresh = random.uniform(settings.REFRESH_INTERVALS['lower'], settings.REFRESH_INTERVALS['upper'])
            # Leave chrome running to keep the sid from changing (Valid for a month from last refresh)
            while self.__driving:
                try:
                    # Refresh the page every 1 to 24 hours
                    if self.__time_on_page() > next_refresh:
                        next_refresh = random.uniform(self.__ONE_HOUR, self.__DAY)
                        self.__refresh()
                except:
                    print("The Driver Experienced and exception some how...")
                    break
                # Check for new things
                with self.__r_lock:
                    new = self.__server.get_new()
                    if len(new) > 0:
                        if len(self.to_be_updated) > 0:
                            print(
                                "\n\n!!!WARNING!!!\n\n You have not cleared the 'RoboBoi.to_be_updated"
                                " list. Be sure you pay attention to execution order. This may get hard to debug!"
                            )
                        # Check for new things
                        self.to_be_updated = new
        end = time.time() - self.__start_time / self.__MINUTE
        self.__sigkill()
        print("Closed browser...We've been driving the browser for {} minutes" % (str(end)))

    def get_new(self):
        with self.__r_lock:
            must_update = self.to_be_updated.copy()
            self.to_be_updated.clear()
            return must_update

    def __configure(self):
        """
        Configure the chrome browser to run headless as well as a few performance
        and stealth options.

        TODO: Integrate user agent switching and total browser Anonymity
        """
        options = ChromeOptions()
       # Don't run headless if in debug mode
        if not self.__debug:
            options.add_argument('--headless')
            # Might cause detection due to shader testing
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-permissions-bubbles')
            options.add_argument("--disable-save-password-bubbles")
            options.add_argument('--disable-session-crashed-bubble')
            # Run in guest mode (No addons, sync, bookmarks, etc.)
            options.add_argument("--bwsi")
            #options.add_argument('--incognito')
        if self.__proxy:
            options.add_argument("--proxy-server=%s" % self.__proxy)
        options.add_argument('--disable-extensions')

        return Chrome(options=options)
    
    def get_sid(self, user=None, from_login=True) -> str:
        """
        :Args:
            - user: The user object representing who we're currently logged in as.
                Not only used to hold the sid but also to allow RoboBoi to
                autonomously log back in after having been logged out.
            - from_login: If True, RoboBoi will use the credentials in the user object
                or have you choose an account, then log in to Text Now to get the sid
        :Returns:
            The value of the connect.sid cookie in the currently open browser
        """
        if not from_login:
            sid = self.__driver.get_cookie('connect.sid')
            # We must have been kicked off, log back in
            if not sid:
                return self.get_sid(user, True)
            return sid
        # No user was provided, make the user choose an account
        if not user:
            user = self.choose_account()
        self.__wait_msg = "Please wait while we log in..."
        self.__login(user)
        return self.__driver.get_cookie('connect.sid').get('value')

    def __please_wait(self, message="Working...") -> None:
        """
        Give the user some feedback so they know the program is still running
        """
        count = 0
        last_dot_amount = 0
        min_dots = 0
        max_dots = 25
        going_down = False
        going_up = True
        print(self.__wait_msg)
        while self.__working:
            # Don't print anything so some output isn't buried
            if self.__feedback_wait:
                continue
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
            if not self.__working:
                break
            # Tell them that we're still going every ten seconds
            if self.count % 20 == 0:
                print("\nStill Working...\n")
            count += 1
            # Don't bury the messages from the program
            time.sleep(0.25)
        self.__wait_thread_running = False
        print("\n\nDone!")
    
    def choose_account(self, assign_sid=False) -> User:
        """
        Return a user object for logging in or general use in the program
        :Args:
            - accounts: The list of accounts (User objects) to choose from
            - assign_sid: If True log in to text now with the account credentials,
                then get the sid, assign it to the user and return the user object

        :Returns:
            User object. If assign_sid=False, user.sid will likely be None
        """
        user = None
        users = self.__db_handler.get_all_users()
        if len(users) == 0:
            user = self.new_user()
        # Don't get the user if we already have it
        if len(users) < 2 and len(users) > 0 and not user:
            return users[0]
        # Don't get the user if we already have it
        elif len(users) > 1 and not user:
            for user_idx in range(len(users)):
                print(user_idx, " : ", users[user_idx].username)
            chosen_idx = input("Enter the number next to an account: ")
            try:
                chosen_idx = int(chosen_idx)
                user = users[chosen_idx]
            except IndexError:
                return self.choose_account(assign_sid)
        # Get the sid if we need to
        if assign_sid:
            user.sid = self.get_sid(user)
        return user
        
    def new_user(
            self, username=None,
            password=None
        ) -> typing.Union[User, None]:
        """
        Get the login credentials from the user and update the database to
        have the new account credentials. If instructed to, return an object
        of the information entered in the database.
        """
        print("\n\n...Please Provide Login Credentials...\n")
        # We may require input. 'Pause' the thread so it's not buried
        self.__feedback_wait = True
        if not username:
            username = getpass.getpass("Please enter your username: ")
        # Don't print what they enter to the console
        if not password:
            password = getpass.getpass("Please enter your password: ")
        if len(username) == 0 or len(password) == 0:
            print("Please fill both fields...\n\n")
            return self.new_user(username, password)
        # Resume the feedback thread
        self.__feedback_wait = False
        existing = self.__db_handler.get_user(username)
        if not existing:
            self.__db_handler.\
                create_user({
                    'username': username,
                    "password": password,
                    "object_type": USER_TYPE
                    })
            user = self.__db_handler.get_user(username)
        return user

    def __login(self, user):
        """
        Log in to Text Now
        """
        print("\n\nInside login method:", user)
        def __sucessful_login():
            """
            Make sure we're logged in by looking for the phone number
            element that only shows up after a successful login.

            Also, if the user doesn't already have it, take that number
            and assign it to their user instance and update it in the database
            """
            loading = True
            logged_in = False
            print("\n\n...Waiting for successful login verification...\n\n")
            started = time.time()
            while loading:
                try:
                    number = self.__driver.find_element_by_class_name("phoneNumber")
                except:
                    number = None
                    if time.time() - started % 2 == 0:
                        print("\n...Still loading...\n")
                if number:
                    print("One of the elements loaded!\n\n", number,"\n\n")
                    loading = False
                    logged_in = True
                # Wait for the timeout
                if time.time() - started >= self.__timeout:
                    raise Exception("Timed out while waiting for a page to load. "
                                    "Raise the time out limit or try again."
                                    "Location: tools/robot.py -> RoboBoi -> __login() --> __successful_login()"
                                    )
            print("\n\n",self.__driver.current_url, "\n\n")
            if logged_in:
                return True
            self.__driver.save_screenshot("UnexpectedPage.png")
            raise Exception("!!!WARNING: RoboBoi ended on an unexpected page!!!")           

        self.get_page('https://textnow.com/login')
        self.__sleep(0.05, 0.2)
        username_field = self.__driver.find_element_by_id('txt-username')
        self.__sleep(0.05, 0.2)
        password_field = self.__driver.find_element_by_id('txt-password')
        self.__sleep(0.05, 0.2)
        username_field.send_keys(user.username)
        self.__sleep(0.05, 0.2)
        password_field.send_keys(user.password)
        self.__sleep(0.05, 0.3)
        self.__driver.find_element_by_id('btn-login').click()
        self.__sleep(0.05, 0.2)
        if __sucessful_login():
            self.__last_refresh = time.time()
            return
        print("\n\n!!!WARNING: Failed to login!!!\n\n")
        time.sleep(1)
        return self.__driver.save_screenshot("LastSeen.png")

    def get_page(self, url):
        """
        Get the page and fill self.__last_reload
        """
        self.__last_refresh = time.time()
        self.__driver.get(url)
        self.__driver.inject_script
        return 

    def __refresh(self):
        self.__last_refresh = time.time()
        return self.__driver.refresh()

    @property
    def uptime(self):
        return time.time() - self.__start_time

    def __time_on_page(self):
        """
        Get the time difference between the time this function is
        called and the last time the page was refreshed
        """
        return time.time() - self.__last_refresh

    def __sleep(self, lower_limit=0.01, upper_limit=1.0):
        time.sleep(random.uniform(lower_limit, upper_limit))

    def kill_driver(self):
        self.__driver.quit()

    def kill_listener(self):
        self.__server.stop()