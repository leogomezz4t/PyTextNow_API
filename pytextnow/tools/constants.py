MESSAGE_TYPE = 0
MULTIMEDIA_MESSAGE_TYPE = 1

# new
USER_TYPE = 3
CONTACT_TYPE = 4
ACCOUNT_TYPE = 5
SENT_MESSAGE_TYPE = 2
RECEIVED_MESSAGE_TYPE = 1

SIP_ENDPOINT = "prod.tncp.textnow.com"

MAX_FILE_SIZE = 2500

TABLES_CLASSES = {
    'sms': "Message",
    'mms': "MultiMediaMessage",
    'contacts': "Contact",
    'users': "User",
    'accounts': "Account"
}
TABLE_ATTRS = {
    # I'm annoyed with figuring out how to get an uninstantiated classes
    # attributes so we're doing this for now
            "Message": [
                    'content',
                    'number',
                    'date',
                    'first_contact',
                    'read',
                    'id',
                    'direction',
                    'sent',
                    'received',
                    # For easy mapping
                    'object_type',
                    'db_id',
                    # Relational things
                    "user_id", # To
                    "contact_id" # From
            ],
            "MultiMediaMessage": [
                    'content',
                    'number',
                    'date',
                    'first_contact',
                    'read',
                    'id',
                    #'sent',
                    #'received',
                    'direction',
                    'content_type',
                    'extension',
                    'type',
                    'object_type',
                    'db_id',
                    # Relational things
                    "user_id", # To
                    "contact_id" # From
            ],
            "User": [
                'username',
                'password',
                'object_type',
                'db_id'
            ],
            "Contact": [
                'name',
                'number',
                'db_id',
                'object_type',
                # What user does this contact belong to?
                "user_id"
            ],
            "Account": [

            ]
        }
FALSE = 0
TRUE = 1

TN_MSG_PREV_LST_XPATH = "/html/body/div[1]/div/div[2]/div[2]/div[2]/div[2]/div[1]/div[2]/div/div/ul"
FK_FIELDS = {
    "User": "user_id",
    "Message": "sms_id",
    "MultiMediaMessage": "mms_id",
    "Account": "account_id",
    "Contact": "contact_id"
}
DEFAULT_TABLES = {
            "users": {
                'user_id': "INTEGER",
                'username': "TEXT",
                'password': "TEXT",
                "object_type": "INTEGER",
            },
            "sms": {
                "content": "TEXT",
                'number': "TEXT",
                'date': "TEXT",
                'first_contact': "TEXT",
                'read': "TEXT",
                'sms_id': "INTEGER",
                'sent': "TEXT",
                'received': "TEXT",
                'direction': "INTEGER",
                'id': "TEXT",
                # Integer because of constants
                "object_type": "INTEGER",

                "user_id": "INTEGER NOT NULL",
                "contact_id": "INTEGER NOT NULL",
                "relations": {
                    "FOREIGN KEY(user_id) ": "REFERENCES users(user_id)",
                    "FOREIGN KEY(contact_id) ": "REFERENCES contacts(contact_id)"
                }
            },
            "mms": {
                "content": "TEXT",
                'number': "TEXT",
                'date': "TEXT",
                'first_contact': "TEXT",
                'read': "TEXT",
                'mms_id': "INTEGER",
                'direction': "INTEGER",
                'content_type': "TEXT",
                'extension': "TEXT",
                'type': "INTEGER",
                'id': "TEXT",
                "object_type": "INTEGER",  # 2

                "user_id": "INTEGER NOT NULL",
                "contact_id": "INTEGER NOT NULL",
                "relations": {
                    "FOREIGN KEY(user_id) ": "REFERENCES users(user_id)",
                    "FOREIGN KEY(contact_id) ": "REFERENCES contacts(contact_id)"
                }
            },
            "contacts": {
                'contact_id': "INTEGER",
                'name': "TEXT",
                'number': "TEXT",
                "object_type": "INTEGER",

                "user_id": "INTEGER NOT NULL",
                "relations": {
                    "FOREIGN KEY(user_id) ": "REFERENCES users(user_id)"
                }
            },
            "accounts": {
                "account_id": "INTEGER",
                "user_id": "INTEGER NOT NULL",
                "relations": {
                    # Related Table
                    "FOREIGN KEY(user_id) ": "REFRENCES users(user_id)"
                }
            }
        }