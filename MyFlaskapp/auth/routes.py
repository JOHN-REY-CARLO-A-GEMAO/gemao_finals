from flask import render_template, redirect, url_for, flash, request, session
from datetime import datetime
from . import auth_bp
from MyFlaskapp.db import get_db_connection
from MyFlaskapp.utils import (
    login_required, validate_username, validate_email, 
    check_username_exists, check_email_exists, log_activity,
    generate_otp, store_otp, verify_otp, send_otp_email
)
import bcrypt


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            sql_query = "SELECT * FROM user_tb WHERE username = %s"
            cursor.execute(sql_query, (username,))
            user = cursor.fetchone()
            conn.close()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session.permanent = True
                session['user_id'] = user['user_id']
                session['user_name'] = f"{user['firstname']} {user['lastname']}"
                session['user_role'] = user['user_type']
                session['user_info'] = user
                
                # No last_login column in user_tb. If needed, add it to db.py first.
                
                log_activity(user['user_id'], 'login', 'User logged in', ip_address, user_agent)
                flash('You were successfully logged in', 'success')
                
                if user['user_type'] == 'admin':
                    return redirect(url_for('admin.admin_dashboard'))
                else:
                    return redirect(url_for('user.dashboard'))
            else:
                log_activity(None, 'login_failed', f'Failed login attempt for username: {username}', ip_address, user_agent)
                flash('Incorrect Credentials or account not activated', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    if user_id:
        log_activity(user_id, 'logout', 'User logged out', ip_address, user_agent)
    
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', 
                         username=session.get('user_name'),
                         user_role=session.get('user_role'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        
        # Validation
        is_valid, message = validate_username(username)
        if not is_valid:
            flash(message, 'danger')
            return render_template('auth/register.html')
        
        is_valid, message = validate_email(email)
        if not is_valid:
            flash(message, 'danger')
            return render_template('auth/register.html')
        
        if check_username_exists(username):
            flash('Username already exists', 'danger')
            return render_template('auth/register.html')
        
        if check_email_exists(email):
            flash('Email already exists', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('auth/register.html')
        
        # Create user
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                user_id = f"USR{datetime.now().strftime('%Y%m%d%H%M%S')}"
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                cursor.execute("""
                    INSERT INTO user_tb (user_id, firstname, lastname, username, email, password, user_type, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'user', 'pending')
                """, (user_id, firstname, lastname, username, email, hashed_password))
                conn.commit()
                
                # Generate and store OTP
                otp_code = generate_otp()
                if store_otp(user_id, email, otp_code):
                    send_otp_email(email, otp_code, f"{firstname} {lastname}")
                    flash('Registration successful! Please check your email for OTP verification.', 'success')
                    return redirect(url_for('auth.verify_otp', user_id=user_id))
                else:
                    flash('Error generating OTP. Please try again.', 'danger')
                    
            except Exception as e:
                print(f"Error creating user: {e}")
                flash('Error creating account. Please try again.', 'danger')
            finally:
                conn.close()
    
    return render_template('auth/register.html')

@auth_bp.route('/verify-otp/<user_id>', methods=['GET', 'POST'])
def verify_otp(user_id):
    if request.method == 'POST':
        otp_code = request.form.get('otp_code')
        
        if verify_otp(user_id, otp_code):
            flash('Account activated successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid or expired OTP code. Please try again.', 'danger')
    
    return render_template('auth/verify_otp.html', user_id=user_id)

@auth_bp.route('/resend-otp/<user_id>', methods=['POST'])
def resend_otp(user_id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT email, firstname, lastname FROM user_tb WHERE user_id = %s AND status = 'pending'", (user_id,))
            user = cursor.fetchone()
            
            if user:
                otp_code = generate_otp()
                if store_otp(user_id, user['email'], otp_code):
                    send_otp_email(user['email'], otp_code, f"{user['firstname']} {user['lastname']}")
                    flash('OTP code has been resent to your email.', 'success')
                else:
                    flash('Error resending OTP. Please try again.', 'danger')
            else:
                flash('User not found or account already activated.', 'danger')
                
        except Exception as e:
            print(f"Error resending OTP: {e}")
            flash('Error resending OTP. Please try again.', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('auth.verify_otp', user_id=user_id))
