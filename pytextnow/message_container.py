class MessageContainer(list):
    def __init__(self, msg_list: list, outer_self):
        super().__init__(msg_list)
        self.msg_list = msg_list
        self.outer_self = outer_self

    def __str__(self):
        ss = [msg.__str__() for msg in self.msg_list]
        s = '[' + "\n".join(ss) + ']'
        return s

    def get(self, **kwargs):
        filtered_list = []
        for msg in self.msg_list:
            if all(key in msg.__dict__.keys() for key in kwargs):
                if all(getattr(msg, key) == val for key, val in msg.__dict__.items()):
                    filtered_list.append(msg)

        return self.outer_self.MessageContainer(filtered_list, self.outer_self)
