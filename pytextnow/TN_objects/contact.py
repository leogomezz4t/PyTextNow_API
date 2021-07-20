class Contact:
    def __init__(self, raw_obj, from_db=False):
        self.raw_obj = raw_obj
        self.db_id = None
        if not from_db:
            self.number = self.raw_obj.get("contact_value")
        else:
            self.number = self.raw_obj.get('number')
        self.name = self.raw_obj.get("name")

    def __str__(self):
        s = f"<Contact number={self.number}, name={self.name}>"
        return s