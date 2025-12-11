from functools import wraps
from flask import session, redirect, url_for, flash, abort
from MyFlaskapp.db import get_db_connection
import re

def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('user_role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if session.get('user_role') not in allowed_roles:
                flash('Access denied. Insufficient permissions.', 'danger')
                return redirect(url_for('user.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def no_cache(f):
    """Decorator to prevent browser caching"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return decorated_function

def validate_username(username):
    """Validate username format"""
    if not username:
        return False, "Username is required"
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 20:
        return False, "Username must not exceed 20 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Username is valid"

def validate_email(email):
    """Validate email format"""
    if not email:
        return False, "Email is required"
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    return True, "Email is valid"

def check_username_exists(username):
    """Check if username already exists"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT user_id FROM user_tb WHERE username = %s", (username,))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Error checking username: {e}")
            return False
        finally:
            conn.close()
    return False

def check_email_exists(email):
    """Check if email already exists"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT user_id FROM user_tb WHERE email = %s", (email,))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Error checking email: {e}")
            return False
        finally:
            conn.close()
    return False

def log_activity(user_id, action, description="", ip_address="", user_agent=""):
    """Log user activity"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Check if user_id exists in user_tb table
            cursor.execute("SELECT user_id FROM user_tb WHERE user_id = %s", (user_id,))
            if cursor.fetchone() is None:
                print(f"Warning: Cannot log activity for non-existent user_id: {user_id}")
                return
            
            cursor.execute("""
                INSERT INTO activity_logs (user_id, action, description, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, action, description, ip_address, user_agent))
            conn.commit()
        except Exception as e:
            print(f"Error logging activity: {e}")
        finally:
            conn.close()
