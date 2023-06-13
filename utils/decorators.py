from rest_framework.response import Response
from rest_framework import status
from functools import wraps

def required_params(method='get', params=None):
    """
    This is a decorator function to verify whether the required parms and attrs are exist,
    then response unified error ask client side to modify or proceed the normal function

    change log:
    request_attr has been changed to method.

    # :param request_attr:
    # string
    # check whether the request has the attribute
    # it is verifying whether the request is using the correct method

    :param method:
    string
    Check whether the request matches the required method
    By default, it is 'query_params' for GET method, 'data' for POST method.

    :param params:
    list of string
    check whether the request has the parameters inside the request attribute
    """
    
    # Edge case verify
    if params is None:
        params = []

    def decorator(view_func):
        """
        This function use @wraps to pass the function parameters of view_func() to warpped_view().

        This layer of decorator is a generator of the read decorator, wrapped_view.
        Why this layer? Need to use @wraps to pass the parameters.

        :param view_func:
        the function actually called, which will be sent to this decorator() function as a parameter
        """

        # This @wraps function will take the view_func function as a parameter
        # take out the parameters of view_func for wrapped_view to use
        @wraps(view_func)
        def wrapped_view(instance, request, *args, **kwargs):
            """
            instance: the instance(self) of the view_func
            request: the request object directly passed to the view_func
            *args, **kwargs: the arguments directly passed to the view_func
            """
            if method.lower() == 'get':
                data = request.query_params
            elif method.lower() in ['post', 'put', 'patch']:
                data = request.data
            missing_params = [
                param                       # what do you want
                for param in params         # how to iterate
                if param not in data        # requirements
            ]
            if missing_params:
                params_str = ', '.join(missing_params)
                return Response({
                    'success': False,
                    'message': f'Missing parameters: {params_str}',
                }, status=status.HTTP_400_BAD_REQUEST)
            return view_func(instance, request, *args, **kwargs)
        return wrapped_view
    return decorator