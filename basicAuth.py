###########################################################################
#
#   File Name      Date          Owner              Description
#   ---------      ----          ----               -----------
#   basicauth.py  7/8/2014   Archana Bahuguna    Basic Authentication
#                                                for qzengine Restful APIs
#
###########################################################################

from functools import wraps
from flask import request, Response, jsonify, json, session
import models, views, logs

def check_auth(username, password):
    #check for username 
    query_obj = models.User.query.filter_by(username=username).all()
    user_index = None
    for i in range(len(query_obj)):
        if username in query_obj[i].username:
            user_index = i
    if user_index is None:
        return False

    #check for encrypted password 
    if not views.bcrypt.check_password_hash(
                    query_obj[user_index].password, password):
        return False
    return True

def send_authenticate_req():
    response =jsonify(dict())
    response.status_code = 401
    response.headers['WWW-Authenticate'] = 'Basic realm="Login Required"'
    response.location = '/users'
    return response

def login_required(f):
    """Decorator fn that authenticates user/admin """
    @wraps(f) #this fn allows the doc strings of dec fn to be displayed
    def auth_decorator(*args, **kwargs):
        # get username password from HTTP Basic Authentication header in 
        # request- Authorization: 'Basic username:password'
        logs.debug_( "\n-------basicauth.py; login required------\n")
        auth = request.headers.get('Authorization')
        if not auth:
            return send_authenticate_req()

        # Auth header is in the format 'basic username:pwd role:admin'
        username, password = tuple(auth.split()[1].split(':'))

        if not check_auth(username, password):
            #Maybe we need to set a flag to limit the no of times
            # we should authenticate?
            logs.debug_( "Invalid username or password")
            return send_authenticate_req()

        #Create Flask session here after user is authenticated
        if 'username' not in session:
            session['username'] = username

        return f(*args, **kwargs)

    return auth_decorator
