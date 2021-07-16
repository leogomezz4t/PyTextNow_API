import typing
from base import BaseError

class RobotError(BaseError):
    def __init__(self, message: str, errors: typing.Union[list, str]) -> None:
        super().__init__(message, errors)

