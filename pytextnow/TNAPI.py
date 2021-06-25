from pytextnow.TN_objects.user import User
from pytextnow.database.db import DatabaseHandler
from pytextnow.tools.utils import login
from pytextnow.tools.constants import *
from pytextnow.TN_objects.error import FailedRequest, AuthError, InvalidEvent
from pytextnow.TN_objects.multi_media_message import MultiMediaMessage
from pytextnow.TN_objects.message import Message
from pytextnow.TN_objects.container import Container
from pytextnow.TN_objects.contact import Contact
import mimetypes
import requests
from datetime import datetime, time
import datetime as dt

import json
from os.path import realpath, dirname, join
import time
import atexit


class Client:
    def __init__(
        # Make username required so sids are saved to db properly
            self, username,
            cookie=None, schema: str = None,
            db_name="text_nowAPI.sqlite3"
        ):
        # Automatically creates database and tables.
        # Give a schema to have a custom db layout
        # Give a db_name to name the db what you want
        self.db_handler = DatabaseHandler()
        self.__user = User(
            username=username,
            sid=self.db_handler.get_user(username).sid or self.__login(username)
        )
        self.cookies = {
            'connect.sid': self.__user.sid
        }
        self.allowed_events = ["message"]
        self.events = []
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.104 Safari/537.36 '
        }
        self.session = requests.session()
        atexit.register(self.on_exit)

    # Functions
    def on_exit(self):
        if len(self.events) == 0:
            return

        while 1:
            for event, func in self.events:
                if event == "message":
                    unread_msgs = self.get_unread_messages()
                    for msg in unread_msgs:
                        msg.mark_as_read()
                        func(msg)

    def auth_reset(self, sid=None, auto_rotate=False, method=None):
        """
        If auto rotating, print out something to show that it changed

        :optional param sid: String of the connect.sid cookie
        :optional param auto_rotate: Indicates if auto rotating user sid
        :optional param method: The method we're auto rotating from
        """
        if auto_rotate:
            print(
                "\nconnect.sid for user", self.__user.username,
                "has changed!\nOld sid:", self.__user.sid,
                "\nNew sid:", sid,
                f"\nLocation: TNAPI.py -> Client -> {method}"
            )
        if sid:
            updated_user = self.db_handler.update_user(
                self.__user.id, {'sid': sid}
            # If the user doesn't exist in the db. Possibly catches obscure SymaticError
            ) or self.__login(self.__user.username)
        else:
            updated_user = None
        if not updated_user:
            print("\n\nYou don't seem to have logged in before. Please do so now...\n\n")
            # Give time to notice what what printed
            time.sleep(1.3)
            self.__user = self.__login(self.user.username)
        self.cookies['connect.sid'] = self.__user.sid
        print("User sid successfully updated and cookie is set. Returning...")
        self.__user = updated_user
        return

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
                Message(msg, self)\
                if msg["type"] == MESSAGE_TYPE\
                else MultiMediaMessage(msg, self)\
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
                "https://www.textnow.com/api/users/" + self.username + f"/messages?contact_value={contact.number}&start_message_id=99999999999999&direction=past&page_size=200&get_archived=1",
                headers=self.headers, cookies=self.cookies)
            # Change user sid if it's changed
            new_sid = req.cookies['connect.sid']
            if new_sid != self.__user.sid:
                self.auth_reset(sid=new_sid, auto_rotate=True, method="get_raw_messages() After GET request")
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
            self.auth_reset(sid=cookie_sid, auto_rotate=True, method="send_mms() After GET request")


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
                file_req_sid = place_file_req.cookies['connect.sid']
                # Refresh the page after sending (Possibly not needed)
                self.session.get(place_file_req.url)
                if file_req_sid != self.__user.sid:
                    self.auth_reset(sid=file_req_sid, auto_rotate=True, method="send_mms() After PUT request")

                if str(place_file_req.status_code).startswith("2"):

                    json_data = {
                        "contact_value": to,
                        "contact_type": 2, "read": 1,
                        "message_direction": 2, "message_type": msg_type,
                        "from_name": self.username,
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
                'json': '{"contact_value":"' + to + '","contact_type":2,"message":"' + text + '","read":1,'
                                                                                              '"message_direction":2,'
                                                                                              '"message_type":1,'
                                                                                              '"from_name":"' +
                        self.username + '","has_video":false,"new":true,"date":"' + datetime.now().isoformat() + '"} '
            }

        response = self.session.post('https://www.textnow.com/api/users/' + self.username + '/messages',
                                     headers=self.headers, cookies=self.cookies, data=data)
        # Refresh after post
        self.session.get(response.url)
        # Check sid again
        new_sid = response.cookies['connect.sid']
        if new_sid != self._user_sid:
            self.auth_reset(sid=new_sid, auto_rotate=True, method="send_sms() After POST request")

        if not str(response.status_code).startswith("2"):
            self.request_handler(response.status_code)
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

    def request_handler(self, status_code: int):
        status_code = str(status_code)
        raise FailedRequest(status_code)


    def __login(self, username):
        """
        Wrap the call to login to save the sid/username
        to the database on login completion
        """
        sid = login()
        user = self.db_handler.user_exists(
                username=self.username, return_user=True
            ) or None
        if user:
            return self.db_handler.update_user({'id': user.id,'sid': sid})
        return self.db_handler.create_user({'username': username, 'sid': sid})