from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.utils import secure_filename
from . import blog_bp
from MyFlaskapp.db import get_db_connection
from MyFlaskapp.utils import login_required, log_activity
from MyFlaskapp.utils.decorators import admin_required
from datetime import datetime
import os

def get_category_counts():
    """Get post counts for each category"""
    conn = get_db_connection()
    categories = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM blog_posts 
                WHERE status = 'published' AND category IS NOT NULL
                GROUP BY category
                ORDER BY count DESC
            """)
            categories = cursor.fetchall()
            
        except Exception as e:
            print(f"Error getting category counts: {e}")
        finally:
            conn.close()
    
    return categories

@blog_bp.route('/')
def index():
    """Blog home page - list all published posts"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    conn = get_db_connection()
    posts = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT bp.*, u.firstname, u.lastname, u.username,
                       (SELECT COUNT(*) FROM blog_comments WHERE post_id = bp.id AND status = 'approved') as comment_count
                FROM blog_posts bp 
                LEFT JOIN user_tb u ON bp.author_id = u.user_id 
                WHERE bp.status = 'published'
            """
            params = []
            
            if search:
                query += " AND (bp.title LIKE %s OR bp.content LIKE %s)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param])
            
            if category:
                query += " AND bp.category = %s"
                params.append(category)
            
            query += " ORDER BY bp.created_at DESC LIMIT 20"
            
            cursor.execute(query, params)
            posts = cursor.fetchall()
            
        except Exception as e:
            print(f"Error getting blog posts: {e}")
        finally:
            conn.close()
    
    # Get category counts for sidebar
    categories = get_category_counts()
    
    return render_template('blog/index.html', posts=posts, search=search, category=category, categories=categories)

@blog_bp.route('/post/<int:post_id>')
def view_post(post_id):
    """View individual blog post"""
    conn = get_db_connection()
    post = {}
    comments = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get post
            cursor.execute("""
                SELECT bp.*, u.firstname, u.lastname, u.username
                FROM blog_posts bp 
                LEFT JOIN user_tb u ON bp.author_id = u.user_id 
                WHERE bp.id = %s AND bp.status = 'published'
            """, (post_id,))
            post = cursor.fetchone()
            
            if post:
                # Increment view count
                cursor.execute("UPDATE blog_posts SET view_count = view_count + 1 WHERE id = %s", (post_id,))
                conn.commit()
                
                # Get approved comments
                cursor.execute("""
                    SELECT bc.*, u.firstname, u.lastname, u.username
                    FROM blog_comments bc
                    LEFT JOIN user_tb u ON bc.user_id = u.user_id
                    WHERE bc.post_id = %s AND bc.status = 'approved'
                    ORDER BY bc.created_at ASC
                """, (post_id,))
                comments = cursor.fetchall()
            
        except Exception as e:
            print(f"Error viewing post: {e}")
        finally:
            conn.close()
    
    if not post:
        flash('Post not found', 'danger')
        return redirect(url_for('blog.index'))
    
    return render_template('blog/view_post.html', post=post, comments=comments)

@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create new blog post"""
    user_id = session.get('user_id')
    user_role = session.get('user_role', 'user')
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        tags = request.form.get('tags', '')
        category = request.form.get('category', 'General')
        
        # Determine status based on user role
        if user_role == 'admin':
            status = request.form.get('status', 'published')  # Admins can publish directly
        else:
            status = 'draft'  # Non-admin posts always start as draft (require approval)
        
        if not title or not content:
            flash('Title and content are required', 'danger')
            return render_template('blog/create_post.html', user_role=user_role)
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO blog_posts (title, content, author_id, status, tags, category)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (title, content, user_id, status, tags, category))
                conn.commit()
                
                post_id = cursor.lastrowid
                log_activity(user_id, 'blog_post_created', f'Created blog post: {title}', request.remote_addr)
                
                if user_role == 'admin':
                    if status == 'published':
                        flash('Blog post published successfully!', 'success')
                    else:
                        flash('Blog post saved as draft', 'info')
                else:
                    flash('Blog post submitted for admin approval', 'info')
                
                return redirect(url_for('blog.my_posts') if user_role != 'admin' else url_for('blog.view_post', post_id=post_id))
                
            except Exception as e:
                print(f"Error creating post: {e}")
                flash('Error creating blog post', 'danger')
            finally:
                conn.close()
    
    return render_template('blog/create_post.html', user_role=user_role)

