import atexit
import datetime as dt
import json
import mimetypes
import time
from datetime import datetime, time

import requests

from TN_objects.contact import Contact
from TN_objects.container import Container
from TN_objects.error import FailedRequest, InvalidEvent
from TN_objects.message import Message
from TN_objects.multi_media_message import MultiMediaMessage
from database.db import DatabaseHandler
from tools.constants import *
from tools.robot import RoboBoi


class Client:
    # Allow empty username for choosing which account to use
    def __init__(
            self, username: str = None,
            schema: str = None,
            db_name: str = None,
            debug: bool = False
        ):
        print("\n\nCreating DatabaseHandler Instance\n\n")
        self.__db_handler = DatabaseHandler(
                schema=schema, db_name=db_name,
                main_handler=True
            )
        # Start event loop
        print("\n\nCreating RoboBoi Instance...\n\n")
        self.__robo_boi = RoboBoi()
        self.__user = self.__get_user_object(username)
        self.cookies = {
            'connect.sid': self.__user.sid
        }
        # At this point, is there any use for this?
        #self.allowed_events = self.events.registered_events
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.104 Safari/537.36 '
        }
        self.session = requests.session()
        #atexit.register(self.on_exit)

    def __get_user_object(self, username):
        user = None
        if username:
            # Try to get the user with the DB Handler
            # This will be None if the user is not found.
            user = self.__db_handler.get_user(self.__user.username)
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

    def get_raw_contacts(self):
        """
        Gets all textnow contacts

        TODO: Start worker to check if contacts are not in db
            if not, create them. Possibly even get the length of
            contacts, split the length between workers then start
            processes to get them all asynchronously (possible db lock error)
        """
        params = (
            ('page_size', '50'),
        )
        res = requests.get("https://www.textnow.com/api/v3/contacts", params=params, cookies=self.cookies)
        contacts = json.loads(res.text)
        return contacts["result"]

    def get_contacts(self):
        return Container(
            [Contact(contact, self) for contact in self.get_raw_contacts()]
        )

    def get_messages(self):
        """
            This gets most of the messages both sent and received. However It won't get all of them just the past 10-15
        """
        return Container(
            [
                Message(msg) if msg["type"] == MESSAGE_TYPE else MultiMediaMessage(msg)
                for msg in self.get_raw_messages()
            ]
        )

    def get_raw_messages(self):
        """
            This gets most of the messages both sent and received. It takes about 30 seconds though
        """
        all_messages = []
        # Loop contacts
        for contact in self.get_contacts():
            # Send get for 200 contacts per page
            req = self.session.get(
                "https://www.textnow.com/api/users/"
                + self.__user.username
                + f"/messages?contact_value="
                  f"{contact.number}&start_message_id=99999999999999&direction=past&page_size=200&get_archived=1",
                headers=self.headers, cookies=self.cookies)

            # Change user sid if it's changed
            new_sid = req.cookies['connect.sid']
            if new_sid != self.__user.sid:
                self.__reset_sid(sid=new_sid, auto_rotating=True, method="get_raw_messages() After GET request")
            if str(req.status_code).startswith("2"):
                messages = json.loads(req.content)
                all_messages.append(messages["messages"])
            else:
                self.request_handler(req.status_code)
        return all_messages

    def get_sent_messages(self):
        """
            This gets all the past 10-15 messages sent by your account
        """
        return Container(
            [msg for msg in self.get_messages() if msg.direction == SENT_MESSAGE_TYPE]
        )

    def get_received_messages(self):
        """
            Gets inbound messages
        """
        return Container(
            [msg for msg in self.get_messages() if msg.direction == RECEIVED_MESSAGE_TYPE]
        )

    def get_unread_messages(self):
        """
            Gets unread messages
        """
        return Container(
            [msg for msg in self.get_received_messages() if not msg.read]
        )

    def get_read_messages(self):
        """
            Gets read messages
        """
        return Container(
            [msg for msg in self.get_received_messages() if msg.read]
        )

    def send_mms(self, to, file):
        """
            This function sends a file/media to the number
        """
        mime_type = mimetypes.guess_type(file)[0]
        file_type = mime_type.split("/")[0]
        has_video = True if file_type == "video" else False
        msg_type = 2 if file_type == "image" else 4

        file_url_holder_req = self.session.get("https://www.textnow.com/api/v3/attachment_url?message_type=2",
                                               cookies=self.cookies, headers=self.headers)
        cookie_sid = file_url_holder_req.cookies["connect.sid"]
        # Reassign to new sid
        if cookie_sid != self.__user.sid:
            self.__reset_sid(sid=cookie_sid, auto_rotating=True, method="send_mms() After GET request")

        if str(file_url_holder_req.status_code).startswith("2"):
            file_url_holder = json.loads(file_url_holder_req.text)["result"]

            with open(file, mode="rb") as f:
                raw = f.read()

                headers_place_file = {
                    'accept': '*/*',
                    'content-type': mime_type,
                    'accept-language': 'en-US,en;q=0.9',
                    "mode": "cors",
                    "method": "PUT",
                    "credentials": 'omit'
                }

                place_file_req = self.session.put(file_url_holder, data=raw, headers=headers_place_file,
                                                  cookies=self.cookies)
                sid = place_file_req.cookies.get('connect.sid')
                
                # Refresh the page after sending (Possibly not needed)
                self.session.get(place_file_req.url)
                browser_sid = self.__robo_boi.get_sid(self.__user, False)
                if sid != self.__user.sid:
                    if sid != browser_sid:
                        sid = browser_sid
                    self.__reset_sid(sid=sid, auto_rotating=True,  method="send_mms() After PUT request")

                if str(place_file_req.status_code).startswith("2"):

                    json_data = {
                        "contact_value": to,
                        "contact_type": 2, "read": 1,
                        "message_direction": 2, "message_type": msg_type,
                        "from_name": self.__user.username,
                        "has_video": has_video,
                        "new": True,
                        "date": datetime.now().isoformat(),
                        "attachment_url": file_url_holder,
                        "media_type": file_type
                    }

                    send_file_req = self.session.post("https://www.textnow.com/api/v3/send_attachment", data=json_data,
                                                      headers=self.headers, cookies=self.cookies)
                    return send_file_req
                else:
                    self.request_handler(place_file_req.status_code)
        else:
            self.request_handler(file_url_holder_req.status_code)

    def send_sms(self, to, text):
        """
            Sends an sms text message to this number
        """
        data = \
            {
                'json': {
                    "contact_value": str(to),
                    "contact_type":2,
                    "message": str(text),
                    "read":1,
                    "message_direction":2,
                    "message_type":1,
                    "from_name": self.__user.username,
                    "has_video": False,
                    "new": True,
                    "date": datetime.now().isoformat()
                    }
            }
        print("\n\nSending text message to", to, "\n\n")
        response = self.session.post('https://www.textnow.com/api/users/' + self.__user.username + '/messages',
                                     headers=self.headers, cookies=self.cookies, json=data["json"])
        # Refresh after post
        self.session.get(response.url)
        # Check sid again
        browser_sid = self.__robo_boi.get_sid(self.__user, False)
        sid = response.cookies['connect.sid']
        if sid != self.__user.sid:
            sid = sid
            if sid != browser_sid:
                sid = browser_sid
            self.__reset_sid(sid=sid, auto_rotating=True, method="send_sms() After POST request")

        if not str(response.status_code).startswith("2"):
            self.request_handler(response.status_code)
        print("Response: ", json.dumps(response.json(), indent=4))
        return response

    def wait_for_response(self, number, timeout_bool=True):
        for msg in self.get_unread_messages():
            msg.mark_as_read()
        timeout = datetime.now() + dt.timedelta(minute=10)
        if not timeout_bool:
            while 1:
                unread_msgs = self.get_unread_messages()
                filtered = unread_msgs.get(number=number)
                if len(filtered) == 0:
                    time.sleep(0.2)
                    continue
                return filtered[0]

        else:
            while datetime.now() > timeout:
                unread_msgs = self.get_unread_messages()
                filtered = unread_msgs.get(number=number)
                if len(filtered) == 0:
                    time.sleep(0.2)
                    continue
                return filtered[0]

    def on(self, event: str):
        if event not in self.allowed_events:
            raise InvalidEvent(event)

        def deco(func):
            self.events.append([event, func])

        return deco

    @staticmethod
    def request_handler(status_code: int):
        raise FailedRequest(str(status_code))
