#!/usr/bin/env python3
"""
Script to remove dummy users and keep only real users in the database.
This will identify and remove fictional Naruto characters while keeping legitimate users.
"""

import mysql.connector
from MyFlaskapp import db

def get_current_users():
    """Get all current users from the database"""
    conn = db.get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_tb ORDER BY created_at")
        users = cursor.fetchall()
        return users
    except Exception as e:
        print(f"Error getting users: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def identify_dummy_users():
    """Identify likely dummy/fictional users based on names"""
    dummy_names = [
        'Kakashi', 'Hatake', 'Naruto', 'Uzumaki', 'Sasuke', 'Uchiha',
        'Sakura', 'Haruno', 'Hinata', 'Hyuga', 'Shikamaru', 'Nara',
        'Choji', 'Akimichi', 'Ino', 'Yamanaka', 'Kiba', 'Inuzuka',
        'Shino', 'Aburame', 'Rock', 'Lee', 'Neji', 'Tenten',
        'Gaara', 'Temari', 'Kankuro', 'Jiraiya', 'Tsunade', 'Orochimaru',
        'Itachi', 'Deidara', 'Sasori', 'Hidan', 'Kakuzu', 'Pain',
        'Konan', 'Madara', 'Obito', 'Tobirama', 'Hashirama', 'Sarutobi',
        'Minato', 'Kushina', 'Boruto', 'Himawari', 'Sarada', 'Mitsuki'
    ]
    
    users = get_current_users()
    dummy_users = []
    real_users = []
    
    for user in users:
        first_name = (user.get('firstname') or '').lower()
        last_name = (user.get('lastname') or '').lower()
        full_name = f"{first_name} {last_name}"
        
        is_dummy = False
        for dummy_name in dummy_names:
            if dummy_name.lower() in first_name or dummy_name.lower() in last_name:
                is_dummy = True
                break
        
        if is_dummy:
            dummy_users.append(user)
        else:
            real_users.append(user)
    
    return dummy_users, real_users

def remove_dummy_users(dummy_users):
    """Remove dummy users from database"""
    conn = db.get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        for user in dummy_users:
            user_id = user['user_id']
            print(f"Removing dummy user: {user['firstname']} {user['lastname']} ({user_id})")
            
            # Delete related records first (foreign key constraints)
            cursor.execute("DELETE FROM game_access WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM activity_logs WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM otp_tb WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM profiles WHERE user_id = %s", (user_id,))
            
            # Delete the user
            cursor.execute("DELETE FROM user_tb WHERE user_id = %s", (user_id,))
        
        conn.commit()
        print(f"Successfully removed {len(dummy_users)} dummy users")
        return True
        
    except Exception as e:
        print(f"Error removing dummy users: {e}")
        conn.rollback()
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def update_game_access_for_real_users(real_users):
    """Ensure all real users have access to all games"""
    conn = db.get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Get all games
        cursor.execute("SELECT game_code FROM games")
        games = cursor.fetchall()
        
        # Grant access to all real users
        for user in real_users:
            user_id = user['user_id']
            for game in games:
                game_code = game[0]
                
                # Insert access if not exists
                cursor.execute("""
                    INSERT IGNORE INTO game_access (user_id, game_code, granted_by)
                    VALUES (%s, %s, 'admin001')
                """, (user_id, game_code))
        
        conn.commit()
        print(f"Updated game access for {len(real_users)} real users")
        return True
        
    except Exception as e:
        print(f"Error updating game access: {e}")
        conn.rollback()
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def main():
    print("Checking current users in database...")
    dummy_users, real_users = identify_dummy_users()
    
    print(f"\nFound {len(dummy_users)} dummy users:")
    for user in dummy_users:
        print(f"  - {user['firstname']} {user['lastname']} ({user['username']})")
    
    print(f"\nFound {len(real_users)} real users:")
    for user in real_users:
        print(f"  - {user['firstname']} {user['lastname']} ({user['username']})")
    
    if dummy_users:
        print(f"\nRemoving {len(dummy_users)} dummy users...")
        if remove_dummy_users(dummy_users):
            print("Dummy users removed successfully!")
            
            print("Updating game access for real users...")
            update_game_access_for_real_users(real_users)
        else:
            print("Failed to remove dummy users")
    else:
        print("No dummy users found!")
    
    print("\nCleanup complete!")

if __name__ == "__main__":
    main()
