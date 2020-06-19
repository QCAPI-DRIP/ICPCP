class APIError(Exception):
    """API erorr handling"""

    def __init__(self, message, status=None):
        if status is not None:
            self.status = status
        self.message = message

    def __str__(self):
        return "API error: {} status code= {}".format(self.message, self.status)