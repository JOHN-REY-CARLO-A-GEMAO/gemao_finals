from flask import flash
from MyFlaskapp.db import get_db_connection

def Alert_Success(message):
    flash(message, 'success')

def Alert_Fail(message):
    flash(message, 'danger')

def get_system_setting(setting_key, default=None):
    """Get system setting from database"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = %s", (setting_key,))
            result = cursor.fetchone()
            return result['setting_value'] if result else default
        except Exception as e:
            print(f"Error getting system setting: {e}")
            return default
        finally:
            conn.close()
    return default
