class ContactContainer(list):
    def __init__(self, contact_list: list):
        super().__init__(contact_list)
        self.contact_list = contact_list

    def __str__(self):
        ss = [contact.__str__() for contact in self.contact_list]
        s = '[' + "\n".join(ss) + ']'
        return s

    def get(self, **kwargs):
        filtered_list = []
        for contact in self.contact_list:
            if all(key in contact.__dict__.keys() for key in kwargs):
                if all(getattr(contact, key) == val for key, val in dict(kwargs).items()):
                    filtered_list.append(contact)

        return ContactContainer(filtered_list)
