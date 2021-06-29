class User:

    def __init__(self, username=None, sid=None, db_id=None, *args, **kwargs) -> None:
        self.db_id = db_id
        self.sid = sid
        self.username = username
    
    def __str__(self):
        return f'<{self.__class__.__name__} db_id={self.db_id}>'
