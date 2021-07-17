# TextNow API
### TNAPI is a python module that uses [TextNow](https://www.textnow.com/) to enable free programmable texting 

## Credit
- Developer: Leonardo Wu-Gomez
- Collaborators: [SilverStrings024](https://github.com/SilverStrings024), bryanperez43
- Reddit: [leogomezz4t](https://www.reddit.com/user/leogomezz4t)
- Please tell me if you have any ideas for the API or reporting a bug

## Contents
[Credits](credits)
1. [Setup](setup)
2. [CellPhone](cellphone)
    A. [How's It Work?](cellphone-how)
    B. [Basic Usage](cellphone-basic-use)
    C. [Advanced Usage](cellphone-advanced-use)

3. [RoboBoi](robo-boi)
    A. [How's It Work?](robo-how)
    B. [Basic Usage](robo-basic)
    C. [Advanced Usage](robo-advanced)
    D. [Low Level Api](robo-low-lvl)
    E. [Waiting For A Page](page-waits)

4. [Event Listener](listner)
    A. [How's It Work?](event-how)
    B. [Low Level Api](low-lvl-listener)

5. [DatabaseHandler](database-handler)
    A. [High Level API](dbh-high-api)
    B. [Lower Level API](dbh-lower-api)
    C. [Database Customization](custom-dbh)

6. [TN Objects](text-now-objects) (Important objects)
    A. [ApiHandler](api)
    B. [CellPhoneTower](cell-tower)
    C. [Container](container)

# Setup
### Running The Tests
Running the tests to verify that the API was installed correctly and will work on your system is extremely easy.
Either open a python shell in your terminal or create a new file then do...
```python
from pytextnow.tests import StabilityTest
StabilityTest(cleanup_after_test=True)
```
On instantiation, the StabilityTest class will begin testing all components of this package.
As it tests, you **will** see various debug statements telling you what it's testing and when it completes each test.
If any tests fail, you will see an exception with some sort of error description.
If the tests fail on your device, please create an issue on github and include your system specs such as OS, RAM, CPU (include speed and type), and your settings.py file.

## Installation
### NOTE: Chrome (or at least Chromium) MUST be installed on your system. You will get cryptic errors otherwise!

### NOTE EXTENDED: Installing this package globally will likely cause you to have to run in root....
### This is to be expected; if this isn't what you want, install in a virtual environment instead! **!!!DO NOT submit an issue for this as it is EXPECTED BEHAVIOR!!!**

#### Method One: ***Using git clone***
```bash
git clone https://github.com/leogomezz4t/PyTextNow_API
```

#### Method Two: ***Using pip***
```bash
pip install PyTextNow
```
*Note: If there is a permissions error with the pip install, try installing with **sudo** or by adding the **--user** flag to it.*


## Usage
**NOTE** - The version of your password stored in the database IS NOT encrypted.
### Stay logged in forever!
[SilverStrings024]() found a way to, after you provide credentials to the database, not have to login manually nor get the sid ever again unless the accounts stored in the database are destroyed, your account(s) is suspended/banned or the robot plain out fails.

**How It Works**
When you start the program, the CellPhone object will create a Database Handler object which will create
the database and tables automatically. After the database handler has completed its set up, the CellPhone
will create a RoboBoi instance and use its `choose_account` method to do one of three things.

1. Prompt you for a username and password (only happens if no account exists in the database yet)
2. Automatically chooses the first account in the database if it's the only one we have
OR
3. List all of your accounts and allow you to choose one to use by entering the number listed to the left of it

After you choose an account or provide details to create a new one, RoboBoi will navigate to textnow.com/login and use the information you entered to log in. The robot will attempt to verify that it logged in successfully after submitting the form, if it did not get a successful login, it will look for signs of incorrect credentials. If It sees that the credentials were incorrect, it will pause everything and ask you to re-enter them.
After a successful login, RoboBoi will have the DatabaseHandler update the information in the database to match what you just successfully logged in with.

If/when we get a successful login, the robot will leave the page open and refresh it at random intervals between 12 to 24 hours. This completely removes the need for YOU to go get the connect.sid cookie value and instead, pawn it off on a robot to get it for you! Don't you just love automation? :D

NOTE: If the program stops, the robot WILL have to log in again however, it will retain your account information. so you only need to start the program again and choose the account you want

### How to get the cookie
#### **Replaced with autonomous login** See [Ways to authenticate](auth)
DEPRECATED - [How to get the cookie](get_cookie.mp4)

### How to get your username
[How to get TextNow username](get_username.mp4)

### Ways to authenticate
```python
# Yes, this is seriously all you have to do
import pytextnow
cell_phone = pytextnow.CellPhone()
# The cell phone will automatically create the database and its tables,
# then prompt you to provide a username and password. After you provide
# login credentials the first time, you won't have to do it again unless
# you change your password, your account is banned/suspended or you
# want to use a different account
```
### What replaced Client.auth_reset()?
The CellPhone object replaces the Client object completely.
It was designed to prevent you from having to do the more tedious/annoying things like finding your connect.sid cookie value or manually logging in over and over.
**How It Works**
When you call a CellPhone method like cellphone.send_sms(), it will attempt to send your message using the
connect.sid cookie value that the robot found. If the message fails to send, the cellphone will tell the robot to make sure we're still logged in. If we're not, it will print something to the terminal saying "!!!WARNING!!! RoboBoi was logged out, attempting to log in again..."
This is purely just to keep you informed since the robot should handle everything for you.

If the robot is banned, suspended or redirected to an unexpected page, it will take a screenshot of the last thing it saw and raise a [RobotException](robot-exceptions).

**TODO**
If the robot is told that it has the wrong username or password, it will prompt you to re-enter the credentials. After a successful log in, the credentials in the database will be updated with your new information.

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
#### Replaced with Event Listener
DEPRECATED - New messages are automatically grabbed from the API and saved in the database.
This is an optimization technique that will dramatically decrease the amount of requests we send and how much data is stored in RAM while python does things.
This also dramatically increases speeds since SQL is MUCH faster than api calls.

```python
# Check if the cellphone has new sms
new_sms = cellphone.new_sms()
if new_sms:
    for message in new_sms.order_by('-date'):

        print(message)

new_messages = cellphone.get_unread_messages() -> MessageContainer list
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
    # reply_sms() will send an sms to the number who sent the message
    # reply_mms() will send an mms to the number who sent the message (calls self.__api_handler.send_* since all this happens in the cellphone object)
    
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
messages = cellphone.get_messages(paginate_by=50) -> Container list
# Same as above
```
### How to get all sent messages
```python 
sent_messages = cellphone.get_sent_messages() -> Container list
#Same as above
```

### How to filter messages
```python
# 50 messages per page. Only get messages with this number
filtered = cellphone.sms.filter(number="+19876543212")
```

### How to get contacts
```python
# Returns a Container object which has a .first()
contacts = client.get_contacts()
first_contact = contacts.first()
print(contact.number)
print(contact.name)
```

### How to filter contacts
```python
filtered = contacts.filter(name="Alice")
```

### How to synchronously block until a response
```python
# This will wait for a response from someone and return the Message

msg = client.await_response("number")

# This function will work with a message object too
# I don't understand this. Why would you wait for a response to a message you haven't read
# If this means get sent unread then this needs to change
unreads = client.get_unread_messages()
for unread in unreads:
    msg = unread.await_response()
```

## NEW Simple bot snippet
```python
import pytextnow as pytn

client = pytn.CellPhone("username goes here") # Username is optional
# Uses the new ListenerEvents object
@cellphone.on_incoming("new_Message")
def handler(msg):
    print(msg)
    if msg.type == pytn.MESSAGE_TYPE:
        if msg.content == "ping":
            msg.reply_sms("pong")
        else:
            msg.mv("test" + msg.extension)
``` 

## Custom Module Exceptions

### FailedRequest:
This API runs on web requests and if the request fails this Exception will be raised

### AuthError:
If the provided username or password was incorrect, your account was banned/suspended or deleted, this will be raised

### RobotError:
If the robot encounters something it was not prepared for, it will raise a RobotException. This will happen if the robot has run out of options to accomplish its goal.

### ListenerError
You will see this if the Event Listener Server raises an exception. This should be rare but *can* happen.
If it does and you're not using it directly, please create a new issue on github.

### TNApiError
Occurs when the ApiHandler object hits an exception internally or if Text Now returns an error code.

### NetworkError
There's an issue with your internet

### DatabaseHandlerError
This will obviously be raised any time the database handler runs into an error.
Please note that if it hits an error before committing its last entry, you **will** lose that data.

### BrowserError
Occurs when something is wrong with the browser. Such as a crash, freezing, no loading, etc.

## Patch Notes

### 2.0.0
- Refactoring files/cleaning up
- [Stay Logged in Forever!](staying-logged-in)
- Added `User` class to represent user accounts
- Added `Contact` class
- Added `Container` class
    - [Added convenience methods](using-the-container)
- Switched from using a file to [database](database-handler)
- Added [Robot](roboboi) for autonomous login
- Added [Event Listener server](event-listening) for notifications on new messages
- [ApiHandler object created](api-handler)
- [QueryBuilder object created](query-building)
- [New exceptions created](custom-exceptions)
- [SilverStrings024 wrote tests](running-the-tests)

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
