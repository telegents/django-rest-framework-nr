from rest_framework.exceptions import status, APIException

class ConflictError(APIException):
    """
    Base class for REST framework exceptions.
    Subclasses should provide `.status_code` and `.default_detail` properties.
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = u'A database conflict occurred.'

    def __init__(self, detail=None):
        self.detail = detail if detail else self.default_detail

    def __str__(self):
        return self.detail

