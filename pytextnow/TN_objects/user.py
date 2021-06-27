
class User(object):

    def __init__(self, username, sid=None, db_id=None) -> None:
        self.db_id = db_id
        self.sid = sid
        self.username = username