@blog_bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit existing blog post"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    conn = get_db_connection()
    post = {}
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get post and check permissions
            cursor.execute("""
                SELECT * FROM blog_posts 
                WHERE id = %s AND (author_id = %s OR %s = 'admin')
            """, (post_id, user_id, user_role))
            post = cursor.fetchone()
            
            if not post:
                flash('Post not found or access denied', 'danger')
                return redirect(url_for('blog.index'))
            
            if request.method == 'POST':
                title = request.form.get('title')
                content = request.form.get('content')
                tags = request.form.get('tags', '')
                category = request.form.get('category', 'General')
                status = request.form.get('status', 'draft')
                
                if not title or not content:
                    flash('Title and content are required', 'danger')
                    return render_template('blog/edit_post.html', post=post)
                
                cursor.execute("""
                    UPDATE blog_posts 
                    SET title = %s, content = %s, tags = %s, category = %s, status = %s, updated_at = NOW()
                    WHERE id = %s
                """, (title, content, tags, category, status, post_id))
                conn.commit()
                
                log_activity(user_id, 'blog_post_updated', f'Updated blog post: {title}', request.remote_addr)
                
                if status == 'published':
                    flash('Blog post updated and published!', 'success')
                else:
                    flash('Blog post updated as draft', 'info')
                
                return redirect(url_for('blog.view_post', post_id=post_id))
            
        except Exception as e:
            print(f"Error editing post: {e}")
            flash('Error editing blog post', 'danger')
        finally:
            conn.close()
    
    return render_template('blog/edit_post.html', post=post)

@blog_bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete blog post"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get post and check permissions
            cursor.execute("""
                SELECT title FROM blog_posts 
                WHERE id = %s AND (author_id = %s OR %s = 'admin')
            """, (post_id, user_id, user_role))
            post = cursor.fetchone()
            
            if post:
                # Delete comments first
                cursor.execute("DELETE FROM blog_comments WHERE post_id = %s", (post_id,))
                # Delete post
                cursor.execute("DELETE FROM blog_posts WHERE id = %s", (post_id,))
                conn.commit()
                
                log_activity(user_id, 'blog_post_deleted', f'Deleted blog post: {post["title"]}', request.remote_addr)
                flash('Blog post deleted successfully', 'success')
            else:
                flash('Post not found or access denied', 'danger')
                
        except Exception as e:
            print(f"Error deleting post: {e}")
            flash('Error deleting blog post', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('blog.index'))

@blog_bp.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add comment to blog post"""
    user_id = session.get('user_id')
    comment_text = request.form.get('comment')
    
    if not comment_text:
        flash('Comment cannot be empty', 'danger')
        return redirect(url_for('blog.view_post', post_id=post_id))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO blog_comments (post_id, user_id, comment, status)
                VALUES (%s, %s, %s, 'pending')
            """, (post_id, user_id, comment_text))
            conn.commit()
            
            log_activity(user_id, 'comment_added', f'Added comment to post {post_id}', request.remote_addr)
            flash('Comment submitted for approval', 'info')
            
        except Exception as e:
            print(f"Error adding comment: {e}")
            flash('Error adding comment', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('blog.view_post', post_id=post_id))

