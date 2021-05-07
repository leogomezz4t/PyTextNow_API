import pytextnow as pytn

client = pytn.Client("example_email_address") # You can also include the cookie in ther Client constructor
# Here you should input your connect.sid cookie

client.send_mms("number", "filepath")
