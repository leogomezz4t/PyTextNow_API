# TextNow API
### TNAPI is a python module that uses [TextNow](https://www.textnow.com/) to enable free programmable texting 

## Credit
- Developer: Leonardo Wu-Gomez
- Reddit: [leogomezz4t](https://www.reddit.com/user/leogomezz4t)
- Please tell me if you have any ideas for the API or reporting a bug

## Installation
#### Method One: ***Using git clone***
```bash
git clone https://github.com/WuGomezCode/TextNow-API.git
```
#### Method Two: ***Using pip***
```bash
pip install PyTextNow
```
*Note: If there is an unexplained error with the pip install, try adding the **--user** flag to it.*



## Usage

### How to get the cookie
[How to get the cookie](get_cookie.mp4)

### How to get your username
[How to get TextNow username](get_username.mp4)

### Ways to authenticate
```python
import pytextnow

# Way 1. Include connect.sid and csrf cookie in the constructor
client = pytextnow.Client("username", sid_cookie="sid", csrf_cookie="csrf").

# Way 2. Just instantiate and a prompt will appear on the command line

# Way 3. If you inputed the wrong cookie and are getting RequestFailed. This is how to reset it
client.auth_reset()
# will redo the prompt
```

### How to send an sms message
```python
client.send_sms("number", "Hello World!")
```
### How to send an mms message
```python
file_path = "./img.jpeg"
client.send_mms("number", file_path)
```
### How to get new messages
```python
new_messages = client.get_unread_messages() -> MessageContainer list
for message in new_messages:
    message.mark_as_read()
    print(message)
    # Class Message | Class MultiMediaMessage
    # Message
    # content: "body of sms"
    # number: "number of sender"
    # date: datetime object of when the message was received
    # read: bool
    # id: int
    # direction: SENT_MESSAGE_TYPE or RECEIVED_MESSAGE_TYPE
    # first_contact: bool if its the first time that number texted you
    # type: MESSAGE_TYPE if class is Message and MULTIMEDIAMESSAGE_TYPE if class is MultiMediaMessage

    # Functions
    # mark_as_read() will post the server as read
    # send_sms() will send an sms to the number who sent the message
    # send_mms() will send an mms to the number who sent the message
    
    # MultiMediaMessage
    # All the attributes of Message
    # content: url of media
    # raw_data: bytes of the media
    # content_type: str the MIME type ie. "image/jpeg" or "video/mp4"
    # extension: str of the file extension is. "jpeg" or "mp4"
    # Functions
    # mv(file_path): downloads the file to file_path

    print(message.number)
    print(message.content)

    # MultiMediaMessage

    print(message.content_type)
    message.mv("./image." + message.extension)

```
### How to get all messages
```python
messages = client.get_messages() -> MessageContainer list
# Same as above
```
### How to get all sent messages
```python 
sent_messages = client.get_sent_messages() -> MessageContainer list
#Same as above
```

### How to filter messages
```python
filtered = client.get_messages().get(number="number")
```

### How to synchronously block until a response
```python
# This will wait for a response from someone and return the Message

msg = client.wait_for_response("number")

# This function will work with a message object too

unreads = client.get_unread_messages()
for unread in unreads:
    msg = unread.wait_for_response()
```

## NEW Simple bot snippet
```python
import pytextnow as pytn

client = pytn.Client("username", sid_cookie="connect.sid", csrf_token="_csrf")

@client.on("message")
def handler(msg):
    print(msg)
    if msg.type == pytn.MESSAGE_TYPE:
        if msg.content == "ping":
            msg.send_sms("pong")
        else:
            msg.mv("test" + msg.extension)
``` 

## Custom Module Exceptions

### FailedRequest:
#### This API runs on web requests and if the request fails this Exception will be raised

### AuthError:
#### During an auth reset if a cookie is not passed and there is no stored cookie in the file it will raise this error.


## Patch Notes

### 1.1.9
- Updated MANIFEST

### 1.1.8
- Fixed 'Messgage not sending' error
- Added new required cookie
- `csrf_token` header is automatically fetched

### 1.1.7
- Added get_username.mp4 video
- Changed Client system from email to username. You now input your textnow username instead of email.
- Bug fixes

### 1.1.6
- Bug Fixes

### 1.1.5
- New better way of getting new messages with Client.on method
- Client.on works like an event handler that takes a decorator function and calls it with the parameter of one Message object
- Bug Fixes
- Added examples
- Get cookie.mp4 video
- Smarter cookie detection

### 1.1.4
- bug fixes

### 1.1.3
- bug fixes

### 1.1.2
- bug fixes

### 1.1.1
- Import Bug Fixes

## 1.1.0
- bug fixes
- if a cookie argument is passed to `Client` it will overide the stored cookie.
- cookie argument can now be passed to `client.auth_reset()`
- Changed import name from `TNAPI` to `pytextnow`
```python
#Pre 1.1.0
import TNAPI as tn
# Now
import pytextnow as pytn
```

### 1.0.3
- Bug fixes

### 1.0.2
- `Client` has new function `client.wait_for_response(number, timeout=True)`. Documentation on how to use it above
- `Message` has same function but the number argument is set to the number who sent the message. `client.Message.wait_for_response(timeout=True)`

### 1.0.1
- Fixed config json.JSONDecodeError
- new Class `MessageContainer` that acts as a list with some added functions and `__str__()`
- `MessageContainer` has method `get` which will return a `MessageContainer` that filtered through all messages
- Fixed readme.md Usage section.

## 1.0.0
- Complete overhaul of the way this module works.

- `client.get_new_messages()` is now deprecated and no longer in use. Instead of that use the new method `client.get_unread_messages()` which will return all unread messages. It will return the same thing each time unless you mark the messages as read with `Message.mark_as_read()`

- `Message` and `MultiMediaMessage` class have a new `mark_as_read()` method to mark the message as read. `mark_as_read()` will make a POST to the textnow.com server.

-  `client.get_messages()` now returns a list of `Message` or `MultiMediaMessage` classes. For the old function which returned the raw dict use `client.get_raw_messages()`

- `client.get_sent_messages()` is a new method that gets all messages you have sent

- `client.get_received_messages()` is a new method that gets all messages you have received regardless of whether or not it has been read.

- `client.get_read_messages()` is a new method that returns all messages that have been read by you.



### 0.9.8
- Bug Fixes

### 0.9.7
- Bug Fixes

### 0.9.6
- Bug Fixes

### 0.9.5
- Linux `__file__` not absolute.
Used os.path.abspath

### 0.9.4
- Bug fixes

### 0.9.3
- Added constants such as
    - SENT_MESSAGE_TYPE
    - RECEIVED_MESSAGE_TYPE
    - MESSAGE_TYPE
    - MULTIMEDIAMESSAGE_TYPE
- Fixed MultiMediaMessage.mv() function

### 0.9.2
- No longer have to use selenium to authenticate. Now you have to manually grab connect.sid cookie.

### 0.9.1
- Nothing much

## 0.9.0
- Using Message and MultiMediaMessage classes instead of dictionary for /get_new_messages/get_sent_messages
- get_messages still returns old dictionary
- Fixed user_sids.json overwrite problem

## 0.8.0
- Fixed the receiving messages. Now working 100%

## 0.7.0
- Added FailedRequest and InvalidFileType errors to Client instance

## 0.5.0
- bug fixes

## 0.4.0
- Added `Client = TNAPI.Client` in \_\_init\_\_.py
- Fixed the failed login import in TNAPI.py

## 0.3.0
- Receiving messages are better but not good

## 0.2.0
- Nothing much

## 0.1.0
- Initial Commit
- Can send messages and photos/videos
- receiving messages a work in progress

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
