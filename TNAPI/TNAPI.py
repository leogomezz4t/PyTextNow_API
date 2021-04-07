import mimetypes
if __name__ == "__main__":
    from login import login
else:
    from TNAPI.login import login
import requests
from datetime import datetime
import json
from os.path import abspath
from urllib.parse import quote

MESSAGE_TYPE = 0
MULTIMEDIAMESSAGE_TYPE = 1

SENT_MESSAGE_TYPE = 2
RECEIVED_MESSAGE_TYPE = 1

SIP_ENDPOINT = "prod.tncp.textnow.com"

class Client():
    def __init__(self, email: str):
        #Load SIDS
        user_SID_filepath = "/".join(abspath(__file__).replace("\\", "/").split("/")[:-1]) + "/user_sids.json"
        user_SIDS_file = open(user_SID_filepath, mode="r+")
        
        user_sids_file_data = user_SIDS_file.read()
        user_SIDS = json.loads(user_sids_file_data) if user_sids_file_data else {}

        self.email = email
        self.username = email.split("@")[0]
        self.name = self.username

        if self.email in user_SIDS.keys():
            self.cookies = {
            'connect.sid': user_SIDS[self.email]
            }
        else:
            sid = login()
            self.cookies = {
                'connect.sid': sid
            }
            user_SIDS[self.email] = sid
            user_SIDS_file.seek(0)
            user_SIDS_file.write(json.dumps(user_SIDS))
            user_SIDS_file.truncate()

        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
        }
        
        user_SIDS_file.close()

        self.tasks = {}

    #Functions
    def auth_reset(self):
        user_SID_filepath = "/".join(abspath(__file__).replace("\\", "/").split("/")[:-1]) + "/user_sids.json"
        with open(user_SID_filepath, "r") as user_SIDS_file:
            user_SIDS = json.loads(user_SIDS_file.read()) 

        if self.email in user_SIDS.keys():
            del user_SIDS[self.email]  

            with open(user_SID_filepath, "w") as user_SIDS_file:
                user_SIDS_file.write(json.dumps(user_SIDS))

            self.__init__(self.email)
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
            return messages
        else:
            raise self.FailedRequest(str(req.status_code))

    def get_raw_messages(self):
        """
            This gets most of the messages both sent and received. However It won't get all of them just the past 10-15
        """
        req = requests.get("https://www.textnow.com/api/users/" + self.username + "/messages", headers=self.headers, cookies=self.cookies)
        if str(req.status_code).startswith("2"):
            messages = json.loads(req.content)
            return messages["messages"]
        else:
            raise self.FailedRequest(str(req.status_code))

    def get_sent_messages(self):
        """
            This gets all the past 10-15 messages sent by your account
        """
        sent_messages = self.get_messages()
        sent_messages = [msg for msg in sent_messages if msg.direction == SENT_MESSAGE_TYPE]

        return sent_messages

    def get_received_messages(self):
        """
            Gets inbound messages
        """
        messages = self.get_messages()
        messages = [msg for msg in messages if msg.direction == RECEIVED_MESSAGE_TYPE]

        return messages

    def get_unread_messages(self):
        """
            Gets unread messages
        """
        new_messages = self.get_messages()
        new_messages = [msg for msg in new_messages if msg.direction == RECEIVED_MESSAGE_TYPE]
        new_messages = [msg for msg in new_messages if not msg.read]
        
        return new_messages

    def get_read_messages(self):
        """
            Gets read messages
        """
        new_messages = self.get_messages()
        new_messages = [msg for msg in new_messages if msg.direction == RECEIVED_MESSAGE_TYPE]
        new_messages = [msg for msg in new_messages if msg.read]
        
        return new_messages

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

                place_file_req = requests.put(file_url_holder, data=raw, headers=headers_place_file, cookies=self.cookies)
                if str(place_file_req.status_code).startswith("2"):

                    json_data = {
                        "contact_value": to,
                        "contact_type":2,"read":1,
                        "message_direction":2,"message_type": msg_type,
                        "from_name": self.name,
                        "has_video":has_video,
                        "new":True,
                        "date": datetime.now().isoformat(),
                        "attachment_url": file_url_holder,
                        "media_type": file_type
                    }

                    send_file_req = requests.post("https://www.textnow.com/api/v3/send_attachment", data=json_data, headers=self.headers, cookies=self.cookies)
                    return send_file_req
                else:
                    raise self.FailedRequest(str(place_file_req.status_code))
        else:
            raise self.FailedRequest(str(file_url_holder_req.status_code))
    
    def send_sms(self, to, text):
        """
            Sends an sms text message to this number
        """
        data = {
        'json': '{"contact_value":"' + to + '","contact_type":2,"message":"' + text + '","read":1,"message_direction":2,"message_type":1,"from_name":"' + self.name + '","has_video":false,"new":true,"date":"' + datetime.now().isoformat() + '"}'
        }

        response = requests.post('https://www.textnow.com/api/users/' + self.username + '/messages', headers=self.headers, cookies=self.cookies, data=data)
        if not str(response.status_code).startswith("2"):
            raise self.FailedRequest(str(response.status_code))
        return response

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
                self.reason = "server returned a Client error. Request Failed."
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
            print(class_name)
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
                            "from_name": self.self.name,
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
                'json': '{"contact_value":"' + self.number + '","contact_type":2,"message":"' + text + '","read":1,"message_direction":2,"message_type":1,"from_name":"' + self.self.name + '","has_video":false,"new":true,"date":"' + datetime.now().isoformat() + '"}'
            }

            response = requests.post('https://www.textnow.com/api/users/' + self.self.username + '/messages', headers=self.self.headers, cookies=self.self.cookies, data=data)
            if not str(response.status_code).startswith("2"):
                raise self.FailedRequest(str(response.status_code))
            return response

        def mark_as_read(self):
            self.patch({"read": True})
        
        def patch(self, data):
            if not all(key in self.raw for key in data): return

            base_url = "https://www.textnow.com/api/users/leojwu18/conversations/"
            url = base_url + quote(self.number)

            params = {
                "latest_message_id": self.id,
                "http_method": "PATCH"
            }

            res = requests.post(url, params=params, data=data,cookies=self.self.cookies, headers=self.self.headers)
            return res

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
