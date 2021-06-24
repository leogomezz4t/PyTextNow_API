from pytextnow.database.db import DatabaseHandler


class User(object):

    def __init__(self, username, sid=None, id=None) -> None:
        self.id = id
        self.db_handler = DatabaseHandler()
        self._sid = sid
        self.username = username
        if not self._sid and self.username:
            self.get_sid(self.username)
        super().__init__()

    def get_sid(self, username: str):
        """
        Get a users SID by username or return None
        """
        return self.db_handler._map_to_class(
            self.db_handler.filter(
                "user_sids", {
                    "username": username
                }
            )[0]
        ).sid

    @property
    def sid(self):
        """
        Work around for self.get_sid() throwing an error when
        we get no sid from the database
        """
        return self._sid if len(self._sid) > 0 else None
