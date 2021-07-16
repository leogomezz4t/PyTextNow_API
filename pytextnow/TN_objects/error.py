# Custom Errors
"""
class InvalidFileType(Exception):
    def __init__(self, file_type):
        self.message = f"The file type {file_type} is not supported.\nThe only types supported are images and videos."

    def __str__(self):
        return self.message
"""


import typing
from pytextnow import settings

class FailedRequest(Exception):
    def __init__(self, status_code: str):
        self.status_code = status_code

        if status_code.startswith('3'):
            self.error_msg = "server redirected the request. Request Failed."
        elif status_code.startswith('4'):
            self.error_msg = "server returned a Client error. Request Failed. Try resetting your authentication with " \
                          "client.auth_reset() "
        elif status_code.startswith('5'):
            if status_code == "500":
                self.error_msg = "Internal Server Error. Request Failed."
            else:
                self.error_msg = "server return a Server error. Request Failed."

    def __str__(self):
        message = f'Could not send message. {self.error_msg}\nStatus Code: {self.status_code}'
        return message


class AuthError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


class InvalidEvent(Exception):
    def __init__(self, event):
        self.event = event

    def __str__(self):
        return f"{self.event} is an invalid event."


class BaseError(Exception):
    def __init__(self, message: str, errors: typing.Union[list, str]) -> None:
        super().__init__(message)
        self.errors = errors
        if isinstance(errors, list):
            print("\n\nERRORS\n\n")
            for error in errors:
                print(error)
        else:
           print(self.error)

class NetworkError(BaseError):
    """
    Error describing some sort of unexpected network issue like
    disconnecting or if the Listener server fails and exits.
    """
    def __init__(
        self, message: str,
        errors: typing.Union[list, str],
        proxy=None, vpn=None, port=settings.LISTENER_PORT
        ) -> None:
        super().__init__(message, errors)

class BrowserError(BaseError):
    def __init__(self, message: str, errors: typing.Union[list, str]) -> None:
        super().__init__(message, errors)
    
class ApiError(BaseError):
    def __init__(self, message: str, errors: typing.Union[list, str]) -> None:
        super().__init__(message, errors)

class ListenerError(BaseError):
    def __init__(self, message: str, errors: typing.Union[list, str]) -> None:
        super().__init__(message, errors)

class DatabaseHandlerError(BaseError):
    def __init__(self, message: str, errors: typing.Union[list, str]) -> None:
        super().__init__(message, errors)

class RobotError(BaseError):
    def __init__(self, message: str, errors: typing.Union[list, str]) -> None:
        super().__init__(message, errors)

