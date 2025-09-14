from api.errors.core.grader_exception import GraderException


class IncorrectPasswordError(GraderException):
    def __init__(self):
        super().__init__("Incorrect password.", 406)