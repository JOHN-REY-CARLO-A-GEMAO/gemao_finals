import sys
sys.path.append('.')
from MyFlaskapp.db import get_db_connection

conn = get_db_connection()
if conn:
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT COUNT(*) as count FROM blog_posts WHERE status = "published"')
    result = cursor.fetchone()
    print(f'Published blog posts: {result["count"]}')
    
    cursor.execute('SELECT COUNT(*) as count FROM blog_posts')
    result = cursor.fetchone()
    print(f'Total blog posts: {result["count"]}')
    
    cursor.execute('SELECT id, title, status, created_at FROM blog_posts LIMIT 5')
    posts = cursor.fetchall()
    print('Sample posts:')
    for post in posts:
        print(f'  ID: {post["id"]}, Title: {post["title"]}, Status: {post["status"]}')
    
    conn.close()
else:
    print('Database connection failed')
