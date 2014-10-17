###########################################################################
#
#   File Name      Date          Owner              Description
#   ----------    -------      ---------          -----------------
#   role.py      7/8/2014   Archana Bahuguna    Manages user and admin roles 
#                                                 for qzengine APIs
#
###########################################################################

from functools import wraps
from flask import request, Response,json
import logs

def admin_required(f):
    """Decorator fn that authenticates user:admin """
    @wraps(f) #this fn allows the doc strings of dec fn to be displayed
    def role_decorator(*args, **kwargs):
        # get username password from HTTP Basic Authentication header in 
        # request- Authorization: 'Basic username:password'
        logs.debug_ ( "\n-------role.py required------\n")
        auth = request.headers.get('Authorization')
        # Auth header is in the form 'basic username:pwd role:admin'
        import views
        from views import handle_invalid_usage, InvalidUsageException
        if not auth:
            response = handle_invalid_usage(InvalidUsageException \
                                            ('Error: Authorization required', \
                                            status_code=401))
            return response
        role = auth.split()[2].split(':').pop()
        if ("admin" != role):
            logs.debug_ ( "Error role should be admin to access the resource")
            response = handle_invalid_usage(InvalidUsageException \
                        ('Error: Cannot access resource, role should be admin', \
                                            status_code=401))
            return response
        return f(*args, **kwargs)

    return role_decorator
