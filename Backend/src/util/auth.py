from src import  app

from  werkzeug.security import  check_password_hash
import traceback

# imports for PyJWT authentication
import jwt
from datetime import datetime, timedelta
from functools import wraps

from flask import  request
from flask_api import status
import re


from src.service.response import *
from src.handler.users import *
# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            token = token.split()[1]
        # return 401 if token is not passed
        if not token:
            return ApiResponse(message='Token is missing !!'), status.HTTP_401_UNAUTHORIZED
        try:
            
            # decoding the payload to fetch the stored details
            user_info = jwt.decode(token, 'Goback-TVS', algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return ApiResponse(message='Signature expired. Please log in again.'), status.HTTP_401_UNAUTHORIZED
        except jwt.InvalidTokenError:
            print(traceback.format_exc())
            return ApiResponse(message='Invalid token. Please log in again.'), status.HTTP_401_UNAUTHORIZED
        except:
            print(traceback.format_exc())
            return ApiResponse(message='Token is invalid !!'), status.HTTP_401_UNAUTHORIZED

        # returns the current logged in users contex to the routes
        return  f(user_info, *args, **kwargs)
    return decorated

def get_authen_info_from_context(authenicateInfo,log):
    pass

def validate_password(password,log):
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    if not password :
        return False,'password cannot be empty'
    pwd =re.compile(reg)

    match = re.search(pwd, password)
    if not match:
        return False, 'Password is invalid'
    return True, None

def compare_password(hash_password,current_password,log):
    try:
        res = check_password_hash(hash_password, current_password)
        if res :
            return DataReponse(message = 'Successful',code= CODE_DONE)
        return DataReponse(message = 'Wrong password!!!',code= CODE_UNAUTHORIZE)
    except Exception as e:
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)


def generate_jwt_token(payload,secret_key,log):
    try:
        token = jwt.encode(payload, 'Goback-TVS',algorithm="HS256")
        return True,token
    except Exception as e:
        log.error(e)
        return False, None