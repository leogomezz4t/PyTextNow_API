"""
This file holds all objects that are used by the database
handler
"""
import datetime
import typing
from tools.utils import map_to_class, str_to_date

class Results(object):
    """
    An object to represent multiple results gotten from database
    operations
    """
    def __init__(self, results, ordering="desc-date") -> None:
        """
        An object to represent database query results
        in python objects
        """
        # Automated validation happens in map_to_class
        if ordering == "desc-date":
            self.objects = self.order_by(map_to_class(data_dicts=results, multiple=True, or_none=True))
        else:
            raise NotImplementedError(
                "Orderings other than descending date are not yet implemented.\n\n"
                "Please submit a Pull Request if you feel so inclined"
            )
        super().__init__()

    def first(self):
        return self.objects if isinstance(self.objects, None) else self.objects[0]

    def filter(self, conditions: typing.Dict[str, str]):
        """
        Take in conditions and filter the results we have then
        return what we find
        """
        found = []
        unmet_conditions = conditions.copy()
        # Loop the objects we have
        for obj in self.objects:
            # Go through the conditions
            for field, value in conditions.items():
                # If the object actually has the attribute
                if hasattr(obj, field):
                    if getattr(obj, field) == value:
                        unmet_conditions.pop(field)
                else:
                    raise Exception(
                        f'Cannot filter by {field} because object of type {obj.__class__.__name__} '
                        'does not have that attribute '
                        'Location: database -> objects.py -> Results -> filter()'
                    )
            if len(unmet_conditions) == 0:
                found.append(obj)
        return found
    
    def order_by(self, objects):
        """
        NOTE: This ONLY supports ordering by date and only
        if the objects have a date field. Otherwise the list
        will be in the same order it was fetched from the database.


        Order by the values corresponding to the passed
        field
        """
        try:
            return objects.sort(key=lambda obj: str_to_date(obj.date), reversed=True)
        except:
            return objects