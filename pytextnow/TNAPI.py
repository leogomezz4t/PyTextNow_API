import mimetypes
if __name__ == "__main__":
    from login import login
else:
    from pytextnow.login import login
import requests
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
import json
from os.path import abspath
from urllib.parse import quote
import time
import atexit

MESSAGE_TYPE = 0
MULTIMEDIAMESSAGE_TYPE = 1

SENT_MESSAGE_TYPE = 2
RECEIVED_MESSAGE_TYPE = 1

SIP_ENDPOINT = "prod.tncp.textnow.com"

class Client():
    def __init__(self, username: str = None, cookie=None):
        #Load SIDS
        user_SID_filepath = "/".join(abspath(__file__).replace("\\", "/").split("/")[:-1]) + "/user_sids.json"
        try:
            with open(user_SID_filepath, "r") as user_SIDS_file:
                user_SIDS = json.loads(user_SIDS_file.read())
        except json.decoder.JSONDecodeError:
            with open(user_SID_filepath, "w") as user_SIDS_file:
                user_SIDS_file.write("{}")
            with open(user_SID_filepath, "r") as user_SIDS_file:
                user_SIDS = json.loads(user_SIDS_file.read())
        else:
            with open(user_SID_filepath, "r") as user_SIDS_file:
                user_SIDS = json.loads(user_SIDS_file.read())

        self.username = username
        self.allowed_events = ["message"]

        self.events = []

        if self.username in user_SIDS.keys():
            sid = cookie if cookie else user_SIDS[self.username]
            self.cookies = {
            'connect.sid': sid
            }
            user_SIDS[self.username] = sid
            if cookie:
                with open(user_SID_filepath, "w") as user_SIDS_file:
                    user_SIDS_file.write(json.dumps(user_SIDS))
        else:
            sid = cookie if cookie else login()
            self.cookies = {
                'connect.sid': sid
            }
            user_SIDS[self.username] = sid
            with open(user_SID_filepath, "w") as user_SIDS_file:
                user_SIDS_file.write(json.dumps(user_SIDS))

        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
        }
        
        user_SIDS_file.close()

        def on_exit():
            if len(self.events) == 0: return
            while 1:
                for event, func in self.events:
                    if event == "message":
                        unreads = self.get_unread_messages()
                        for msg in unreads:
                            msg.mark_as_read()
                            func(msg)
                
        atexit.register(on_exit)

    #Functions
    def auth_reset(self, cookie=None):
        user_SID_filepath = "/".join(abspath(__file__).replace("\\", "/").split("/")[:-1]) + "/user_sids.json"
        with open(user_SID_filepath, "r") as user_SIDS_file:
            user_SIDS = json.loads(user_SIDS_file.read()) 

        if self.username in user_SIDS.keys():
            del user_SIDS[self.username]  

            with open(user_SID_filepath, "w") as user_SIDS_file:
                user_SIDS_file.write(json.dumps(user_SIDS))


            self.__init__(self.username, cookie)
        else:
            if cookie:
                user_SIDS[self.username] = cookie
                with open(user_SID_filepath, "w") as user_SIDS_file:
                    user_SIDS_file.write(json.dumps(user_SIDS))
                self.__init__(self.username)
            else:
                raise self.AuthError("You haven't authenticated before.")

    def get_messages(self):
        """
            This gets most of the messages both sent and received. However It won't get all of them just the past 10-15
        """
        req = requests.get("https://www.textnow.com/api/users/" + self.username + "/messages", headers=self.headers, cookies=self.cookies)
        if str(req.status_code).startswith("2"):
            messages = json.loads(req.content)
            messages = [self.Message(msg, self) if not msg["message"].startswith("http") else self.MultiMediaMessage(msg, self) for msg in messages["messages"]]
            return self.MessageContainer(messages, self)
        else:
            self.FailedRequestHandler(req.status_code)

    def get_raw_messages(self):
        """
            This gets most of the messages both sent and received. However It won't get all of them just the past 10-15
        """
        req = requests.get("https://www.textnow.com/api/users/" + self.username + "/messages", headers=self.headers, cookies=self.cookies)
        if str(req.status_code).startswith("2"):
            messages = json.loads(req.content)
            return messages["messages"]
        else:
            self.FailedRequestHandler(req.status_code)

    def get_sent_messages(self):
        """
            This gets all the past 10-15 messages sent by your account
        """
        sent_messages = self.get_messages()
        sent_messages = [msg for msg in sent_messages if msg.direction == SENT_MESSAGE_TYPE]

        return self.MessageContainer(sent_messages, self)

    def get_received_messages(self):
        """
            Gets inbound messages
        """
        messages = self.get_messages()
        messages = [msg for msg in messages if msg.direction == RECEIVED_MESSAGE_TYPE]

        return self.MessageContainer(messages, self)

    def get_unread_messages(self):
        """
            Gets unread messages
        """
        new_messages = self.get_received_messages()
        new_messages = [msg for msg in new_messages if not msg.read]
        
        return self.MessageContainer(new_messages, self)

    def get_read_messages(self):
        """
            Gets read messages
        """
        new_messages = self.get_received_messages()
        new_messages = [msg for msg in new_messages if msg.read]
        
        return self.MessageContainer(new_messages, self)

    def send_mms(self, to, file):
        """
            This function sends a file/media to the number
        """
        mime_type = mimetypes.guess_type(file)[0]
        file_type = mime_type.split("/")[0]
        has_video = True if file_type == "video" else False
        msg_type = 2 if file_type == "image" else 4

        file_url_holder_req = requests.get("https://www.textnow.com/api/v3/attachment_url?message_type=2", cookies=self.cookies, headers=self.headers)
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

                place_file_req = requests.put(file_url_holder, data=raw, headers=headers_place_file, cookies=self.cookies)
                if str(place_file_req.status_code).startswith("2"):

                    json_data = {
                        "contact_value": to,
                        "contact_type":2,"read":1,
                        "message_direction":2,"message_type": msg_type,
                        "from_name": self.username,
                        "has_video":has_video,
                        "new":True,
                        "date": datetime.now().isoformat(),
                        "attachment_url": file_url_holder,
                        "media_type": file_type
                    }

                    send_file_req = requests.post("https://www.textnow.com/api/v3/send_attachment", data=json_data, headers=self.headers, cookies=self.cookies)
                    print(send_file_req.request)
                    return send_file_req
                else:
                    self.FailedRequestHandler(place_file_req.status_code)
        else:
            self.FailedRequestHandler(file_url_holder_req.status_code)
    
    def send_sms(self, to, text):
        """
            Sends an sms text message to this number
        """
        data = {
        'json': '{"contact_value":"' + to + '","contact_type":2,"message":"' + text + '","read":1,"message_direction":2,"message_type":1,"from_name":"' + self.username + '","has_video":false,"new":true,"date":"' + datetime.now().isoformat() + '"}'
        }
        response = requests.post('https://www.textnow.com/api/users/' + self.username + '/messages', headers=self.headers, cookies=self.cookies, data=data)
        if not str(response.status_code).startswith("2"):
            self.FailedRequestHandler(response.status_code)
        return response

    def wait_for_response(self, number, timeout_bool=True):
            for msg in self.self.get_unread_messages():
                msg.mark_as_read()
            timeout = datetime.now() + relativedelta(minute=10)
            if not timeout_bool: 
                while 1:
                    unreads = self.self.get_unread_messages()
                    filtered = unreads.get(number=number)
                    if len(filtered) == 0: 
                        time.sleep(0.2)
                        continue
                    return filtered[0]

            else:     
                while datetime.now() > timeout:
                    unreads = self.self.get_unread_messages()
                    filtered = unreads.get(number=number)
                    if len(filtered) == 0: 
                        time.sleep(0.2)
                        continue
                    return filtered[0]

    def on(self, event: str):
        if not event in self.allowed_events: raise self.InvalidEvent(event)
        def deco(func):
            self.events.append([event, func])
        return deco

    #Custom Errors
    """
    class InvalidFileType(Exception):
        def __init__(self, file_type):
            self.message = f"The file type {file_type} is not supported.\nThe only types supported are images and videos."

        def __str__(self):
            return self.message
    """
    class FailedRequest(Exception):
        def __init__(self, status_code: str):
            self.status_code = status_code
            if status_code.startswith('3'):
                self.reason = "server redirected the request. Request Failed."
            elif status_code.startswith('4'):
                self.reason = "server returned a Client error. Request Failed. Try resetting your authentication with client.auth_reset()"
            elif status_code.startswith('5'):
                if status_code == "500":
                    self.reason = "Internal Server Error. Request Failed."
                else:
                    self.reason = "server return a Server error. Request Failed."

        def __str__(self):
            message = f"Could not send message. {self.reason}\nStatus Code: {self.status_code}"
            return message
    
    class AuthError(Exception):
        def __init__(self, reason):
            self.reason = reason
        
        def __str__(self):
            return self.reason

    class InvalidEvent(Exception):
        def __init__(self, event):
            self.event = event
        def __str__(self):
            return f"{self.event} is an invalid event."
    
    def FailedRequestHandler(self, req_code):
        req_code = str(req_code)
        if req_code == "401":
            exc = self.FailedRequest(req_code)
            print(exc)

            self.auth_reset()
            return
        
        raise self.FailedRequest(req_code)

    #Custom Classes
    class Message():
        def __init__(self, msg_obj, outer_self):
            self.content = msg_obj["message"]
            self.number = msg_obj["contact_value"]
            self.date = datetime.fromisoformat(msg_obj["date"].replace("Z", "+00:00"))
            self.first_contact = msg_obj["conversation_filtering"]["first_time_contact"]
            self.type = MESSAGE_TYPE
            self.read = msg_obj["read"]
            self.id = msg_obj["id"]
            self.direction = msg_obj["message_direction"]
            self.raw = msg_obj
            self.self = outer_self

        def __str__(self):
            class_name = self.__class__.__name__
            s = f"<{class_name} number: {self.number}, content: {self.content}>"
            return s
        
        def send_mms(self, file):
            mime_type = mimetypes.guess_type(file)[0]
            file_type = mime_type.split("/")[0]
            has_video = True if file_type == "video" else False
            msg_type = 2 if file_type == "image" else 4

            file_url_holder_req = requests.get("https://www.textnow.com/api/v3/attachment_url?message_type=2", cookies=self.self.cookies, headers=self.self.headers)
            if str(file_url_holder_req.status_code).startswith("2"):
                file_url_holder = json.loads(file_url_holder_req.text)["result"]

                with open(file, mode="br") as f:
                    raw = f.read()

                    headers_place_file = {
                        'accept': '*/*',
                        'content-type': mime_type,
                        'accept-language': 'en-US,en;q=0.9',
                        "mode": "cors",
                        "method": "PUT",
                        "credentials": 'omit'
                    }

                    place_file_req = requests.put(file_url_holder, data=raw, headers=headers_place_file, cookies=self.self.cookies)
                    if str(place_file_req.status_code).startswith("2"):

                        json_data = {
                            "contact_value": self.number,
                            "contact_type":2,"read":1,
                            "message_direction":2,"message_type": msg_type,
                            "from_name": self.self.username,
                            "has_video":has_video,
                            "new":True,
                            "date": datetime.now().isoformat(),
                            "attachment_url": file_url_holder,
                            "media_type": file_type
                        }

                        send_file_req = requests.post("https://www.textnow.com/api/v3/send_attachment", data=json_data, headers=self.self.headers, cookies=self.self.cookies)
                        return send_file_req
                    else:
                        raise self.self.FailedRequest(str(place_file_req.status_code))
            else:
                raise self.self.FailedRequest(str(file_url_holder_req.status_code))
        
        def send_sms(self, text):
            data = {
                'json': '{"contact_value":"' + self.number + '","contact_type":2,"message":"' + text + '","read":1,"message_direction":2,"message_type":1,"from_name":"' + self.self.username + '","has_video":false,"new":true,"date":"' + datetime.now().isoformat() + '"}'
            }

            response = requests.post('https://www.textnow.com/api/users/' + self.self.username + '/messages', headers=self.self.headers, cookies=self.self.cookies, data=data)
            if not str(response.status_code).startswith("2"):
                self.FailedRequestHandler(response.status_code)
            return response

        def mark_as_read(self):
            self.patch({"read": True})
        
        def patch(self, data):
            if not all(key in self.raw for key in data): return

            base_url = "https://www.textnow.com/api/users/" + self.self.username + "/conversations/"
            url = base_url + quote(self.number)

            params = {
                "latest_message_id": self.id,
                "http_method": "PATCH"
            }

            res = requests.post(url, params=params, data=data,cookies=self.self.cookies, headers=self.self.headers)
            return res

        def wait_for_response(self, timeout_bool=True):
            self.mark_as_read()
            for msg in self.self.get_unread_messages():
                msg.mark_as_read()
            timeout = datetime.now() + relativedelta(minute=10)
            if not timeout_bool: 
                while 1:
                    unreads = self.self.get_unread_messages()
                    filtered = unreads.get(number=self.number)
                    if len(filtered) == 0: 
                        time.sleep(0.2)
                        continue
                    return filtered[0]

            else:     
                while datetime.now() > timeout:
                    unreads = self.self.get_unread_messages()
                    filtered = unreads.get(number=self.number)
                    if len(filtered) == 0: 
                        time.sleep(0.2)
                        continue
                    return filtered[0]

    class MultiMediaMessage(Message):
        def __init__(self, msg_obj, outer_self):
            super().__init__(msg_obj, outer_self)
            file_req = requests.get(self.content)
            self.raw_data = file_req.content
            self.content_type = file_req.headers["Content-Type"]
            self.extension = self.content_type.split("/")[1]
            self.type = MULTIMEDIAMESSAGE_TYPE
            self.self = outer_self

        def mv(self, file_path=None):
            if not file_path:
                file_path = f"./file.{self.extension}"
            with open(file_path, mode="wb") as f:
                f.write(self.raw_data)

    class MessageContainer(list):
        def __init__(self, msg_list: list, outer_self):
            super().__init__(msg_list)
            self.msg_list = msg_list
            self.outer_self = outer_self
        
        def __str__(self):
            ss = [msg.__str__() for msg in self.msg_list]
            s = '[' + "\n".join(ss) + ']'
            return s
        
        def get(self, **kwargs):
            filtered_list = []
            for msg in self.msg_list:
                if all(key in msg.__dict__.keys() for key in kwargs):
                    if all(getattr(msg, key) == val for key, val in msg.__dict__.items()):
                        filtered_list.append(msg)
            
            return self.outer_self.MessageContainer(filtered_list, self.outer_self)

