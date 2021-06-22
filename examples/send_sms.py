import pytextnow as pytn

client = pytn.Client("username") # You can also include the cookie in ther Client constructor
# Here you should input your connect.sid cookie

client.send_sms("number", "text")
