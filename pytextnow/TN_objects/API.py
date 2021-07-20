import requests
from copy import deepcopy
from datetime import datetime
import datetime as dt
import time
import json
from copy import deepcopy
from pytextnow.tools.utils import map_to_class
from pytextnow.database.db import DatabaseHandler
from urllib.parse import quote_plus
import mimetypes
"""
from pytextnow.TN_objects.error import (
    TNApiError,
    DatabaseHandlerError,
    NetworkError
)
"""
from pytextnow.TN_objects.user import User
from pytextnow.TN_objects.contact import Contact
from pytextnow.TN_objects.container import Container
from pytextnow.TN_objects.message import Message
from pytextnow.TN_objects.multi_media_message import MultiMediaMessage
from pytextnow.tools.constants import MESSAGE_TYPE
from pytextnow.TN_objects.account import Account

class URLBuilder:
    def __init__(
            self,
            user,
            api : str,
            query_dict={},
            validate=True,
            auto_build=True
        ) -> None:
        """
        :Args:
            - api: a key to apis dict
            - query_dict: your query parameters in dictionary where the outer
                most keys are the fields in the url. This is optional and will default
                to get all messages
                Example: {
                    'contact': '+1987654321',
                    'start_id': "76254899'
                }
            - validate: If True, make sure all fields provided and that they will
                be accepted by Text Now. All acceptable fields are located in self.__default_query
            - auto_build: Whether or not to automatically build the query (Raises an Exception if query_dict not provided)
        :Return:
            - A string that will be appended to the base url to query the Text Now API
        """
        self.version_endpoints = {
            "default": "https://www.textnow.com/api/",
            "v1": "https://www.textnow.com/api/v1/",
            "v2": "https://www.textnow.com/api/v2/",
            "v3": "https://www.textnow.com/api/v3/"
        }
        self.__default_query = {
            # Add ? BEFORE the FIRST param and = AFTER EACH PARAM
            #
            "contact_value": "0",
            "start_message_id": "99999999999999",
            "direction": "past",
            "page_size": "100",
            "get_archived": "1",
            "msg_type": "2",
            "message_type": "2"
        }
        self.user_query = {}
        self.apis = {
            "messages": {
                "url": f"users/{user.username}/messages",
                "endpoint": "default",
                "params": [
                    "contact_value",
                    "start_message_id",
                    "direction",
                    "page_size",
                    "get_archived",
                ]
                },
            "contacts": {
                "url": "contacts",
                "endpoint": "v3",
                "params": [
                    "page_size"
                ]
            },
            "attachment_url": {
                "url": "attachment_url",
                "endpoint": "v3",
                "params": [
                    "message_type"
                ]
            },
            "send_attachment": {
                "url": "send_attachment",
                "endpoint": "v3",
                "params": []
            },
            "account_info": {
                "url": f"users/{user.username}",
                "endpoint": "default",
                "params": []
            },
            "sip": {
                "url": "sip",
                "endpoint": "v3",
                "params": []
            },
            "sms": {
                "url": f"users/{user.username}/messages",
                "endpoint": "default",
                "params": []
            },
            "file_url": {
                "url": f"attachment_url",
                "endpoint": "v3",
                "params": [
                    "message_type"
                ]
            }
        }
        self.__api = self.apis[api]
        self.query_dict = query_dict
        self.auto_build = auto_build
        self.self_validate = validate

        ### Set base url
        self.base_url = self.build_base_url(self.__api)

        self.__validate_self()
        super().__init__()

    def __validate_self(self):
        """
        if self.auto_build and not self.query_dict:
            raise Exception(
                "ERROR: Cannot build a query string without a dictionary of params/values.\n"
                "Location: TN_objects/API.py -> QueryBuilder().__init__()"
            )
        """
        if self.self_validate and self.query_dict:
            self.validate(self.query_dict)
        if self.auto_build:
            self.url = self.build_url()

    def validate(self, query_dict):
        for param, value in query_dict.items():
            try:
                self.__default_query[param]
            except KeyError:
                raise Exception("INVALID QUERY DATA: ")

    def build_query(self, query_info, verify_filters=True):
        """
        Take in a dictionary of filters whose keys are strings corresponding
        to url parameters whose values are derived from the value assigned to the key
        in the dictionary we got.
        Verify that the url parameters are valid then go ahead and build the url.
        
        NOTE
        Normally we want to verify that the filters are valid so we don't get flagged
        for endpoint scraping but when we are indeed endpoint scraping, don't verify params,
        just escape/convert their values.
        :Args:
            - filter_dict: A dictionary whose keys correspond to a query parameter
                and value is what you want to assign to the key in your query.
            - verify_filters: If True, we will make sure that every filter key you enter
                is a valid parameter that we know is recognized by Text Now.
                NOTE: Disable this to run automated tests to discover new endpoints.
                    You most likely will get errors but if set up correctly, the errors
                    should be handled automatically.
        
        :Returns:
            - A URL built with the given filters and other required parameters
                
                Example: "https://www.textnow.com/api/users/username/messages?contact_value=%s&start_message_id=%s&direction=past&page_size=%s&get_archived=1"
        """
        if not query_info:
            query_info = self.__default_query
        q = "?"
        q_dict = deepcopy(query_info)
        for key, q_info in q_dict.items():
            if verify_filters:
                if key not in self.__api["params"]:
                    if self.query_dict == {}:
                        continue
                    else:
                        raise Exception("Invalid Parameter")

            if isinstance(q_info, dict):
                val = json.loads(q_info)
            else:
                val = str(q_info)
            strung = f"{str(key)}={quote_plus(val)}"

            query_info.pop(key)
            if len(query_info) == 0:
                q += strung
            else:
                q += strung + "&"
        return q

    def build_url(self):
        q_info = {key: self.__default_query[key] for key in self.__api["params"]}
        query = self.build_query(q_info)
        
        final_url = self.base_url + query

        return final_url
    
    def build_base_url(self, api):
        return self.version_endpoints[api["endpoint"]] + api["url"]

