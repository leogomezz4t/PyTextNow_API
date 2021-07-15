from pytextnow.database.db import DatabaseHandler
from flask import Response
from flask.app import Flask



class Communicator(object):

    class __EndpointAction(object):

        def __init__(self, action):
            self.action = action

        def __call__(self, *args):
            # Perform the action
            answer = self.action(request)
            # Create the answer (bundle it in a correctly formatted HTTP answer)
            self.response = Response(answer, status=200, headers={})
            # Send it
            return self.response

    def __init__(self):
        self.app = Flask(__name__)
        self.__endpoints = {
            "received_sms": {
                "url": "/rec_sms/",
                "func": self.__received_sms
            },
            "received_mms": {
                "url": "/rec_mms/",
                "func": self.__received_mms
            },
            "sms_sent": {
                "url": "/sent_sms/",
                "func": self.__sent_sms
            },
            "mms_sent": {
                "url": "/sent_mms/",
                "func": self.__sent_mms
            },
        }
        self.__db_handler = DatabaseHandler()
        self.new_things = []
        self.__request = request

    def __call__(self, *args):
        
        body = request.json()

        # Perform the action
        answer = self.__events.get(body["event"])(request)
        # Create the answer (bundle it in a correctly formatted HTTP answer)
        self.response = Response(answer, status=200, headers={})
        # Send it
        return self.response

    def __add_all_endpoints(self):
        for name, info in self.__endpoints.items():
            self.add_endpoint(endpoint=info["url"], endpoint_name=name, handler=info['func'])

    def __add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, self.__EndpointAction(handler), methods=["POST"]) 
        # You can also add options here : "... , methods=['POST'], ... "


    def __received_sms(self):
        """
        Alert of a new message
        """
        raw = self.request.json()
        obj_data = raw.get('object_info')


    def __received_mms(self):
        raw = self.request.json()

        new_mms = self.__db_handler.create_mms(raw['object_info'])
        self.new_things.append(new_mms)

    def __sent_sms(self):
        raw = self.request.json()
        new_sms = self.__db_handler.create_sms(raw['object_info'])
        self.new_things.append(new_sms)
        pass

    def __sent_mms(self):
        self.new_things.append(self.__db_handler.get_mms(
            {'id': self.__request.json()['object_info']['id']}
        ))
    
    def get_new(self):
        """
        !!!WARNING!!!
        This clears the new_things list after copying it for return
        THIS IS NOT THREAD SAFE
        """
        things = self.new_things.copy()
        self.new_things.clear()
        return things