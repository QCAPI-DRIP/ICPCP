class APIError(Exception):
    """API erorr handling"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIEERROR: status={}".format(self.status)