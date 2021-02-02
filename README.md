# TextNow API
### TNAPI is a python module that uses [TextNow](https://www.textnow.com/) to enable free programmable texting 

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

*Edit: New Note: The first time using this module will require firefox to authenticate TextNow. It may or may not provide a recaptcha for you to do once.*

**Edit: New Note: The first authentication process uses geckodriver.exe. The module installs geckodriver.exe for windows. However if you are on MacOS or Linux, install your OS specific version of GeckoDriver and specify the path when instantiating Client*


## Usage
### How to send an sms message
```python
import TNAPI

client = TNAPI.Client("Email address", "Password", "Name") #The name is used for the message storing.

client.send_sms("18006969420", "Hello World!")
```
### How to send an mms message
```python
file_path = "./img.jpeg"
client.send_mms("18006969420", file_path)
```
### How to get new messages
```python
new_messages = client.get_new_messages() -> List
for message in new_messages:
    print(message)
    # Class Message | Class MultiMediaMessage
    # Message
    # content: "body of sms"
    # number: "number of sender"
    # date: datetime object of when the message was received
    # first_contact: bool if its the first time that number texted you
    # type: int 0 if class is Message and 1 if class is MultiMediaMessage
    
    # MultiMediaMessage
    # number: "number of sender"
    # date: datetime object of when the message was received
    # first_contact: bool if its the first time that number texted you
    # type: int 0 if class is Message and 1 if class is MultiMediaMessage
    # url: "url of the media"
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
### How to get all received messages
```python
messages = client.get_messages() -> List
# Same as above
```
### How to get all sent messages
```python 
sent_messages = client.get_sent_messages() -> List
#Same as above
```

## Custom Module Exceptions

### InvalidFileType:
#### When using send_mms() if the file type is not an image or video it will raise this Exception
### FailedRequest:
#### This API runs on web requests and if the request fails this Exception will be raised


## Patch Notes 

### 9.0
- Using Message and MultiMediaMessage classes instead of dictionary for /get_new_messages/get_sent_messages
- get_messages still returns old dictionary

### 0.8
- Fixed the receiving messages. Now working 100%

### 0.7
- Added FailedRequest and InvalidFileType errors to Client instance

### 0.6
- Fixed the user_sids.json overwrite bug

### 0.5
- bug fixes

### 0.4
- Added `Client = TNAPI.Client` in \_\_init\_\_.py
- Fixed the failed login import in TNAPI.py

### 0.3
- Receiving messages are better but not good

### 0.2
- Nothing much

### 0.1
- Initial Commit
- Can send messages and photos/videos
- receiving messages a work in progress

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)