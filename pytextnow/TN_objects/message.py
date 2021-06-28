from datetime import datetime
import datetime as dt
from urllib.parse import quote

import mimetypes
import json
import time

MESSAGE_TYPE = 0


class Message:
    def __init__(self, from_db=False, **kwargs):
        print("\n\nFrom Message.__init__\n",json.dumps(kwargs, indent=4))
        msg_obj = kwargs
        if from_db:
            self.content = msg_obj['content']
            self.number = msg_obj["number"]
            self.first_contact = msg_obj['first_contact']
            self.direction = msg_obj["direction"]
            # Work around for no id on object creation
            self.db_id = msg_obj.get('db_id')

        else:
            self.first_contact = msg_obj["conversation_filtering"]["first_time_contact"]
            self.direction = msg_obj["message_direction"]
            self.content = msg_obj["message"]
            self.number = msg_obj["contact_value"]

        self.date = datetime.fromisoformat(msg_obj["date"])
        self.read = msg_obj["read"]
        self.id = msg_obj["id"]
        self.raw = msg_obj

    def __str__(self):
        s = f"<{self.__class__.__name__} number: {self.number}, content: {self.content}>"
        return s