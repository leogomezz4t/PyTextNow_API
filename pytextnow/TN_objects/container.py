import datetime


class Container(list):
    def __init__(self, item_list: list):
        super().__init__(item_list)
        self.item_list = item_list

    def __str__(self):
        return str(self.item_list)

    def filter(self, **kwargs):
        filtered_list = []
        for item in self.item_list:
            if all(key in item.__dict__.keys() for key in kwargs):
                if all(getattr(item, key) == val for key, val in dict(kwargs).items()):
                    filtered_list.append(item)

        setattr(self, 'item_list', filtered_list)
        return self

    def order_by(self):
        """
        NOTE: This ONLY supports ordering by date and only
        if the objects have a date field. Otherwise the list
        will be in the same order it was on call to this method


        Order by the values corresponding to the passed
        field
        """
        try:
            # Modify this objects item list
            new_items = self.item_list.sort(key=lambda obj: self.str_to_date(obj.date), reversed=True)
            setattr(self, 'item_list', new_items)
            return self
        except:
            return self

    def first(self):
        """
        Returns the first object in the list
        """
        return None if len(self.item_list) == 0 else self.item_list[0]

    @staticmethod
    def str_to_date(string):
        """
        Convert a string into a datetime object
        """
        # This may not work
        return datetime.datetime.strptime(string)

    @property
    def length(self):
        return len(self.item_list)