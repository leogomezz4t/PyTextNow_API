from pytextnow.TN_objects.container import Container
from pytextnow.TN_objects.contact import Contact
from pytextnow.TN_objects.user import User
from pytextnow.tools.utils import map_to_class
from pytextnow.database.objects import Results

import datetime
import sqlite3
import typing


class __BaseDatabaseHandler(object):
  # CRUD
    def __init__(
        self, schema: typing.Dict[str, typing.Dict[str, str]] = None,
        db_name: str = "text_nowAPI.sqlite3"
        ) -> None:
        self.__db_name = db_name
        self.__database = sqlite3.connect(self.__db_name)
        self.__cursor = self.__database.cursor()
        # In case we want to change the database at somepoint
        self.__tables = schema if schema else {
            # Should be valid and dynamically compatible
            "sms" : {
                "content": "TEXT",
                'number': "TEXT",
                'date': "TEXT",
                'first_contact': "TEXT",
                'type': "INTEGER",
                'read': "TEXT",
                'id': "INTEGER",
                'direction': "INTEGER",
                # Integer because of constants
                "object_type": "INTEGER" # 1
            },
            "mms": {
                "content": "TEXT",
                'number': "TEXT",
                'date': "TEXT",
                'first_contact': "TEXT",
                'type': "INTEGER",
                'read': "TEXT",
                'id': "INTEGER",
                'direction': "INTEGER",
                'content_type': "TEXT",
                'extension': "TEXT",
                'type': "INTEGER",
                "object_type": "INTEGER" # 2
            },
            "user_sids": {
                'id': "INTEGER",
                'username': "TEXT",
                "sid": "TEXT",
                "object_type": "INTEGER" # 3
            }, 
            "contacts": {
                'id': "INTEGER",
                'name': "TEXT",
                'number': "TEXT",
                "object_type": "INTEGER" # 4
            },
        }

    def __create_record(
            self, table_name: str,
            info: typing.Dict[str, str],
            return_mapped: typing.Optional[bool] = True,
        ) -> None:
        if info.get('id', None):
            raise Exception(
                "WARNING: Do not pass an ID when creating an object "
                "because they are automatically created! "
                "Location: db.py -> DatabaseHandler -> create_record()"
            )
        self.__validate_data(info)
        unsafe_params = ""
        columns = ""
        safe_values = []
        for column, value in info.items():
            safe_values.append(value)
            columns+f"{column}"+", "
            unsafe_params+"?, "
        # Gives back (one, two, three)
        safe_columns = f"({self.__clean_query(columns)})"
        # Gives back (?, ?, ?, ...)
        question_marks = f"({self.__clean_query(unsafe_params)})"
        sql = f"INSERT INTO {table_name}{safe_columns} VALUES {question_marks}"
        if return_mapped:
            return self.__execute_sql(sql, tuple(safe_values))
        self.__execute_sql(sql, tuple(safe_values))

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
        if not info.get('id', None):
            info['id'] = "INT"
        for column, col_type in info.items():
            # If the table already exits don't add another one lest we
            # get an error or mess up a stable database
            if not self.__table_exists(table_name):
                # Ensure IDs are unique, never none, auto increment and are defined
                # as primary keys
                if column == "id":
                    vals += f"{column} {col_type} NOT NULL UNIQUE AUTOINCREMENT PRIMARY KEY, "
                # Ensure important data is unique and not none
                if column in [
                        "number", "phone_number",
                        "sid", "username"
                    ]:
                    vals += f"{column} {col_type} NOT NULL UNIQUE, "
                    continue
                vals += f"{column} {col_type}, "
            else:
                continue
        vals += ")"
        # If all the tables already exist, stripping out the ()
        # should leave the vals variable with a length of 0
        if len(vals.strip("(").strip(")")) == 0:
            # Nothing to do, exit
            return self.__close_connection()
        vals = self.__clean_query(vals)
        sql = f'CREATE TABLE {table_name} '+ vals
        self.__execute_sql(sql, return_results=False)

    def __filter(
            self, table_name: str,
            filters: typing.Dict[str, typing.Union[str, int, bool]]
        ) -> Results:
        """
        Filter a table based on the given parameters
        """
        # Using a filter with a trailing ", " causes an error
        # therefore it's unsafe until that's stripped off
        unsafe_filters = ""
        for column, value in filters.items():
            unsafe_filters += f"{column}={value}, "
        safe_filters = self.__clean_query(unsafe_filters)
        sql = f"FROM {table_name} SELECT * WHERE "+safe_filters+";"
        return self.__execute_sql(sql)

    def __update_obj(self, table_name: str, new_data: typing.Dict[str, str]) -> None:
        """
        Update an object
        
        :param table_name: The name of the table as a string
        :param new_data: Dict where keys are columns and values are their new values
        :return: project id
        """
        self.__validate_data(new_data)
        if obj_id := not new_data.get('id', None):
            raise Exception(
                "You must pass the object id to update a record! "
                "Location: db.py -> DatabaseHandler -> update_obj()"
            )
        ordered_values = []
        set_data = ""
        for column, value in new_data.items():
            # Save the id of the object and continue
            if column == "id":
                continue
            set_data+=f"{column} = ?, "
            ordered_values.append(value)
        set_data = self.__clean_query(set_data)
        sql = f""" UPDATE {table_name}
                SET {set_data}
                WHERE id = {obj_id}"""

        # Return 
        return self.__execute_sql(
            sql, tuple(ordered_values),
            return_results=False
        ).first()

    def __bulk_update(
            self,
            table_data: typing.Dict[str, typing.Dict[str, str]],
            return_objs: bool = False
        ) -> typing.Union[Results, None]:
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
            self.__validate_data(data)
            if obj_id := not data.get("id", None):
                raise Exception(
                    f"ERROR: You must pass IDs with every object you wish to update! "
                    "Location: db.py -> DatabaseHandler -> bulk_update()"
                )
            # Construct Query
            base_query = f"UPDATE {table_name}"
            set_clause = "SET "
            where_clause = f"WHERE id = {obj_id}"
            set_data = []
            for column, value in data.items():
                set_clause+f"{column} = ?, "
                set_data.append(value)
            # Clean the query
            clean_set_clause = self.__clean_query(set_clause)
            # Produces
            # UPDATE user_sids SET username = some_username, sid = some_sid WHERE id = 2;
            # Execute the query
            results.append(self.__execute_sql(
                base_query
                +clean_set_clause
                +where_clause
                +";",
                tuple(set_data),
                commit=True,
                return_results=return_objs
            ))
        if return_objs:
            return Results(results)

    def ___delete_obj(self, table_name: str, obj_id: int) -> None:
        """
        Delete an object

        :param table_name: The name of the table as a string
        :param id: The ID of the object to delete
        """
        self.__execute_sql(
            f"DELETE FROM {table_name} WHERE id = {obj_id}",
            return_results=False, commit=True
        )

  # Utilities
    def __create_tables(self) -> None:
        """
        Create the default tables defined in self.__tables
        """
        for table_name, col_info in self.__tables.items():
            self.__create_table(table_name, col_info)

    def __table_exists(self, table_name: str) -> bool:
        return len(self.__cursor.fetchall(f"FROM {table_name} SELECT *")) > 0

    def __clean_query(self, sql_string: str) -> str:
        if sql_string.endswith(", "):
            return sql_string[:len(sql_string)-2]
        else:
            print("No need to string the trailing ', ' as it doesn't exist")
            return sql_string

    def __execute_sql(
            self, sql: str,
            values: str = None, return_id: bool = False,
            return_class: bool = False,
            return_raw: bool = False, return_results: bool = True,
            commit: bool = False, dynamic_map: bool = True
        ):
        """
        A wrapper to execute any SQL. This is used to keep from
        having connections and such scattered through the class
        and catch any errors without having to repeatedly write
        try/excepts
        If no params are set to True, try to return a Results/Result object


        :param sql: The SQL to be executed        
        :param values: Values to be parameter bound to the sql command if any
        :param return_id: If True, return the id of the last created object    
        :param map_to_class: If True return a class corresponding to the type
            of object we're getting from the database whos attributes are
            filled by the information returned from the query
        :param return_class: If True, return an uninstantiated class corresponding
            to the type of object we're getting
        :param return_raw: If True, return the raw data returned from the database operation
        """
        return_value = None
        try:
            # If we're not commiting, we want the results
            if values:
                results = self.__cursor.execute(sql, values)
            else:
                # Assume we're getting something. No harm if not
                results = self.__cursor.execute(sql)
            if commit:
                self.database.commit()

            elif return_id:
                return self.__cursor.lastrowid
            elif return_class:
                return map_to_class(results)[0].__class__
            elif return_raw:
                return results
            elif return_results:
                # Map results to Results object  if len > 1
                result_dicts = self.__dict_factory(results)
                try:
                    if dynamic_map:
                        return map_to_class(data_dicts=result_dicts, multple=True)
                    return Results(result_dicts)
                except:
                    raise NotImplementedError(
                        "Error handling for failed Result instantiation is not yet implemented!"
                    )
            elif len(results) == 1:
                return map_to_class(
                    self.__dict_factory(results)[0]
                )
            print("No arguments were True, not returning anything...")
            return

        except sql.OperationalError as e:
            raise sql.OperationalError(f"FAILED to execute sql command\n\n"
                "SQL: {sql}\n\nVALUES: {values}\n\nERROR: {e}"
            )

    def __validate_data(
            self, data: typing.Dict[str, typing.Dict[str, str]]
        ) -> None:
        """
        Ensure we have the correct data in the correct format
        so we don't get a failed commit
        """

        col_types = {
            "TEXT": str,
            "INTEGER": int
            #"BOOLEAN": bool <-- Requires custom db type
        }
        try:
            # Handles missing attributes in the case of updates/inserts with nullable fields
            # Won't allow data with no corresponding field in any table
            cls_name = map_to_class(data).__class__.__name__
        except Exception as e:
            raise Exception(f"{e}")
        # Validate the data types
        # get schema for table
        table_schema = self.__tables.get(cls_name)
        for field, field_type in table_schema.items():
            try:
                # Attempt to cast the data to the type its field requires
                f_type = col_types.get(field_type)(data.get(field))
            except:
                # Failed to cast, cannot accept incompatible data
                raise Exception(
                    f'INVALID DATA: The column "{field}" requires type '
                    f'{field_type} but got {type(data.get(field))} instead '
                    'Location: db.py -> __DatabaseHandler -> __validate_data()'
                )

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
            for index,column in enumerate(self.__cursor.description):
                result_dict[column[0]] = result[index]
            return result_dict
        dicts = []
        # Convert all results
        for result in results:
            dicts.append(__to_dict(result))
        return dicts

    def __close_connection(self) -> None:
        if self.database:
            self.database.close()
        else:
            print("Database is already closed, cannot close it again.")
            print(
                "Location: pytextnow -> database -> db.py -> "
                "DatabaseHandler -> __close_connection()"
            )

