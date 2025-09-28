from api.errors.core.grader_exception import GraderException

class InvalidTokenError(GraderException):
    def __init__(self):
        super().__init__("Token expired or invalid.", 401)

class ItemNotFoundError(GraderException):
    def __init__(self, item: str = "Item"):
        super().__init__(f"{item} not found.", 404)

class PermissionDeniedError(GraderException):
    def __init__(self):
        super().__init__("You do not have permission.", 403)

# TODO: Move this file
class InvalidFileError(GraderException):
    def __init__(self):
        super().__init__("Invalid file.", 400)

class InternalServerError(GraderException):
    def __init__(self, e: Exception):
        super().__init__(e if e else "Internal server error.", 500)

class BadRequestError(GraderException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, 400)
