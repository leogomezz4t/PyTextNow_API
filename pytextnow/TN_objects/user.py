class User:

    def __init__(
            self, username=None,
            number=None, sid=None,
            password="", db_id=None,
            logged_in=False,
            *args, **kwargs
        ) -> None:
        self.db_id = db_id
        self.sid = sid
        self.username = username
        self.password = password
        self.number = number
        self.logged_in = False
    
    def __str__(self):
        return f'<{self.__class__.__name__} db_id={self.db_id}>'