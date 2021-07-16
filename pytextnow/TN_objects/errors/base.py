import typing

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