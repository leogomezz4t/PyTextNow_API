import mimetypes
from TNAPI import login
import requests
from datetime import datetime
import json

class Client():
    def __init__(self, email: str, password: str, name: str = "", geckodriver_path=None):
        #Load SIDS
        user_SID_filepath = "\\".join(__file__.split("\\")[:-1]) + "\\user_sids.json"
        user_SIDS_file = open(user_SID_filepath, mode="r+")
        user_SIDS = json.loads(user_SIDS_file.read())

        self.email = email
        self.username = email.split("@")[0]
        self.password = password
        self.name = name if not name == "" else self.username

        if self.email in user_SIDS.keys():
            self.cookies = {
            'connect.sid': user_SIDS[self.email]
            }
        else:
            sid = login.login(self.email, self.password, geckodriver_path) if geckodriver_path else login.login(self.email, self.password)
            self.cookies = {
                'connect.sid': sid
            }
            user_SIDS[self.email] = sid
            user_SIDS_file.write(json.dumps(user_SIDS))

        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
        }
    #Functions
    def get_messages(self):
        req = requests.get("https://www.textnow.com/api/users/" + self.username + "/messages", headers=self.headers, cookies=self.cookies)
        if str(req.status_code).startswith("2"):
            messages = json.loads(req.content)
            messages = [msg for msg in messages["messages"] if msg['message_direction'] == 1]
            return messages
        else:
            raise self.FailedRequest(str(req.status_code))

    def get_sent_messages(self):
        req = requests.get("https://www.textnow.com/api/users/" + self.username + "/messages", headers=self.headers, cookies=self.cookies)
        if str(req.status_code).startswith("2"):
            sent_messages = json.loads(req.content)
            sent_messages = [msg for msg in sent_messages["messages"] if msg['message_direction'] == 2]
            return sent_messages
        else:
            raise self.FailedRequest(str(req.status_code))

    def get_new_messages(self):
        req = requests.get("https://www.textnow.com/api/users/" + self.username + "/messages", headers=self.headers, cookies=self.cookies)
        if str(req.status_code).startswith('2'):
            new_messages = json.loads(req.content)
            new_messages = [msg for msg in new_messages["messages"] if msg['message_direction'] == 1]
            new_messages = [msg for msg in new_messages if msg not in self.get_messages()]

            return new_messages
        else:
            raise self.FailedRequest(str(req.status_code))

    def send_mms(self, to, file):
        mime_type = mimetypes.guess_type(file)[0]
        file_type = mime_type.split("/")[0]
        has_video = True if file_type == "video" else False
        msg_type = 2 if file_type == "image" else 4

        if file_type == "image" or file_type == "video":

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
                            "media_type":"images"
                        }

                        send_file_req = requests.post("https://www.textnow.com/api/v3/send_attachment", data=json_data, headers=self.headers, cookies=self.cookies)
                        return send_file_req
                        if not str(send_file_req.status_code).startswith('2'):
                            raise self.FailedRequest(str(send_file_req.status_code))
                    else:
                        raise self.FailedRequest(str(place_file_req.status_code))
            else:
                raise self.FailedRequest(str(file_url_holder_req.status_code))
        else:
            raise self.InvalidFileType(file_type)
    
    def send_sms(self, to, text):
        data = {
        'json': '{"contact_value":"' + to + '","contact_type":2,"message":"' + text + '","read":1,"message_direction":2,"message_type":1,"from_name":"' + self.name + '","has_video":false,"new":true,"date":"' + datetime.now().isoformat() + '"}'
        }

        response = requests.post('https://www.textnow.com/api/users/' + self.username + '/messages', headers=self.headers, cookies=self.cookies, data=data)
        if not str(response.status_code).startswith("2"):
            raise self.FailedRequest(str(response.status_code))
        return response
    #Custom Errors
    class InvalidFileType(Exception):
        def __init__(self, file_type):
            self.message = f"The file type {file_type} is not supported.\nThe only types supported are images and videos."

        def __str__(self):
            return self.message

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