from functools import wraps
from flask import redirect, render_template, request, session

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not "user_id" in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function