@blog_bp.route('/my-posts')
@login_required
def my_posts():
    """View current user's blog posts"""
    user_id = session.get('user_id')
    user_role = session.get('user_role', 'user')
    
    conn = get_db_connection()
    posts = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT bp.*, 
                       (SELECT COUNT(*) FROM blog_comments WHERE post_id = bp.id) as comment_count
                FROM blog_posts bp 
                WHERE bp.author_id = %s 
                ORDER BY bp.created_at DESC
            """, (user_id,))
            posts = cursor.fetchall()
            
        except Exception as e:
            print(f"Error getting user posts: {e}")
        finally:
            conn.close()
    
    return render_template('blog/my_posts.html', posts=posts, user_role=user_role)

@blog_bp.route('/admin/pending')
@admin_required
def pending_posts():
    """Admin route to view pending posts for approval"""
    conn = get_db_connection()
    posts = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT bp.*, u.firstname, u.lastname, u.username,
                       (SELECT COUNT(*) FROM blog_comments WHERE post_id = bp.id) as comment_count
                FROM blog_posts bp 
                LEFT JOIN user_tb u ON bp.author_id = u.user_id 
                WHERE bp.status = 'draft'
                ORDER BY bp.created_at DESC
            """)
            posts = cursor.fetchall()
            
        except Exception as e:
            print(f"Error getting pending posts: {e}")
        finally:
            conn.close()
    
    return render_template('blog/pending_posts.html', posts=posts)

@blog_bp.route('/admin/approve/<int:post_id>', methods=['POST'])
@admin_required
def approve_post(post_id):
    """Admin route to approve a pending post"""
    user_id = session.get('user_id')
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get post details
            cursor.execute("SELECT title FROM blog_posts WHERE id = %s", (post_id,))
            post = cursor.fetchone()
            
            if post:
                # Approve the post
                cursor.execute("UPDATE blog_posts SET status = 'published', updated_at = NOW() WHERE id = %s", (post_id,))
                conn.commit()
                
                log_activity(user_id, 'blog_post_approved', f'Approved blog post: {post["title"]}', request.remote_addr)
                flash('Blog post approved and published!', 'success')
            else:
                flash('Post not found', 'danger')
                
        except Exception as e:
            print(f"Error approving post: {e}")
            flash('Error approving blog post', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('blog.pending_posts'))

@blog_bp.route('/admin/reject/<int:post_id>', methods=['POST'])
@admin_required
def reject_post(post_id):
    """Admin route to reject a pending post"""
    user_id = session.get('user_id')
    rejection_reason = request.form.get('reason', 'No reason provided')
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get post details
            cursor.execute("SELECT title FROM blog_posts WHERE id = %s", (post_id,))
            post = cursor.fetchone()
            
            if post:
                # Delete the post (rejection)
                cursor.execute("DELETE FROM blog_posts WHERE id = %s", (post_id,))
                conn.commit()
                
                log_activity(user_id, 'blog_post_rejected', f'Rejected blog post: {post["title"]} - Reason: {rejection_reason}', request.remote_addr)
                flash('Blog post rejected', 'warning')
            else:
                flash('Post not found', 'danger')
                
        except Exception as e:
            print(f"Error rejecting post: {e}")
            flash('Error rejecting blog post', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('blog.pending_posts'))

@blog_bp.route('/admin/all-posts')
@admin_required
def admin_all_posts():
    """Admin route to view all posts with management controls"""
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    conn = get_db_connection()
    posts = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT bp.*, u.firstname, u.lastname, u.username,
                       (SELECT COUNT(*) FROM blog_comments WHERE post_id = bp.id) as comment_count
                FROM blog_posts bp 
                LEFT JOIN user_tb u ON bp.author_id = u.user_id 
            """
            params = []
            
            if status_filter != 'all':
                query += " WHERE bp.status = %s"
                params.append(status_filter)
            
            query += " ORDER BY bp.created_at DESC LIMIT 50"
            
            cursor.execute(query, params)
            posts = cursor.fetchall()
            
        except Exception as e:
            print(f"Error getting admin posts: {e}")
        finally:
            conn.close()
    
    return render_template('blog/admin_all_posts.html', posts=posts, status_filter=status_filter)
