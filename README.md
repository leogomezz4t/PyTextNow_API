# TextNow API
### TNAPI is a python module that uses [TextNow](https://www.textnow.com/) to enable free programmable texting 

## Installation
#### Method One: ***Using git clone***
```bash
git clone https://github.com/WuGomezCode/TextNow-API.git
```
#### Method Two: ***Using pip***
```bash
pip install TNAPI
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
    #output: {
    # "id": int,
    # "username": str,
    # "contact_value": str, Phone Number
    # "message": str|link to media,
    # "read": bool,
    # "date": ISO date string
    # }
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

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)