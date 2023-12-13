from rest_framework.views import exception_handler
from .exception import CustomExceptionHandler
from rest_framework.response import Response

def custom_exception_handler(exc,context):
    if isinstance(exc,CustomExceptionHandler):
        response_data = {
            'error': {
                'code': exc.code,
                'message': exc.message,
                'errors': exc.errors,
            }
        }
        return Response(response_data, status=getattr(exc, 'status_code', 400))

    return exception_handler(exc, context)