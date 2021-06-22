import pytextnow as pytn

client = pytn.Client("username") # You can also include the cookie in ther Client constructor
# Here you should input your connect.sid cookie

@client.on("message")
def on_message(msg):
    if not msg.type == pytn.MESSAGE_TYPE: return

    if msg.content == "ping":
        msg.send_sms("pong")