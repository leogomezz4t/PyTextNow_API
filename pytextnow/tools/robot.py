
import random
import getpass
import typing
import threading
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver.v2 import ChromeOptions, Chrome

from pytextnow.database.db import DatabaseHandler
from pytextnow.TN_objects.user import User

class RoboBoi(object):

    def __init__(self, start_listening=True) -> None:
        self.__MINUTE = 60
        self.__HOUR = self.__MINUTE * 60
        self.__DAY = self.__HOUR * 24
        self.__ONE_HOUR = 60*60*60
        self.__start_time = time.time()
        self.__last_refresh = time.time
        self.__working = False
        self.__db_handler = DatabaseHandler()
        self.__driving = False
        self.__driver = self.configure()
        # Start the browser and keep it running
        threading.Thread(target=self.__drive(), daemon=True).start()
        self.__plz_wait = threading.Thread(
            target=self.__please_wait,
            daemon=True
        )
        self.__feedback_wait = False
    
    def __drive(self):
        with self.__driver:
            next_refresh = random.uniform(self.__ONE_HOUR, self.__DAY)
            # Leave chrome running to keep the sid from changing (Valid for a month from last refresh)
            while self.__driving:
                # Refresh the page every 1 to 24 hours
                if self.__time_on_page() > next_refresh:
                    next_refresh = random.uniform(self.__ONE_HOUR, self.__DAY)
                    self.__refresh()
        end = time.time() - self.__start_time / self.__MINUTE
        print("Closed browser...We've been driving the browser for {} minutes" % (end))

    def __configure(self):
        """
        Configure the chrome browser to run headless
        """
        options = ChromeOptions()
        options.headless = True
        options.add_argument('--headless')
        options.add_argument('--disable-extensions')
        # Might cause detection due to shader testing
        options.add_argument('--disable-gpu')
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
            # We must have been kicked off, log back in
            if not self.__driver.get_cookie('connect.sid').get('value', None):
                return self.get_sid(user, True)
        # No user was provided, make the user choose an account
        if not user:
            user = self.choose_account(user)
        self.working = True
        # Give feedback while we log in
        self.__plz_wait.start()
        self.__login(user)
        # Stop the feedback, we're done
        self.__working = False
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
        print(message)
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
            if not self.working:
                break
            # Tell them that we're still going every ten seconds
            if self.count % 20 == 0:
                print("\nStill Working...\n")
            count += 1
            # Don't bury the messages from the program
            time.sleep(0.5)
        print("\n\nDone!")
    
    def choose_account(self, accounts=[], assign_sid=False) -> User:
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
        # First check if the username and password are in the
        # database
        accounts = self.__db_handler.get_all_users() if len(accounts) == 0 else accounts
        # No user exists in the database
        if len(accounts) == 0:
            user = self.new_user()
        elif len(accounts) == 1:
            user = accounts[0]
        else:
            # Multiple users exist in the database, have the user choose one
            print(
                "\n\nPlease enter the number associated with the account you'd like to use.\n"
            )
            time.sleep(0.5)
            for idx in range(len(accounts)):
                print("\n",idx, ":", accounts[idx].username,"\n")
            chosen_idx = input("\n\nEnter the number next to your desired account: ")
            try:
                user = accounts[chosen_idx]
            except IndexError:
                print("\nInvalid Entry!\nPlease enter a number from the list of accounts\n")
                return self.choose_account(accounts, assign_sid=assign_sid)
        if assign_sid:
            # Choosing an account always means login, right?
            user.sid = self.get_sid(user, from_login=True)
        return user

    def new_user(
            self, username=None,
            password=None, return_mapped=True
        ) -> typing.Union[User, None]:
        """
        Get the login credentials from the user and update the database to
        have the new account credentials. If instructed to, return an object
        of the information entered in the database.
        """
        # We may require input. 'Pause' the thread so it's not buried
        self.__feedback_wait = True
        if not username:
            username = input("Please enter your username: ")
        # Don't print what they enter to the console
        if not password:
            password = getpass.getpass("Please enter your password: ")
        if len(password) or len(username) == 0:
            filled_field = username if len(username) > 0 else password
            print("Please fill both fields...\n\n")
            return self.new_user(filled_field)
        # Resume the feedback thread
        self.__feedback_wait = False
        return DatabaseHandler().\
            create_user({
                'username': username,
                "password": password
            }, return_mapped=return_mapped)


    def __sleep(self, lower_limit=0.01, upper_limit=1.0):
        time.sleep(random.uniform(lower_limit, upper_limit))

    def __login(self, user):
        """
        Log in to Text Now
        """
        def __sucessful_login():
            """
            Make sure we're logged in by looking for the phone number
            element that only shows up after a successful login.

            Also, if the user doesn't already have it, take that number
            and assign it to their user instance and update it in the database
            """
            # wait until either the phoneNumber or txt-username tag is loaded
            WebDriverWait(self.__driver, 0.1).until(
                lambda elem: elem.find_elements_by_class_name("phoneNumber") or elem.find_elements_by_id("txt-username")
            )
            not_logged_in = self.__driver.find_elements_by_id("txt-username")
            logged_in = self.__driver.find_elements_by_class_name("phoneNumber")
            if not_logged_in:
                return False
            elif logged_in:
                return len(logged_in) > 0
            # It's unlikely but possible we end up on an unexpected page (Like a "you're banned" screen)
            else:
                self.__driver.save_screenshot("UnexpectedPage.png")
                raise Exception("!!WARNING: RoboBoi ended on an unexpected page!!!")

        self.__driver.get('https://textnow.com/login')
        username_field = self.__driver.find_element_by_id('txt-username')
        password_field = self.__driver.find_element_by_id('txt-password')
        username_field.send_keys(user.username)
        self.__sleep(0.05, 0.2)
        password_field.send_keys(user.password)
        self.__sleep(0.05, 0.3)
        self.__driver.find_element_by_id('btn-login').click()
        self.__sleep(0.05, 0.2)
        if __sucessful_login():
            return
        print("\n\n!!!WARNING: Failed to login!!!\n\n")
        time.sleep(1)
        try:
            return self.__driver.save_screenshot("LastSeen.png")
        except Exception as e:
            raise Exception(
                "\n\nI tried to make it graceful but the package said no.\n"
                "An exception occured: Most likely because self.__driver has no attribute save_screenshot\n\n"
                "ERROR: %s" % (e)
            )

    def get_page(self, url):
        """
        Get the page and fill self.__last_reload
        """
        self.__last_refresh = time.time()
        return self.__driver.get(url)

    def __refresh(self):
        self.__last_refresh = time.time()
        return self.__driver.refresh()

    @property
    def uptime(self):
        return time.time()

    def time_on_page(self):
        return time.time() - self.__last_refresh