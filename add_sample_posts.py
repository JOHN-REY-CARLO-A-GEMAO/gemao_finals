#!/usr/bin/env python3
"""Script to add sample blog posts with categories for testing"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'MyFlaskapp'))

from MyFlaskapp.db import get_db_connection
from datetime import datetime

def add_sample_posts():
    """Add sample blog posts with different categories"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Sample posts with categories
        sample_posts = [
            {
                'title': 'Welcome to Our Ninja Academy',
                'content': 'Welcome to the Naruto-themed blog system! This is a general announcement about our new platform where you can find games, tutorials, and community updates.',
                'author_id': '573',
                'category': 'General',
                'status': 'published',
                'tags': 'welcome, introduction, academy'
            },
            {
                'title': 'New Rasengan Training Game Released',
                'content': 'We are excited to announce the release of our new Rasengan Training game! Test your reaction time and see how fast you can charge your Rasengan. This game features multiple difficulty levels and high score tracking.',
                'author_id': '573',
                'category': 'Updates',
                'status': 'published',
                'tags': 'game, rasengan, update, release'
            },
            {
                'title': 'System Maintenance Scheduled',
                'content': 'Important announcement: Our system will undergo scheduled maintenance this weekend from 2 AM to 6 AM EST. During this time, some features may be temporarily unavailable. We apologize for any inconvenience.',
                'author_id': '573',
                'category': 'Announcements',
                'status': 'published',
                'tags': 'maintenance, announcement, system'
            },
            {
                'title': 'Ninja Trivia Challenge Tips',
                'content': 'Here are some helpful tips for mastering our Ninja Trivia Challenge game. Learn about the different question categories, how to earn bonus points, and strategies for achieving high scores.',
                'author_id': '573',
                'category': 'General',
                'status': 'published',
                'tags': 'tips, trivia, tutorial, game'
            },
            {
                'title': 'User Dashboard Improvements',
                'content': 'We have updated the user dashboard with new features including better game statistics, achievement tracking, and personalized recommendations. Check out the improved interface and let us know what you think!',
                'author_id': '573',
                'category': 'Updates',
                'status': 'published',
                'tags': 'dashboard, update, features, improvement'
            }
        ]
        
        for post in sample_posts:
            cursor.execute("""
                INSERT INTO blog_posts (title, content, author_id, category, status, tags, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                content = VALUES(content),
                category = VALUES(category),
                updated_at = VALUES(updated_at)
            """, (
                post['title'],
                post['content'],
                post['author_id'],
                post['category'],
                post['status'],
                post['tags'],
                datetime.now(),
                datetime.now()
            ))
        
        conn.commit()
        print(f"Added {len(sample_posts)} sample blog posts with categories!")
        return True
        
    except Exception as e:
        print(f"Error adding sample posts: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    add_sample_posts()
