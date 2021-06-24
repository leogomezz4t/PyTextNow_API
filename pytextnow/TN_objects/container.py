class Container(list):
    def __init__(self, item_list: list):
        super().__init__(item_list)
        self.item_list = item_list

    def __str__(self):
        ss = [item.__str__() for item in self.item_list]
        s = '[' + "\n".join(ss) + ']'
        return s

    def filter(self, **kwargs):
        filtered_list = []
        for item in self.item_list:
            if all(key in item.__dict__.keys() for key in kwargs):
                if all(getattr(item, key) == val for key, val in dict(kwargs).items()):
                    filtered_list.append(item)

        return Container(filtered_list)

    # is this necessary?
    # where is it being used?
    def get(item_list, **kwargs):
        filtered_list = []
        for item in item_list:
            if all(key in item.__dict__.keys() for key in kwargs):
                if all(getattr(item, key) == val for key, val in dict(kwargs).items()):
                    filtered_list.append(item)

        return Container(filtered_list)
