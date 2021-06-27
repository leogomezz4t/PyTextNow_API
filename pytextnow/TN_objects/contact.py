from datetime import datetime

import mimetypes
import json


class Contact:
    def __init__(self, raw_obj, client, db_id=None):
        self.raw_obj = raw_obj
        self.db_id = db_id
        self.client = client
        self.number = self.raw_obj["contact_value"]
        self.name = self.raw_obj["name"]

    def __str__(self):
        s = f"<Contact number={self.number}, name={self.name}>"
        return s

    def send_sms(self, text):
        data = \
            {
                'json': '{"contact_value":"' + self.number
                        + '","contact_type":2,"message":"' + text
                        + '","read":1,"message_direction":2,"message_type":1,"from_name":"'
                        + self.client.username + '","has_video":false,"new":true,"date":"'
                        + datetime.now().isoformat() + '"}'
            }

        response = self.client.session.post('https://www.textnow.com/api/users/' + self.client.username + '/messages',
                                            headers=self.client.headers, cookies=self.client.cookies, data=data)
        if not str(response.status_code).startswith("2"):
            self.client.request_handler(response.status_code)
        return response

    def send_mms(self, file):
        mime_type = mimetypes.guess_type(file)[0]
        file_type = mime_type.split("/")[0]
        has_video = True if file_type == "video" else False
        msg_type = 2 if file_type == "image" else 4

        file_url_holder_req = self.client.session.get("https://www.textnow.com/api/v3/attachment_url?message_type=2",
                                                      cookies=self.client.cookies, headers=self.client.headers)
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

                place_file_req = self.client.session.put(file_url_holder, data=raw, headers=headers_place_file,
                                                         cookies=self.client.cookies)
                if str(place_file_req.status_code).startswith("2"):

                    json_data = {
                        "contact_value": self.number,
                        "contact_type": 2, "read": 1,
                        "message_direction": 2, "message_type": msg_type,
                        "from_name": self.client.username,
                        "has_video": has_video,
                        "new": True,
                        "date": datetime.now().isoformat(),
                        "attachment_url": file_url_holder,
                        "media_type": file_type
                    }

                    send_file_req = self.client.session.post("https://www.textnow.com/api/v3/send_attachment",
                                                             data=json_data,
                                                             headers=self.client.headers, cookies=self.client.cookies)
                    return send_file_req
                else:
                    raise self.client.FailedRequest(str(place_file_req.status_code))
        else:
            raise self.client.FailedRequest(str(file_url_holder_req.status_code))
