MESSAGE_TYPE = 0
MULTIMEDIA_MESSAGE_TYPE = 1

# new
USER_TYPE = 3
CONTACT_TYPE = 4

SENT_MESSAGE_TYPE = 2
RECEIVED_MESSAGE_TYPE = 1

SIP_ENDPOINT = "prod.tncp.textnow.com"

MAX_FILE_SIZE = 2500

TABLES_CLASSES = {
    'sms': "Message",
    'mms': "MultiMediaMessage",
    'contacts': "Contact",
    'users': "User"
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
                    'sent',
                    'received',
                    'direction',
                    'object_type'
                'db_id'
            ],
            "MultiMediaMessage": [
                    'content',
                    'number',
                    'date',
                    'first_contact',
                    'read',
                    #'sent',
                    #'received',
                    'direction',
                    'content_type',
                    'extension',
                    'type',
                    'object_type',
                    'db_id'
            ],
            "User": [
                'sid',
                'username',
                'object_type',
                'db_id'
            ],
            "Contact": [
                'name',
                'number',
                'db_id',
                'object_type'
            ]
        }
FALSE = 0
TRUE = 1