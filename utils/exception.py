

class CustomExceptionHandler(Exception):
    def __init__(self,message,code = None,errors = None):
        self.message = message
        self.code = code
        self.errors = errors
        super().__init__(message)
        
        
        
        