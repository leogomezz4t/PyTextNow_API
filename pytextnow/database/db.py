from ..TN_objects.container import Container
from ..TN_objects.message import Message
from ..TN_objects.multi_media_message import MultiMediaMessage
from ..TN_objects.contact import Contact
from ..TN_objects.user import User
from ..tools.constants import *
from ..tools.utils import map_to_class

import sqlite3
import typing


class BaseDatabaseHandler(object):
    # CRUD
    def __init__(
            self, db_name: str = "textnow_API.sqlite3",
            schema: typing.Dict[str, typing.Dict[str, str]] = {},
            uneven_classes=True
    ) -> None:
        self.__database = sqlite3.connect(db_name)
        self.__cursor = self.__database.cursor()
        # In case we want to change the database at somepoint
        self.__default_tables = {
            # Should be valid and dynamically compatible
            "sms": {
                "content": "TEXT",  # Common
                'number': "TEXT",  # Common
                'date': "TEXT",  # Common (Change to datetime)
                'first_contact': "TEXT",  # Common
                'read': "TEXT",  # Common
                'db_id': "INTEGER",  # Common
                'sent': "TEXT",  # Common
                'received': "TEXT",  # Common
                'direction': "INTEGER",  # Common,
                'id': "TEXT",
                # Integer because of constants
                "object_type": "INTEGER"  # 1 # Common
            },
            "mms": {
                "content": "TEXT",
                'number': "TEXT",
                'date': "TEXT",
                'first_contact': "TEXT",
                'read': "TEXT",
                'db_id': "INTEGER",
                'direction': "INTEGER",
                'content_type': "TEXT",  # UNCOMMON
                'extension': "TEXT",  # UNCOMMON
                'type': "INTEGER",
                'id': "TEXT",
                "object_type": "INTEGER"  # 2
            },
            "users": {
                'db_id': "INTEGER",
                'username': "TEXT",  # UNCOMMON
                "sid": "TEXT",  # UNCOMMON
                "object_type": "INTEGER"  # 3
            },
            "contacts": {
                'db_id': "INTEGER",
                'name': "TEXT",  # UNCOMMON
                'number': "TEXT",
                "object_type": "INTEGER"  # 4
            },
        }
        self.__tables = schema if schema else self.__default_tables
        self.__create_tables()
        self.__table_names = self.__assign_table_names()

    def _create_record(
            self, table_name: str,
            info: typing.Dict[str, str],
            return_mapped: typing.Optional[bool] = True,
    ) -> None:
        if info.get('db_id', None):
            raise Exception(
                "WARNING: Do not pass an DB_ID when creating an object "
                "because they are automatically created! "
                "Location: db.py -> DatabaseHandler -> create_record()"
            )
        self.__validate_data(table_name, info)
        columns = ""
        safe_values = []
        for column, value in info.items():
            if type(value) == type(int()):
                safe_values.append(value)
            else:
                safe_values.append(value)
            columns += f"{column}" + ", "
        # Gives back (one, two, three)
        safe_columns = f"{self.__clean_query(columns)}"
        sql = "INSERT INTO %s (%s) VALUES %s;" % (
            table_name, safe_columns, tuple(safe_values)
        )
        if return_mapped:
            return self._execute_sql(sql, commit=True, return_results=True)
        self._execute_sql(sql, commit=True)

    def filter(
            self, table_name: str,
            filters: typing.Dict[str, typing.Union[str, int, bool]]
    ) -> Container:
        """
        Filter a table based on the given parameters
        
        :param table_name: String name of the table to operate on
        :param filters: Dictionary of key value pairs where keys are
            fields and their values are the ones we will use to find
            the desired records.
        :return: Any TN_Object
        """
        # Using a filter with a trailing ", " causes an error
        # therefore it's unsafe until that's stripped off
        unsafe_filters = ""
        for column, value in filters.items():
            unsafe_filters += f"{column}='{value}', "
        safe_filters = self.__clean_query(unsafe_filters)
        sql = """SELECT * 
        FROM %s 
        WHERE %s;""" % (table_name, safe_filters)
        return self._execute_sql(sql, return_results=True)

    def _update_obj(self, table_name: str, db_id: int, new_data: typing.Dict[str, str], return_obj=True) -> None:
        """
        Update an object
        
        :param table_name: The name of the table as a string
        :param new_data: Dict where keys are columns and values are their new values
        :return: db_id
        """

        self.__validate_data(table_name, new_data)
        ordered_values = []
        set_data = ""
        for column, value in new_data.items():
            set_data += f"{column} = '{value}' "
        set_data = self.__clean_query(set_data)
        sql = """ UPDATE %s
        SET %s
        WHERE db_id = %s;""" % (
            table_name, set_data, db_id
        )

        if return_obj:
            # Update the record
            self._execute_sql(
                sql, tuple(ordered_values)
            )
            # Get the updated record and try to return the result
            result = self._execute_sql(
                f"""
                SELECT *
                FROM {table_name}
                WHERE db_id = {db_id};
                """, return_results=True
            )
            try:
                return result[0]
            except sqlite3.OperationalError:
                return None
            except IndexError:
                return None
            except Exception as e:
                # 
                print(
                    "\n\n!!!WARNING!!! Uncaught exception in __BasedatabaseHandler._update_obj() "
                    "ERROR: ", e,
                    "\n\nReturning None...\n"
                )
                return None
        # Update the record
        self._execute_sql(
            sql, tuple(ordered_values),
            return_results=False
        )

    def __bulk_update(
            self,
            table_data: typing.Dict[str, typing.Dict[str, str]],
            return_objs: bool = False
    ) -> typing.Union[Container, None]:
        """
        Construct update operations then execute and commit the
        changes after fully building out the sql command

        :param data: A dictionary whose outer most keys are table names and values
            are a dictionary of data whos keys are field names and values
            are the new values to be inserted
        """
        if len(table_data.keys()) == 0 or len(table_data.values()):
            raise Exception(
                "ERROR: The data dictionary cannot be empty! "
                "Location: db.py -> DatabaseHandler -> bulk_update()"
            )
        results = []
        # Each table gets its own update statement
        for table_name, data in table_data.items():
            # Validation
            self.__validate_data(table_name, data)
            db_id = data.get('db_id', None)
            if not db_id:
                raise Exception(
                    f"ERROR: You must pass DB_IDs with every object you wish to update! "
                    "Location: db.py -> DatabaseHandler -> bulk_update()"
                )
            # Construct Query
            base_query = f"UPDATE {table_name}"
            set_clause = "SET "
            where_clause = f"WHERE db_id = {db_id}"
            set_data = []
            for column, value in data.items():
                set_clause + f"{column} = ?, "
                set_data.append("'" + value + "'")
            # Clean the query
            clean_set_clause = self.__clean_query(set_clause)
            # Produces
            # UPDATE user_sids SET username = some_username, sid = some_sid WHERE id = 2;
            # Execute the query
            results.append(self._execute_sql(
                f"""{base_query}
                {clean_set_clause}
                {where_clause}
                ;""",
                tuple(set_data),
                commit=True,
                return_results=return_objs
            ))
        if return_objs:
            return Container(results)

    def _delete_obj(self, table_name: str, db_id: int) -> None:
        """
        Delete an object

        :param table_name: The name of the table as a string
        :param db_id: The DB_ID of the object to delete
        """
        self._execute_sql(
            f'DELETE FROM {table_name} WHERE db_id={db_id}',
            return_results=False, commit=True
        )

    # Utilities

    def __create_table(
            self, table_name: str,
            info: typing.Dict[str, str]
    ) -> None:
        """
        Dynamically create a table based on the values given
        """
        # Add the table information to self.__tables for insert/update validation
        self.__tables[table_name] = info
        # Build the values of the table
        vals = "("
        # Add the id row if one wasn't passed
        db_id_done = False
        for column, col_type in info.items():
            # If the table already exits don't add another one lest we
            # get an error or mess up a stable database
            if self.__table_exists(table_name):
                print(f"Table {table_name} already exists")
                continue
            # Ensure IDs are unique, never none, auto increment and are defined
            # as primary keys
            if column == "db_id" and not db_id_done:
                vals += f"{column} {col_type} NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT, "
                db_id_done = True
                continue
                # Ensure important data is unique and not none
            if column in [
                "number", "phone_number",
                "sid", "username"
            ]:
                vals += f"{column} {col_type} NOT NULL UNIQUE, "
                continue
            vals += f"{column} {col_type}, "
        vals = self.__clean_query(vals)
        vals += ")"
        # If all the tables already exist, stripping out the ()
        # should leave the vals variable with a length of 0
        if len(vals.strip("(").strip(")")) == 0:
            # Nothing to do, exit
            return
        sql = 'CREATE TABLE %s %s' % (table_name, vals)
        self._execute_sql(sql, return_results=False, commit=True)

    def __assign_table_names(self):
        """
        get the name of the table that corresponds to the class
        name
        """
        objs = [
            Message,
            MultiMediaMessage,
            Contact,
            User,
        ]
        names = {}
        for obj in objs:
            for table_name, obj_name in TABLES_CLASSES.items():
                if obj_name == obj.__name__:
                    names[obj.__name__] = table_name
        return names

    def __create_tables(self) -> None:
        """
        Create the tables defined in self.__tables
        """
        for table_name, col_info in self.__tables.items():
            if self.__table_exists(table_name):
                continue
            else:
                self.__create_table(table_name, col_info)

    def __table_exists(self, table_name: str) -> bool:
        try:
            results = self._execute_sql("SELECT * FROM %s;" % (table_name), return_results=True)
            return True
        except sqlite3.OperationalError:
            return False
        except Exception as e:
            raise Exception(f"FAILED to see if table exists {e}")

    def __clean_query(self, sql_string: str) -> str:
        if sql_string.endswith(", "):
            return sql_string[:len(sql_string) - 2]
        else:
            print("No need to string the trailing ', ' as it doesn't exist")
            return sql_string

    def _execute_sql(
            self, sql: str,
            values: str = None, return_id: bool = False,
            return_class: bool = False,
            return_raw: bool = False, return_results: bool = True,
            commit: bool = False
    ):
        """
        A wrapper to execute any SQL. This is used to keep from
        having connections and such scattered through the class
        and catch any errors without having to repeatedly write
        try/excepts
        If no params are set to True, try to return a Results/Result object


        :param sql: The SQL to be executed        
        :param values: Values to be parameter bound to the sql command if any
        :param return_id: If True, return the db_id of the last created object    
        :param map_to_class: If True return a class corresponding to the type
            of object we're getting from the database whos attributes are
            filled by the information returned from the query
        :param return_class: If True, return an uninstantiated class corresponding
            to the type of object we're getting
        :param return_raw: If True, return the raw data returned from the database operation
        """
        try:
            print("\n\nSQL COMMAND:", sql, "\n\n")
            # If we're not commiting, we want the results for sure
            if values:
                results = self.__cursor.execute(sql, values)
            else:
                # Assume we're getting something. No harm if not
                results = self.__cursor.execute(sql)
            dicts = self.__dict_factory(results)
            if commit:
                self.__database.commit()
            elif not return_results:
                return
            elif return_id:
                return self.__cursor.lastrowid
            elif return_class:
                return map_to_class(results)[0].__class__
            elif return_raw:
                return results
            elif len(dicts) == 0:
                print("Empty results")
                return dicts
            elif return_results:
                # Map results to Results object  if len > 1
                return Container(
                    map_to_class(
                        data_dicts=dicts,
                        multiple=True
                    )
                )

            print("No arguments were True, not returning anything...")
            return

        except sqlite3.OperationalError as e:
            raise sqlite3.OperationalError(f"FAILED to execute sql command\n\n"
                                           f"SQL: {sql}\n\nVALUES: {values}\n\nERROR: {e}"
                                           )

    def __validate_data(
            self, table_name, data: typing.Dict[str, typing.Dict[str, str]]
    ) -> None:
        """
        Ensure we have the correct data in the correct format
        so we don't get a failed commit
        """

        col_types = {
            "TEXT": str,
            "INTEGER": int
            # "BOOLEAN": bool <-- Requires custom db type
        }
        cls_name = TABLES_CLASSES.get(table_name)
        if data.get('date'):
            data['date'] = str(data['date'])
        invalid_fields = {}
        for field in data.keys():
            if field not in TABLE_ATTRS.get(cls_name):
                invalid_field = invalid_fields.get(field, None)
                if not invalid_field:
                    invalid_fields[field] = f"Attribute {field} is not defined in table {table_name} attributes"
                else:
                    invalid_fields[field].append(f"Attribute {field} is not defined in table {table_name} attributes")
            # obj = map_to_class(data_dicts=[data], multiple=True).first()
        # Validate the data types
        # get schema for table
        for field, field_type in self.__tables.get(self.get_table_name(cls_name)).items():
            try:
                # Attempt to cast the data to the type its field requires
                f_type = col_types.get(field_type)(data.get(field))
            except:
                invalid_field = invalid_fields.get(field)
                if type(data.get(field)) == type(None):
                    # Null values...
                    continue
                error = f'INVALID DATA: The column "{field}" requires type ' \
                        f'{field_type} but got {type(data.get(field))} instead ' \
                        'Location: db.py -> __DatabaseHandler -> __validate_data()'
                # Failed to cast, cannot accept incompatible data
                if invalid_field:
                    invalid_fields[field].append(error)
                else:
                    invalid_fields[field] = [error]
        if len(list(invalid_fields.keys())):
            print("\n\n!!!ERROR INVALID DATA!!!\n")
            for field, err in invalid_fields.items():
                print("Showing errors for field: ", field)
                print(err)
            quit()
        return True

    def __dict_factory(
            self, results: typing.List[sqlite3.Row]
    ) -> typing.List[typing.Dict[str, str]]:
        """
        Convert a list of query results into a dictionary
        add them to a list and return it
        """
        # Convert single results to lists
        if not type(results) == type(list):
            try:
                results = list(results)
            except:
                raise Exception(
                    "Attempted to convert results into a list but got an exception. "
                    "Location: db.py -> __DatabaseHandler -> __dict_factory()"
                )

        def __to_dict(result: sqlite3.Row) -> typing.Dict[str, str]:
            """
            Convert a result into a dictionary
            """
            result_dict = {}
            for index, column in enumerate(self.__cursor.description):
                result_dict[column[0]] = result[index]
            return result_dict

        dicts = []
        # Convert all results
        for result in results:
            dicts.append(__to_dict(result))
        return dicts

    def __close_connection(self) -> None:
        if self.__database:
            self.__database.close()
        else:
            print("Database is already closed, cannot close it again.")
            print(
                "Location: pytextnow -> database -> db.py -> "
                "DatabaseHandler -> __close_connection()"
            )

    def get_table_name(self, obj_name):
        """
        Get the table name that was given
        """
        return self.__table_names.get(obj_name)


