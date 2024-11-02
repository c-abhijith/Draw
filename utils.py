from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # Check if user is logged in
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:  # Prevent logged-in users from accessing certain routes
            flash("You are already logged in.", "info")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function
