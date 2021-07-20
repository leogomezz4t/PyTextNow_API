import requests

class Voicemail(str):
    def __init__(self, url):
        self.url = url

    def __new__(cls, content):
        super().__new__(cls, content)

    def download(self, file_path):
        res = requests.get(self.url)

        with open(file_path, "wb") as f:
            f.write(res.content)

class Account():
    def __init__(self, raw_obj):
        self.raw_obj = raw_obj
        
        ### Boring and tedious part coming up
        ### Mapping all values from raw_obj to class

        self.number_expired = True if self.raw_obj.get("sip") == None else False

        self.account_status = raw_obj.get("account_status")
        self.area_code = raw_obj.get("area_code")
        self.captcha_required = raw_obj.get("captcha_required")
        self.disable_calling = None if self.number_expired else False if raw_obj.get("disable_calling") == 0 else True
        self.email = raw_obj.get("email")
        self.email_verified = False if raw_obj.get("email_verified") == 0 else True
        self.first_name = raw_obj.get("first_name")
        self.forward_email = raw_obj.get("forward_email")
        self.guid_hex = raw_obj.get("guid_hex")
        self.has_password = raw_obj.get("has_password")
        self.last_name = raw_obj.get("last_name")
        self.last_update = raw_obj.get("last_update")
        self.messaging_email = raw_obj.get("messaging_email")
        self.phone_number = raw_obj.get("phone_number")
        self.signature = raw_obj.get("signature")
        self.voicemail = None if self.number_expired else Voicemail(raw_obj.get("sip").get("voicemail_url"))
        self.user_id = raw_obj.get("user_id")
        self.unlimited_calling = raw_obj.get("unlimited_calling")
        self.username = raw_obj.get("username")
