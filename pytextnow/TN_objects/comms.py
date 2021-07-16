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
        self.__v3 = "https://www.textnow.com/api/v3/"
        self.__db_handler = DatabaseHandler()
        self.__default_query = "?contact_value=0"\
                + "&start_message_id=99999999999999"\
                    + "&direction=past"\
                        + "&page_size=100"\
                            + "&get_archived=1"
        self.cookies = {
            'connect.sid': user.sid
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

    def get_new_mms(self, newest=True, query=None, from_="", raw=False):
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


    def build_query(self, query_info=None):
        """
        Dynamically create a query to be appended to the end
        of a url to complete it.

        Build a query like this
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
            return self.default_query
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
    
