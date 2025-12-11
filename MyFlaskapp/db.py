import mysql.connector
from mysql.connector import Error
import bcrypt

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS gemao_db")
            cursor.execute("USE gemao_db")
            print("Connected to database: gemao_db")
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_user_table():
    """Creates the user_tb table in the database and inserts default users."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_tb (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50) UNIQUE,
                firstname VARCHAR(100),
                middlename VARCHAR(100),
                lastname VARCHAR(100),
                username VARCHAR(100) UNIQUE,
                password VARCHAR(255),
                user_type ENUM('user', 'admin'),
                status ENUM('pending', 'active', 'disabled') DEFAULT 'pending',
                birthdate DATE,
                address VARCHAR(255),
                mobile_number VARCHAR(20),
                email VARCHAR(100),
                avatar_url VARCHAR(255)
            )
        """)
        conn.commit()
        print("Table 'user_tb' created successfully.")

        # Hash passwords
        admin_password_hashed = bcrypt.hashpw('admin_password'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_password_hashed = bcrypt.hashpw('user_password'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert or update default admin user
        cursor.execute("""
            INSERT INTO user_tb (user_id, firstname, lastname, username, password, user_type, status, birthdate, address, mobile_number, email)
            VALUES ('573', 'carlo', 'arguilles', 'admin', %s, 'admin', 'active', '2008-06-26', 'mhv', '09634628387', 'nevop74006@gmail.com')
            ON DUPLICATE KEY UPDATE
                firstname=VALUES(firstname),
                lastname=VALUES(lastname),
                password=VALUES(password),
                user_type=VALUES(user_type),
                status=VALUES(status),
                birthdate=VALUES(birthdate),
                address=VALUES(address),
                mobile_number=VALUES(mobile_number),
                email=VALUES(email)
        """, (admin_password_hashed,))

        # Insert or update default normal user
        cursor.execute("""
            INSERT INTO user_tb (user_id, firstname, lastname, username, password, user_type, status, birthdate, address, mobile_number, email)
            VALUES ('221', 'john', 'rey', 'user', %s, 'user', 'active', '2003-06-12', '123 Main St, Anytown, USA', '094563421', 'j23245164@gmail.com')
            ON DUPLICATE KEY UPDATE
                firstname=VALUES(firstname),
                lastname=VALUES(lastname),
                password=VALUES(password),
                user_type=VALUES(user_type),
                status=VALUES(status),
                birthdate=VALUES(birthdate),
                address=VALUES(address),
                mobile_number=VALUES(mobile_number),
                email=VALUES(email)
        """, (user_password_hashed,))

        conn.commit()
        print("Default users 'admin' and 'user' ensured.")

    except Error as e:
        print(f"Error creating table or inserting users: {e}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_activity_logs_table():
    """Creates the activity_logs table in the database."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50),
                action VARCHAR(100),
                description TEXT,
                ip_address VARCHAR(45),
                user_agent VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Table 'activity_logs' created successfully.")
    except Error as e:
        print(f"Error creating activity_logs table: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_games_table():
    """Creates the games table in the database."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INT AUTO_INCREMENT PRIMARY KEY,
                game_code VARCHAR(50) UNIQUE,
                game_name VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        conn.commit()
        print("Table 'games' created successfully.")
    except Error as e:
        print(f"Error creating games table: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_game_access_table():
    """Creates the game_access table in the database."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_access (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50),
                game_code VARCHAR(50),
                access_granted BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES user_tb(user_id),
                FOREIGN KEY (game_code) REFERENCES games(game_code)
            )
        """)
        conn.commit()
        print("Table 'game_access' created successfully.")
    except Error as e:
        print(f"Error creating game_access table: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_blog_posts_table():
    """Creates the blog_posts table in the database."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blog_posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                author_id VARCHAR(50),
                title VARCHAR(255),
                content TEXT,
                status ENUM('draft', 'published') DEFAULT 'draft',
                tags TEXT,
                view_count INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES user_tb(user_id)
            )
        """)
        conn.commit()
        print("Table 'blog_posts' created successfully.")
    except Error as e:
        print(f"Error creating blog_posts table: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_profiles_table():
    """Creates the profiles table in the database."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50) UNIQUE,
                first_name VARCHAR(100),
                middle_name VARCHAR(100),
                last_name VARCHAR(100),
                birthday DATE,
                contact VARCHAR(20),
                email VARCHAR(100),
                dream_job VARCHAR(100),
                bio TEXT,
                FOREIGN KEY (user_id) REFERENCES user_tb(user_id)
            )
        """)
        conn.commit()
        print("Table 'profiles' created successfully.")
    except Error as e:
        print(f"Error creating profiles table: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_otp_table():
    """Creates the otp_tb table in the database."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otp_tb (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50),
                otp_code VARCHAR(10),
                email VARCHAR(100),
                used BOOLEAN DEFAULT FALSE,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Table 'otp_tb' created successfully.")
    except Error as e:
        print(f"Error creating otp_tb table: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_system_settings_table():
    """Creates the system_settings table in the database."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                setting_key VARCHAR(100) UNIQUE,
                setting_value TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Table 'system_settings' created successfully.")
    except Error as e:
        print(f"Error creating system_settings table: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_blog_comments_table():
    """Creates the blog_comments table in the database."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blog_comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                post_id INT,
                user_id VARCHAR(50),
                comment TEXT,
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES blog_posts(id),
                FOREIGN KEY (user_id) REFERENCES user_tb(user_id)
            )
        """)
        conn.commit()
        print("Table 'blog_comments' created successfully.")
    except Error as e:
        print(f"Error creating blog_comments table: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    create_user_table()
    create_activity_logs_table()
    create_games_table()
    create_game_access_table()
    create_blog_posts_table()
    create_blog_comments_table()
    create_profiles_table()
    create_otp_table()
    create_system_settings_table()
