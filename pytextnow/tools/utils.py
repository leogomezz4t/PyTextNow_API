import time
from pytextnow.TN_objects.contact import Contact
from pytextnow.TN_objects.message import Message
from pytextnow.TN_objects.container import Container
from pytextnow.TN_objects.multi_media_message import MultiMediaMessage
from pytextnow.TN_objects.user import User
from pytextnow.tools.constants import *


def map_to_class(data_dict=None, data_dicts=None, multiple=False, or_none=False):
    """
    !!!WARNING!! There is a possible error here where, if you pass only
    one dictionary and leave multiple=False you'll ge

    Take in a dictionary and match the information inside of it to
    an object then loop the keys/values (attributes and values),
    set the objects attributes and return it
    """
    if not data_dict and not data_dicts:
        raise Exception(
            "You must pass either a data dictionary or pass "
            "multiple=True and a list of data dictionaries "
            "Location: tools -> utils.py -> map_to_class()"
        )
    def __map_it(data_dict):
        objects = {
            MESSAGE_TYPE: Message,
            MULTIMEDIA_MESSAGE_TYPE: MultiMediaMessage,
            USER_TYPE: User,
            CONTACT_TYPE: Contact,
        }
        mapped_obj = None
        # The easy way...there's an object type :)
        if "object_type" in data_dict.keys():
            # Get the FK Field then replace the one from the db
            # with a normalized db_id attribute
            fk_field = FK_FIELDS.get(objects.get(data_dict['object_type']).__name__)
            data_dict['db_id'] = data_dict[fk_field]
            obj = objects.get(data_dict['object_type'])(from_db=True, raw_obj=data_dict)
            return obj
        # Find the object we must map to
        if 'content' in list(data_dict.keys()) and 'extension' not in list(data_dict.keys()):
            mapped_obj = objects.get(MESSAGE_TYPE)
        elif 'extension' in list(data_dict.keys()):
            mapped_obj = objects.get(MULTIMEDIA_MESSAGE_TYPE)
        elif 'name' in list(data_dict.keys()):
            mapped_obj = objects.get(CONTACT_TYPE)
        elif 'password' in list(data_dict.keys()) or 'username' in list(data_dict.keys()):
            mapped_obj = objects.get(USER_TYPE)
        if not mapped_obj:
            raise Exception(
                f"Failed to find object with one or more of the following attributes: {data_dict.keys()} "
                "Location: tools -> utils.py -> map_to_class() -> __map_it()"
            )
        return mapped_obj

    if multiple:
        if data_dicts and len(data_dicts) > 0:
            objs = []
            for data_dict in data_dicts:
                objs.append(__map_it(data_dict))
            # Wrap the objects in the appropriate container
            # or return a normal list of objects
            container = Container(objs)
            return container
        elif or_none:
            return None
        else:
            raise Exception(
                "ERROR: List of data dictionaries cannot be None or empty!"
                "Location: tools -> utils.py -> map_to_class()"
            )
    return __map_it(data_dict)

def date_to_str(dt_time):
    """
    Convert a date time object into a string
    """
    return 10000 * dt_time.year + 100 * dt_time.month + dt_time.day
