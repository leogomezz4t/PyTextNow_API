class ClassProxy(object):
    """
    A proxy class to allow instantiation without needing required
    arguments
    """
    def __init__(self, proxied_class, db_data={}) -> None:
        self._proxied_class = proxied_class()
        self.db_data = db_data

    def instantiate_class(self, data):
        return self.proxied_class(**data)

    def __getattr__(self, attr):
        def wrapped_method(*args, **kwargs):
            result = getattr(self.__proxied, attr)(*args, **kwargs)
            return result    
        return wrapped_method

class DatabaseMeta(type):
    def __new__(cls, clsname, superclasses, attributedict):
        new_dict = {}
        print("clsname: ", clsname)
        print("superclasses: ", superclasses)
        print("attributedict: ", attributedict)
        is_sms = False
        is_user = False
        is_mms = False
        is_contact = False
        attrs = list(attributedict.keys())
        if 'content' in attrs and 'extension' not in attrs:
            is_sms = True
        elif 'extension' in attrs:
            is_mms = True
        elif 'name' in attrs:
            is_contact = True
        elif 'sid' in attrs or 'username' in attrs:
            is_user = True
        
        # Replace the attribute dictionary
        if is_sms:
            # Assign new attributedict because we have to parse the data
            new_dict['message'] = attributedict.get('content')
            new_dict['contact_value'] = attributedict.get('number')
            new_dict['first_contact'] = attributedict.get('first_contact')
            new_dict['date'] = attributedict.get('date')
            new_dict['read'] = attributedict.get('read')
            new_dict['id'] = attributedict.get('id')
            new_dict['db_id'] = attributedict.get('db_id')
            new_dict['direction'] = attributedict.get('message_direction')
            new_dict['type'] = attributedict.get('type')

        elif is_mms:
            new_dict['message'] = attributedict.get('content')
            new_dict['contact_value'] = attributedict.get('number')
            new_dict['first_contact'] = attributedict.get('first_contact')
            new_dict['date'] = attributedict.get('date')
            new_dict['read'] = attributedict.get('read')
            new_dict['id'] = attributedict.get('id')
            new_dict['db_id'] = attributedict.get('db_id')
            new_dict['direction'] = attributedict.get('message_direction')
            new_dict['content_type'] = attributedict.get('content')
            new_dict['extension'] = attributedict.get('extension')
            new_dict['type'] = attributedict.get('type')
        #elif is_user:
         #   new_dict['sid'] = attributedict.get('sid')
          #  new_dict['username'] = attributedict.get('username')
           # new_dict['db_id'] = attributedict.get('db_id')
      #  elif is_contact:
       #     new_dict['name'] = attributedict
            # Figure out which attrs correspond to which fields
            # fill attrs
            # if message, will have content but no extension
            # if mms, will have extension
            # if contact will have name
            # if user will have sid/username
        # Return __new__ class
        return type.__new__(cls, clsname, superclasses, attributedict)