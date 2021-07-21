from os import stat
from dateutil import parser

class Message:
    def __init__(self, raw_obj, from_db=False): 
        self.raw_obj = raw_obj
        if from_db:
            self.content = self.raw_obj['content']
            self.number = self.raw_obj["number"]
            self.first_contact = self.raw_obj['first_contact']
            self.direction = self.raw_obj["direction"]
            # Work around for no id on object creation
            self.db_id = self.raw_obj['db_id']
            self.user_id = self.raw_obj['user_id']
            self.contact_id = self.raw_obj['contact_id']

        else:
            self.first_contact = self.raw_obj["conversation_filtering"]["first_time_contact"]
            self.direction = self.raw_obj["message_direction"]
            self.content = self.raw_obj["message"]
            self.number = self.raw_obj["contact_value"]

        self.date = parser.parse(self.raw_obj["date"])
        self.read = self.raw_obj["read"]
        self.id = self.raw_obj["id"]
        self.raw = self.raw_obj

    def __str__(self):
        return f'<{self.__class__.__name__} number: {self.number}, content: {self.content}>'

    @staticmethod
    def cls_type():
        return 0