class DatabaseHandler(__BaseDatabaseHandler):
    """
    High level API for database interactions
    """
    def __init__(self, db_name: str = "text_nowAPI.sqlite3") -> None:
        self.__db_name = db_name
        # Connect by default
        super(DatabaseHandler, self).__init__(self.__db_name)

    def filter(self, table_name: str,  filters: typing.Dict[str, str]) -> Results:
        """
        Take in a dictionary whose keys are field names and values
        are the expected values in the contacts tables
        """
        return self.__filter(table_name, filters)

# High Level Helper Methods

  # Usernames & SID
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

        :param data: Dictionary that holds data to insert
        """
        return self.__create_record("user_sids", data)

    def get_user(self, username: str = None) -> typing.Union[User, None]:
        """
        Get the sid from the USER_SID table that corresponds
        to the given username or, if it's the only sid that exists,
        return what we find.
        
        If no value, prompt for login OR raise exception.
        """
        results = dict(self.__filter("user_sids", {'username': username}))
        if result_len := len(results) > 1 and not username:
            raise Exception(
                                "There is more than one record in the user_sids table. "
                                "Please provide a username and retry;"
                                "Location: db.py -> DatabaseHandler -> get_user()"
                            )
        elif result_len > 1 and username:
            # Returns {
            #   'username': "Some Username",
            #   'sid': "Some SID"
            # }
            return { key:value for (key,value) in results.items() if key == username}
        elif result_len == 1:
            return dict(results[0])
        return None

    def update_user(self, new_data: typing.Dict[str, str]) -> User:
        """
        Update a user record in the database

        :param new_data: Dictionary whose keys are fields and values
            are the new values for the field.
        """
        return self.__update_obj('user_sids', new_data)

    def delete_user(self, id: int) -> None:
        self.__delete_obj("user_sids", id)

  # Contacts
    def create_contact(self, data: typing.Dict[str, str]) -> Contact:
        self.__create_record('contacts', data)

    def get_all_contacts(self) -> Container:
        # returns results by default
        return self.__execute_sql("SELECT * FROM contacts;")

    def update_contact(self, info_dict, return_obj=True):
        if return_obj:
            return self.__update_obj('contacts', info_dict)
        else:
            self.__update_obj('contacts', info_dict)

    def delete_contact(self):
        self.__delete_obj()

  # SMS
    def create_message(self, data):
        self.__create_record('sms', data)

    def get_all_sms(self, sent=False, received=True):
        """
        Get and return ALL sms

        :param sent_only: If True, only get sms that the user sent
        :param received_only: Default of True, If True, return only sms the user received
            ordered by the time they were received (newest first)
        """
        if sent:
            return self.__filter('sms', {'sent': "True"})
        elif received:
            return self.__filter('sms', {'received': "True"})
        # Return both sent and received
        return map_to_class(
            self.__dict_factory(self.__execute_sql("FROM sms SELECT *")),
            multiple=True
        )

    def get_sms(self, filters):
        """
        This is mainly for getting sms by dates.
        NOTE You MUST pass a string version of a date time object
        to filter by dates. Use str(date_object)


        :param filters: A dictionary of conditions to be met 
            key = field name, value is it's expected value
        """
        return self.__filter('sms', filters)

    # No need to update a message. If need be, use self.__update_obj()

    def delete_message(self, id):
        self.__delete_obj('sms', id)
  
  # MMS sms
    def create_mms(self, data):
        return self.__create_record('mms', data)
    
    def get_mms(self, filters):
        return self.__filter('mms', filters)
    
    def delete_mms(self, new_data):
        self.___delete_obj('mms', new_data)