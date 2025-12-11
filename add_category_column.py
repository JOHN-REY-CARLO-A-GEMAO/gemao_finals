#!/usr/bin/env python3
"""Script to add category column to blog_posts table"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'MyFlaskapp'))

from MyFlaskapp.db import get_db_connection

def add_category_column():
    """Add category column to blog_posts table"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("SHOW COLUMNS FROM blog_posts LIKE 'category'")
        if cursor.fetchone():
            print("Category column already exists")
            return True
        
        # Add category column
        print("Adding category column to blog_posts table...")
        cursor.execute("""
            ALTER TABLE blog_posts 
            ADD COLUMN category ENUM('General', 'Updates', 'Announcements') DEFAULT 'General' AFTER tags
        """)
        
        # Update existing posts to have 'General' as default
        cursor.execute("UPDATE blog_posts SET category = 'General' WHERE category IS NULL")
        
        # Add index for category filtering
        cursor.execute("ALTER TABLE blog_posts ADD INDEX idx_category (category)")
        
        conn.commit()
        print("Category column added successfully!")
        return True
        
    except Exception as e:
        print(f"Error adding category column: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    add_category_column()