class DatabaseHandler(BaseDatabaseHandler):
    """
    High level API for database interactions
    """

    def __init__(self, schema=None, db_name="text_nowAPI.sqlite3") -> None:

        super(DatabaseHandler, self).__init__(schema=schema, db_name=db_name)

    # High Level Helper Methods

    # Usernames & SID
    def get_all_users(self):
        return self._execute_sql("SELECT * FROM users;", return_results=True)

    def create_user(self, data: typing.Dict[str, str]) -> User:
        """
        Take in a dictionary where the keys are the fields
        and their values are the values to be inserted into
        the DB.
        NOTE: Both fields are required in the user_sids table
        example dict:{
                        "username": "some username",
                        "sid": "some sid"
                    }

        :param data: Dictionary whose keys are fields and values are
            the values to insert into the corresponding columns
        :return: User object
        """
        return self._create_record(self.get_table_name('User'), data)

    def get_user(self, username: str = None) -> typing.Union[User, None]:
        """
        Get the sid from the USER_SID table that corresponds
        to the given username or, if it's the only sid that exists,
        return what we find.

        :return: User object or None
        """
        # container of results
        container_obj = self.filter(self.get_table_name('User'), {'username': username})
        if container_obj:
            # print(f'container val: {container_obj}\ntype: {type(container_obj)}')
            return container_obj.first()
        return

    def update_user(self, db_id, new_data: typing.Dict[str, str]) -> typing.Union[User, None]:
        """
        Update a user record in the database

        :param new_data: Dictionary whose keys are fields and values
            are the new values for the field.
            MUST contain a key 'db_id' with an integer value of an existing object
        """
        return self._update_obj(self.get_table_name('User'), db_id, new_data)

    def user_exists(
            self, username: str = None,
            sid: str = None, return_user: bool = False
    ) -> typing.Union[bool, User]:
        """
        Return True/False if user exists in db
        """
        # Figure out which field was provided
        if not username and not sid:
            raise Exception(
                "To check if a user exists, pass either a username or sid "
                "Location: db.py -> DatabaseHandler -> user_exists()"
            )
        # Assign the field
        field = "username" if username else "sid"
        value = username or sid
        results = self.filter(
            self.get_table_name('User'), {field: value}
        )
        return len(results) > 0

    def delete_user(self, db_id: int) -> None:
        self._delete_obj(self.get_table_name('User'), db_id)

    # Contacts
    def contact_exists(
            self, name=None, number=None,
            return_user: bool = False
    ) -> typing.Union[bool, User]:
        """
        Return True/False if contact exists in db
        """
        if not name and not number:
            raise Exception(
                "To check if a contact exists, pass either a username or sid "
                "Location: db.py -> DatabaseHandler -> contact_exists()"
            )
        field = "name" if name else "number"
        value = name or number
        results = self.filter(
            self.get_table_name('Contact'), {field: value}
        )
        return isinstance(results[0], Contact.__class__)

    def create_contact(self, data: typing.Dict[str, str]) -> Contact:
        self._create_record(self.get_table_name('Contact'), data)

    def get_all_contacts(self) -> Container:
        # returns results by default
        return self._execute_sql("SELECT * FROM %s;" % (self.get_table_name('Contact')))

    def update_contact(
            self, db_id,
            info_dict, return_obj=True,
    ) -> typing.Union[None, Contact]:
        """
        :param info_dict: Dictionary with new information to update the record with
            MUST contain a key 'db_id' with an integer value of an existing object
        """
        if return_obj:
            return self._update_obj(self.get_table_name('Contact'), db_id, info_dict, return_obj=True)
        else:
            self._update_obj(self.get_table_name('Contact'), db_id, info_dict)

    def delete_contact(self, db_id):
        self._delete_obj(self.get_table_name("Contact"), db_id)

    # SMS

    def create_sms(self, data):
        self._create_record(self.get_table_name('Message'), data)

    def get_all_sms(self, sent=False, received=True):
        """
        Get and return ALL sms

        :param sent_only: If True, only get sms that the user sent
        :param received_only: Default of True, If True, return only sms the user received
            ordered by the time they were received (newest first)
        """
        if sent:
            # TODO: Either make sent/received attrs in Message object or figure out which
            # fields can represent them
            return self.filter(self.get_table_name('Message'), {'sent': "True"})
        elif received:
            return self.filter(self.get_table_name('Message'), {'received': "True"})
        # Return both sent and received
        return self._execute_sql("SELECT * FROM %s;" % (self.get_table_name("Message")))

    def get_sms(self, filters):
        """
        This is mainly for getting sms by dates.
        NOTE You MUST pass a string version of a date time object
        to filter by dates. Use str(date_object)


        :param filters: A dictionary of conditions to be met 
            key = field name, value is it's expected value
        """
        return self.filter(self.get_table_name('Message'), filters)

    # No need to update a message. If need be, use self._update_obj()

    def delete_sms(self, db_id):
        self._delete_obj(self.get_table_name('Message'), db_id)

    # MMS sms
    def create_mms(self, data):
        return self._create_record(self.get_table_name('MultiMediaMessage'), data)

    def get_all_mms(self):
        return self._execute_sql("SELECT * FROM %s;" % (self.get_table_name("MultiMediaMessage")))

    def get_mms(self, filters):
        return self.filter(self.get_table_name('MultiMediaMessage'), filters)

    def delete_mms(self, db_id):
        self._delete_obj(self.get_table_name('MultiMediaMessage'), db_id)
