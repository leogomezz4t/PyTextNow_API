from .message import Message
import json
MULTIMEDIA_MESSAGE_TYPE = 1


class MultiMediaMessage(Message):
    def __init__(self, from_db=False, *args, **kwargs):
        print("MULTI-MEDIA MESSAGE\n", json.dumps(kwargs, indent=4))
        super(MultiMediaMessage, self).__init__(from_db=from_db, **kwargs)
        self.db_id = None
        msg_obj = kwargs
        # Can't be filled from the database
        if not from_db:
            file_req = self.client.session.get(self.content)
            self.raw_data = file_req.content
            self.content_type = file_req.headers["Content-Type"]
            self.extension = self.content_type.split("/")[1]
        else:
            self.raw_data = {}
            self.content_type = msg_obj['content_type']
            self.extension = msg_obj['extension']
        self.type = MULTIMEDIA_MESSAGE_TYPE

    def mv(self, file_path=None):
        if not file_path:
            file_path = f"./file.{self.extension}"
        with open(file_path, mode="wb") as f:
            f.write(self.raw_data)
