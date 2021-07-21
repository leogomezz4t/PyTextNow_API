import random
import os
import secrets
from faker import Faker
from datetime import timedelta
import time
import datetime
from pytextnow.tools.constants import *
from pytextnow.database.db import DatabaseHandler
from pytextnow.TN_objects.API import URLBuilder
from pytextnow.TN_objects.user import User
from pytextnow.TN_objects.container import Container
from pytextnow.TNAPI import CellPhone

class DatabaseHandlerTest:
    """
    Run various queries to see if the methods work
    """
    def __init__(self) -> None:
        self.faker = Faker()
        self.db_handler = DatabaseHandler(main_handler=True)
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
                'password': [],
                "username": [],
                'db_id': []
            },
            "contacts": {
                'name': [],
                'number': [],
                'db_id': []
            },
            "connections": {
                'contacts': [],
                'sms': [],
                'mms': []
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
        self.generate_contacts()
        self.generate_sms()
        self.generate_mms()
        print("\n\nAll tables and objects created successfully...Moving on to testing...")
        time.sleep(0.75)

    def start_tests(self, test_deletes=True):
        print("\n\n\t\t...Testing Regular Filters...\n\n")
        time.sleep(1)
        self.test_filters()
        print("\n\n\t\t...Testing Relational Filters...\n\n")
        time.sleep(1)
        self.test_relational_filters()
        print("\n\n\t\t...Testing Updates...\n\n")
        time.sleep(1)
        Faker.seed(random.randint(0,500))
        self.test_updates()
        print("\n\n\t\t...Testing Deletes...\n\n")
        time.sleep(1)
        success_msg = "\n\n\t\t!!!All tests ran successfully. Database handler is now stable!!!\n\n"
        if not test_deletes:
            return print(success_msg)
        self.test_deletes()
        return print(success_msg)

    def generate_users(self):
        with open("pytextnow/usernames.txt", 'r') as usernames:

            for name in usernames.readlines():
                name = name.strip("\n")
                name = name.strip()
                password = secrets.token_hex(16)
                self.test_data['users']['password'].append(password)
                self.test_data['users']['username'].append(name)
                if self.db_handler.user_exists(name):
                    pass
                if not self.db_handler.user_exists(name):
                    self.db_handler.create_user({'username': name, 'password': password, 'object_type': USER_TYPE})
                new_user = self.db_handler.get_user(name)
                self.test_data['users']['db_id'].append(new_user.db_id)
        users = self.db_handler.get_all_users()
        # Should be 88 lines
        assert len(users) > 87
        print("Users Successfully created!\n\n")
        time.sleep(0.75)


    def generate_contacts(self):
        # Generate unique phone numbers
        numbers = []
        start = time.time()
        for i in range(0,151):
            found_num = False
            num = str(self.faker.phone_number())
            if num in numbers:
                while num in numbers:
                    if time.time() - start > 10:
                        raise Exception("Timed out generating unique phone number!")
                    num = str(self.faker.phone_number())
                    if num not in numbers:
                        numbers.append(num)
                        found_num = True
                        break
            if found_num:
                continue
            numbers.append(num)
        start = 0
        stop = len(self.test_data['users']['db_id'])
        for i in range(0,151):
            Faker.seed(random.randint(0,9999))
            name = self.faker.name()
            number = numbers[i]
            self.test_data['contacts']['number'].append(number)
            self.test_data['contacts']['name'].append(name)
            user = random.choice(self.test_data['users']['db_id'])
            self.test_data['connections']['contacts'].append({'contact_id': i, 'user_id': user})
            self.db_handler.create_contact({
                'name': name,
                'number': number,
                'object_type': CONTACT_TYPE,
                'user_id': user
            })
            new_contact = self.db_handler.filter('contacts', {'number': number}).first()
            self.test_data['connections']['contacts'].append(
                {
                    'contact_id': new_contact.db_id,
                    'user_id': new_contact.user_id
                }
            )
            self.test_data['contacts']['db_id'].append(new_contact.db_id)
        contacts = self.db_handler.get_all_contacts()
        assert len(contacts) > 149
        print("Contacts Successfully created!")
        #self.extract_ids('contacts')
        time.sleep(0.75)
    
    def generate_sms(self):
        import random
        with open("pytextnow/words.txt", 'r') as words:
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
                user = random.choice(self.test_data['users'].get('db_id'))
                contact = random.choice(self.test_data['contacts'].get('db_id'))
                

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
                    'object_type': MESSAGE_TYPE,
                    'user_id': user,
                    'contact_id': contact
                })
                new_sms = self.db_handler.filter('sms', {'id': an_id})[0]
                self.test_data['connections']['sms'].append(
                    {
                        'sms_id': new_sms.db_id,
                        'user_id': new_sms.user_id,
                        'contact_id': new_sms.contact_id
                    }
                )
                self.test_data['sms']['db_id'].append(new_sms.db_id)
        sms = self.db_handler.get_all_sms()
        assert len(sms) > 0
        time.sleep(0.75)

    def generate_mms(self):
        with open('pytextnow/words.txt', 'r') as words:

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
                user = random.choice(self.test_data['users'].get('db_id'))
                contact = random.choice(self.test_data['contacts'].get('db_id'))
                if type(line) != type(int):
                    line = random.choice(self.clean_line(line))
                self.db_handler.create_mms({
                    'content': line+str(i)*2,
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
                    'user_id': user,
                    'contact_id': contact
                })
                new_mms = self.db_handler.filter('mms', {'id': an_id})[0]
                self.test_data['connections']['mms'].append(
                    {
                        'mms_id': new_mms.db_id,
                        'user_id': new_mms.user_id,
                        'contact_id': new_mms.contact_id
                    }
                )
                self.test_data['mms']['db_id'].append(new_mms.db_id)
        mms = self.db_handler.get_all_mms()
        # There should be 60 lines
        assert len(mms) > 58
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
            except AssertionError:
                assert len(users) == 0
                print(f"\n\nERROR: Filter with col {col_filter} FAILED on the users table!!\n\n")
            except Exception as e:
                raise e

        # Testing SMS
            col_filter = 'number'
            col_val = random.choice(self.test_data['sms']['number'])
            sms = self.db_handler.filter('sms', {col_filter :col_val})
            try:
                assert len(sms) > 0
            except AssertionError:
                assert len(sms) == 0
                print(f"\n\nERROR: Filter with col {col_filter} FAILED on the sms table!!\n\n")
            except Exception as e:
                raise e
        # Testing MMS

            col_filter = 'number'
            col_val = random.choice(self.test_data['mms']['number'])
            mms = self.db_handler.filter('mms', {col_filter :col_val})
            try:
                assert len(mms) > 0
            except AssertionError:
                assert len(mms) == 0
                print(f"\n\nERROR: Filter with col {col_filter} FAILED on the mms table!!\n\n")
            except Exception as e:
                raise e
        # Testing Contacts
            col_filter = random.choice(list(self.test_data['contacts'].keys()))
            col_val = random.choice(self.test_data['contacts'][col_filter])
            contacts = self.db_handler.filter('contacts', {col_filter :col_val})
            # Case one
            try:
                assert len(contacts) > 0
            except AssertionError:
                assert len(contacts) == 0
                print(f"\n\nERROR: Filter with col {col_filter} FAILED on the contacts table!!\n\n")
            except Exception as e:
                raise e
        time.sleep(0.75)

    def test_relational_filters(self):
        """
        Test to make sure the new relational things work
        """
        results = {}
        for tbl_name, relation_list in self.test_data['connections'].items():
            for relation in relation_list:
                filter_result = self.db_handler.filter(tbl_name, relation)
                if results.get(tbl_name, None):
                    results[tbl_name].append(filter_result)
                else:
                    results[tbl_name] = [filter_result]
        for tbl, results in results.items():
            # Since we used the connections information in self.test_data
            # we should get every single connection it has
            assert len(results) == len(self.test_data['connections'][tbl])
            print("\nRelational Filters On Table:", tbl, "were all tested successfully!\n")


    def test_updates(self):
        for contact_id in self.test_data['contacts']['db_id']:
            old = self.db_handler.filter('contacts', {'db_id': contact_id}).first()
            modified = self.db_handler.update_contact(contact_id, {'name': self.faker.name()})
            assert old.name != modified.name

        for user_id in self.test_data['users']['db_id']:
            old = self.db_handler.filter('users', {'db_id': user_id}).first()
            modified = self.db_handler.update_user(user_id, {'username': self.faker.name()})
            assert old.username != modified.username
        time.sleep(0.75)

    def test_deletes(self):
        for contact_id in self.test_data['contacts']['db_id']:
            self.db_handler.delete_contact(contact_id)
            after = self.db_handler.filter('contacts', {'db_id': contact_id})
            if len(after) > 0:
                raise AssertionError("\n\n!!!DATABASE OPERATION ERROR!!!\n Delete operation on contact table failed")

        for user_id in self.test_data['users']['db_id']:
            self.db_handler.delete_user(user_id)
            result = self.db_handler.filter('users', {'db_id': user_id})
            if len(result):
                raise AssertionError("\n\n!!!DATABASE OPERATION ERROR!!!\n Delete operation on user table failed")

        for sms_id in self.test_data['sms']['db_id']:
            self.db_handler.delete_sms(sms_id)
            result = self.db_handler.filter('sms', {'db_id': sms_id})
            if len(result):
                raise AssertionError("\n\n!!!DATABASE OPERATION ERROR!!!\n Delete operation on sms table failed")

        for mms_id in self.test_data['mms']['db_id']:
            self.db_handler.delete_mms(mms_id)
            result = self.db_handler.filter('mms', {'db_id': mms_id})
            if len(result):
                raise AssertionError("\n\n!!!DATABASE OPERATION ERROR!!!\n Delete operation on mms table failed")

        print("\n\nAll deletes work!")
        time.sleep(0.75)

    def clean_line(self, line):
        for i in self.useless_characters:
            line.strip(i)
        return line

class CellPhoneTest:
    def __init__(self) -> None:
        # Test RoboBoi.choose_account(), and DB setup right away
        print("\n\nInstantiating cellphone. Tests DB handler & robot\n\n")
        self.cellphone = CellPhone()

    def test_it(self):
        print("...Testing sms...")
        num = input("Number: ")
        self.cellphone.send_sms(num, input("Message: "))
        print("...Testing mms...")
        file_path = input("Enter path to file: ")
        self.cellphone.send_mms(num, file_path)
        print("All good!")

class URLBuilderTest:
    def __init__(self):
        self.user = User(username="test")
        qb = URLBuilder(self.user, "messages")
        print(qb.url)

if __name__ == "__main__":
    try:
        db_test = DatabaseHandlerTest()
        # db_test.setup()
       # os.remove("text_nowAPI.sqlite3")
    except Exception as e:
        print(e)
       # os.remove("text_nowAPI.sqlite3")
        raise e
