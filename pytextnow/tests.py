from pytextnow.tools.events import EventManager
import random
import os
import secrets
from faker import Faker
from datetime import timedelta
import time
import datetime
from unittest import TestCase
from uuid import uuid1
from database.db import DatabaseHandler
from tools.constants import *

class DatabaseHandlerTest:
    """
    Run various queries to see if the methods work
    """
    def __init__(self) -> None:
        self.faker = Faker()
        self.db_handler = DatabaseHandler()
        self.test_data = {

            # Get sms and mms by number
            "sms": {
                'number': [],
                'db_id': [],
                'id': []
            },
            "mms": {
                'number': [],
                'db_id': [],
                'id': []
            },
            "users": {
                'sid': [],
                "username": [],
                'db_id': []
            },
            "contacts": {
                'name': [],
                'number': [],
                'db_id': []
            }
        }
        self.useless_characters = [
                "\n", '\t', ";",
                "'"
            ]
        self.setup()

        self.start_tests()

    def setup(self, *args, **kwargs):
        """
        Set everything up and test creation
        """
        self.generate_users()
        self.generate_sms()
        self.generate_mms()
        self.generate_contacts()
        print("\n\nAll tables and objects created successfully...Moving on to testing...")
        time.sleep(0.75)

    def generate_users(self):
        with open("usernames.txt", 'r') as usernames:

            for name in usernames.readlines():
                name = name.strip("\n")
                name = name.strip()
                sid = secrets.token_hex(16)
                self.test_data['users']['sid'].append(sid)
                self.test_data['users']['username'].append(name)
                if self.db_handler.user_exists(name):
                    print("User exists")
                    pass
                if not self.db_handler.user_exists(name):
                    self.db_handler.create_user({'username': name, 'sid': sid, 'object_type': USER_TYPE})
        users = self.db_handler.get_all_users()
        # Should be 88 lines
        assert len(users) > 87
        self.extract_ids('users', users)
        print("\n\nUsers Successfully created!\n\n")
        time.sleep(0.75)


    
    def generate_sms(self):
        import random
        with open("words.txt", 'r') as words:
            lines = words.readlines()
            for line in range(len(lines)+1):
                minus_days = str(datetime.datetime.now() - timedelta(
                    days=random.randint(0,53)
                ))
                if type(line) != type(int()):
                    line = random.choice(self.clean_line(line))
                an_id = secrets.token_hex(16)
                self.test_data['sms']['id'].append(an_id)
                number = str(self.faker.phone_number())
                self.test_data['sms']['number'].append(number)
                sms = self.db_handler.create_sms({
                    'content': line,
                    'number': number,
                    'date': str(datetime.datetime.now()),
                    'first_contact': str(minus_days),
                    'id': an_id,
                    'read': random.choice(['False', 'True']),
                    'sent': random.choice(['False', 'True']),
                    'received': random.choice(['False', 'True']),
                    'direction': random.choice([1,2]),
                    'object_type': MESSAGE_TYPE
                })
        sms = self.db_handler.get_all_sms()
        assert len(sms) > 0
        self.extract_ids('sms', sms)
        print("\n\nSMS Successfully created!\n\n")
        time.sleep(0.75)

    def generate_mms(self):
        with open('words.txt', 'r') as words:

            lines = words.readlines()
            for i in range(len(lines) + 1):
                line = random.choice(lines)
                minus_days = str(datetime.datetime.now() - timedelta(
                    days=random.randint(0,53)
                ))
                number = str(self.faker.phone_number())
                self.test_data['mms']['number'].append(number)
                an_id = secrets.token_hex(16)
                self.test_data['mms']['id'].append(an_id)

                if type(line) != type(int):
                    line = random.choice(self.clean_line(line))
                self.db_handler.create_contact
                self.db_handler.create_mms({
                    'content': line,
                    'number': number,
                    'date': str(datetime.datetime.now()),
                    'first_contact': str(minus_days),
                    'read': random.choice(['False', 'True']),
                    #'sent': random.choice(['False', 'True']),
                    #'received': random.choice(['False', 'True']),
                    'id': an_id,
                    'direction': random.choice([1,2]),
                    'content_type': secrets.token_hex(),
                    'extension': random.choice(['.png', '.txt', '.xml', '.py', 'docx', 'ppt']),
                    'type': MULTIMEDIA_MESSAGE_TYPE,
                    'object_type': MULTIMEDIA_MESSAGE_TYPE,
                })
        mms = self.db_handler.get_all_mms()
        # There should be 60 lines
        assert len(mms) > 58
        self.extract_ids('mms', mms)
        print("MMS Successfully created!")
        time.sleep(0.75)

    def generate_contacts(self):
        for i in range(0,151):
            Faker.seed(random.randint(0,9999999))
            name = self.faker.name()
            number = str(self.faker.phone_number())
            self.test_data['contacts']['number'].append(number)
            self.test_data['contacts']['name'].append(name)
            self.db_handler.create_contact({
                'name': name,
                'number': number,
                'object_type': CONTACT_TYPE
            })
        contacts = self.db_handler.get_all_contacts()
        assert len(contacts) > 149
        self.extract_ids('contacts', contacts)
        print("Contacts Successfully created!")
        time.sleep(0.75)

    def test_filters(self):
        """
        Test various filters to be used in the database queries
        to ensure they work properly
        """
        for i in range(0,53):
        # Testing Users
            # Get a random column to filter against
            col_filter = random.choice(list(self.test_data['users'].keys()))
            # Get a random value corresponding to the column to use
            # in the test query
            col_val = random.choice(self.test_data['users'][col_filter])
            users = self.db_handler.filter('users', {col_filter: col_val})
            try:
                assert len(users) > 0
                print(f"Filters with col {col_filter} seem to work on the users table!!")
            except:
                assert len(users) > 0
                print(f"Filters with col {col_filter} seem to work on the users table!!")
            

        # Testing SMS
            col_filter = 'number'
            col_val = random.choice(self.test_data['sms']['number'])
            sms = self.db_handler.filter('sms', {col_filter :col_val})
            try:
                assert len(sms) > 0
                print(f"Filters with col {col_filter} seem to work on the sms table!!")
            except:
                assert len(sms) > 0
                print(f"Filters with col {col_filter} seem to work on the sms table!!")

        # Testing MMS

            col_filter = 'number'
            col_val = random.choice(self.test_data['mms']['number'])
            mms = self.db_handler.filter('mms', {col_filter :col_val})
            try:
                assert len(mms) > 0
                print(f"Filters with col {col_filter} seem to work on the mms table!!")
            except:
                assert len(mms) > 0
                print(f"Filters with col {col_filter} seem to work on the mms table!!")

        # Testing Contacts
            col_filter = random.choice(list(self.test_data['contacts'].keys()))
            col_val = random.choice(self.test_data['contacts'][col_filter])
            contacts = self.db_handler.filter('contacts', {col_filter :col_val})
            # Case one
            try:
                assert len(contacts) > 0
                print(f"Filters with col {col_filter} seem to work on the contacts table!!")
            except:
                assert len(users) > 0
                print(f"Filters with col {col_filter} seem to work on the contacts table!!")
        time.sleep(0.75)


    def test_updates(self):
        time.sleep(0.75)
        
        for contact_id in self.test_data['contacts']['db_id']:
            old = self.db_handler.filter('contacts', {'db_id': contact_id}).first()
            modified = self.db_handler.update_contact(contact_id, {'name': self.faker.name()})
            print(old.name, modified.name)
            assert old.name != modified.name

        for user_id in self.test_data['users']['db_id']:
            old = self.db_handler.filter('users', {'db_id': user_id}).first()
            modified = self.db_handler.update_user(user_id, {'username': self.faker.name()})
            print(old.username, modified.username)
            assert old.username != modified.username
        print("\n\nAll updates work!\n")
        time.sleep(0.75)

    def test_deletes(self):
        for contact_id in self.test_data['contacts']['db_id']:
            self.db_handler.delete_contact(contact_id)
            after = self.db_handler.filter('contacts', {'db_id': contact_id})
            if len(after) > 0:
                raise AssertionError("\n\n!!!DATABASE OPERATION ERROR!!!\n Delete operation on contact table failed")
            else:
                print("Contact successfully deleted!!")
                continue

        for user_id in self.test_data['users']['db_id']:
            self.db_handler.delete_user(user_id)
            result = self.db_handler.filter('users', {'db_id': user_id})
            if len(result):
                raise AssertionError("\n\n!!!DATABASE OPERATION ERROR!!!\n Delete operation on user table failed")
            else:
                print("Successfully deleted user!")
                continue

        for sms_id in self.test_data['sms']['db_id']:
            self.db_handler.delete_sms(sms_id)
            result = self.db_handler.filter('sms', {'db_id': sms_id})
            if len(result):
                raise AssertionError("\n\n!!!DATABASE OPERATION ERROR!!!\n Delete operation on sms table failed")
            else:
                print("Successfully deleted sms!")
                continue

        for mms_id in self.test_data['mms']['db_id']:
            self.db_handler.delete_mms(mms_id)
            result = self.db_handler.filter('mms', {'db_id': mms_id})
            if len(result):
                raise AssertionError("\n\n!!!DATABASE OPERATION ERROR!!!\n Delete operation on mms table failed")
            else:
                print("Successfully deleted mms!")
                continue
        print("\n\nAll deletes work!")
        time.sleep(0.75)

    def extract_ids(self, key, objects):
        for i in objects:
            print(i.db_id)
            self.test_data[key]['db_id'].append(i.db_id)


    def start_tests(self):
        print("\n\nTesting Filters...\n\n")
        self.test_filters()
        print("\n\nTesting Updates...\n\n")
        time.sleep(1)
        Faker.seed(random.randint(0,500))
        self.test_updates()
        print("\n\nTesting Deletes...\n\n")
        time.sleep(1)
        self.test_deletes()
        print("\n\nAll tests ran successfully. Database handler is now stable!!!\n\n")
        return print("\n\nAll tests ran successfully. Database handler is now stable!!!\n\n")

    def clean_line(self, line):
        for i in self.useless_characters:
            line.strip(i)
        return line

class EventHandlerTest:

    def __init__(self) -> None:
        # Initialize database, start event dispatcher
        self.events = EventManager(5)
        self.result_signatures = {}
        self.setup()
        pass

    def setup(self):
        pass
    
    def count_to_one_thousand(self):
        for i in range(0, 1001):
            print(i)

    def random_calculation(self):
        """
        Perform a random calculation to test
        results
        """
        pass

    def test_max_threads(self):
        pass

    def test_custom_events(self):
        pass

    def test_custom_callbacks(self):
        pass

    def test_result_tracking(self):
        pass

    def test_stops(self):
        pass
    
    def test_waits(self):
        pass


if __name__ == "__main__":
    try:
        test = DatabaseHandlerTest()
        test.setup()
        events = EventManager(3)
        os.remove("text_nowAPI.sqlite3")
    except Exception as e:
        print(e)
        os.remove("text_nowAPI.sqlite3")
        raise e