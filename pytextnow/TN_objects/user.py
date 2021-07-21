class User:
    def __init__(
            self, raw_obj,
            from_db=False
        ) -> None:
        self.raw_obj = raw_obj
        self.db_id = self.raw_obj['db_id']
        self.username = self.raw_obj['username']
        self.password = self.raw_obj['password']

    def __str__(self):
        return f'<{self.__class__.__name__} db_id={self.db_id}>'
    
    @staticmethod
    def cls_type():
        return 3