import pytextnow as pytn

client = pytn.Client("example_email_address") # You can also include the cookie in ther Client constructor
# Here you should input your connect.sid cookie

while True:
    unreads = client.get_unread_messages()
    for msg in unreads:
        if not msg.type == pytn.MESSAGE_TYPE: continue

        if msg.content == "ping":
            msg.send_sms("pong")