from threading import Lock
from flask import Response, Flask, request
import werkzeug.serving import make_server
from logging import getLogger
from pytextnow.database.db import DatabaseHandler

class Listener(object):

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
        # Don't user the reloader so we can use this in a separate thread
        self. __app = Flask("RoboBoi-Event-Listener")
        self.__app.use_reloader = False
        self.__server = make_server("127.0.0.1", 5050, self.__app)
        self._running = False
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
        self.new_things = []
        self.__request = request
        self.__lock = Lock()

    def __call__(self, *args):
        
        body = request.json()

        # Perform the action
        answer = self.__events.get(body["event"])(self.__request)
        # Create the answer (bundle it in a correctly formatted HTTP answer)
        self.response = Response(answer, status=200, headers={})
        # Send it
        return self.response
    

    def start(self):
        """
        Do some setup and run the server
        """
        # Mute the logger
        log = getLogger('werkzeug')
        log.disabled = True
        self.__add_all_endpoints()
        self.__server.daemon_threads = True
        self._running = True
        self.__server.server_forever()

    def kill(environ):
        if not 'werkzeug.server.shutdown' in environ:
            raise RuntimeError('Not running the listener server')
        print("\n\nShutting down the Listener Server...\n\n")
        environ['werkzeug.server.shutdown']()

    def __add_all_endpoints(self):
        for name, info in self.__endpoints.items():
            self.__add_endpoint(
                endpoint=info["url"],
                endpoint_name=name,
                handler=info['func']
            )

    def __add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(
            endpoint, endpoint_name,
            self.__EndpointAction(handler),
            methods=["GET"]
        ) 
        # You can also add options here : "... , methods=['POST'], ... "

    def __received_sms(self):
        """
        Alert of a new message
        """
        with self.__lock:
            self.new_things.append("rec_Message")

    def __received_mms(self):
        with self.__lock:
            self.new_things.append("rec_MultiMediaMessage")

    def __sent_sms(self):
        with self.__lock:
            self.new_things.append("sent_Message")

    def __sent_mms(self):
        with self.__lock:
            self.new_things.append("sent_MultiMediaMessage")

    def get_new(self):
        """
        !!!WARNING!!!
        This clears the new_things list after copying it for return
        """
        with self.__lock:
            things = self.new_things.copy()
            self.new_things.clear()
            return things