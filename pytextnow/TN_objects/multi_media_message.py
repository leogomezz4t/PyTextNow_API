from pytextnow.TN_objects.message import Message
from pytextnow.tools.constants import MULTIMEDIA_MESSAGE_TYPE
import requests


class MultiMediaMessage(Message):
    def __init__(self, raw_obj, from_db=False):
        super(MultiMediaMessage, self).__init__(raw_obj, from_db=from_db)
        self.db_id = None
        self.raw_obj = raw_obj
        # Can't be filled from the database
        if not from_db:
            file_req = requests.get(self.content)
            self.raw_data = file_req.content
            self.content_type = file_req.headers["Content-Type"]
            self.extension = self.content_type.split("/")[1]
        else:
            self.raw_data = {}
            self.content_type = self.raw_obj['content_type']
            self.extension = self.raw_obj['extension']
            self.db_id = self.raw_obj['db_id']
            self.user_id = self.raw_obj['user_id']
            self.contact_id = self.raw_obj['contact_id']
        self.type = MULTIMEDIA_MESSAGE_TYPE

    def mv(self, file_path=None):
        if not file_path:
            file_path = f"./file.{self.extension}"
        with open(file_path, mode="wb") as f:
            f.write(self.raw_data)

    @staticmethod
    def cls_type():
        return 1