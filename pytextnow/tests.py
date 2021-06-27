import random
import typing
import unittest
from faker import Faker
from datetime import timedelta
import time
import datetime
from unittest import TestCase
from uuid import uuid1
from database.db import DatabaseHandler
from tools.constants import *

class DatabaseHandlerTest(TestCase):
    """
    Run various queries to see if the methods work
    """
    def __init__(self, methodName: str) -> None:
        self.faker = Faker()
        self.db_handler = DatabaseHandler()
        super().__init__(methodName=methodName)
        self.test_data = {

            # Get sms and mms by number
            "sms": {
                'number': [],
                'db_id': []
            },
            "mms": {
                'number': [],
                'db_id': []
            },
            "users": {
                'sid': [],
                "username": [],
                'db_id': []
            },
            "contacts": {
                'names': [],
                'number': [],
                'db_id': []
            }
        }
        self.useless_characters = [
                "\n", '"', ";", ":", ">", "<", "*"
            ]
        self.setup()

        self.start_test()

    def setup(self, *args, **kwargs):
        """
        Set everything up and test creation
        """
        self.generate_users()
        time.sleep(1)
        self.generate_sms()
        time.sleep(1)
        self.generate_mms()
        time.sleep(2)
        self.generate_contacts()
        time.sleep(1)

    def generate_users(self):
        with open("/home/trip/Desktop/Code/python/TNAPI/PyTextNow_API/pytextnow/usernames.txt", 'r') as usernames:

            for name in usernames.readlines():
                name = name.strip("\n")
                name = name.strip()
                sid = str(uuid1())
                self.test_data['users']['sid'].append(sid)
                self.test_data['users']['username'].append(name)
                if self.db_handler.user_exists(name):
                    print("User already exists!")
                    pass
                if not self.db_handler.user_exists(name):
                    print("User doesn't exist!!")
                    self.db_handler.create_user({'username': name, 'sid': sid, 'object_type': USER_TYPE})
        # Should be 88 lines
        print(self.db_handler.get_all_users())
        assert len(self.db_handler.get_all_users()) > 45
        print("\n\nUsers Successfully created!\n\n")

    
    def generate_sms(self):
        import random
        with open("/home/trip/Desktop/Code/python/TNAPI/PyTextNow_API/pytextnow/words2.txt", 'r') as words:
            lines = words.readlines()
            for line in range(len(lines)+1):
                minus_days = datetime.datetime.now() - timedelta(
                    days=random.randint(0,53)
                )
                if type(line) != type(int()):
                    line = random.choice(line.strip(self.useless_characters))
                number = str(self.faker.phone_number())
                self.test_data['sms']['number'].append(number)
                self.db_handler.create_sms({
                    'content': line,
                    'number': number,
                    'date': str(datetime.datetime.now()),
                    'first_contact': str(minus_days),
                    'read': random.choice(['False', 'True']),
                    'sent': random.choice(['False', 'True']),
                    'received': random.choice(['False', 'True']),
                    'direction': random.choice([1,2]),
                    'object_type': MESSAGE_TYPE
                })
        words.close()
        assert len(self.db_handler.get_all_sms()) > 0
        print("\n\nSMS Successfully created!\n\n")

    def generate_mms(self):
        with open('/home/trip/Desktop/Code/python/TNAPI/PyTextNow_API/pytextnow/words.txt', 'r') as words:

            lines = words.readlines()
            for i in range(len(lines + 1)):
                minus_days = datetime.datetime.now() - timedelta(
                    days=random.randint(0,53)
                )
                number = str(self.faker.phone_number())
                self.test_data['mms']['number'].append(number)
                if type(line) != type(int):
                    line = random.choice(line.strip(self.useless_characters))
                str(datetime.datetime.now())
                self.db_handler.create_contact
                self.db_handler.create_sms({
                    'content': line,
                    'number': number,
                    'date': datetime.datetime.now(),
                    'first_contact': str(minus_days),
                    'read': random.choice(['False', 'True']),
                    #'sent': random.choice(['False', 'True']),
                    #'received': random.choice(['False', 'True']),
                    'direction': random.choice([1,2]),
                    'content_type': str(uuid1()),
                    'extension': random.choice(['.png', '.txt', '.xml', '.py', 'docx', 'ppt']),
                    'type': str(uuid1()),
                    'object_type': MULTIMEDIA_MESSAGE_TYPE,
                })
        # There should be 60 lines
        assert len(self.db_handler.get_all_mms()) > 58
        print("MMS Successfully created!")
        time.sleep(0.15)

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
                'object_name': CONTACT_TYPE
            })
        assert len(self.db_handler.get_all_contacts()) > 149
        print("Contacts Successfully created!")
        time.sleep(0.15)

    def test_filters(self):
        """
        Test various filters to be used in the database queries
        to ensure they work properly
        """
        for i in range(0,53):
        # Testing Users
            # Get a random column to filter against
            col_filter = random.choice(self.test_data['users'].keys())
            # Get a random value corresponding to the column to use
            # in the test query
            col_val = random.choice(self.test_data['users'][col_filter])
            users = self.db_handler.filter('users', {col_filter: col_val})
            for i in contacts:
                self.test_data['contacts']['ids'].append(i.db_id)
            try:
                assert len(users) > 0
                print(f"Filters with col {col_filter} seem to work on the users table!!")
                time.sleep(1.5)
            except:
                assert len(users) > 0
                print(f"Filters with col {col_filter} seem to work on the users table!!")
                time.sleep(1.5)

        # Testing SMS
            col_filter = 'number'
            col_val = random.choice(self.test_data['sms']['number'])
            sms = self.db_handler.filter('sms', {col_filter :col_val})
            for i in sms:
                self.test_data['sms']['ids'].append(i.db_id)
            try:
                assert len(sms) > 0
                print(f"Filters with col {col_filter} seem to work on the sms table!!")
                time.sleep(1.5)
            except:
                assert len(sms) > 0
                print(f"Filters with col {col_filter} seem to work on the sms table!!")
                time.sleep(1.5)

        # Testing MMS

            col_filter = 'number'
            col_val = random.choice(self.test_data['mms']['number'])
            mms = self.db_handler.filter('mms', {col_filter :col_val})
            for i in mms:
                self.test_data['mms']['ids'].append(i.db_id)
            try:
                assert len(mms) > 0
                print(f"Filters with col {col_filter} seem to work on the mms table!!")
                time.sleep(1.5)
            except:
                assert len(mms) > 0
                print(f"Filters with col {col_filter} seem to work on the mms table!!")
                time.sleep(1.5)

        # Testing Contacts
            col_filter = random.choice(self.test_data['contacts'].keys())
            col_val = random.choice(self.test_data['contacts'][col_filter])
            contacts = self.db_handler.filter('contacts', {col_filter :col_val})
            for i in contacts:
                self.test_data['contacts']['ids'].append(i.db_id)
            # Case one
            try:
                assert len(contacts) > 0
                print(f"Filters with col {col_filter} seem to work on the contacts table!!")
                time.sleep(1.5)
            except:
                assert len(users) > 0
                print(f"Filters with col {col_filter} seem to work on the contacts table!!")
                time.sleep(1.5)

    def test_updates(self):
        
        for contact_id in self.test_data['contacts']['id']:
            old = self.db_handler.filter('contacts', {'db_id': contact_id}).first()
            modified = self.db_handler.update_contact(contact_id, {'name': self.faker.name()})
            assert old.name != modified.name

        for user_id in self.test_data['users']['id']:
            old = self.db_handler.filter('users', {'db_id': user_id}).first().sid
            modified = self.db_handler.update_user(user_id, {'name': self.faker.name()})
            assert old.sid != modified.sid


    def test_deletes(self):
        for contact_id in self.test_data['contacts']['id']:
            old = self.db_handler.delete_contact(contact_id)
            modified = self.db_handler.update_contact(contact_id, {'name': self.faker.name()})
            assert old.name != modified.name

        for user_id in self.test_data['users']['id']:
            old = self.db_handler.filter('users', {'db_id': user_id}).first().sid
            modified = self.db_handler.update_user(user_id, {'name': self.faker.name()})
            assert old.sid != modified.sid

        for sms_id in self.test_data['sms']['id']:
            old = self.db_handler.filter('sms', {'db_id': sms_id}).first().sid
            modified = self.db_handler.update_sms(sms_id, {'name': self.faker.name()})
            assert old.sid != modified.sid

        for mms_id in self.test_data['mms']['id']:
            old = self.db_handler.filter('mms', {'db_id': mms_id}).first().sid
            modified = self.db_handler.update_contact(mms_id, {'name': self.faker.name()})
            assert old.sid != modified.sid

    def start_tests(self):
        self.test_filters()
        self.test_updates()
        self.test_deletes()

if __name__ == "__main__":
    unittest.main()