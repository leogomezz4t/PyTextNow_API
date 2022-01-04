from pytextnow.message import Message
import requests
import cloudscraper

MULTIMEDIA_MESSAGE_TYPE = 1

scraper = cloudscraper.create_scraper()

class MultiMediaMessage(Message):
    def __init__(self, msg_obj, outer_self):
        super().__init__(msg_obj, outer_self)
        file_req = scraper.get(self.content)
        self.raw_data = file_req.content
        self.content_type = file_req.headers["Content-Type"]
        self.extension = self.content_type.split("/")[1]
        self.type = MULTIMEDIA_MESSAGE_TYPE
        self.self = outer_self

    def mv(self, file_path=None):
        if not file_path:
            file_path = f"./file.{self.extension}"
        with open(file_path, mode="wb") as f:
            f.write(self.raw_data)
