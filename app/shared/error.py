class BizError(Exception):
    def __init__(self, message: str, code: int = 400, data=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data
