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

        self.account_status = raw_obj["account_status"]
        self.area_code = raw_obj["area_code"]
        self.captcha_required = raw_obj["captcha_required"]
        self.disable_calling = False if raw_obj["disable_calling"] == 0 else True
        self.email = raw_obj["email"]
        self.email_verified = False if raw_obj["email_verified"] == 0 else True
        self.first_name = raw_obj["first_name"]
        self.forward_email = raw_obj["forward_email"]
        self.guid_hex = raw_obj["guid_hex"]
        self.has_password = raw_obj["has_password"]
        self.last_name = raw_obj["last_name"]
        self.last_update = raw_obj["last_update"]
        self.messaging_email = raw_obj["messaging_email"]
        self.phone_number = raw_obj["phone_number"]
        self.signature = raw_obj["signature"]
        self.voicemail = Voicemail(raw_obj["sip"]["voicemail_url"])
        self.user_id = raw_obj["user_id"]
        self.unlimited_calling = raw_obj["unlimited_calling"]
        self.username = raw_obj["username"]
