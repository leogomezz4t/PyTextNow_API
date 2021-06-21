from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import quote

import mimetypes
import json
import requests
import time

MESSAGE_TYPE = 0


class Message:
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

        file_url_holder_req = requests.get("https://www.textnow.com/api/v3/attachment_url?message_type=2",
                                           cookies=self.self.cookies, headers=self.self.headers)
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

                place_file_req = requests.put(file_url_holder, data=raw, headers=headers_place_file,
                                              cookies=self.self.cookies)
                if str(place_file_req.status_code).startswith("2"):

                    json_data = {
                        "contact_value": self.number,
                        "contact_type": 2, "read": 1,
                        "message_direction": 2, "message_type": msg_type,
                        "from_name": self.self.username,
                        "has_video": has_video,
                        "new": True,
                        "date": datetime.now().isoformat(),
                        "attachment_url": file_url_holder,
                        "media_type": file_type
                    }

                    send_file_req = requests.post("https://www.textnow.com/api/v3/send_attachment", data=json_data,
                                                  headers=self.self.headers, cookies=self.self.cookies)
                    return send_file_req
                else:
                    raise self.self.FailedRequest(str(place_file_req.status_code))
        else:
            raise self.self.FailedRequest(str(file_url_holder_req.status_code))

    def send_sms(self, text):
        data = \
            {
                'json': '{"contact_value":"' + self.number
                        + '","contact_type":2,"message":"' + text
                        + '","read":1,"message_direction":2,"message_type":1,"from_name":"'
                        + self.self.username + '","has_video":false,"new":true,"date":"'
                        + datetime.now().isoformat() + '"}'
            }

        response = requests.post('https://www.textnow.com/api/users/' + self.self.username + '/messages',
                                 headers=self.self.headers, cookies=self.self.cookies, data=data)
        if not str(response.status_code).startswith("2"):
            self.self.request_handler(response.status_code)
        return response

    def mark_as_read(self):
        self.patch({"read": True})

    def patch(self, data):
        if not all(key in self.raw for key in data):
            return

        base_url = "https://www.textnow.com/api/users/" + self.self.username + "/conversations/"
        url = base_url + quote(self.number)

        params = {
            "latest_message_id": self.id,
            "http_method": "PATCH"
        }

        res = requests.post(url, params=params, data=data, cookies=self.self.cookies, headers=self.self.headers)
        return res

    def wait_for_response(self, timeout_bool=True):
        self.mark_as_read()
        for msg in self.self.get_unread_messages():
            msg.mark_as_read()
        timeout = datetime.now() + relativedelta(minute=10)
        if not timeout_bool:
            while 1:
                unread_msgs = self.self.get_unread_messages()
                filtered = unread_msgs.get(number=self.number)
                if len(filtered) == 0:
                    time.sleep(0.2)
                    continue
                return filtered[0]

        else:
            while datetime.now() > timeout:
                unread_msgs = self.self.get_unread_messages()
                filtered = unread_msgs.get(number=self.number)
                if len(filtered) == 0:
                    time.sleep(0.2)
                    continue
                return filtered[0]