class ApiHandler(object):
    """
    NOTE this object is ONLY for getting results from the
    Text Now API. It does nothing other than that. This is
    because we may end up needing to build more complex urls
    orif we find more end points.
    A wrapper to obscure the API code away from the main class
    based "program".
    Also dynamically builds url queries based on the information it was given
    which are automatically converted to be url safe. This can be extremely useful
    if we think there will be some more endpoints that we didn't forsee.
    """

    def __init__(self, user) -> None:
        self.user = user

        self.__db_handler = DatabaseHandler(db_name="text_nowAPI.sqlite3")
        self.cookies = {
            'connect.sid': self.user.sid
        }
        # At this point, is there any use for this?
        #self.allowed_events = self.events.registered_events
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.104 Safari/537.36 '
        }
        self.session = requests.session()

    def send_sms(self, number, content):
        json = {
            "contact_value": number,
            "contact_type": 2,
            "message": content,
            "read": 1,
            "message_direction": 2,
            "message_type": 1,
            "from_name": self.user.username,
            "has_video": False,
            "new": True,
            "date": datetime.now().isoformat()
            }
        
        url = URLBuilder(self.user, "sms").url
        res = self.session.post(url, headers=self.headers, cookies=self.cookies, json=json)

        return res

    def send_mms(self, number, filepath):
        mime_type = mimetypes.guess_type(filepath)[0]
        file_type = mime_type.split("/")[0]
        has_video = True if file_type == "video" else False
        msg_type = 2 if file_type == "image" else 4

        file_url_holder_req = self.session.get(URLBuilder(self.user, "file_url").url,
                                               cookies=self.cookies, headers=self.headers)
        
        file_url_holder = json.loads(file_url_holder_req.text)["result"]

        with open(filepath, mode="rb") as f:
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
            json_data = {
                "contact_value": number,
                "contact_type": 2,
                "read": 1,
                "message_direction": 2,
                "message_type": msg_type,
                "from_name": self.user.username,
                "has_video": has_video,
                "new": True,
                "date": datetime.now().isoformat(),
                "attachment_url": file_url_holder,
                "media_type": file_type
            }

            send_file_req = self.session.post(URLBuilder(self.user, "send_attachment").url, data=json_data,
                                                headers=self.headers, cookies=self.cookies)
            return send_file_req

    def get_new_messages(self, newest=True, from_="", raw=False):
        """
        Get the newest messages from the text now api
        :Args:
            - newest: If True, will use the newest sms in the database
                and use its TN-id in a query to the api to get all messages
                with a TN-id that's higher than the one we have
            - query: The URL query to be appended to the endpoint
            - from_: The Contact object or phone number of the person or
                contact you want to see the messages from
        
        :Returns:
            Container of Message & MultiMediaMessages orded by descending ID
        """
        params = {}
        # If no query provided, use defaults to get everything
        if newest:
            # Get the newest message id we have on record
            newest_id = self.__db_handler.get_newest_sms().id
            params["start_message_id"] = str(newest_id)

        if from_ != "":
            params["contact_value"] = from_

        url = URLBuilder(self.user, "messages", params).url

        result_json = json.loads(self.session.get(
                url,
                headers=self.headers, cookies=self.cookies
            ).content)
        if raw:
            return result_json
        return map_to_class(data_dicts=result_json, multiple=True)

    def get_raw_contacts(self):
        """
        Gets all textnow contacts
        TODO: Start worker to check if contacts are not in db
            if not, create them. Possibly even get the length of
            contacts, split the length between workers then start
            processes to get them all asynchronously (possible db lock error)
        """
        url = URLBuilder(self.user, "contacts").url
        res = self.session.get(url, headers=self.headers, cookies=self.cookies)
        contacts = json.loads(res.content)

        return contacts["result"]

    def get_raw_messages(self, all=False):
        """
            This gets most of the messages both sent and received. It takes about 30 seconds though
        """
        if all:
            all_messages = []
            # Loop contacts
            for contact in self.get_contacts():
                # Send get for 200 contacts per page
                url = URLBuilder(self.user, "messages").url
                req = self.session.get(
                    url,
                    headers=self.headers, cookies=self.cookies)

                # Change user sid if it's changed
                new_sid = req.cookies['connect.sid']
                if new_sid != self.__user.sid:
                    self.__reset_sid(sid=new_sid, auto_rotating=True, method="get_raw_messages() After GET request")
                if str(req.status_code).startswith("2"):
                    messages = json.loads(req.content)
                    all_messages.append(messages["messages"])

            return all_messages["messages"]
        else:
            url = URLBuilder(self.user, "messages").url
            res = self.session.get(url, headers=self.headers, cookies=self.cookies)
            messages = json.loads(res.content)
            return messages["messages"]
    
    def get_messages(self, all=False):
        raw_messages = self.get_raw_messages(all=all)
        messages = [Message(msg) if msg["message_type"] == MESSAGE_TYPE else MultiMediaMessage(msg) for msg in raw_messages]
        return Container(messages)

    def get_contacts(self):
        raw_contacts = self.get_raw_contacts()
        contacts = [Contact(contact) for contact in raw_contacts]

        return Container(contacts)

    def get_sip_info(self):
        url = URLBuilder(self.user, "sip").url
        res = self.session.get(url, headers=self.headers, cookies=self.cookies)
        sip_info = json.loads(res.content)
        return sip_info

    def get_account_info(self):
        url = URLBuilder(self.user, "account_info").url
        res = self.session.get(url, headers=self.headers, cookies=self.cookies)

        acc_info = json.loads(res.content)
        return Account(acc_info)

    def await_response(self, number, timeout_bool=True):
        
        for msg in self.get_unread_messages():
            msg.mark_as_read()
        timeout = datetime.now() + dt.timedelta(minute=10)
        if not timeout_bool:
            while 1:
                # Slow down the requests because this is too many
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
