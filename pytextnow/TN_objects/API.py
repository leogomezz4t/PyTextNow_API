from copy import deepcopy
import json
from pytextnow.tools.utils import map_to_class
from pytextnow.database.db import DatabaseHandler
from urllib.parse import quote_plus
import requests

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
        self.__msg_url = "https://www.textnow.com/api/users/%s/messages" % (user.username)
        self. "https://www.textnow.com/api/v3/contacts"
        self.__v3 = "https://www.textnow.com/api/v3/"
        self.__db_handler = DatabaseHandler()
        self.__default_query = {
            "?contact_value=": "0",
            "&start_message_id=":"99999999999999",
            "&direction=": "past",
            "&page_size=": "100",
            "&get_archived=": "1"
        }
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

    def get_new_sms(self, newest=True, query=None, from_="", raw=False):
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
        # If no query provided, use defaults to get everything

        if not query:
            query = self.__default_query
        result_json = json.loads(self.session.get(
                quote_plus(self.__msg_url+query),
                headers=self.headers, cookies=self.cookies
            ).content)
        if raw:
            return result_json
        return map_to_class(data_dicts=result_json, multiple=True)

    def get_new_mms(self, newest=True, from_="", raw=False):
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

    def build_query(self, query_info=None):
        """
        Dynamically create a query to be appended to the end
        of a url to complete it.

        Build a query that looks like this
        "https://www.textnow.com/api/users/"
                + self.__user.username
                + "/messages?contact_value=%s"
                + "&start_message_id=%s"
                + "&direction=past"
                + "&page_size=%s"
                + "&get_archived=1"
        but dynamically. This helps if scraping to find endpoints
        """
        if not query_info:
            query_info = self.__default_query
        q = "?"
        q_dict = deepcopy(query_info)
        for param, value in q_dict.items():
            strung = str(param)+str(value)
            query_info.pop(param)
            if len(query_info) == 0:
                q += strung
            if len(q) == 1:
                q = strung + "&"
            else:
                q += strung + "&"
        return q

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
        res = requests.get(, params=params, cookies=self.cookies)
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