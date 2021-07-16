import threading
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
            "missed_call": {
                "url": "/missed/call/",
                "func": self.__missed_call
            },
            "missed_video": {
                "url": "/missed/video/",
                "func": self.__missed_video
            },
        }
        self.new_things = []
        self.__request = request
        self.__lock = threading.Lock()

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
        print("\n\n...Setting up Listener Server...\n\n")
        # Mute the logger
        log = getLogger('werkzeug')
        log.disabled = True
        self.__add_all_endpoints()
        self.__server.daemon_threads = True
        self._running = True
        print("\n\n...Starting listener server for RoboBoi...\n\n")
        threading.Thread(
            target=self.__server.serve_forever
        ).start()
        print("\n\n...Listener Server Started...\n\n")

    def kill(self, environ):
        if not 'werkzeug.server.shutdown' in environ:
            raise RuntimeError('Not running the listener server')
        print("\n\nShutting down the Listener Server...\n\n")
        environ['werkzeug.server.shutdown']()
        self._running = False

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

    def __missed_call(self):
        """
        NOTE this is PURELY for notifications until the SIP calling is done.
        """
        with self.__lock:
            self.new_things.append("missed_call")

    def __missed_video(self):
        """
        NOTE this is PURELY for notifications until the SIP calling is done.
        """
        with self.__lock:
            self.new_things.append("missed_video")

    def __handle_exception()