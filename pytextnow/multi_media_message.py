from pytextnow.message import Message
import cloudscraper

MULTIMEDIA_MESSAGE_TYPE = 1

scraper = cloudscraper.create_scraper()

from pytextnow.message import Message
import requests

from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import quote
import mimetypes
import json
import time

MESSAGE_TYPE = 0

MULTIMEDIA_MESSAGE_TYPE = 1


class MultiMediaMessage(Message):
    def __init__(self, msg_obj, outer_self):
        super().__init__(msg_obj, outer_self)
        try:
            file_req = requests.get(self.content)
            self.raw_data = file_req.content
            self.content_type = file_req.headers["Content-Type"]
            self.extension = self.content_type.split("/")[1]
            self.type = MULTIMEDIA_MESSAGE_TYPE
            self.self = outer_self
        except:
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


    def mv(self, file_path=None):
        if not file_path:
            file_path = f"./file.{self.extension}"
        with open(file_path, mode="wb") as f:
            f.write(self.raw_data)
