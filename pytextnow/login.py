# Functions
def login():
    print("Go to https://www.textnow.com/messaging and open developer tools")
    print("\n")
    print("Open application tab and copy connect.sid cookie and paste it here.")
    sid = input("connect.sid: ")
    print("Open application tab and copy _csrf cookie and paste it here.")
    csrf = input("_csrf: ")

    return sid, csrf
