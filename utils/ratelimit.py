from rest_framework.views import exception_handler as drf_exception_handler
from ratelimit.exceptions import Ratelimited

def exception_handler(exc, context):
    # Call REST framework default exception handler first
    # Get the standard error response.
    response = drf_exception_handler(exc, context)

    # Add the HTTP status code to response
    if isinstance(exc, Ratelimited):
        response.data['detail'] = 'Too many requests, try again later.'
        response.status_code = 429

    return response