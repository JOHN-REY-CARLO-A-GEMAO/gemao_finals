import random
import string
from datetime import datetime, timedelta
from flask import current_app, url_for
from MyFlaskapp.db import get_db_connection

def generate_otp(length=4):
    """Generate a random OTP code"""
    return ''.join(random.choices(string.digits, k=length))

def store_otp(user_id, email, otp_code):
    """Store OTP in database"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Delete any existing OTP for this user
            cursor.execute("DELETE FROM otp_tb WHERE user_id = %s", (user_id,))
            
            # Insert new OTP
            cursor.execute("""
                INSERT INTO otp_tb (user_id, otp_code, email, expires_at)
                VALUES (%s, %s, %s, %s)
            """, (user_id, otp_code, email, datetime.now() + timedelta(minutes=15)))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error storing OTP: {e}")
            return False
        finally:
            conn.close()
    return False

def verify_otp(user_id, otp_code):
    """Verify OTP code"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM otp_tb 
                WHERE user_id = %s AND otp_code = %s 
                AND used = FALSE AND expires_at > NOW()
            """, (user_id, otp_code))
            otp_record = cursor.fetchone()
            
            if otp_record:
                # Mark OTP as used
                cursor.execute("UPDATE otp_tb SET used = TRUE WHERE id = %s", (otp_record['id'],))
                # Activate user account
                cursor.execute("UPDATE user_tb SET status = 'active' WHERE user_id = %s", (user_id,))
                conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Error verifying OTP: {e}")
            return False
        finally:
            conn.close()
    return False

def send_otp_email(email, otp_code, user_name):
    """Send OTP via email using Flask-Mail"""
    try:
        from flask_mail import Message
        from flask import current_app
        
        mail = current_app.extensions.get('mail')
        if not mail:
            print("Flask-Mail not initialized")
            return False
            
        msg = Message(
            'Your OTP Code - Ninja Academy',
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = f"Hello {user_name},\n\nYour OTP code is: {otp_code}\n\nThis code will expire in 15 minutes.\n\nThank you,\nNinja Academy Team"
        mail.send(msg)
        
        print(f"Email sent to: {email}, OTP: {otp_code}")
        return True
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False

def cleanup_expired_otp():
    """Clean up expired OTP codes"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM otp_tb WHERE expires_at < NOW()")
            conn.commit()
            return True
        except Exception as e:
            print(f"Error cleaning up OTP: {e}")
            return False
        finally:
            conn.close()
    return False
