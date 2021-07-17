from copy import deepcopy
from datetime import datetime
import datetime as dt
import time
import json
from copy import deepcopy
from pytextnow.tools.utils import map_to_class
from pytextnow.database.db import DatabaseHandler
from urllib.parse import quote_plus

from TN_objects.error import (
    TNApiError,
    DatabaseHandlerError,
    NetworkError
)

class QueryBuilder:
    def __init__(
            self, user,
            api="v3",
            query_dict=None,
            validate=True,
            auto_build=True
        ) -> None:
        """
        :Args:
            - api: The api version (i.e 'v1' or 'v3')
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
            "number": {
                "param": "contact_value",
                "value": "0"
            },
            "start_id": {
                "param": "start_message_id",
                "value":"99999999999999"
            },
            "direction": {
                "param": "direction",
                "value": "past"
            },
            "size": {
                "param": "page_size",
                "value": "100"
            },
            "archived": {
                "param": "get_archived",
                "value": "1"
            },
            "msg_type": {
                "param": "message_type",
                "value": "2"
            }
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
                "params": []
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
            }
        }
        self.__api = self.apis[api]
        self.auto_build = auto_build
        self.__validate_self()
        super().__init__()

    def __validate_self(self):
        if self.auto_build and not self.query_dict:
            raise Exception(
                "ERROR: Cannot build a query string without a dictionary of params/values.\n"
                "Location: TN_objects/API.py -> QueryBuilder().__init__()"
            )
        if self.validate:
            self.validate(self.query_dict)
        if self.auto_build:
            self.build_url()

    def validate(self, query_dict):
        for param, value in query_dict.items():
            try:
                self.__default_query[param]
            except KeyError:
                raise Exception("INVALID QUERY DATA: ")

    def build_query(self, query_info, filter_dict, verify_filters=True):
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
            if isinstance(q_info['value'], dict):
                val = json.loads(q_info['value'])
            else:
                val = str(q_info['value'])
            strung = str(q_info['param'])+val

            query_info.pop(key)
            if len(query_info) == 0:
                q += strung
            if len(q) == 1:
                q = strung + "&"
            else:
                q += strung + "&"
        return q


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
    Considering we already have v3...if wer're lazy we can build a ApiPatcher object
    which literally just extends this to use the new things
    """

    def __init__(self, user) -> None:
<<<<<<< HEAD

        self.__db_handler = DatabaseHandler()
        self.__q_builder = QueryBuilder()
=======
        self.version_endpoints = {
            "default": "https://www.textnow.com/api/",
            "v1": "https://www.textnow.com/api/v1/",
            "v2": "https://www.textnow.com/api/v2/",
            "v3": "https://www.textnow.com/api/v3/"
        }

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
                "params": []
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
            }
        }
        self.__db_handler = DatabaseHandler()
        self.param_values = {
            "contact_value": "string",
            "start_message_id": "number",
            "direction": ["past", "future"],
            "page_size": "number",
            "get_archived=": ["0", "1"]
        }
>>>>>>> ceed049cec39e2a3f9beb5d84bad3c68af262c93
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

    def get_new_sms(self, newest=True, from_="", raw=False):
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
        # If no query provided, use defaults to get everything
        if newest:
            # Get the newest message id we have on record
            newest_id = self.__db_handler.get_newest_sms().id
        query = deepcopy(self.__default_query)
        if from_ != "":
            query['contact']['value'] = from_
        result_json = json.loads(self.session.get(
                quote_plus(
                    self.__msg_url
                    + self.build_query(query)
                ),
                headers=self.headers, cookies=self.cookies
            ).content)
        if raw:
            return result_json
        return map_to_class(data_dicts=result_json, multiple=True)

    def get_new_mms(self, newest=True, query="", from_="", raw=False):
        """
        Get the newest messages from the text now api
        :Args:
            - newest: If True, will use the newest sms in the database
                and use its TN-id in a query to the api
            - query: The URL query to be appended to the /messages/
                endpoint
            - from_: The Contact object or phone number of the person or
                contact you want to see the messages from
        
        :Returns:
            Container of Message & MultiMediaMessages orded by descending ID
        """
        result_json = json.loads(self.session.get(
                quote_plus(self.__msg_url+query),
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
        params = (
            ('page_size', '50'),
        )
        res = requests.get(self.apis["contacts"]["endpoint"] + self.apis["contacts"]["url"], params=params, cookies=self.cookies)
        contacts = json.loads(res.text)
        return contacts["result"]

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
                + "/messages?contact_value="
                + "%s&start_message_id=99999999999999&direction=past&page_size=%s&get_archived=1" % (contact.number),
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

    def generate_query(self, api, info_dict):
        url = self.apis.get(api, None) or self.apis.get('v3')
        # generate query
        return url+quote_plus(self.build_query(info_dict))