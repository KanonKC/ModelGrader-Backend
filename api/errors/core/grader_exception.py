from rest_framework.response import Response

class GraderException(Exception):
    def __init__(self, error: str, status: int):
        self.error = error
        self.status = status
        super().__init__(self.error)

    def django_response(self):
        return Response({'message': self.error}, status=self.status)