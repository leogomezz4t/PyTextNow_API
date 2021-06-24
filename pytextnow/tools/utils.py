from database.objects import Results
from TN_objects.contact_container import ContactContainer
from TN_objects.message_container import MessageContainer
import datetime
from TN_objects.contact import Contact
from TN_objects.message import Message
from TN_objects.multi_media_message import MultiMediaMessage
from TN_objects.user import User
from constants import *

def map_to_class(data_dict=None, dynamic_map=True, data_dicts=None, multiple=False, or_none=False):
    """
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
    containers = {
        MESSAGE_TYPE: MessageContainer,
        CONTACT_TYPE: ContactContainer,
    }
    def __map_it(data_dict):
        objects = {
            MESSAGE_TYPE: Message,
            MULTIMEDIA_MESSAGE_TYPE: MultiMediaMessage,
            USER_TYPE: User,
            CONTACT_TYPE: Contact
        }

        mapped_obj = None
        # The easy way...there's an object type :)
        if "object_type" in data_dict.keys():
            obj = objects.get("obj_type")
            for attr, value in data_dict.items():
                # Set the attr if it exists
                if hasattr(obj, attr):
                    setattr(obj, attr, value)
                # Warn the developer and continue trying to map attrs
                else:
                    print(
                            f"WARNING: Object of type {data_dict.get('object_type')} "
                            f"does not have the attribute {attr}. There may be "
                            "missing information in your class!!"
                            "\n\n!!!Disregard if updating a record or inserting an incomplete record!!!"
                        )
            return obj

            # 
        # Find the object we must map to
        # FIX ME - SymanticError("
        # # {'name': "Trippy"}
            # {'name': "", 'number': ""}
            # We have a name so does the other dict - assign current to mapped_obj
            # We don't have name, don't assign and move on")
        for obj in objects.values():
            for attr in obj.__dict__.keys():
                # Mismatched attributes, go to the next object
                if attr not in data_dict.keys():
                    mapped_obj = None
                    continue
                else:
                    # Don't reassign for no reason
                    if not mapped_obj:
                        mapped_obj = obj
            # There was a mismatched attribute, go to the next object
            if not mapped_obj:
                continue
        if not mapped_obj:
            raise Exception(
                f"Failed to find object with one or more of the following attributes: {data_dict.keys()} "
                "Location: tools -> utils.py -> map_to_class() -> __map_it()"
            )
        # Actually map the object
        for attr, value in data_dict.items():
            setattr(mapped_obj, attr, value)
        return mapped_obj

    if multiple:
        if data_dicts and len(data_dicts) > 0:
            objs = []
            for data_dict in data_dicts:
                objs.append()
            # Wrap the objects in the appropriate container
            # or return a normal list of objects
            container = containers.get(objs[0].object_type, None)(objs)
            return container if container and dynamic_map else Results(objs)
        elif or_none:
            return None
        else:
            raise Exception(
                "ERROR: List of data dictionaries cannot be None or empty!"
                "Location: tools -> utils.py -> map_to_class()"
            )
    return __map_it(data_dict)
    

def serialize(obj):
    """
    Syntactic sugar for turning a classes attributes into
    a dictionary
    """
    return obj.__dict__.items()


def str_to_date(self, string):
    """
    Convert a string into a datetime object
    """
    # This may not work
    return datetime.datetime.strptime(string)
    
def date_to_str(self, dt_time):
    """
    Convert a date time object into a string
    """
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day
