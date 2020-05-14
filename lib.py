import hashlib, binascii, os

from flask import redirect, request, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorate routes to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin") is None:
            return redirect("/adminlogin")
        return f(*args, **kwargs)
    return decorated_function

def hashPassword(password):
    # hash password
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verifyPassword(storepwd, newpwd):
    salt = storepwd[:64]
    storepwd = storepwd[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  newpwd.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return storepwd == pwdhash